"""Artifact-level PDF tests: text, navigation, pagination, fidelity, and drift."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
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

    def test_diagram_keeps_offline_and_protected_nodes_disconnected(self):
        source = (ROOT / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        diagrams = [token for token in docs.MARKDOWN(source) if token["type"] == "block_code" and token.get("attrs", {}).get("info") == "mermaid"]
        self.assertEqual(len(diagrams), 1)
        nodes, edges = docs.parse_diagram(diagrams[0]["raw"])
        self.assertEqual(len(nodes), 12)
        self.assertEqual(len(edges), 9)
        self.assertFalse(any(a in {"ROOT", "HOME"} or b in {"ROOT", "HOME"} for a, b, _, _ in edges))
        with self.assertRaisesRegex(ValueError, "Unsupported Mermaid"):
            docs.parse_diagram(diagrams[0]["raw"] + "\nclick FW https://example.com\n")

    def test_pdf_link_targets_cannot_escape_or_use_active_schemes(self):
        with self.assertRaises(ValueError):
            docs.resolve_link("guide.md", "../private.pdf", {"guide.md"})
        with self.assertRaises(ValueError):
            docs.resolve_link("guide.md", "javascript:unsafe", {"guide.md"})
        target = docs.resolve_link("reports/T1-Report.md", "../docs/DECISIONS.md", {"docs/governance/DECISIONS.md"})
        self.assertTrue(target.endswith("docs/governance/DECISIONS.pdf"))


if __name__ == "__main__":
    unittest.main()
