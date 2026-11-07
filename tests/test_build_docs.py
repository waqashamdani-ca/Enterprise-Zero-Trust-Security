"""Artifact-level PDF tests: text, navigation, pagination, fidelity, and drift."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_docs", ROOT / "scripts/build_docs.py")
docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docs)
VALIDATOR_SPEC = importlib.util.spec_from_file_location("pdf_publication", ROOT / "scripts/validate_docs.py")
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)


def quiet_build(root, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return docs.build(root=root, **kwargs)


class PdfArtifactTests(unittest.TestCase):
    content = b"# Fixture\n\n## Access\n\n[Jump](#access) and [reference](https://example.com).\n\n```powershell\nGet-Item .\n```\n"

    def test_pdf_text_links_named_navigation_and_metadata(self):
        data = docs.render_pdf("fixture.md", self.content, {"fixture.md"})
        reader = docs.PdfReader(io.BytesIO(data))
        text = " ".join(page.extract_text() for page in reader.pages)
        self.assertIn("Get-Item .", text)
        self.assertIn("Page 1", text)
        self.assertIn("access", reader.named_destinations)
        self.assertNotIn(str(ROOT), str(reader.metadata))
        details = docs.inspect_pdf(data, "fixture.md", self.content)
        self.assertEqual(details["uri_links"], 1)
        self.assertGreaterEqual(details["internal_links"], 1)
        self.assertGreaterEqual(details["text_token_coverage"], 0.975)

    def test_repeated_render_is_byte_identical(self):
        first = docs.render_pdf("fixture.md", self.content, {"fixture.md"})
        second = docs.render_pdf("fixture.md", self.content, {"fixture.md"})
        self.assertEqual(first, second)

    def test_long_table_repeats_headers_and_retains_last_row(self):
        source = "# Long table\n\n## Records\n\n| ID | Description |\n| --- | --- |\n"
        for number in range(80):
            source += f"| R{number:03d} | Synthetic record {number}; readable wrapping text with a declared expected result and evidence. |\n"
        content = source.encode()
        data = docs.render_pdf("fixture.md", content, {"fixture.md"})
        reader = docs.PdfReader(io.BytesIO(data))
        self.assertGreater(len(reader.pages), 2)
        self.assertIn("R079", " ".join(page.extract_text() for page in reader.pages))
        self.assertGreater(sum("Description" in page.extract_text() for page in reader.pages), 1)
        docs.inspect_pdf(data, "fixture.md", content)

    def test_build_detects_stale_source_and_does_not_rewrite_unchanged_outputs(self):
        base = ROOT / "local/pdf-tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            self.assertTrue(root.resolve().is_relative_to(base.resolve()))
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / "docs").mkdir()
            (root / "fixture.md").write_bytes(self.content)
            (root / ".gitignore").write_text("private/\n", encoding="utf-8")
            (root / "private").mkdir()
            (root / "private/notes.md").write_text("Not a public source", encoding="utf-8")
            self.assertNotIn("private/notes.md", docs.discover_sources(root))
            quiet_build(root)
            pdf = root / "fixture.pdf"
            stamp, data = pdf.stat().st_mtime_ns, pdf.read_bytes()
            quiet_build(root)
            self.assertEqual(pdf.stat().st_mtime_ns, stamp)
            self.assertEqual(pdf.read_bytes(), data)
            quiet_build(root, check=True, rebuild_check=True)
            (root / "fixture.md").write_bytes(self.content + b"\nAdded source text.\n")
            with self.assertRaisesRegex(ValueError, "Stale/missing"):
                quiet_build(root, check=True)
            self.assertEqual(pdf.read_bytes(), data)

    def test_unknown_or_changed_binary_pdf_is_rejected(self):
        base = ROOT / "local/pdf-tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            self.assertTrue(root.resolve().is_relative_to(base.resolve()))
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / "docs").mkdir()
            (root / "fixture.md").write_bytes(self.content)
            quiet_build(root)
            self.assertEqual(validator.generated_pdf_issues(root, "fixture.pdf"), [])
            (root / "fixture.pdf").write_bytes((root / "fixture.pdf").read_bytes() + b"\nchanged")
            self.assertTrue(any("differ" in item for item in validator.generated_pdf_issues(root, "fixture.pdf")))
            self.assertTrue(validator.generated_pdf_issues(root, "unapproved.pdf"))

    def test_reports_are_excluded_and_report_edits_do_not_churn_document_pdfs(self):
        base = ROOT / "local/pdf-tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / "docs").mkdir()
            (root / "docs/reports/nested").mkdir(parents=True)
            content = b"# Guide\n\n[Task record](docs/reports/T1-Report.md#c-testing-and-validation).\n"
            (root / "guide.md").write_bytes(content)
            for name in ("README.md", "T1-Report.md", "T1-Addendum-001-Format.md", "nested/guide.md"):
                (root / "docs/reports" / name).write_text("Not a PDF source; no title required.\n", encoding="utf-8")
            archive = root / "docs/reports/T1-Report.pdf"
            archive.write_bytes(b"untouched archive fixture")
            self.assertEqual(docs.discover_sources(root), ["guide.md"])
            first = quiet_build(root)
            self.assertEqual([entry["source"] for entry in first["documents"]], ["guide.md"])
            pdf = root / "guide.pdf"
            stamp, data = pdf.stat().st_mtime_ns, pdf.read_bytes()
            archive_stamp = archive.stat().st_mtime_ns
            (root / "docs/reports/T1-Report.md").write_text("Updated report only.\n", encoding="utf-8")
            second = quiet_build(root, check=True, rebuild_check=True)
            self.assertEqual(first, second)
            self.assertEqual((pdf.stat().st_mtime_ns, pdf.read_bytes()), (stamp, data))
            self.assertEqual((archive.stat().st_mtime_ns, archive.read_bytes()),
                             (archive_stamp, b"untouched archive fixture"))
            self.assertEqual(list((root / "docs/reports").rglob("*.pdf")), [archive])

    def test_direct_report_pdf_generation_is_refused(self):
        for name in ("docs/reports/T1-Report.md", "docs/reports/README.md", "docs/reports/INDEX.md", "docs/reports/nested/guide.md", "DOCS/REPORTS/Guide.md", "reports/T1-Report.md"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Markdown only"):
                docs.render_pdf(name, self.content, {name})

    def test_pdf_report_links_open_markdown_with_normal_heading_anchors(self):
        target = docs.REPOSITORY + "/blob/main/docs/reports/T1-Report.md#c-testing-and-validation"
        content = b"# Guide\n\n[Task record](reports/T1-Report.md#c-testing-and-validation).\n"
        self.assertEqual(docs.resolve_link("docs/guide.md", "reports/T1-Report.md#c-testing-and-validation", {"docs/guide.md"}), target)
        data = docs.render_pdf("docs/guide.md", content, {"docs/guide.md"})
        reader = docs.PdfReader(io.BytesIO(data))
        uris = [str(ref.get_object()["/A"]["/URI"]) for page in reader.pages
                for ref in page.get("/Annots", []) if ref.get_object().get("/A", {}).get("/S") == "/URI"]
        self.assertEqual(uris, [target])
        self.assertEqual(docs.inspect_pdf(data, "docs/guide.md", content)["uri_links"], 1)
        with self.assertRaisesRegex(ValueError, "Unknown PDF source"):
            docs.resolve_link("docs/guide.md", "missing.md", {"docs/guide.md"})

    def test_markdown_reports_need_no_pdf_and_cannot_enter_generated_inventory(self):
        report = "# Report\n\nReport state: FINALIZED\n\n"
        for section in validator.REPORT_SECTIONS:
            report += "## " + section + "\n\n"
            if section == "A. Task Information":
                report += "| Field | Record |\n| --- | --- |\n| Task ID | T1 |\n\n"
            report += "Fixture evidence.\n\n"
        manifest = {"schema": 1, "documents": [{"source": "guide.md", "pdf": "guide.pdf"}]}
        texts = {"guide.md": "# Guide\n", "docs/reports/T1-Report.md": report,
                 "docs/reports/README.md": "# Report index\n", validator.PDF_MANIFEST: json.dumps(manifest)}
        paths = list(texts) + ["guide.pdf"]  # No report PDFs, including optional archives.
        self.assertEqual(validator.report_issues(texts, require_finalized=True), [])
        self.assertEqual(validator.pdf_inventory_issues(paths, texts), [])
        manifest["documents"].append({"source": "docs/reports/T1-Report.md", "pdf": "docs/reports/T1-Report.pdf"})
        texts[validator.PDF_MANIFEST] = json.dumps(manifest)
        self.assertTrue(validator.pdf_inventory_issues(paths + ["docs/reports/T1-Report.pdf"], texts))
        manifest["documents"] = [{"source": "guide.md", "pdf": "docs/reports/T1-Report.pdf"}]
        texts[validator.PDF_MANIFEST] = json.dumps(manifest)
        self.assertTrue(validator.pdf_inventory_issues(paths + ["docs/reports/T1-Report.pdf"], texts))

    def test_historical_report_pdf_bytes_are_pinned_and_new_report_pdfs_are_rejected(self):
        base = ROOT / "local/pdf-tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            (root / "docs/reports").mkdir(parents=True)
            for name, expected in validator.ARCHIVED_REPORT_PDFS.items():
                with self.subTest(name=name):
                    data = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                                    validator.REPORT_ARCHIVE_BASELINE + ":" + name.removeprefix("docs/")])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
                    path = root / name
                    path.write_bytes(data)
                    self.assertEqual(validator.generated_pdf_issues(root, name), [])
                    (root / (name[:-4] + ".md")).write_text("Current Markdown need not match archive.\n", encoding="utf-8")
                    self.assertEqual(validator.generated_pdf_issues(root, name), [])
                    path.write_bytes(data + b"\nchanged")
                    self.assertTrue(any("frozen" in issue for issue in validator.generated_pdf_issues(root, name)))
            name = "docs/reports/T3-Addendum-001-Markdown-Only-Reporting.pdf"
            (root / name).write_bytes(docs.render_pdf("fixture.md", self.content, {"fixture.md"}))
            self.assertTrue(any("prohibited" in issue for issue in validator.generated_pdf_issues(root, name)))

    def test_diagram_keeps_offline_and_protected_nodes_disconnected(self):
        source = (ROOT / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        diagrams = [token for token in docs.MARKDOWN(source) if token["type"] == "block_code" and token.get("attrs", {}).get("info") == "mermaid"]
        self.assertEqual(len(diagrams), 1)
        nodes, edges = docs.parse_diagram(diagrams[0]["raw"])
        self.assertEqual(len(nodes), 11)
        self.assertEqual(len(edges), 10)
        self.assertFalse(any(a in {"CA", "HOME"} or b in {"CA", "HOME"} for a, b, _, _ in edges))
        self.assertEqual({b for a, b, label, _ in edges if a == "Remote"}, {"App"})
        self.assertEqual([label for a, b, label, _ in edges if a == "Remote"], ["HTTPS only"])
        with self.assertRaisesRegex(ValueError, "Unsupported Mermaid"):
            docs.parse_diagram(diagrams[0]["raw"] + "\nclick FW https://example.com\n")

    def test_pdf_link_targets_cannot_escape_or_use_active_schemes(self):
        with self.assertRaises(ValueError):
            docs.resolve_link("guide.md", "../private.pdf", {"guide.md"})
        with self.assertRaises(ValueError):
            docs.resolve_link("guide.md", "javascript:unsafe", {"guide.md"})
        target = docs.resolve_link("docs/reports/T1-Report.md", "../docs/DECISIONS.md", {"docs/governance/DECISIONS.md"})
        self.assertTrue(target.endswith("docs/governance/DECISIONS.pdf"))

    def test_frozen_report_aliases_exist_resolve_and_are_excluded_from_pdf_sources(self):
        self.assertEqual(set(docs.ALIASES), validator.PDF_ALIASES)
        sources = set(docs.discover_sources(ROOT))
        for alias, destination in docs.ALIASES.items():
            with self.subTest(alias=alias):
                self.assertTrue((ROOT / alias).is_file())
                self.assertTrue((ROOT / destination).is_file())
                self.assertNotIn(alias, sources)
                self.assertEqual(validator.link_issues(ROOT, alias, (ROOT / alias).read_text(encoding="utf-8")), [])
        record = json.loads((ROOT / "docs/docs/documentation-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / "docs/docs" / record["moved_to"]).resolve(), ROOT / docs.MANIFEST)
        self.assertEqual(record["url"], docs.REPOSITORY + "/blob/main/" + docs.MANIFEST)

    def test_assignment_is_concise_and_keeps_filenames_whole(self):
        content = (ROOT / docs.ASSIGNMENT).read_bytes()
        sources = set(docs.discover_sources(ROOT))
        data = docs.render_pdf(docs.ASSIGNMENT, content, sources)
        reader = docs.PdfReader(io.BytesIO(data))
        self.assertGreaterEqual(len(reader.pages), 3)
        self.assertLessEqual(len(reader.pages), 4)
        text = "\n".join(page.extract_text() for page in reader.pages)
        self.assertNotIn("Assignment contents", text)
        self.assertNotRegex(text, r"\b(?:T6A?|T7|A-L)\b")
        self.assertIn("PLANNED", text)
        self.assertIn("NOT TESTED", text)
        for name in validator.DELIVERABLE_FILENAMES:
            self.assertTrue(any(name in line for line in text.splitlines()), name)
        self.assertTrue(any(all(name in p.extract_text() for name in validator.DELIVERABLE_FILENAMES)
                            for p in reader.pages))
        self.assertTrue(any(all(f"FWT-{n:02d}" in p.extract_text() for n in range(1, 11))
                            for p in reader.pages))
        for title in validator.ASSIGNMENT_HEADINGS:
            self.assertIn(docs.anchor_for(title, set()), reader.named_destinations)
        for alias in validator.ASSIGNMENT_COMPATIBILITY_ANCHORS:
            self.assertIn(alias, reader.named_destinations)
        self.assertIn("100 points", text)
        self.assertEqual(docs.inspect_pdf(data, docs.ASSIGNMENT, content, sources)["text_token_coverage"], 1.0)
        rubric = content.decode().partition("## Evaluation Criteria")[2].split("\n## ", 1)[0]
        weights = [(name.strip(), int(points)) for name, points in
                   re.findall(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", rubric, re.M)]
        self.assertEqual(weights, list(validator.RUBRIC_WEIGHTS))

    def test_assignment_aliases_do_not_allow_active_html(self):
        content = b'# Assignment\n\n<a id="legacy" onclick="unsafe()"></a>\n\n## Section\n'
        with self.assertRaisesRegex(ValueError, "Unreviewed inline HTML"):
            docs.render_pdf(docs.ASSIGNMENT, content, {docs.ASSIGNMENT})

    def test_office_migration_preserves_unaffected_sources_pdfs_and_frozen_records(self):
        base = "d408c4571105bd42396dd5e71aae22f4f3d9290c"
        sources = {"README.md", "docs/README.md", docs.ASSIGNMENT, docs.GUIDE,
                   "docs/testing/TEST-PLAN.md", "docs/testing/ACCEPTANCE-CRITERIA.md",
                   "docs/governance/DECISIONS.md", "docs/governance/RISKS.md",
                   "docs/governance/DOCUMENTATION-BUILD.md"}
        allowed = sources | {n[:-3] + ".pdf" for n in sources} | {"docs/reports/INDEX.md", docs.MANIFEST}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        for name in files:
            if name in allowed or name.startswith("docs/deliverables/") or not name.endswith((".md", ".pdf", ".docx", ".xlsx")):
                continue
            old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
            self.assertEqual((ROOT / name).read_bytes(), old, name)

    def test_guide_pdf_keeps_filenames_whole_and_preserves_navigation(self):
        content = (ROOT / docs.GUIDE).read_bytes()
        sources = set(docs.discover_sources(ROOT))
        data = docs.render_pdf(docs.GUIDE, content, sources)
        reader = docs.PdfReader(io.BytesIO(data))
        pages = [p.extract_text() for p in reader.pages]
        text = "\n".join(pages)
        self.assertNotRegex(text, r"\b(?:T6[AB]?|T7|Codex)\b")
        self.assertIn("Guide contents", pages[0])
        self.assertIn("PLANNED", pages[0])
        self.assertIn("NOT TESTED", pages[0])
        self.assertTrue(any(all(name in p.splitlines() for name in validator.DELIVERABLE_FILENAMES)
                            for p in pages))
        for n, title in enumerate(validator.PHASE_TITLES, 1):
            self.assertIn(docs.anchor_for(f"Phase {n}: {title}", set()), reader.named_destinations)
        self.assertIn("required-lab-deliverables", reader.named_destinations)
        self.assertEqual(docs.inspect_pdf(data, docs.GUIDE, content, sources)["text_token_coverage"], 1.0)
        compact_pages = [re.sub(r"\s+", "", p) for p in pages]
        tokens = docs.MARKDOWN(content.decode())
        for index, token in enumerate(tokens):
            if token["type"] == "block_code":
                code = re.sub(r"\s+", "", docs.normalize(token["raw"]))
                self.assertTrue(any(code in p for p in compact_pages),
                                "Code block split across pages: " + token["raw"][:70])
                previous = next(t for t in reversed(tokens[:index]) if t["type"] != "blank_line")
                context = re.sub(r"\s+", "", docs.normalize(docs.plain(previous["children"])))
                self.assertTrue(any(code in p and context in p for p in compact_pages),
                                "Command target/context split from code: " + token["raw"][:70])
            if token["type"] == "list" and token.get("attrs", {}).get("ordered"):
                for item in token["children"]:
                    step = docs.normalize(docs.plain(item["children"][0]["children"]))
                    self.assertTrue(any(re.sub(r"\s+", "", step) in p for p in compact_pages),
                                    "Numbered step split across pages: " + step[:70])

    def test_guide_retains_core_commands_and_moves_publication_details_to_build_guide(self):
        base = "a3d7b1c6effde3bd5b18ab1a4b529c07a7cc7c61"
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + docs.GUIDE]).decode()
        current = (ROOT / docs.GUIDE).read_text(encoding="utf-8")
        fences = r"^```([^\n]*)\n(.*?)^```"
        current_blocks = re.findall(fences, current, re.M | re.S)
        for language, block in re.findall(fences, old, re.M | re.S):
            if block.startswith("<VirtualHost"):
                site = next(b for lang, b in current_blocks if lang == "apache" and b.startswith("<VirtualHost *:443>"))
                # T8 adds explicit site logs; every approved TLS/auth directive stays.
                for line in block.splitlines():
                    self.assertIn(line, site)
            elif "python scripts/validate_docs.py" in block:
                build_guide = (ROOT / "docs/governance/DOCUMENTATION-BUILD.md").read_text(encoding="utf-8")
                for line in block.splitlines():
                    # The build guide uses its explicit pinned-environment executable.
                    self.assertIn(line.partition("python ")[2] if "python " in line else line, build_guide)
                self.assertNotIn("scripts/validate_docs.py", current)
            else:
                self.assertIn((language, block), current_blocks)
        for command in ("Test-ComputerSecureChannel -Verbose", "apachectl configtest", "tailscale status",
                        "htpasswd -B -c /etc/labapp/users ava", "htpasswd -B /etc/labapp/users eli"):
            self.assertIn(command, old)
            self.assertIn(command, current)

    def test_five_active_templates_replace_eight_recoverable_originals_in_history(self):
        baseline = "6f5352bb6d5e2eca37ac2384703367543530b952"
        names = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only",
                                         baseline, "--", "docs/deliverables"]).decode().splitlines()
        self.assertEqual(len(names), 8)
        current = sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                         for p in (ROOT / "docs/deliverables").iterdir())
        self.assertEqual(current, sorted("docs/deliverables/" + n for n in validator.DELIVERABLE_FILENAMES))
        self.assertFalse(set(current) & set(names))
        expected = {
            "01-Lab-Environment.xlsx": "afb0a0ecaec2c76b665d83382414074f79debd0bc6b8f4394c365fb89abe5656",
            "02-Architecture-and-Network-Design.docx": "81b41b07cc6f5cb36ca1b4303bb4a5ad6c6a0222b23980299ce52af83a926c66",
            "03-Identity-and-Access-Management.xlsx": "2c0fc70f5776bd7b4559a095fb965cdd08ca43c217d2170ef01579cae250d251",
            "04-Zero-Trust-Implementation.docx": "cf600aeb6903ca167f43f3a0d12a17d4cd73f1fd978c05b8287931bf793c5985",
            "05-Security-Monitoring.xlsx": "c9a1839a440689ae0bfff6556136dbda7d1d4b9c25c632224eb5e3cf716f6248",
            "06-Testing-and-Validation.xlsx": "2c1ad86eaba5e26bc3ed401e71797fab6e45e199bb5554fca860b66289734530",
            "07-Troubleshooting-and-Lessons.xlsx": "95e5e8ad44035b325cd13d5c4310fdf7573e7b8870d39b8fd2cbcc90b62c93a7",
            "08-Final-Lab-Submission.docx": "49087edf0b43626d41c563a651b3495ee67d600d75cb67be5664c8b34f8d9dba",
        }
        for name in names:
            old = subprocess.check_output(["git", "-C", str(ROOT), "show", baseline + ":" + name])
            self.assertEqual(hashlib.sha256(old).hexdigest(), expected[Path(name).name], name)


if __name__ == "__main__":
    unittest.main()
