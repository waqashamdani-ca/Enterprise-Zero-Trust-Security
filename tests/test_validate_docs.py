"""Focused negative/positive cases for publication and link boundaries.

Only temporary synthetic text is created. No network access or lab testing.
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_docs.py"
SPEC = importlib.util.spec_from_file_location("validate_docs", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def temporary_directory():
    # Keep fixtures within the workspace, including on restricted Windows hosts.
    base = SCRIPT.parents[1] / "local" / "validator-tests"
    base.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.TemporaryDirectory(dir=base)
    if not Path(temporary.name).resolve().is_relative_to(base.resolve()):
        raise RuntimeError("Temporary fixture escaped the approved test directory")
    return temporary


class PublicReviewTests(unittest.TestCase):
    def test_token_findings_do_not_disclose_value(self):
        synthetic = "ghp_" + "A" * 36
        findings = validator.public_content_issues("sample.md", synthetic)
        self.assertTrue(any("GitHub token" in finding for finding in findings))
        self.assertNotIn(synthetic, "\n".join(findings))

    def test_ipv4_and_ipv6_real_address_examples_are_rejected(self):
        synthetic_private = ".".join(("10", "42", "0", "7"))
        synthetic_ipv6 = ":".join(("fd00", "1234", "", "7"))
        findings = validator.public_content_issues("sample.md", synthetic_private + "\n" + synthetic_ipv6)
        self.assertEqual(len(findings), 2)
        self.assertTrue(all("value omitted" in finding for finding in findings))

    def test_reserved_documentation_addresses_and_synthetic_email_are_allowed(self):
        findings = validator.public_content_issues(
            "sample.md", "192.0.2.7 2001:db8::7 user@example.com user@ad.lab.test",
        )
        self.assertEqual(findings, [])

    def test_non_synthetic_email_is_rejected_without_value(self):
        synthetic = "reviewer@" + "organization" + ".com"
        findings = validator.public_content_issues("sample.md", synthetic)
        self.assertEqual(len(findings), 1)
        self.assertNotIn(synthetic, findings[0])

    def test_unknown_binary_and_private_path_fail_closed(self):
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "private").mkdir()
            (root / "private" / "capture.bin").write_bytes(b"\0\1\2")
            findings, content = validator.file_issues(root, "private/capture.bin")
            self.assertIsNone(content)
            self.assertTrue(any("private directory" in finding for finding in findings))
            self.assertTrue(any("unreviewed file type" in finding for finding in findings))
            self.assertTrue(any("binary/NUL" in finding for finding in findings))

    def test_tracked_ignored_file_is_still_reviewed(self):
        with temporary_directory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / "tracked.md").write_text("review me", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.md"], check=True)
            (root / ".gitignore").write_text("tracked.md\nprivate/\n", encoding="utf-8")
            (root / "private").mkdir()
            (root / "private" / "notes.md").write_text("not a candidate", encoding="utf-8")
            candidates = validator.candidate_paths(root)
            self.assertIn("tracked.md", candidates)
            self.assertNotIn("private/notes.md", candidates)


class MarkdownBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = temporary_directory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "README.md").write_text("# Main\n", encoding="utf-8")
        (self.root / "guide.md").write_text("# Repeat\n# Repeat\n", encoding="utf-8")

    def test_missing_destination_and_anchor_are_rejected(self):
        findings = validator.link_issues(self.root, "README.md", "[a](absent.md) [b](guide.md#absent)")
        self.assertEqual(len(findings), 2)

    def test_duplicate_heading_anchor_and_reference_definition_resolve(self):
        findings = validator.link_issues(self.root, "README.md", "[a](guide.md#repeat-1)\n[g]: guide.md#repeat\n")
        self.assertEqual(findings, [])

    def test_encoded_parent_escape_is_rejected_even_if_file_exists(self):
        findings = validator.link_issues(self.root, "README.md", "[a](%2e%2e/outside.md)")
        self.assertTrue(any("escapes repository" in finding for finding in findings))

    def test_code_examples_are_not_treated_as_live_links(self):
        findings = validator.link_issues(self.root, "README.md", "```text\n[a](absent.md)\n```\n[real](guide.md)")
        self.assertEqual(findings, [])

    def test_unclosed_fence_and_dangerous_scheme_are_rejected(self):
        findings = validator.link_issues(self.root, "README.md", "[a](javascript:unsafe)\n```\n")
        self.assertEqual(len(findings), 2)

    def test_malformed_table_is_rejected(self):
        findings = validator.link_issues(self.root, "README.md", "| A | B |\n| --- | --- |\n| one |\n")
        self.assertTrue(any("table columns" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
