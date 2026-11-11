"""Offline regression checks for approved blank shells and unsafe Office parts.

Fixtures are private temporary copies. No Office process, formula execution,
external link, installation or lab resource is used by these tests.
"""
from contextlib import contextmanager
import hashlib
import io
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from scripts import office_template_contract as contract
from scripts import validate_office_templates as office
from scripts.validate_docs import public_content_issues, file_issues

ROOT = Path(__file__).resolve().parents[1]
REL = "docs/deliverables/"


@contextmanager
def fixture():
    base = ROOT / "local/office-tests"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "docs/deliverables", root / REL)
        for relative in ("docs/testing/TEST-PLAN.md", "docs/assignments/PROJECT-ASSIGNMENT.md", "docs/architecture/ARCHITECTURE.md"):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        yield root


def rewrite(path, member, edit, extra=None):
    with ZipFile(path) as package:
        parts = {n: package.read(n) for n in package.namelist()}
    parts[member] = edit(parts[member])
    parts.update(extra or {})
    with ZipFile(path, "w", ZIP_DEFLATED) as package:
        for name, content in parts.items():
            package.writestr(name, content)


def set_cell(raw, address, value=None, formula=None):
    tree = ET.fromstring(raw)
    cell = tree.find(f".//s:c[@r='{address}']", office.NS)
    cell.set("t", "str")
    for node in list(cell):
        cell.remove(node)
    if formula is not None:
        ET.SubElement(cell, "{" + office.NS["s"] + "}f").text = formula
    ET.SubElement(cell, "{" + office.NS["s"] + "}v").text = value or ""
    return ET.tostring(tree)


