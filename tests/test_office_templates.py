"""Offline regression checks for approved blank shells and unsafe Office parts.

Fixtures are private temporary copies. No Office process, formula execution,
external link, installation or lab resource is used by these tests.
"""
from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

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
            rewrite(path, "xl/_rels/workbook.xml.rels", lambda b: b.replace(b"/xl/styles.xml", b"/xl/missing.xml"))
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
            path = root / REL / office.FILES[5]
            rewrite(path, "xl/worksheets/sheet1.xml", lambda b: set_cell(b, "H8", "Pass"))
            self.assertTrue(any("records an outcome" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[5]
            rewrite(path, "xl/worksheets/sheet1.xml", lambda b: set_cell(b, "I8", "Synthetic unsupported result"))
            self.assertTrue(any("actual/evidence" in x for x in office.template_set_issues(root)))

    def test_test_plan_drift_and_owner_acceptance_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[5]
            rewrite(path, "xl/worksheets/sheet1.xml", lambda b: set_cell(b, "F8", "Changed expectation"))
            self.assertTrue(any("approved test plan" in x for x in office.template_set_issues(root)))
        with fixture() as root:
            path = root / REL / office.FILES[5]
            rewrite(path, "xl/worksheets/sheet7.xml", lambda b: set_cell(b, "D8", "Accepted"))
            self.assertTrue(any("UAT must remain Pending" in x for x in office.template_set_issues(root)))

    def test_missing_legacy_plan_fails_closed(self):
        with fixture() as root:
            with patch.object(office.subprocess, "check_output",
                              side_effect=subprocess.CalledProcessError(1, ["git"])):
                self.assertTrue(any("could not be verified" in x for x in office.template_set_issues(root)))

    def test_removed_status_dropdown_rejected(self):
        with fixture() as root:
            path = root / REL / office.FILES[6]
            def remove(raw):
                tree = ET.fromstring(raw)
                for node in tree.findall("s:dataValidations", office.NS):
                    tree.remove(node)
                return ET.tostring(tree)
            rewrite(path, "xl/worksheets/sheet1.xml", remove)
            self.assertTrue(any("dropdown" in x for x in office.template_set_issues(root)))


if __name__ == "__main__":
    unittest.main()
