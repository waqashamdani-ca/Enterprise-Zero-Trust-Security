"""Focused negative/positive cases for publication and link boundaries.

Only temporary synthetic text is created. No network access or lab testing.
"""

import importlib.util
import hashlib
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


class ReportingGovernanceTests(unittest.TestCase):
    @staticmethod
    def report(number=1, state="DRAFT"):
        content = f"# Task report\n\nReport state: {state}\n\n"
        for section in validator.REPORT_SECTIONS:
            content += f"## {section}\n\n"
            if section.startswith("A."):
                content += f"| Task ID | T{number} |\n\n"
            content += "Synthetic fixture details; owner UAT pending.\n\n"
        return content

    def test_report_gaps_and_noncanonical_names_are_rejected(self):
        texts = {"docs/reports/T1-Report.md": self.report(), "docs/reports/T3-Report.md": self.report(3)}
        self.assertTrue(any("sequential" in item for item in validator.report_issues(texts)))
        texts["docs/reports/T02-Report.md"] = self.report(2)
        self.assertTrue(any("filename" in item for item in validator.report_issues(texts)))

    def test_missing_section_and_wrong_task_id_are_rejected(self):
        content = self.report(2).replace("## H. Next Task", "## Future work")
        findings = validator.report_issues({"docs/reports/T1-Report.md": content})
        self.assertTrue(any("A–H" in item for item in findings))
        self.assertTrue(any("Task ID" in item for item in findings))

    def test_draft_is_allowed_during_work_but_not_at_completion(self):
        texts = {"docs/reports/T1-Report.md": self.report()}
        self.assertEqual(validator.report_issues(texts), [])
        self.assertTrue(any("finalized" in item for item in validator.report_issues(texts, True)))

    def t9_umbrella(self):
        texts = {f"docs/reports/T{i}-Report.md": self.report(i, "FINALIZED") for i in range(1, 9)}
        texts[validator.T9_UMBRELLA_REPORT] = self.report(9).replace(
            "| Task ID | T9 |", "| Task ID | T9 |\n| Umbrella status | IN PROGRESS |")
        return texts

    def test_t9_interim_draft_requires_explicit_exception(self):
        texts = self.t9_umbrella()
        self.assertEqual(validator.report_issues(texts), [])
        self.assertEqual(len(validator.report_issues(texts, True)), 1)
        self.assertEqual(validator.report_issues(texts, True, True), [])

    def test_t9_exception_does_not_exempt_other_reports(self):
        texts = self.t9_umbrella()
        texts["docs/reports/T8-Report.md"] = self.report(8)
        findings = validator.report_issues(texts, True, True)
        self.assertTrue(any("T8-Report.md: report must be finalized" in item for item in findings))
        for label in "ABCDEF":
            with self.subTest(label=label):
                extra = dict(texts)
                extra[f"docs/reports/T9{label}-Report.md"] = self.report(9)
                self.assertTrue(any("invalid task-report" in item for item in validator.report_issues(extra, True, True)))

    def test_t9_exception_rejects_missing_finalized_or_completed_umbrella(self):
        for before, after in (("Report state: DRAFT", "Report state: FINALIZED"),
                              ("| IN PROGRESS |", "| COMPLETE |"),
                              ("| Umbrella status | IN PROGRESS |", "")):
            with self.subTest(after=after):
                texts = self.t9_umbrella()
                texts[validator.T9_UMBRELLA_REPORT] = texts[validator.T9_UMBRELLA_REPORT].replace(before, after)
                self.assertTrue(any("T9 draft exception requires" in item for item in validator.report_issues(texts, True, True)))
        texts = self.t9_umbrella()
        del texts[validator.T9_UMBRELLA_REPORT]
        self.assertTrue(any("T9 draft exception requires" in item for item in validator.report_issues(texts, True, True)))
        self.assertTrue(any("T9 draft exception requires" in item for item in validator.report_issues(self.t9_umbrella(), False, True)))

    def test_t9_finalization_uses_normal_gate_and_history_protection(self):
        texts = self.t9_umbrella()
        name = validator.T9_UMBRELLA_REPORT
        content = texts[name].replace("Report state: DRAFT", "Report state: FINALIZED")
        texts[name] = content
        self.assertEqual(validator.report_issues(texts, True), [])
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "docs/reports").mkdir(parents=True)
            (root / name).write_text(content, encoding="utf-8", newline="\n")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", name], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c",
                            "user.email=fixture@example.test", "-c", "commit.gpgsign=false",
                            "commit", "--quiet", "-m", "Freeze synthetic T9"], check=True)
            self.assertEqual(validator.finalized_history_issues(root, {name: content}), [])
            (root / name).write_text(content + "Changed\n", encoding="utf-8", newline="\n")
            self.assertTrue(any("modified" in item for item in validator.finalized_history_issues(root, {name: content + "Changed\n"})))
            self.assertTrue(any("deleted or renamed" in item for item in validator.finalized_history_issues(root, {})))

    def test_addendum_requires_existing_parent_and_sequential_number(self):
        texts = {
            "docs/reports/T1-Report.md": self.report(),
            "docs/reports/T2-Addendum-002-Correction.md": self.report(2),
        }
        findings = validator.report_issues(texts)
        self.assertTrue(any("parent" in item for item in findings))
        self.assertTrue(any("001" in item for item in findings))

    def test_finalized_reports_cannot_be_changed_deleted_or_renamed(self):
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "docs/reports").mkdir(parents=True)
            original = self.report(state="FINALIZED")
            (root / "docs/reports/T1-Report.md").write_text(original, encoding="utf-8", newline="\n")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "docs/reports/T1-Report.md"], check=True)
            subprocess.run([
                "git", "-C", str(root), "-c", "user.name=Fixture", "-c",
                "user.email=fixture@example.test", "-c", "commit.gpgsign=false",
                "commit", "--quiet", "-m", "Finalize synthetic fixture",
            ], check=True)
            self.assertEqual(validator.finalized_history_issues(root, {"docs/reports/T1-Report.md": original}), [])
            (root / "docs/reports/T1-Report.md").write_text(original + "Change\n", encoding="utf-8", newline="\n")
            modified = validator.finalized_history_issues(root, {"docs/reports/T1-Report.md": original + "Change\n"})
            self.assertTrue(any("modified" in item for item in modified))
            renamed = validator.finalized_history_issues(root, {"docs/reports/T2-Report.md": original})
            self.assertTrue(any("deleted or renamed" in item for item in renamed))

    def test_t1_source_and_bootstrap_evidence_are_preserved(self):
        project = SCRIPT.parents[1]
        source = subprocess.check_output([
            "git", "-C", str(project), "show",
            "4186787b153b2967381cffab353aaa81c72e6f70:docs/FINAL-REPORT.md",
        ])
        migrated = (project / "docs/reports/T1-Report.md").read_bytes()
        payload = migrated.split(b"<!-- ORIGINAL-SOURCE-BEGIN -->\n```markdown\n", 1)[1]
        payload = payload.split(b"```\n<!-- ORIGINAL-SOURCE-END -->", 1)[0]
        self.assertEqual(payload, source)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), "e53bf1111c5f66bcc4280246792142f82024f77d7d1e5ba4c72e1b06ac67b999")
        evidence = subprocess.check_output([
            "git", "-C", str(project), "show",
            "4186787b153b2967381cffab353aaa81c72e6f70:evidence/BOOTSTRAP-VALIDATION.md",
        ])
        self.assertEqual((project / "evidence/BOOTSTRAP-VALIDATION.md").read_bytes(), evidence)

    def test_legacy_finalized_report_can_only_move_with_same_basename_and_bytes(self):
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            original = self.report(state="FINALIZED")
            old = root / "reports/T1-Report.md"
            old.write_text(original, encoding="utf-8", newline="\n")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "reports/T1-Report.md"], check=True)
            commit = ["git", "-C", str(root), "-c", "user.name=Fixture", "-c",
                      "user.email=fixture@example.test", "-c", "commit.gpgsign=false",
                      "commit", "--quiet", "-m", "Synthetic migration fixture"]
            subprocess.run(commit, check=True)
            (root / "docs/reports").mkdir(parents=True)
            new = root / "docs/reports/T1-Report.md"
            old.rename(new)
            texts = {"docs/reports/T1-Report.md": original}
            self.assertEqual(validator.finalized_history_issues(root, texts), [])
            subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)
            subprocess.run(commit, check=True)
            self.assertEqual(validator.finalized_history_issues(root, texts), [])
            # Raw byte checks must catch newline changes hidden by read_text().
            new.write_bytes(original.replace("\n", "\r\n").encode())
            self.assertTrue(any("modified" in item for item in validator.finalized_history_issues(root, texts)))
            new.write_text(original, encoding="utf-8", newline="\n")
            new.rename(root / "docs/reports/T2-Report.md")
            self.assertTrue(any("deleted or renamed" in item for item in validator.finalized_history_issues(root, {"docs/reports/T2-Report.md": original})))

    def test_all_eleven_migrated_files_match_baseline_and_detect_missing_or_changed_files(self):
        project = SCRIPT.parents[1]
        self.assertEqual(validator.report_migration_issues(project), [])
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "docs/reports").mkdir(parents=True)
            for name, expected in validator.MIGRATED_REPORT_FILES.items():
                data = subprocess.check_output(["git", "-C", str(project), "show",
                                               validator.REPORT_MIGRATION_BASELINE + ":" + name.removeprefix("docs/")])
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
                (root / name).write_bytes(data)
            self.assertEqual(validator.report_migration_issues(root), [])
            index = root / "docs/reports/README.md"
            index.write_bytes(index.read_bytes() + b"\nchanged")
            self.assertTrue(any("differs" in item for item in validator.report_migration_issues(root)))
            index.unlink()
            self.assertTrue(any("missing" in item for item in validator.report_migration_issues(root)))

    def test_recreated_legacy_report_location_is_rejected(self):
        with temporary_directory() as directory:
            root = Path(directory)
            (root / "reports").mkdir()
            (root / "reports/T1-Report.md").write_text(self.report(state="FINALIZED"), encoding="utf-8")
            findings = validator.structure_issues(root, ["reports/T1-Report.md"])
            self.assertTrue(any("duplicate report locations" in item for item in findings))


    def test_authorized_companions_keep_numbering_and_require_finalized_parent(self):
        for label in ("T6A", "T6B"):
            with self.subTest(label=label):
                texts = {f"docs/reports/T{i}-Report.md": self.report(i, state="FINALIZED") for i in range(1, 7)}
                companion = self.report(6).replace("| Task ID | T6 |", f"| Task ID | {label} |")
                name = f"docs/reports/{label}-Report.md"
                texts[name] = companion
                self.assertEqual(validator.report_issues(texts), [])
                self.assertTrue(any("finalized" in x for x in validator.report_issues(texts, True)))
                texts["docs/reports/T6-Report.md"] = self.report(6)
                self.assertTrue(any("finalized parent" in x for x in validator.report_issues(texts)))
                texts["docs/reports/T6-Report.md"] = self.report(6, state="FINALIZED")
                texts[name] = companion.replace(f"| {label} |", "| T7 |")
                self.assertTrue(any("Task ID" in x for x in validator.report_issues(texts)))

    def test_other_lettered_reports_are_not_implicitly_authorized(self):
        texts = {"docs/reports/T1-Report.md": self.report(),
                 "docs/reports/T6C-Report.md": self.report(6)}
        self.assertTrue(any("filename" in x for x in validator.report_issues(texts)))

    def test_finalized_authorized_companions_are_protected_by_history_checks(self):
        for label in ("T6A", "T6B"):
            with temporary_directory() as directory:
                root = Path(directory)
                (root / "docs/reports").mkdir(parents=True)
                name = f"docs/reports/{label}-Report.md"
                content = self.report(6, state="FINALIZED").replace("| Task ID | T6 |", f"| Task ID | {label} |")
                (root / name).write_text(content, encoding="utf-8", newline="\n")
                subprocess.run(["git", "init", "--quiet", str(root)], check=True)
                subprocess.run(["git", "-C", str(root), "add", name], check=True)
                subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c",
                                "user.email=fixture@example.test", "-c", "commit.gpgsign=false",
                                "commit", "--quiet", "-m", "Freeze synthetic companion"], check=True)
                self.assertEqual(validator.finalized_history_issues(root, {name: content}), [])
                (root / name).write_text(content + "Changed\n", encoding="utf-8", newline="\n")
                self.assertTrue(any("modified" in x for x in validator.finalized_history_issues(root, {name: content + "Changed\n"})))
                self.assertTrue(any("deleted or renamed" in x for x in validator.finalized_history_issues(root, {})))

