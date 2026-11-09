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

    def test_diagram_preserves_physical_chain_three_boundaries_and_app_only_overlay(self):
        source = (ROOT / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        diagrams = [token for token in docs.MARKDOWN(source) if token["type"] == "block_code" and token.get("attrs", {}).get("info") == "mermaid"]
        self.assertEqual(len(diagrams), 1)
        nodes, edges, boundaries = docs.parse_diagram(diagrams[0]["raw"])
        self.assertEqual(len(nodes), 10)
        self.assertEqual(len(edges), 9)
        self.assertEqual(set(boundaries), {"Management", "Corporate", "Restricted"})
        self.assertIn("physical OPNsense", nodes["FW"])
        self.assertIn("Dell Precision 5820", nodes["Host"])
        self.assertEqual({(a, b) for a, b, _, dotted in edges if not dotted},
                         {("FW", "Switch"), ("Switch", "Host"), ("Host", "Corp"),
                          ("Host", "App"), ("Admin", "Mgmt")})
        self.assertIn(("WAN", "FW", "Egress approval gate", True), edges)
        self.assertFalse(any(a == "HOME" or b == "HOME" for a, b, _, _ in edges))
        self.assertEqual({b for a, b, label, _ in edges if a == "Remote"}, {"App"})
        self.assertEqual([label for a, b, label, _ in edges if a == "Remote"], ["FF-06: APP1 TCP 443"])
        with self.assertRaisesRegex(ValueError, "Unsupported Mermaid"):
            docs.parse_diagram(diagrams[0]["raw"] + "\nclick FW https://example.com\n")
        with self.assertRaisesRegex(ValueError, "boundaries changed"):
            docs.parse_diagram(diagrams[0]["raw"].replace("subgraph Corporate", "subgraph Extra"))
        with self.assertRaisesRegex(ValueError, "Unclosed"):
            docs.parse_diagram(diagrams[0]["raw"].replace("    end\n", "", 1).split("subgraph Corporate")[0])

    def test_architecture_capacity_and_flow_contract(self):
        content = (ROOT / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| (DC1|WIN1|APP1) \| (\d+) \| (\d+) \| (\d+) \|", content, re.M)
        self.assertEqual({name: tuple(map(int, values)) for name, *values in rows},
                         {"DC1": (2, 6, 64), "WIN1": (2, 6, 64), "APP1": (2, 4, 32)})
        self.assertEqual(tuple(sum(int(row[i]) for row in rows) for i in range(1, 4)), (6, 16, 160))
        self.assertIn("| Total | 6 | 16 | 160 |", content)
        self.assertIn("**320 GiB**", content)
        self.assertEqual(re.findall(r"^\| (FF-\d\d) \|", content, re.M), [f"FF-{n:02d}" for n in range(1, 9)])
        self.assertNotRegex(content, r"\b(?:Ordered|Delivered|Installed|T9[A-F]?|Codex)\b")
        self.assertNotRegex(content, r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\bVLAN\s+\d+|\bvmbr\d+")
        sources = set(docs.discover_sources(ROOT))
        data = docs.render_pdf("docs/architecture/ARCHITECTURE.md", content.encode(), sources)
        extracted = "\n".join(p.extract_text() for p in docs.PdfReader(io.BytesIO(data)).pages)
        for phrase in ("physical OPNsense", "Dell Precision 5820", "TL-SG108E", "Management boundary",
                       "Corporate boundary", "Restricted boundary", "APP1 TCP 443", "320 GiB"):
            self.assertIn(phrase, extracted)
        self.assertNotIn("operational controls NOT TESTED", extracted)
        self.assertIn("Contents", docs.PdfReader(io.BytesIO(data)).pages[0].extract_text())
        self.assertIn("hardware-status-and-preparation", docs.PdfReader(io.BytesIO(data)).named_destinations)

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
        self.assertNotRegex(text, r"\b(?:T[0-9]+[A-F]?|Codex|A-L|PLANNED|NOT TESTED|UAT PENDING)\b")
        for name in validator.DELIVERABLE_FILENAMES:
            self.assertTrue(any(name in line for line in text.splitlines()), name)
        self.assertTrue(any(all(name in p.extract_text() for name in validator.DELIVERABLE_FILENAMES)
                            for p in reader.pages))
        pages = [page.extract_text() for page in reader.pages]
        # Tables may continue with repeated headers; each complete requirement
        # and its matching test must stay on one page without a split row.
        for row in re.findall(r"^\| (FWR-\d{2}) \| ([^|]+) \| (FWT-\d{2}) \|$", content.decode(), re.M):
            self.assertTrue(any(all(re.sub(r"\s+", "", cell) in re.sub(r"\s+", "", page)
                                    for cell in row) for page in pages), row[0])
        for title in validator.ASSIGNMENT_HEADINGS:
            self.assertIn(docs.anchor_for(title, set()), reader.named_destinations)
        for alias in validator.ASSIGNMENT_COMPATIBILITY_ANCHORS:
            self.assertIn(alias, reader.named_destinations)
        self.assertIn("100 points", text)
        self.assertEqual(docs.inspect_pdf(data, docs.ASSIGNMENT, content, sources)["text_token_coverage"], 1.0)
        rubric = content.decode().partition("## Evaluation Rubric")[2].split("\n## ", 1)[0]
        weights = [(name.strip(), int(points)) for name, points in
                   re.findall(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", rubric, re.M)]
        self.assertEqual(weights, list(validator.RUBRIC_WEIGHTS))

    def test_assignment_aliases_do_not_allow_active_html(self):
        content = b'# Assignment\n\n<a id="legacy" onclick="unsafe()"></a>\n\n## Section\n'
        for source in (docs.ASSIGNMENT, docs.ARCHITECTURE):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, "Unreviewed inline HTML"):
                docs.render_pdf(source, content, {source})

    def test_office_migration_preserves_unaffected_sources_pdfs_and_frozen_records(self):
        base = "d408c4571105bd42396dd5e71aae22f4f3d9290c"
        published = "1fbc006450d5a9815844202bf3f1098283f8a0b6"
        sources = {"README.md", "AGENTS.md", "docs/README.md", docs.ASSIGNMENT, docs.GUIDE,
                   "docs/testing/TEST-PLAN.md", "docs/testing/ACCEPTANCE-CRITERIA.md",
                   "docs/governance/DECISIONS.md", "docs/governance/RISKS.md",
                   "docs/governance/DOCUMENTATION-BUILD.md"}
        allowed = sources | {n[:-3] + ".pdf" for n in sources} | {"docs/reports/INDEX.md", docs.MANIFEST}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        for name in files:
            if name in allowed or name.startswith("docs/deliverables/") or not name.endswith((".md", ".pdf", ".docx", ".xlsx")):
                continue
            old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
            actual = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
            self.assertEqual(actual, old, name)

    def test_t9_initialization_preserves_t8_specifications_office_and_history(self):
        # Check the immutable published initialization snapshot. Each later
        # microtask has a separate bounded preservation contract below.
        base = "1f8c7f9a99ee488fcb5673f6b3914e87ec50fed9"
        published = "1fbc006450d5a9815844202bf3f1098283f8a0b6"
        allowed = {"AGENTS.md", "AGENTS.pdf", "docs/reports/INDEX.md", docs.MANIFEST,
                   "scripts/validate_docs.py", "tests/test_validate_docs.py", "tests/test_build_docs.py"}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        for name in files:
            if name in allowed:
                continue
            old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
            actual = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
            self.assertEqual(actual, old, name)

    def test_t9a_preserves_all_excluded_sources_pdfs_office_and_history(self):
        base = "1fbc006450d5a9815844202bf3f1098283f8a0b6"
        published = "7387219ab2c4690e5bbed3615c47d892f13b0e12"
        allowed = {"docs/architecture/ARCHITECTURE.md", "docs/architecture/ARCHITECTURE.pdf",
                   "docs/governance/DECISIONS.md", "docs/governance/DECISIONS.pdf",
                   "docs/governance/RISKS.md", "docs/governance/RISKS.pdf",
                   "scripts/build_docs.py", "tests/test_build_docs.py", docs.MANIFEST,
                   "docs/reports/T9-Report.md"}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files), "T9A introduces no additional public files")
        for name in files:
            if name not in allowed:
                old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
                actual = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
                self.assertEqual(actual, old, name)

    def test_t9b_preserves_every_excluded_file_and_other_t9_sections(self):
        base = "7387219ab2c4690e5bbed3615c47d892f13b0e12"
        # T9B is published. Retain every assertion against that immutable
        # snapshot; the separately authorized T9C.1 boundary is checked below.
        published = "cb344c8be49e1c6a57489c5031f825df6b7ad1ea"
        allowed = {docs.ASSIGNMENT, docs.ASSIGNMENT[:-3] + ".pdf", docs.MANIFEST,
                   "scripts/validate_docs.py", "tests/test_validate_docs.py", "tests/test_build_docs.py",
                   "scripts/validate_office_templates.py", "tests/test_office_templates.py",
                   "docs/reports/T9-Report.md"}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files), "T9B introduces no additional public files")
        for name in files:
            if name not in allowed:
                old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
                actual = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
                self.assertEqual(actual, old, name)
        report = "docs/reports/T9-Report.md"
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + report])
        new = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + report])
        for value in (old, new):
            self.assertEqual(value.count(b"### T9B - Assignment Refinement\n"), 1)
            self.assertEqual(value.count(b"### T9C - Lab Guide Simplification\n"), 1)
        def outside_t9b(value):
            before, rest = value.split(b"### T9B - Assignment Refinement\n", 1)
            _, after = rest.split(b"### T9C - Lab Guide Simplification\n", 1)
            return before, after
        self.assertEqual(outside_t9b(new), outside_t9b(old))
        old_manifest = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + docs.MANIFEST]))
        new_manifest = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + docs.MANIFEST]))
        for manifest in (old_manifest, new_manifest):
            manifest["documents"] = [entry for entry in manifest["documents"] if entry["source"] != docs.ASSIGNMENT]
        self.assertEqual(new_manifest, old_manifest)

    def test_t9c1_preserves_every_excluded_file_and_other_report_sections(self):
        base = "cb344c8be49e1c6a57489c5031f825df6b7ad1ea"
        # Keep the full published sample/refinement boundary immutable.
        # The live T9C.2 boundary has its own stricter check below.
        published = "f41a5f296a772faa76df3089cb86b4b12b044d13"
        report = "docs/reports/T9-Report.md"
        allowed = {report, "tests/test_build_docs.py"}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files), "T9C.1 introduces no public sample or other file")
        for name in files:
            if name not in allowed:
                old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
                actual = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
                self.assertEqual(actual, old, name)
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + report])
        new = subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + report])
        start = b"### T9C - Lab Guide Simplification\n"
        end = b"### T9D - Security and Testing Alignment\n"
        def outside_t9c(value):
            self.assertEqual(value.count(start), 1)
            self.assertEqual(value.count(end), 1)
            before, rest = value.split(start, 1)
            _, after = rest.split(end, 1)
            return before, after
        self.assertEqual(outside_t9c(new), outside_t9c(old))
        self.assertIn(b"Report state: DRAFT\n", new)
        self.assertIn(b"| Umbrella status | IN PROGRESS |", new)

    def test_t9c2_preserves_excluded_files_downstream_and_other_report_bytes(self):
        # Retain every T9C.2 assertion against its merged publication.
        published = "6f5a70529f9bd775aa19b4956a2d6db02dd1ea49"
        def published_bytes(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
        base = "f41a5f296a772faa76df3089cb86b4b12b044d13"
        report = "docs/reports/T9-Report.md"
        allowed = {docs.GUIDE, docs.GUIDE[:-3] + ".pdf", docs.MANIFEST, report,
                   "scripts/build_docs.py", "scripts/validate_docs.py",
                   "tests/test_build_docs.py", "tests/test_validate_docs.py"}
        added = {docs.PREPARED_REFERENCE, docs.PREPARED_REFERENCE[:-3] + ".pdf"}
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files) | added)
        for name in files:
            if name not in allowed:
                old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
                self.assertEqual(published_bytes(name), old, name)
        old_guide = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + docs.GUIDE])
        marker = b"## Phase 2: Identity and Endpoint Security"
        self.assertEqual(published_bytes(docs.GUIDE).split(marker, 1)[1], old_guide.split(marker, 1)[1])
        fences = r"^```([^\n]*)\n(.*?)^```"
        moved = re.findall(fences, published_bytes(docs.PREPARED_REFERENCE).decode(), re.M | re.S)
        original = re.findall(fences, old_guide.split(marker, 1)[0].decode(), re.M | re.S)
        self.assertEqual(len(original), 3)
        for block in original:
            self.assertIn(block, moved, "Preserve each existing read-only/editor block in the reference")
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + report])
        new = published_bytes(report)
        def outside_t9c2(value):
            value = re.sub(rb"^\| T9C\.2 - Introduction and Phase 1 \|[^\n]*\n", b"", value, flags=re.M)
            return re.sub(rb"^#### T9C\.2 - Introduction and Phase 1\n.*?(?=^### T9D -)", b"", value,
                          flags=re.M | re.S)
        self.assertEqual(outside_t9c2(new), outside_t9c2(old))
        self.assertIn(b"Report state: DRAFT\n", new)
        self.assertIn(b"| Umbrella status | IN PROGRESS |", new)
        old_manifest = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + docs.MANIFEST]))
        new_manifest = json.loads(published_bytes(docs.MANIFEST))
        for manifest in (old_manifest, new_manifest):
            manifest["documents"] = [entry for entry in manifest["documents"]
                                     if entry["source"] not in {docs.GUIDE, docs.PREPARED_REFERENCE}]
            for entry in manifest["documents"]:
                entry.pop("renderer_sha256")
        self.assertEqual(new_manifest, old_manifest)

    def test_t9c3_preserves_excluded_sources_history_and_all_moved_commands(self):
        # Preserve all predecessor assertions against its merged publication.
        published = "eb82f2ff5edee9f3af45d44b17a4182a35c29028"
        def published_bytes(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
        base = "6f5a70529f9bd775aa19b4956a2d6db02dd1ea49"
        report = "docs/reports/T9-Report.md"
        allowed = {docs.GUIDE, docs.GUIDE[:-3] + ".pdf", docs.MANIFEST, report,
                   "scripts/build_docs.py", "scripts/validate_docs.py", "tests/test_build_docs.py", "tests/test_validate_docs.py"}
        added = {docs.WINDOWS_REFERENCE, docs.WINDOWS_REFERENCE[:-3] + ".pdf",
                 docs.LINUX_REFERENCE, docs.LINUX_REFERENCE[:-3] + ".pdf"}
        def old(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files) | added)
        for name in files:
            if name not in allowed:
                self.assertEqual(published_bytes(name), old(name), name)
        def guide_parts(content):
            before, rest = content.split(b"## Phase 2: Identity and Endpoint Security\n", 1)
            phase, after = rest.split(b"## Phase 3: Zero Trust Access Controls\n", 1)
            return before, phase, after
        before, phase, after = guide_parts(old(docs.GUIDE))
        actual = guide_parts(published_bytes(docs.GUIDE))
        self.assertEqual(actual[0], before, "Introduction and Phase 1 must remain byte-identical")
        self.assertEqual(actual[2], after, "Phases 3-5 and the appendix must remain byte-identical")
        fences = r"^```([^\n]*)\n(.*?)^```"
        original = re.findall(fences, phase.decode(), re.M | re.S)
        moved = []
        for name in (docs.WINDOWS_REFERENCE, docs.LINUX_REFERENCE):
            moved.extend(re.findall(fences, published_bytes(name).decode(), re.M | re.S))
        self.assertEqual(len(original), 13)
        for block in original:
            self.assertIn(block, moved, "Do not discard or silently alter a moved command/configuration")
        def outside_t9c3(value):
            value = re.sub(rb"^\| T9C\.3 - Phase 2 \|[^\n]*\n", b"", value, flags=re.M)
            return re.sub(rb"^#### T9C\.3 - Phase 2\n.*?(?=^### T9D -)", b"", value, flags=re.M | re.S)
        new_report = published_bytes(report)
        self.assertEqual(outside_t9c3(new_report), outside_t9c3(old(report)))
        self.assertIn(b"Report state: DRAFT\n", new_report)
        self.assertIn(b"| Umbrella status | IN PROGRESS |", new_report)
        manifests = [json.loads(old(docs.MANIFEST)), json.loads(published_bytes(docs.MANIFEST))]
        for manifest in manifests:
            manifest["documents"] = [entry for entry in manifest["documents"]
                                     if entry["source"] not in {docs.GUIDE, docs.WINDOWS_REFERENCE, docs.LINUX_REFERENCE}]
            for entry in manifest["documents"]:
                entry.pop("renderer_sha256")
        self.assertEqual(*manifests)

    def test_t9c4_preserves_excluded_sources_history_report_and_moved_commands(self):
        # Retain the complete predecessor contract against its merged publication.
        published = "052fa098dd1768c82bac850470accf306bc3f0cd"
        def published_bytes(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])
        base = "eb82f2ff5edee9f3af45d44b17a4182a35c29028"
        report = "docs/reports/T9-Report.md"
        allowed = {docs.GUIDE, docs.GUIDE[:-3] + ".pdf", docs.MANIFEST, report,
                   "scripts/build_docs.py", "scripts/validate_docs.py", "tests/test_build_docs.py", "tests/test_validate_docs.py"}
        added = {name for source in docs.ACCESS_REFERENCES for name in (source, source[:-3] + ".pdf")}
        def old(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files) | added, "Only four new reference editions are authorized")
        for name in files:
            if name not in allowed:
                self.assertEqual(published_bytes(name), old(name), name)
        def parts(value):
            prefix, rest = value.split(b"## Phase 3: Zero Trust Access Controls\n", 1)
            phase, suffix = rest.split(b"## Phase 4: Monitoring, Automation and Recovery\n", 1)
            return prefix, phase, suffix
        prefix, original, suffix = parts(old(docs.GUIDE))
        actual = parts(published_bytes(docs.GUIDE))
        self.assertEqual(actual[0], prefix, "Introduction and Phases 1-2 must remain byte-identical")
        self.assertEqual(actual[2], suffix, "Phases 4-5 and appendices must remain byte-identical")
        fences = r"^```([^\n]*)\n(.*?)^```"
        original = re.findall(fences, original.decode(), re.M | re.S)
        moved = [block for name in docs.ACCESS_REFERENCES
                 for block in re.findall(fences, published_bytes(name).decode(), re.M | re.S)]
        self.assertEqual(len(original), 17)
        for block in original:
            self.assertIn(block, moved, "Every original command/configuration must be moved intact")
        def outside_t9c4(value):
            value = re.sub(rb"^\| T9C\.4 - Phase 3 \|[^\n]*\n", b"", value, flags=re.M)
            return re.sub(rb"^#### T9C\.4 - Phase 3\n.*?(?=^### T9D -)", b"", value, flags=re.M | re.S)
        new_report = published_bytes(report)
        self.assertEqual(outside_t9c4(new_report), outside_t9c4(old(report)))
        self.assertIn(b"Report state: DRAFT\n", new_report)
        self.assertIn(b"| Umbrella status | IN PROGRESS |", new_report)
        manifests = [json.loads(old(docs.MANIFEST)), json.loads(published_bytes(docs.MANIFEST))]
        for manifest in manifests:
            manifest["documents"] = [entry for entry in manifest["documents"]
                                     if entry["source"] not in {docs.GUIDE} | docs.ACCESS_REFERENCES]
            for entry in manifest["documents"]:
                entry.pop("renderer_sha256")
        self.assertEqual(*manifests, "No unrelated generated-document change is authorized")

    def test_t9c5_preserves_excluded_sources_history_report_and_all_commands(self):
        # Preserve the complete T9C.5 contract against the merged publication.
        published = "7da96817918b92fc0f75bab6602bc82310c53264"

        def published_bytes(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", published + ":" + name])

        base = "052fa098dd1768c82bac850470accf306bc3f0cd"
        report = "docs/reports/T9-Report.md"
        allowed = {docs.GUIDE, docs.GUIDE[:-3] + ".pdf", docs.MANIFEST, report,
                   "scripts/build_docs.py", "scripts/validate_docs.py", "tests/test_build_docs.py", "tests/test_validate_docs.py"}
        added = {name for source in docs.OPERATIONS_REFERENCES for name in (source, source[:-3] + ".pdf")}
        def old(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])
        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", published]).decode().splitlines()
        self.assertEqual(set(current), set(files) | added, "Only four new reference editions are authorized")
        for name in files:
            if name not in allowed:
                self.assertEqual(published_bytes(name), old(name), name)
        def parts(value):
            prefix, rest = value.split(b"## Phase 4: Monitoring, Automation and Recovery\n", 1)
            phase, suffix = rest.split(b"## Phase 5: Validation and Final Submission\n", 1)
            return prefix, phase, suffix
        before, original, after = parts(old(docs.GUIDE))
        actual = parts(published_bytes(docs.GUIDE))
        self.assertEqual(actual[0], before, "Introduction and Phases 1-3 must remain byte-identical")
        self.assertEqual(actual[2], after, "Phase 5 and appendices must remain byte-identical")
        fences = r"^```([^\n]*)\n(.*?)^```"
        original_blocks = re.findall(fences, original.decode(), re.M | re.S)
        moved = [block for name in docs.OPERATIONS_REFERENCES
                 for block in re.findall(fences, published_bytes(name).decode(), re.M | re.S)]
        self.assertEqual(len(original_blocks), 8)
        for block in original_blocks:
            self.assertIn(block, moved, "Preserve all Phase 4 commands, especially the complete automation")
        old_mock = after.decode().split("### Step 24 - Prepare the permitted and denied network checks\n", 1)[1].split("### Step 25 -", 1)[0].strip()
        # Correct only the obsolete resource-count phrase in the new reference;
        # retain every other instruction/command and keep Phase 5 byte-frozen.
        self.assertEqual(old_mock.count("add no permanent fifth VM or fourth zone."), 1)
        expected_mock = old_mock.replace("add no permanent fifth VM or fourth zone.", "add no permanent VM or zone.")
        self.assertIn(expected_mock, published_bytes(docs.MONITORING_REFERENCE).decode(),
                      "Deferred mock extraction allows only the no-extra-resource wording correction")
        def outside_t9c5(value):
            value = re.sub(rb"^\| T9C\.5 - Phase 4 \|[^\n]*\n", b"", value, flags=re.M)
            return re.sub(rb"^#### T9C\.5 - Phase 4\n.*?(?=^### T9D -)", b"", value, flags=re.M | re.S)
        new_report = published_bytes(report)
        self.assertEqual(outside_t9c5(new_report), outside_t9c5(old(report)))
        self.assertIn(b"Report state: DRAFT\n", new_report)
        self.assertIn(b"| Umbrella status | IN PROGRESS |", new_report)
        manifests = [json.loads(old(docs.MANIFEST)), json.loads(published_bytes(docs.MANIFEST))]
        for manifest in manifests:
            manifest["documents"] = [entry for entry in manifest["documents"]
                                     if entry["source"] not in {docs.GUIDE} | docs.OPERATIONS_REFERENCES]
            for entry in manifest["documents"]:
                entry.pop("renderer_sha256")
        self.assertEqual(*manifests, "No unrelated generated-document change is authorized")

    def test_t9c6_preserves_excluded_sources_reports_and_technical_commands(self):
        base = "7da96817918b92fc0f75bab6602bc82310c53264"
        report = "docs/reports/T9-Report.md"
        allowed = {docs.GUIDE, docs.GUIDE[:-3] + ".pdf", docs.MANIFEST, report,
                   "scripts/build_docs.py", "scripts/validate_docs.py", "tests/test_build_docs.py", "tests/test_validate_docs.py"}

        def old(name):
            return subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + name])

        files = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", base]).decode().splitlines()
        current = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"]).decode().splitlines()
        self.assertEqual(set(current), set(files), "Phase 5 introduces no public file")
        for name in set(files) - allowed:
            self.assertEqual((ROOT / name).read_bytes(), old(name), name)
        boundary = b"## Phase 5: Validation and Final Submission\n"
        prefix, previous_phase = old(docs.GUIDE).split(boundary, 1)
        self.assertEqual((ROOT / docs.GUIDE).read_bytes().split(boundary, 1)[0], prefix)
        fences = rb"^```([^\n]*)\n(.*?)^```"
        previous_commands = re.findall(fences, previous_phase, re.M | re.S)
        self.assertEqual(len(previous_commands), 3)
        reference_commands = re.findall(fences, (ROOT / docs.MONITORING_REFERENCE).read_bytes(), re.M | re.S)
        for command in previous_commands:
            self.assertIn(command, reference_commands, "Reference 06 retains the full technical procedure")

        def outside_t9c6(value):
            value = re.sub(rb"^\| T9C\.6 - Phase 5 \|[^\n]*\n", b"", value, flags=re.M)
            return re.sub(rb"^#### T9C\.6 - Phase 5\n.*?(?=^### T9D -)", b"", value, flags=re.M | re.S)

        current_report = (ROOT / report).read_bytes()
        self.assertEqual(outside_t9c6(current_report), outside_t9c6(old(report)))
        for required in (b"Report state: DRAFT\n", b"| Umbrella status | IN PROGRESS |",
                         b"the owner accepts that Reference 07's manifest",
                         b"may need a shell continuation character", b"Executability is unverified",
                         b"All manifest, backup and restore checks remain mandatory"):
            self.assertIn(required, current_report)
        manifests = [json.loads(old(docs.MANIFEST)), json.loads((ROOT / docs.MANIFEST).read_bytes())]
        for manifest in manifests:
            manifest["documents"] = [entry for entry in manifest["documents"] if entry["source"] != docs.GUIDE]
            for entry in manifest["documents"]:
                entry.pop("renderer_sha256")
        self.assertEqual(*manifests, "No unrelated generated-document change is authorized")

    def test_phase5_pdf_keeps_every_procedure_table_and_compatibility_link_intact(self):
        content = (ROOT / docs.GUIDE).read_bytes()
        sources = set(docs.discover_sources(ROOT))
        reader = docs.PdfReader(io.BytesIO(docs.render_pdf(docs.GUIDE, content, sources)))
        baseline = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                            "7da96817918b92fc0f75bab6602bc82310c53264:" + docs.GUIDE[:-3] + ".pdf"])
        before = docs.PdfReader(io.BytesIO(baseline))
        destinations = reader.named_destinations

        def page_for(anchor):
            return reader.get_destination_page_number(destinations[anchor])

        def without_version(page):
            return re.sub(r"Source version [0-9a-f]{12}", "", page.extract_text())

        phase_start = page_for("phase-5-validation-and-final-submission")
        self.assertEqual(phase_start, 13)
        for i in range(phase_start):
            self.assertEqual(without_version(reader.pages[i]), without_version(before.pages[i]), f"Earlier page {i + 1}")
        self.assertLessEqual(len(reader.pages) - phase_start, 4)
        phase = content.decode().split("## Phase 5: Validation and Final Submission\n", 1)[1]
        phase = re.sub(r'^<a id="[a-z][a-z0-9-]*"></a>\n', '', phase, flags=re.M)
        procedures = re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", phase, re.M | re.S)
        self.assertEqual(len(procedures), 4)
        for title, body in procedures:
            page = reader.pages[page_for(docs.anchor_for(title, set()))].extract_text()
            compact = re.sub(r"\s+", "", page)
            self.assertIn(re.sub(r"\s+", "", title), compact)
            for token in docs.MARKDOWN(body):
                if token["type"] == "table":
                    head, rows = token["children"]
                    parts = head["children"] + [cell for row in rows["children"] for cell in row["children"]]
                elif token["type"] == "list":
                    parts = token["children"]
                elif token["type"] == "paragraph":
                    parts = [token]
                else:
                    continue
                for part in parts:
                    expected = re.sub(r"\s+", "", docs.normalize(docs.plain(part["children"])))
                    self.assertIn(expected, compact, f"Split content in {title}: {expected[:50]}")
        for alias, target in (
            ("step-24---prepare-the-permitted-and-denied-network-checks", "a-prepare-and-verify-network-tests"),
            ("step-25---execute-and-record-the-ten-tests", "b-complete-the-ten-formal-tests"),
            ("historical-requirement-and-test-transition", "b-complete-the-ten-formal-tests"),
            ("step-26---finish-the-five-office-deliverables", "c-complete-the-five-office-deliverables"),
            ("required-lab-deliverables", "c-complete-the-five-office-deliverables"),
            ("step-27---review-evidence-submit-and-obtain-owner-acceptance", "d-review-evidence-submit-and-obtain-owner-acceptance"),
            ("phase-5-checkpoint-and-recovery", "d-review-evidence-submit-and-obtain-owner-acceptance"),
        ):
            self.assertEqual(page_for(alias), page_for(target))
        expected = "06-Logs-Automation-and-Test-Tools.pdf#nameddest=deferred-phase-5-mock-and-connection-tools"
        self.assertTrue(any(expected in str(link.get_object().get("/A", {}).get("/URI", ""))
                            for link in reader.pages[phase_start].get("/Annots", [])))

    def test_phase4_pdf_has_compact_complete_procedures_and_intact_reference_commands(self):
        source = (ROOT / docs.GUIDE).read_bytes()
        reader = docs.PdfReader(io.BytesIO(docs.render_pdf(docs.GUIDE, source, set(docs.discover_sources()))))
        pages = [re.sub(r"\s+", "", page.extract_text()) for page in reader.pages]
        start = reader.get_destination_page_number(reader.named_destinations["phase-4-monitoring-automation-and-recovery"])
        end = reader.get_destination_page_number(reader.named_destinations["phase-5-validation-and-final-submission"])
        self.assertIn(end - start, (3, 4))
        for title, details in (
            ("A. Collect five security events", ("E01", "E02", "E03", "E04", "E05", "FWT-07.01-.07/.09")),
            ("B. Investigate one denied-access event", ("one working allowed control", "Denied Access Investigation", "FWT-07.08/.09")),
            ("C. Run the capacity-summary automation", ("WIN1-capacity.json", "invalid-target", "invalid-output-path", "FWT-08.01-.07")),
            ("D. Back up APP1 and restore it in isolation", ("Start a separate observer clock", "stop and disable copied Tailscale", "B01-B10", "FWT-09.01-.10")),
        ):
            page = next(page for page in pages[start:end] if re.sub(r"\s+", "", title) in page)
            for expected in ("WHERE", "STEPS", "CHECK", "RECORD", *details):
                self.assertIn(re.sub(r"\s+", "", expected), page, title)
        for reference in docs.OPERATIONS_REFERENCES:
            data = (ROOT / reference).read_bytes()
            ref_reader = docs.PdfReader(io.BytesIO(docs.render_pdf(reference, data, set(docs.discover_sources()))))
            ref_pages = [re.sub(r"\s+", "", p.extract_text()) for p in ref_reader.pages]
            for language, code in re.findall(r"^```([^\n]*)\n(.*?)^```", data.decode(), re.M | re.S):
                self.assertTrue(any(re.sub(r"\s+", "", docs.normalize(code)) in page for page in ref_pages),
                                "Reference command must remain intact on one page: " + reference)

    def test_phase3_pdf_keeps_procedures_cases_and_checkpoint_intact_in_four_pages(self):
        content = (ROOT / docs.GUIDE).read_bytes()
        reader = docs.PdfReader(io.BytesIO(docs.render_pdf(docs.GUIDE, content, set(docs.discover_sources()))))
        pages = [re.sub(r"\s+", "", p.extract_text()) for p in reader.pages]
        phase = content.decode().split("## Phase 3:", 1)[1].split("## Phase 4:", 1)[0]
        phase = re.sub(r'<a id="[^"]+"></a>', '', phase)
        tokens = [t for t in docs.MARKDOWN(phase) if t["type"] != "blank_line"]
        for i, token in enumerate(tokens):
            if token["type"] != "heading" or token["attrs"]["level"] != 3:
                continue
            title = docs.plain(token["children"])
            page = pages[reader.get_destination_page_number(reader.named_destinations[docs.anchor_for(title, set())])]
            end = next((n for n in range(i + 1, len(tokens)) if tokens[n]["type"] == "heading"), len(tokens))
            for part in tokens[i:end]:
                if part["type"] == "paragraph" and docs.plain(part["children"]).startswith("Before Phase 4:"):
                    continue
                if part["type"] == "table":
                    for row in part["children"][1]["children"]:
                        for cell in row["children"]:
                            self.assertIn(re.sub(r"\s+", "", docs.normalize(docs.plain(cell["children"]))), page)
                else:
                    items = part["children"] if part["type"] == "list" else [part]
                    for item in items:
                        expected = re.sub(r"\s+", "", docs.normalize(docs.plain(item.get("children", []))))
                        self.assertIn(expected, page, "Split Phase 3 procedure: " + title)
        start = reader.get_destination_page_number(reader.named_destinations["phase-3-zero-trust-access-controls"])
        checkpoint = next(i for i, page in enumerate(pages) if "BeforePhase4:" in page)
        self.assertTrue(3 <= checkpoint - start + 1 <= 4)
        check = next(t for t in tokens if t["type"] == "paragraph" and docs.plain(t["children"]).startswith("Before Phase 4:"))
        self.assertIn(re.sub(r"\s+", "", docs.normalize(docs.plain(check["children"]))), pages[checkpoint])
        for n in range(13, 20):
            self.assertTrue(any(a.startswith(f"step-{n}---") for a in reader.named_destinations))
        old = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                       "eb82f2ff5edee9f3af45d44b17a4182a35c29028:" + docs.GUIDE[:-3] + ".pdf"])
        old_reader = docs.PdfReader(io.BytesIO(old))
        for i in range(start):
            def without_version(value):
                return re.sub(r"Source version [0-9a-f]{12}", "Source version", value)
            self.assertEqual(without_version(reader.pages[i].extract_text()), without_version(old_reader.pages[i].extract_text()),
                             "Phase 1-2 PDF text/layout must remain unchanged except the source-version footer")

    def test_phase2_pdf_keeps_five_procedures_intact_in_four_pages(self):
        content = (ROOT / docs.GUIDE).read_text(encoding="utf-8")
        data = docs.render_pdf(docs.GUIDE, content.encode(), set(docs.discover_sources(ROOT)))
        reader = docs.PdfReader(io.BytesIO(data))
        pages = [re.sub(r"\s+", "", page.extract_text()) for page in reader.pages]
        phase = content.split("## Phase 2:", 1)[1].split("## Phase 3:", 1)[0]
        phase = re.sub(r'<a id="[^"]+"></a>', '', phase)
        parsed = docs.MARKDOWN(phase)
        for index, token in enumerate(parsed):
            if token["type"] != "heading" or token["attrs"]["level"] != 3:
                continue
            title = docs.plain(token["children"])
            anchor = docs.anchor_for(title, set())
            page = pages[reader.get_destination_page_number(reader.named_destinations[anchor])]
            end = next((n for n in range(index + 1, len(parsed)) if parsed[n]["type"] == "heading"), len(parsed))
            for part in parsed[index:end]:
                if part["type"] == "paragraph" and docs.plain(part["children"]).startswith("Before Phase 3:"):
                    continue
                items = part["children"] if part["type"] == "list" else [part]
                for item in items:
                    if item["type"] not in {"paragraph", "list_item", "heading"}:
                        continue
                    expected = re.sub(r"\s+", "", docs.normalize(docs.plain(item["children"])))
                    self.assertIn(expected, page, "Split Phase 2 procedure: " + title)
        start = reader.get_destination_page_number(reader.named_destinations["phase-2-identity-and-endpoint-security"])
        checkpoint = next(i for i, page in enumerate(pages) if "BeforePhase3:" in page)
        self.assertTrue(3 <= checkpoint - start + 1 <= 4)
        checkpoint_text = next(t for t in parsed if t["type"] == "paragraph" and docs.plain(t["children"]).startswith("Before Phase 3:"))
        self.assertIn(re.sub(r"\s+", "", docs.normalize(docs.plain(checkpoint_text["children"]))), pages[checkpoint])
        for n in range(7, 13):
            self.assertTrue(any(a.startswith(f"step-{n}---") for a in reader.named_destinations))

    def test_identity_and_access_references_preserve_code_context_rows_links_and_text(self):
        sources = set(docs.discover_sources(ROOT))
        for name in (docs.WINDOWS_REFERENCE, docs.LINUX_REFERENCE, docs.HTTPS_REFERENCE, docs.TAILSCALE_REFERENCE):
            content = (ROOT / name).read_bytes()
            data = docs.render_pdf(name, content, sources)
            self.assertEqual(docs.inspect_pdf(data, name, content, sources)["text_token_coverage"], 1.0)
            reader = docs.PdfReader(io.BytesIO(data))
            pages = [re.sub(r"\s+", "", page.extract_text()) for page in reader.pages]
            tokens = [t for t in docs.MARKDOWN(content.decode()) if t["type"] != "blank_line"]
            self.assertIn(docs.normalize(docs.plain(tokens[0]["children"])).replace(" ", ""), pages[0])
            for i, token in enumerate(tokens):
                if token["type"] in {"paragraph", "list"}:
                    parts = token["children"] if token["type"] == "list" else [token]
                    for part in parts:
                        expected = re.sub(r"\s+", "", docs.normalize(docs.plain(part["children"])))
                        self.assertTrue(any(expected in page for page in pages), "Split reference action/paragraph")
                if token["type"] == "block_code":
                    code = re.sub(r"\s+", "", docs.normalize(token["raw"]))
                    context = re.sub(r"\s+", "", docs.normalize(docs.plain(tokens[i - 1]["children"])))
                    self.assertTrue(any(code in page and context in page for page in pages), "Split code/context: " + code[:60])
                if token["type"] == "table":
                    for row in token["children"][1]["children"]:
                        cells = [re.sub(r"\s+", "", docs.normalize(docs.plain(cell["children"]))) for cell in row["children"]]
                        self.assertTrue(any(all(cell in page for cell in cells) for page in pages), "Split reference table row")

    def test_assignment_resources_match_architecture_and_unchanged_contracts(self):
        content = (ROOT / docs.ASSIGNMENT).read_text(encoding="utf-8")
        architecture = (ROOT / docs.ARCHITECTURE).read_text(encoding="utf-8")
        rows = re.findall(r"^- \*\*(DC1|WIN1|APP1), (Corporate|Restricted):\*\* .+?; (\d+) vCPU / (\d+) GiB RAM / (\d+) GiB disk\.$", content, re.M)
        self.assertEqual([(row[0], row[1]) for row in rows],
                         [("DC1", "Corporate"), ("WIN1", "Corporate"), ("APP1", "Restricted")])
        expected = re.findall(r"^\| (DC1|WIN1|APP1) \| (\d+) \| (\d+) \| (\d+) \|", architecture, re.M)
        self.assertEqual([(r[0], *r[2:]) for r in rows], expected)
        self.assertEqual([sum(int(row[i]) for row in rows) for i in (2, 3, 4)], [6, 16, 160])
        self.assertIn("Physical OPNsense is separate from these totals", content)
        base = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                        "7387219ab2c4690e5bbed3615c47d892f13b0e12:" + docs.ASSIGNMENT]).decode()
        def retained_rows(value):
            return [line for line in value.splitlines()
                    if (re.match(r"^\| FWR-\d{2} \|", line) and not line.startswith("| FWR-02 |"))
                    or re.match(r"^\| `0[1-5]-", line)
                    or any(line.startswith("| " + title + " |") for title, _ in validator.RUBRIC_WEIGHTS[1:])]
        self.assertEqual(retained_rows(content), retained_rows(base))
        self.assertEqual(len(retained_rows(content)), 18)

    def test_guide_pdf_keeps_filenames_whole_and_preserves_navigation(self):
        content = (ROOT / docs.GUIDE).read_bytes()
        sources = set(docs.discover_sources(ROOT))
        data = docs.render_pdf(docs.GUIDE, content, sources)
        reader = docs.PdfReader(io.BytesIO(data))
        pages = [p.extract_text() for p in reader.pages]
        text = "\n".join(pages)
        self.assertNotRegex(text, r"\b(?:T6[AB]?|T7|Codex)\b")
        self.assertIn("Follow the five phases in order", pages[0])
        self.assertIn("NOT TESTED", pages[0])
        self.assertNotRegex(pages[0], r"PLANNED|Ordered|Delivered|Procurement")
        self.assertTrue(any(all(name in p.splitlines() for name in validator.DELIVERABLE_FILENAMES)
                            for p in pages))
        for n, title in enumerate(validator.PHASE_TITLES, 1):
            self.assertIn(docs.anchor_for(f"Phase {n}: {title}", set()), reader.named_destinations)
        self.assertIn("required-lab-deliverables", reader.named_destinations)
        self.assertEqual(docs.inspect_pdf(data, docs.GUIDE, content, sources)["text_token_coverage"], 1.0)
        parsed = docs.MARKDOWN(content.decode())
        for title in ("A. Verify the lab equipment and VM resources", "B. Verify network zones and management access",
                      "C. Verify isolation and required network access"):
            selected = next(page for page in pages if title in page)
            self.assertIn("WHERE", selected)
            self.assertIn("STEPS", selected)
            self.assertIn("CHECK", selected)
            self.assertIn("RECORD", selected)
            self.assertIn("Deliverable 01 >", selected)
            start = next(i for i, token in enumerate(parsed) if token["type"] == "heading"
                         and docs.plain(token["children"]) == title)
            end = next(i for i in range(start + 1, len(parsed)) if parsed[i]["type"] == "heading"
                       and parsed[i]["attrs"]["level"] <= 3)
            for token in parsed[start:end]:
                parts = ([token] if token["type"] == "paragraph" else
                         token["children"] if token["type"] == "list" else [])
                for part in parts:
                    children = part["children"]
                    if not any(child["type"] == "inline_html" for child in children):
                        expected = re.sub(r"\s+", "", docs.normalize(docs.plain(children)))
                        self.assertIn(expected, re.sub(r"\s+", "", selected), "Split procedure content: " + expected[:60])
        first = reader.get_destination_page_number(reader.named_destinations["phase-1-prepared-infrastructure"])
        last = reader.get_destination_page_number(reader.named_destinations["c-verify-isolation-and-required-network-access"])
        self.assertLessEqual(last - first, 1, "Phase 1 should occupy two adjacent pages")
        self.assertIn("phase-1-infrastructure-and-network", reader.named_destinations)
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

    def test_prepared_reference_has_complete_flow_rows_and_unsplit_commands(self):
        content = (ROOT / docs.PREPARED_REFERENCE).read_bytes()
        sources = set(docs.discover_sources(ROOT))
        data = docs.render_pdf(docs.PREPARED_REFERENCE, content, sources)
        reader = docs.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() for page in reader.pages]
        self.assertIn("Required private records", pages[0])
        self.assertIn("Physical map and Proxmox bridges", pages[0])
        self.assertEqual(docs.inspect_pdf(data, docs.PREPARED_REFERENCE, content, sources)["text_token_coverage"], 1.0)
        compact = [re.sub(r"\s+", "", page) for page in pages]
        active = reader.get_destination_page_number(reader.named_destinations["approved-active-checks"])
        section = content.decode().split("## Approved active checks\n", 1)[1].split("\n## ", 1)[0]
        for token in docs.MARKDOWN(section):
            parts = ([token] if token["type"] == "paragraph" else
                     token["children"] if token["type"] == "list" else [])
            for part in parts:
                expected = re.sub(r"\s+", "", docs.normalize(docs.plain(part["children"])))
                self.assertIn(expected, compact[active], "Split active-check procedure")
        for row in re.findall(r"^\| FF-\d{2} \| (.+) \|$", content.decode(), re.M):
            expected = re.sub(r"\s+", "", row)
            self.assertTrue(any(expected in page for page in compact), "Split flow row: " + row[:60])
        tokens = docs.MARKDOWN(content.decode())
        for index, token in enumerate(tokens):
            if token["type"] == "block_code":
                expected = re.sub(r"\s+", "", docs.normalize(token["raw"]))
                self.assertTrue(any(expected in page for page in compact), "Split reference command")
                context = next(t for t in reversed(tokens[:index]) if t["type"] != "blank_line")
                context_text = re.sub(r"\s+", "", docs.normalize(docs.plain(context["children"])))
                self.assertTrue(any(expected in page and context_text in page for page in compact),
                                "Reference command separated from its target/risk context")

    def test_guide_retains_core_commands_and_moves_publication_details_to_build_guide(self):
        base = "a3d7b1c6effde3bd5b18ab1a4b529c07a7cc7c61"
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", base + ":" + docs.GUIDE]).decode()
        current = (ROOT / docs.GUIDE).read_text(encoding="utf-8")
        fences = r"^```([^\n]*)\n(.*?)^```"
        current_blocks = re.findall(fences, current, re.M | re.S)
        for reference in docs.TECHNICAL_REFERENCES:
            current_blocks += re.findall(fences, (ROOT / reference).read_text(encoding="utf-8"), re.M | re.S)
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
            self.assertTrue(any(command in block for _, block in current_blocks))

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