class OfficeTemplateTests(unittest.TestCase):
    def test_assignment_transition_preserves_frozen_history_and_aligns_office03_description(self):
        baseline = "7387219ab2c4690e5bbed3615c47d892f13b0e12"
        for name, expected in office.T9A_OFFICE_HASHES.items():
            data = subprocess.check_output(["git", "-C", str(ROOT), "show", baseline + ":" + REL + name])
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected, name)
        source = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                          baseline + ":docs/assignments/PROJECT-ASSIGNMENT.md"]).decode()
        self.assertIn("| FWR-02 | " + office.T9A_FWR02 + " | FWT-02 |", source)
        with fixture() as root:
            path = root / "docs/assignments/PROJECT-ASSIGNMENT.md"
            path.write_text(path.read_text().replace(office.T9B_FWR02, "Unapproved requirement", 1))
            self.assertTrue(any("FWR-02 traceability differs" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet4.xml", lambda b: set_cell(b, "B9", office.T9A_FWR02))
            findings = office.template_set_issues(root)
            self.assertIn(f"{office.FILES[2]}: package differs from the approved release", findings)
            self.assertTrue(any("FWR-02 traceability differs" in x for x in findings))

    def test_complete_shipped_shells_and_safe_parts(self):
        self.assertEqual(office.template_set_issues(ROOT), [])
        for filename in office.FILES:
            with self.subTest(filename=filename):
                self.assertEqual(office.package_issues(ROOT, REL + filename, public_content_issues), [])

    def test_missing_or_extra_deliverable_rejected(self):
        with fixture() as root:
            (root / REL / office.FILES[0]).unlink()
            self.assertTrue(office.template_set_issues(root))
        with fixture() as root:
            (root / REL / "unapproved.xlsx").write_bytes(b"unapproved")
            self.assertTrue(office.template_set_issues(root))

    def test_generic_office_extension_is_not_an_allowlist(self):
        with fixture() as root:
            shutil.copyfile(root / REL / office.FILES[0], root / "unreviewed.xlsx")
            findings, _ = file_issues(root, "unreviewed.xlsx")
            self.assertTrue(any("unapproved Office" in x for x in findings))

    def test_corrupt_zip_and_binary_part_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            path.write_bytes(b"not an Office package")
            self.assertTrue(office.package_issues(root, REL + path.name))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "[Content_Types].xml", lambda b: b, {"xl/vbaProject.bin": b"synthetic"})
            self.assertTrue(office.package_issues(root, REL + path.name))

    def test_package_traversal_and_xml_entities_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "[Content_Types].xml", lambda b: b, {"../unexpected.xml": b"<x/>"})
            self.assertTrue(office.package_issues(root, REL + path.name))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/sharedStrings.xml", lambda b: b'<!DOCTYPE x [<!ENTITY x "synthetic">]><x/>')
            self.assertTrue(office.package_issues(root, REL + path.name))

    def test_external_data_and_broken_package_relationship_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            def external(raw):
                tree = ET.fromstring(raw)
                child = list(tree)[0]
                child.set("TargetMode", "External")
                child.set("Target", "https://example.test/data")
                return ET.tostring(tree)
            rewrite(path, "xl/_rels/workbook.xml.rels", external)
            self.assertTrue(any("external data" in x for x in office.package_issues(root, REL + path.name)))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            def missing(raw):
                tree = ET.fromstring(raw)
                child = next(n for n in tree if n.get("Type", "").endswith("/styles"))
                child.set("Target", "missing.xml")
                return ET.tostring(tree)
            rewrite(path, "xl/_rels/workbook.xml.rels", missing)
            self.assertTrue(office.package_issues(root, REL + path.name))

    def test_secret_split_across_word_runs_is_redacted(self):
        with fixture() as root:
            path = root / REL / office.FILES[1]
            secret = "ghp_" + "A" * 36
            def insert(raw):
                tree = ET.fromstring(raw)
                body = tree.find("w:body", office.NS)
                p = ET.SubElement(body, "{" + office.NS["w"] + "}p")
                for text in (secret[:4], secret[4:]):
                    r = ET.SubElement(p, "{" + office.NS["w"] + "}r")
                    ET.SubElement(r, "{" + office.NS["w"] + "}t").text = text
                return ET.tostring(tree)
            rewrite(path, "word/document.xml", insert)
            findings = office.package_issues(root, REL + path.name, public_content_issues)
            self.assertTrue(any("GitHub token" in x for x in findings))
            self.assertNotIn(secret, "\n".join(findings))

    def test_active_formula_and_missing_sheet_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet5.xml", lambda b: set_cell(b, "D8", formula='WEBSERVICE("https://example.test")'))
            self.assertTrue(any("unapproved spreadsheet formula" in x for x in office.package_issues(root, REL + path.name)))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet5.xml", lambda b: set_cell(b, "D8", formula="SUM('Missing Sheet'!A1:A2)"))
            self.assertTrue(any("broken worksheet" in x for x in office.package_issues(root, REL + path.name)))

    def test_protected_workbook_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            def protect(raw):
                tree = ET.fromstring(raw)
                ET.SubElement(tree, "{" + office.NS["s"] + "}workbookProtection")
                return ET.tostring(tree)
            rewrite(path, "xl/workbook.xml", protect)
            self.assertTrue(any("restricted" in x for x in office.package_issues(root, REL + path.name)))

    def test_fabricated_status_or_actual_result_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet3.xml", lambda b: set_cell(b, "G8", "PASS"))
            self.assertTrue(any("records an outcome" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet3.xml", lambda b: set_cell(b, "H8", "Synthetic unsupported result"))
            self.assertTrue(any("actual/evidence" in x for x in office.template_set_issues(root)))

    def test_test_plan_drift_and_owner_acceptance_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet3.xml", lambda b: set_cell(b, "E8", "Changed expectation"))
            self.assertTrue(any("approved test plan" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet8.xml", lambda b: set_cell(b, "C8", "ACCEPTED"))
            self.assertTrue(any("UAT must remain PENDING" in x for x in office.template_set_issues(root)))

    def test_missing_current_plan_fails_closed(self):
        with fixture() as root:
            (root / "docs/testing/TEST-PLAN.md").unlink()
            self.assertTrue(any("could not be verified" in x for x in office.template_set_issues(root)))

    def test_removed_status_dropdown_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[3]
            def remove(raw):
                tree = ET.fromstring(raw)
                for node in tree.findall("s:dataValidations", office.NS):
                    tree.remove(node)
                return ET.tostring(tree)
            rewrite(path, "xl/worksheets/sheet1.xml", remove)
            self.assertTrue(any("dropdown" in x for x in office.template_set_issues(root)))

    def test_missing_subcheck_and_changed_case_outcome_rejected(self):
        for column, value in (("C", "FWT-03.MISSING"), ("E", "Allow")):
            with self.subTest(column=column), fixture() as root:
                path = root / REL / office.FILES[2]
                data = office.workbook_data(office.package_parts(path))["Test Cases"]["cells"]
                address = next(a for a, c in data.items() if a.startswith("C") and c["value"] == "FWT-03.05")
                rewrite(path, "xl/worksheets/sheet3.xml", lambda b: set_cell(b, column + address[1:], value))
                self.assertTrue(any("subcheck" in x or "approved test plan" in x for x in office.template_set_issues(root)))

    def test_plan_change_and_requirement_mapping_drift_rejected(self):
        with fixture() as root:
            p = root / "docs/testing/TEST-PLAN.md"
            p.write_text(p.read_text().replace("No unapproved protected path or integration", "Different approved expectation", 1))
            self.assertTrue(any("approved test plan" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet4.xml", lambda b: set_cell(b, "D8", "FWT-02"))
            self.assertTrue(any("traceability differs" in x for x in office.template_set_issues(root)))

    def test_test_plan_transition_preserves_baseline_and_rejects_scope_drift(self):
        old = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"{office.T9D1_PUBLICATION}:{office.TEST_PLAN}"], encoding="utf-8")
        current = (ROOT / office.TEST_PLAN).read_text(encoding="utf-8")
        self.assertEqual(hashlib.sha256(current.encode("utf-8")).hexdigest(), office.T9D4_PLAN_SHA256)
        self.assertEqual([len(checks) for checks in contract.SUBCHECKS.values()], [9, 9, 13, 7, 7, 11, 9, 7, 10, 9])
        for pattern in (r"^### FWT-.*", r"^\*\*Scope:.*", r"^\| C0[1-6] \|.*", r"^\| (FWR-\d{2}) \| [^|]+(\|.*)"):
            self.assertEqual(re.findall(pattern, old, re.M), re.findall(pattern, current, re.M), pattern)

        with fixture() as root:
            plan = root / office.TEST_PLAN
            plan.write_text(old, encoding="utf-8")
            self.assertTrue(any("approved test plan" in x for x in office.template_set_issues(root)))
            plan.write_text(current.replace("91 mandatory subchecks", "90 mandatory subchecks"), encoding="utf-8")
            self.assertTrue(any("approved test plan" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet3.xml", lambda b: set_cell(b, "D19", "Changed FWT-02.01"))
            findings = office.template_set_issues(root)
            self.assertIn(f"{office.FILES[2]}: package differs from the approved release", findings)
            self.assertTrue(any("FWT-02.01 differs from approved test plan/subchecks" in x for x in findings))

    def test_office03_preserves_exact_child_ids_and_application_cases(self):
        predecessor = "124386dbe95a6d345e72ae0f1086c61b3348708e"
        blob = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{predecessor}:{REL}{office.FILES[2]}"])
        with ZipFile(io.BytesIO(blob)) as package:
            original = office.workbook_data({name: package.read(name) for name in package.namelist()})
        current = office.workbook_data(office.package_parts(ROOT / REL / office.FILES[2]))

        def child_ids(workbook):
            return [cell["value"] for address, cell in workbook["Test Cases"]["cells"].items()
                    if address.startswith("C") and re.fullmatch(r"FWT-\d{2}\.\d{2}", cell["value"])]

        self.assertEqual(len(child_ids(current)), 91)
        self.assertEqual(child_ids(current), child_ids(original))
        original_cases = original["Test Cases"]["cells"]
        current_cases = current["Test Cases"]["cells"]
        for row in range(32, 38):
            for col in "CDEF":
                self.assertEqual(current_cases[f"{col}{row}"], original_cases[f"{col}{row}"])
        self.assertEqual([current_cases[f"E{row}"]["value"] for row in range(32, 38)],
                         ["Allow", "Deny", "Allow", "Allow", "Deny", "Deny"])

    def test_office03_rejects_duplicate_and_extra_child_rows(self):
        with fixture() as root:
            path = root / REL / office.FILES[2]
            rewrite(path, "xl/worksheets/sheet3.xml", lambda raw: set_cell(raw, "C108", "FWT-10.08"))
            self.assertTrue(any("must occur once" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[2]

            def extra_child(raw):
                tree = ET.fromstring(raw)
                ns = "{" + office.NS["s"] + "}"
                row = ET.SubElement(tree.find("s:sheetData", office.NS), ns + "row", {"r": "109"})
                cell = ET.SubElement(row, ns + "c", {"r": "C109", "t": "str"})
                ET.SubElement(cell, ns + "v").text = "FWT-10.10"
                return ET.tostring(tree)

            rewrite(path, "xl/worksheets/sheet3.xml", extra_child)
            self.assertTrue(any("must occur once" in x for x in office.template_set_issues(root)))

    def test_office03_rejects_control_or_procedure_drift(self):
        mutations = (
            (3, "E19", "Four required workload VMs", "FWT-02.01 differs"),
            (3, "D19", "Use a virtual OPNsense VM", "FWT-02.01 differs"),
            (3, "D21", "APP1 may reach DC1 on any service", "FWT-02.03 differs"),
            (3, "D45", "Check only the HP firewall log", "FWT-04.03 differs"),
            (3, "D67", "End the session without recording the revocation change", "FWT-06.09 differs"),
            (6, "A3", "Use an available archive and test path", "A3 approved control or evidence prompt changed"),
            (6, "B15", "Use an isolated existing client", "B15 approved control or evidence prompt changed"),
            (5, "B11", "Run remotely as administrator", "B11 approved control or evidence prompt changed"),
            (1, "C12", "Virtual firewall log", "C12 approved control or evidence prompt changed"),
            (8, "A3", "Accept at 80 points", "A3 approved control or evidence prompt changed"),
        )
        for sheet, address, value, finding in mutations:
            with self.subTest(sheet=sheet, address=address), fixture() as root:
                path = root / REL / office.FILES[2]
                rewrite(path, f"xl/worksheets/sheet{sheet}.xml", lambda raw: set_cell(raw, address, value))
                self.assertTrue(any(finding in issue for issue in office.template_set_issues(root)))

    def test_office03_rejects_missing_evidence_or_unexpected_calculation(self):
        with fixture() as root:
            path = root / REL / office.FILES[2]

            def remove_evidence(raw):
                tree = ET.fromstring(raw)
                row = tree.find(".//s:row[@r='9']", office.NS)
                row.remove(row.find("s:c[@r='I9']", office.NS))
                return ET.tostring(tree)

            rewrite(path, "xl/worksheets/sheet3.xml", remove_evidence)
            self.assertIn("Test Cases: required actual/evidence or other recording field missing",
                          office.template_set_issues(root))
        for sheet, address, value, formula, finding in (
            (3, "G9", "INVALID STATUS", None, "shell status records an outcome"),
            (3, "H9", None, "SUM(1,2)", "unexpected calculation"),
            (8, "G8", "Synthetic acceptance reference", None, "actual/evidence/date fields must be blank"),
        ):
            with self.subTest(sheet=sheet, address=address), fixture() as root:
                path = root / REL / office.FILES[2]
                rewrite(path, f"xl/worksheets/sheet{sheet}.xml",
                        lambda raw: set_cell(raw, address, value, formula))
                self.assertTrue(any(finding in issue for issue in office.template_set_issues(root)))

    def test_missing_formula_guard_and_prepopulated_hardware_state_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet5.xml", lambda b: set_cell(b, "D10", formula="SUM('Virtual Machines'!I8:I11)"))
            self.assertTrue(any("input guards" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet1.xml", lambda b: set_cell(b, "E8", "VALIDATED"))
            self.assertTrue(any("must be blank" in x for x in office.template_set_issues(root)))

    def test_fourth_required_workload_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]

            def add_vm(raw):
                tree = ET.fromstring(raw)
                data = tree.find("s:sheetData", office.NS)
                sheet_ns = "{" + office.NS["s"] + "}"
                row = ET.SubElement(data, sheet_ns + "row", {"r": "11"})
                cell = ET.SubElement(row, sheet_ns + "c", {"r": "A11", "t": "str"})
                ET.SubElement(cell, sheet_ns + "v").text = "OPNsense"
                return ET.tostring(tree)

            rewrite(path, "xl/worksheets/sheet2.xml", add_vm)
            self.assertIn("Virtual Machines: approved inventory or zone order changed", office.template_set_issues(root))

    def test_wrong_planned_budget_or_guest_input_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            formula = office.RESOURCE_FORMULAS["C16"]
            rewrite(path, "xl/worksheets/sheet5.xml", lambda b: set_cell(b, "C16", "336", formula))
            self.assertIn("Resource Allocation: planned guest totals or Dell ledger differ from the approved budget",
                          office.template_set_issues(root))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet2.xml", lambda b: set_cell(b, "E8", "8"))
            self.assertIn("Virtual Machines: approved zone or allocation changed at row 8", office.template_set_issues(root))

    def test_guest_actual_and_stale_actual_formula_cache_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet2.xml", lambda b: set_cell(b, "G8", "2"))
            self.assertTrue(any("actual/evidence/date fields must be blank" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            formula = office.RESOURCE_FORMULAS["D8"]
            rewrite(path, "xl/worksheets/sheet5.xml", lambda b: set_cell(b, "D8", "6", formula))
            self.assertIn("Resource Allocation: cached actual totals must be blank", office.template_set_issues(root))

    def test_missing_evidence_header_or_answer_cell_rejected(self):
        for address in ("L7", "L8"):
            with self.subTest(address=address), fixture() as root:
                path = root / REL / office.FILES[0]

                def remove_cell(raw):
                    tree = ET.fromstring(raw)
                    row = tree.find(f".//s:row[@r='{address[1:]}']", office.NS)
                    row.remove(row.find(f"s:c[@r='{address}']", office.NS))
                    return ET.tostring(tree)

                rewrite(path, "xl/worksheets/sheet2.xml", remove_cell)
                self.assertIn("Virtual Machines: required evidence field missing", office.template_set_issues(root))

    def test_each_office_package_must_match_its_released_bytes(self):
        for filename in office.FILES:
            with self.subTest(filename=filename), fixture() as root:
                path = root / REL / filename
                rewrite(path, "[Content_Types].xml", lambda raw: raw + b"\n")
                self.assertEqual(office.package_issues(root, REL + filename, public_content_issues), [])
                self.assertEqual(office.template_set_issues(root), [f"{filename}: package differs from the approved release"])

    def test_legacy_target_extra_sheet_and_wrong_font_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/worksheets/sheet1.xml", lambda b: set_cell(b, "J8", "six security zones"))
            self.assertTrue(any("obsolete enterprise" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/workbook.xml", lambda b: b.replace(b'Hardware &amp; Readiness', b'Unnecessary Sheet'))
            self.assertTrue(office.template_set_issues(root))
        with fixture() as root:
            path = root / REL / office.FILES[0]
            rewrite(path, "xl/styles.xml", lambda b: b.replace(b'Segoe UI', b'Other Font', 1))
            self.assertTrue(any("fonts must use Segoe UI" in x for x in office.template_set_issues(root)))

    def test_word_answer_score_heading_and_page_fields_rejected(self):
        for target, index, column, value in ((office.FILES[1], 0, 2, "Unsupported observation"), (office.FILES[4], 3, 2, "25"), (office.FILES[4], 3, 1, "24")):
            with self.subTest(target=target, column=column), fixture() as root:
                path = root / REL / target
                def change(raw):
                    tree = ET.fromstring(raw)
                    tables = tree.findall(".//w:body/w:tbl", office.NS)
                    cell = tables[index].findall("w:tr", office.NS)[1].findall("w:tc", office.NS)[column]
                    paragraph = cell.find("w:p", office.NS)
                    for node in list(paragraph):
                        paragraph.remove(node)
                    run = ET.SubElement(paragraph, "{" + office.NS["w"] + "}r")
                    ET.SubElement(run, "{" + office.NS["w"] + "}t").text = value
                    return ET.tostring(tree)
                rewrite(path, "word/document.xml", change)
                self.assertTrue(any("blank" in x or "rubric" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[1]
            rewrite(path, "word/document.xml", lambda b: b.replace(b'Heading1', b'Normal', 1))
            self.assertTrue(any("heading styles" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[1]
            rewrite(path, "word/footer1.xml", lambda b: b.replace(b'NUMPAGES', b'UNAPPROVED'))
            self.assertTrue(any("page numbering" in x for x in office.template_set_issues(root)))
            self.assertTrue(any("active Word field" in x for x in office.package_issues(root, REL + path.name)))

    def test_office02_rejects_control_and_evidence_drift(self):
        changes = (
            ("exactly three workload VMs", "four required workload VMs", "approved three-workload architecture"),
            ("Standard analyst; LabReaders", "Standard analyst; LabAdmins", "approved directory or Apache group memberships"),
            ("AD single sign-on and automatic role synchronization are excluded.",
             "AD automatically synchronizes Apache roles.", "independent Apache roles"),
            ("APP1 TCP 443-only grant", "grant to the Corporate subnet on all ports", "Tailscale access boundary"),
            ("new network requests from existing authenticated and fresh sessions",
             "a request from the same browser", "revocation evidence"),
            ("known-listening denial to the APP1 rule and log or counter.",
             "denial to the HP firewall log.", "endpoint enforcement attribution"),
            ("Match each denial to effective grants, device state, independent APP1 host rules or Apache roles and logs.",
             "A failed connection verifies the grant.", "remote denial attribution"),
            ("[Insert a sanitized certificate/browser screenshot and an evidence ID.]",
             "", "answer or screenshot/evidence prompts missing"),
            ("Evidence ID</w:t>", "Notes</w:t>", "application evidence field missing"),
        )
        for original, altered, finding in changes:
            with self.subTest(finding=finding), fixture() as root:
                path = root / REL / office.FILES[1]

                def mutate(raw):
                    self.assertIn(original.encode(), raw)
                    return raw.replace(original.encode(), altered.encode(), 1)

                rewrite(path, "word/document.xml", mutate)
                self.assertTrue(any(finding in issue for issue in office.template_set_issues(root)))

    def test_office02_rejects_prefilled_case_evidence(self):
        with fixture() as root:
            path = root / REL / office.FILES[1]

            def prefill(raw):
                tree = ET.fromstring(raw)
                table = tree.findall(".//w:body/w:tbl", office.NS)[4]
                evidence_cell = table.findall("w:tr", office.NS)[1].findall("w:tc", office.NS)[4]
                evidence_cell.find(".//w:t", office.NS).text = "QA-FILLED"
                return ET.tostring(tree)

            rewrite(path, "word/document.xml", prefill)
            self.assertTrue(any("actual/score/evidence answer cells must be blank" in issue
                                for issue in office.template_set_issues(root)))

    def test_undeclared_compatibility_prefix_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[1]
            def incompatible(raw):
                tree = ET.fromstring(raw)
                tree.set("{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable", "undeclared")
                return ET.tostring(tree)
            rewrite(path, "word/document.xml", incompatible)
            self.assertTrue(any("compatibility prefix" in x for x in office.package_issues(root, REL + path.name)))

    def test_network_flow_and_word_case_expectations_rejected(self):
        for address in ("C8", "C11", "C15"):
            with self.subTest(address=address), fixture() as root:
                path = root / REL / office.FILES[0]
                rewrite(path, "xl/worksheets/sheet4.xml", lambda b: set_cell(b, address, "Allow all services"))
                self.assertTrue(any("permission/enforcement" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[1]
            def wrong_case(raw):
                tree = ET.fromstring(raw)
                case_table = tree.findall(".//w:body/w:tbl", office.NS)[4]
                expected = case_table.findall("w:tr", office.NS)[1].findall("w:tc", office.NS)[2]
                expected.find(".//w:t", office.NS).text = "Deny"
                return ET.tostring(tree)
            rewrite(path, "word/document.xml", wrong_case)
            self.assertTrue(any("six approved application cases" in x for x in office.template_set_issues(root)))


class FrozenTemplateLinkTests(unittest.TestCase):
    def test_only_unchanged_t5_report_resolves_retired_targets(self):
        from scripts import validate_docs as docs
        relative = "docs/reports/T5-Report.md"
        original = (ROOT / relative).read_text(encoding="utf-8")
        self.assertEqual(docs.link_issues(ROOT, relative, original), [])
        self.assertTrue(any("missing local link" in x for x in docs.link_issues(ROOT, relative, original + "\nChanged")))
        self.assertTrue(docs.link_issues(ROOT, "docs/README.md", "[retired](deliverables/01-Lab-Environment.xlsx)"))
        with patch.object(docs.subprocess, "run", side_effect=OSError("missing history")):
            self.assertTrue(any("missing local link" in x for x in docs.link_issues(ROOT, relative, original)))


if __name__ == "__main__":
    unittest.main()