class AssignmentContractTests(unittest.TestCase):
    def setUp(self):
        project = SCRIPT.parents[1]
        self.texts = {name: (project / name).read_text(encoding="utf-8") for name in (
            "docs/assignments/PROJECT-ASSIGNMENT.md", "docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md",
            "docs/testing/TEST-PLAN.md", "docs/security/SECURITY-REQUIREMENTS.md",
            "docs/testing/ACCEPTANCE-CRITERIA.md", ".github/workflows/documentation.yml",
            validator.GUIDE_TRANSITION)}
        self.assignment = "docs/assignments/PROJECT-ASSIGNMENT.md"
        self.guide = "docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md"
        self.plan = "docs/testing/TEST-PLAN.md"

    def assert_rejected(self, name, before, after, expected):
        texts = dict(self.texts)
        self.assertIn(before, texts[name])
        texts[name] = texts[name].replace(before, after, 1)
        self.assertTrue(any(expected in item for item in validator.completeness_issues(texts)))

    def test_focused_specification_is_complete(self):
        self.assertEqual(validator.completeness_issues(self.texts), [])

    def test_duplicate_filename_wrong_format_and_missing_coverage_are_rejected(self):
        for before, after, expected in (
            ("02-Identity-and-Zero-Trust-Implementation.docx", "01-Lab-Environment-and-Architecture.xlsx", "filenames"),
            ("02-Identity-and-Zero-Trust-Implementation.docx", "02-Identity-and-Zero-Trust-Implementation.xlsx", "filenames"),
            ("(FWR-01, FWR-02).", "(FWR-01).", "cover all"),
        ):
            with self.subTest(expected=expected):
                self.assert_rejected(self.assignment, before, after, expected)

    def test_wrong_weights_are_rejected_even_when_total_remains_100(self):
        texts = dict(self.texts)
        texts[self.assignment] = texts[self.assignment].replace("| 25 |", "| 24 |", 1).replace("| 20 |", "| 21 |", 1)
        self.assertTrue(any("rubric" in x for x in validator.completeness_issues(texts)))

    def test_wrong_phase_or_missing_recovery_field_is_rejected(self):
        self.assert_rejected(self.guide, "## Phase 3: Zero Trust Access Controls",
                             "## Phase 3: More systems", "five approved phases")
        self.assert_rejected(self.guide, "### Phase 1 checkpoint and recovery", "### Other", "missing field")

    def test_historical_mapping_gaps_are_rejected(self):
        self.assert_rejected(validator.GUIDE_TRANSITION, "| R02, R03, R04 |", "| R02, R04 |", "historical requirement transition")
        self.assert_rejected(validator.GUIDE_TRANSITION, "| T18 |", "| Old automation |", "historical test transition")

    def test_guide_procedures_require_actions_context_and_failure_recovery(self):
        self.assert_rejected(self.guide, "### Step 1 -", "### Step 0 -", "numbered procedures")
        self.assert_rejected(self.guide, "**Purpose and location:**", "**Background:**", "instructional context")
        self.assert_rejected(self.guide, "**If it fails:**", "**Notes:**", "instructional context")

    def test_guide_numbered_actions_cannot_merge_into_check_paragraphs(self):
        self.assert_rejected(self.guide, "\n\n2. At the Proxmox console", "\n2. At the Proxmox console", "blank line")

    def test_wrong_test_mapping_or_filled_actual_is_rejected(self):
        self.assert_rejected(self.assignment, "| FWT-01 |", "| FWT-02 |", "wrong primary test")
        self.assert_rejected(self.plan, "| Actual result | |", "| Actual result | PASS |", "must be present and empty")
        self.assert_rejected(self.plan, "| Evidence reference | |", "| Evidence reference | invented |", "must be present and empty")

    def test_incomplete_six_cases_and_wrong_traceability_are_rejected(self):
        self.assert_rejected(self.plan, "| C06 |", "| C07 |", "six approved")
        self.assert_rejected(self.plan, "| FSC-03 | FWT-03 | FAC-03 |", "| FSC-03 | FWT-03 | FAC-04 |", "invalid architecture")

    def test_security_control_mapping_drift_is_rejected(self):
        self.assert_rejected("docs/security/SECURITY-REQUIREMENTS.md",
                             "FWR-03; FWT-03", "FWR-03; FWT-04", "invalid security")

    def test_ordered_status_and_released_template_status_are_required(self):
        self.assert_rejected(self.guide, "Xeon W-2145", "Unspecified CPU", "ordered hardware")
        self.assert_rejected(self.assignment, "available as blank templates", "complete and validated lab", "template availability")

    def test_identity_limits_and_legacy_navigation_are_required(self):
        self.assert_rejected(self.assignment, "separate test accounts", "shared Windows accounts", "application identity")
        self.assert_rejected(self.assignment, '<a id="expected-deliverables"></a>', "", "compatibility anchors")
        self.assert_rejected(self.assignment, "## Learning Objectives", "## Learning Objectives\n\nStart T7 now.", "internal task")

    def test_guide_rejects_jargon_unavailable_template_claims_and_missing_context(self):
        self.assert_rejected(self.guide, "## Before beginning the lab",
                             "## Before beginning the lab\n\nT6 stop.", "internal task jargon")
        self.assert_rejected(self.guide, "available as blank templates", "complete and validated lab", "template availability")
        self.assert_rejected(self.guide, "**READ-ONLY - Windows candidate", "**INSPECTION - Windows candidate",
                             "risk/target context")

    def test_guide_retains_approval_and_existing_phase_test_mappings(self):
        self.assert_rejected(self.guide, "each stage A-L", "optional stages", "safeguards")
        texts = dict(self.texts)
        texts[self.guide] = texts[self.guide].replace("FWT-01", "FWT-99")
        self.assertTrue(any("existing test mapping" in item for item in validator.completeness_issues(texts)))

    def test_short_readiness_controls_remain_required(self):
        self.assert_rejected(self.assignment, "backup and recovery", "storage", "hardware readiness")
        self.assert_rejected(self.assignment, "owner approval", "student discretion", "hardware readiness")


if __name__ == "__main__":
    unittest.main()
