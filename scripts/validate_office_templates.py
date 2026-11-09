#!/usr/bin/env python3
"""Offline checks for the five approved blank four-week Office packages.

This is a bounded package/content check, not a native Office renderer or a
complete secret detector. It never opens external links or executes formulas.
"""
from __future__ import annotations

import hashlib
import io
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
try:
    from office_template_contract import FILES, SHEETS, STATUSES, OWNER_DECISIONS, ISSUE_STATUSES, WORD_SECTIONS, SUBCHECKS, RUBRIC, approved_tests
except ModuleNotFoundError:
    from scripts.office_template_contract import FILES, SHEETS, STATUSES, OWNER_DECISIONS, ISSUE_STATUSES, WORD_SECTIONS, SUBCHECKS, RUBRIC, approved_tests
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
FORMULAS = {"IF", "COUNT", "SUM"}
TEST_PLAN = "docs/testing/TEST-PLAN.md"

# The T9D.4 Test Plan supersedes T9D.2 while workbook 03 still quotes T9D.1.
# Pair the exact audited source (LF-normalized) with the byte-frozen Office
# baseline and keep checking every legacy row against the published plan.
T9D1_PUBLICATION = "2852dbd8b5e85bf7e306650e6e73013860dfec4c"
T9D4_PLAN_SHA256 = "fdc664297e107b8f90179a4bb5da0e30bea8d91220067466ead9d78ff664e900"

# T9B changes only the assignment's FWR-02 architecture wording. Office
# alignment is separately authorized later. Preserve the exact published T9A
# packages and their old description, while still checking every mapping,
# method, subcheck and package safeguard. This is preservation, not alignment.
T9B_FWR02 = "Verify the prepared Dell/Proxmox host, physical HP/OPNsense firewall, three workload VMs and three zones; deny unlisted flows, restrict administration, retain console recovery and confirm measured capacity fits."
T9A_FWR02 = "Run one host, four VMs and three zones; deny unlisted flows, restrict administration, retain console recovery and confirm measured capacity fits."
T9A_OFFICE_HASHES = {
    FILES[0]: "33a0a1ac1204c308b89cff131463d7c75f7ef804aeeef4d61073993f790b26c0",
    FILES[1]: "5ff8ce00c7d83d530643cdbb8c32c6f1ccb8b9e9f9fd26f7dbc80c60824d4d54",
    FILES[2]: "1281d20065d0c74e06e8e2490c81b99086f030b94af57fa75e465cda10e866ec",
    FILES[3]: "084423d2c1daa47a23a8fe9bc2afb0cbc02866e6d0fca836050ead604fd368ae",
    FILES[4]: "6e5622322ab962e03b159e31d4d5b1098d89de656fb7151ac09c24b7f53100c6",
}

BLANK_COLUMNS = {
    "Hardware & Readiness": "DEFGIJ", "Virtual Machines": "GHIJL",
    "Network Zones": "EFHI", "Allowed Network Flows": "DEGH",
    "Resource Allocation": "DGH", "Security Events": "DEFGHIK",
    "Denied Access Investigation": "CDFG", "Test Cases": "HIJKL",
    "Requirements Coverage": "HI", "Automation Verification": "CDFG",
    "Backup & Restore": "CDFG", "Evidence Index": "ABCDEFG",
    "Owner Acceptance": "DEFG", "Issue Log": "ABCDEFGHIJK",
}
RESOURCE_FORMULAS = {
    "C8": "SUM('Virtual Machines'!D8:D11)", "C9": "SUM('Virtual Machines'!E8:E11)",
    "C10": "SUM('Virtual Machines'!F8:F11)",
    "D8": "IF(COUNT('Virtual Machines'!G8:G11)<4,\"\",SUM('Virtual Machines'!G8:G11))",
    "D9": "IF(COUNT('Virtual Machines'!H8:H11)<4,\"\",SUM('Virtual Machines'!H8:H11))",
    "D10": "IF(COUNT('Virtual Machines'!I8:I11)<4,\"\",SUM('Virtual Machines'!I8:I11))",
    "C16": "SUM(C10,C12:C15)", "D16": 'IF(COUNT(D10,D12:D15)<5,"",SUM(D10,D12:D15))',
}


def package_parts(path: Path) -> dict[str, bytes]:
    """Bound reads before decompressing; no extraction to the filesystem."""
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("Office package exceeds 5 MiB")
    with ZipFile(path) as package:
        infos = package.infolist()
        if len(infos) > 200 or len({i.filename for i in infos}) != len(infos):
            raise ValueError("oversized or duplicate package inventory")
        if sum(i.file_size for i in infos) > 15 * 1024 * 1024:
            raise ValueError("Office expanded package exceeds 15 MiB")
        if package.comment or any(i.flag_bits & 1 or i.comment for i in infos):
            raise ValueError("encrypted/commented Office package is not approved")
        for info in infos:
            name = info.filename
            if (name.startswith(("/", "\\")) or "\\" in name or ":" in name
                    or ".." in name.split("/") or not name.endswith((".xml", ".rels"))):
                raise ValueError("unsafe or non-XML Office package member")
            if re.search(r"vba|activex|embeddings|customxml|externallinks|connections|printersettings", name, re.I):
                raise ValueError("active, embedded or external-data Office part")
        parts = {i.filename: package.read(i) for i in infos}
        if any(b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper() for raw in parts.values()):
            raise ValueError("prohibited XML declaration")
        return parts


def package_issues(root: Path, relative: str, scan_text=None) -> list[str]:
    if relative not in {"docs/deliverables/" + n for n in FILES}:
        return [f"{relative}: unapproved Office filename or location"]
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        return [f"{relative}: unsafe Office path"]
    issues = []
    try:
        parts = package_parts(root / relative)
        required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml" if relative.endswith(".docx") else "xl/workbook.xml"}
        if not required.issubset(parts):
            return [f"{relative}: incomplete Office package"]
        sheet_names = set(workbook_data(parts)) if relative.endswith(".xlsx") else set()
        for name, raw in parts.items():
            tree = ET.fromstring(raw)
            declared = {prefix for _, (prefix, _) in ET.iterparse(io.BytesIO(raw), events=("start-ns",))}
            for node in tree.iter():
                ignored = node.get("{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable", "").split()
                if set(ignored) - declared:
                    issues.append(f"{relative}: undeclared Office compatibility prefix")
            if scan_text:
                # Inspect text and attributes, including metadata and relationships.
                # Join runs within a paragraph/cell, retaining record boundaries
                # so an adjacent label cannot conceal a token's word boundary.
                blocks = ["".join(n.itertext()) for n in tree.iter()
                          if n.tag.rsplit("}", 1)[-1] in {"p", "si", "c"}]
                visible = "\n".join(blocks or list(tree.itertext()))
                issues.extend(scan_text(f"{relative}:{name}", raw.decode("utf-8-sig") + "\n" + visible))
            for node in tree.iter():
                tag = node.tag.rsplit("}", 1)[-1]
                if tag in {"documentProtection", "writeProtection", "sheetProtection", "workbookProtection", "fileSharing", "dataConnection", "oleObject", "altChunk", "externalReference"}:
                    issues.append(f"{relative}: restricted or active Office element")
                if tag == "fldSimple" and node.get("{" + NS["w"] + "}instr", "").strip() not in {"PAGE", "NUMPAGES"}:
                    issues.append(f"{relative}: unsupported active Word field")
                if tag == "instrText":
                    issues.append(f"{relative}: complex Word fields are not approved in blank shells")
                if tag == "f":
                    formula = node.text or ""
                    functions = set(re.findall(r"([A-Za-z_.]+)\s*\(", formula))
                    if functions - FORMULAS or any(x in formula for x in ("[", "]", "|")):
                        issues.append(f"{relative}: unapproved spreadsheet formula")
                    references = re.findall(r"'([^']+)'!|([A-Za-z_][A-Za-z0-9_]*)!", formula)
                    if any((quoted or plain) not in sheet_names for quoted, plain in references):
                        issues.append(f"{relative}: broken worksheet formula reference")
                if tag != "Relationship":
                    continue
                target = unquote(node.get("Target", ""))
                if node.get("TargetMode") == "External":
                    url = urlsplit(target)
                    if node.get("Type", "").rsplit("/", 1)[-1] != "hyperlink":
                        issues.append(f"{relative}: external data relationship")
                    elif url.scheme:
                        if url.scheme != "https" or url.hostname != "github.com" or not url.path.lower().startswith("/waqashamdani-ca/enterprise-zero-trust-security/"):
                            issues.append(f"{relative}: unapproved external hyperlink")
                    elif target not in FILES or not (root / "docs/deliverables" / target).is_file():
                        issues.append(f"{relative}: broken supporting-deliverable hyperlink")
                else:
                    base = "" if name == "_rels/.rels" else posixpath.dirname(posixpath.dirname(name))
                    resolved = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(base, target))
                    if resolved not in parts:
                        issues.append(f"{relative}: broken internal package relationship")
    except (OSError, BadZipFile, ET.ParseError, ValueError, RuntimeError, UnicodeError, KeyError, IndexError, TypeError):
        issues.append(f"{relative}: malformed, unsafe or oversized Office package")
    return sorted(set(issues))


def workbook_data(parts: dict[str, bytes]) -> dict[str, dict]:
    strings = []
    if "xl/sharedStrings.xml" in parts:
        strings = ["".join(si.itertext()) for si in ET.fromstring(parts["xl/sharedStrings.xml"])]
    book = ET.fromstring(parts["xl/workbook.xml"])
    relationships = {r.get("Id"): r.get("Target") for r in ET.fromstring(parts["xl/_rels/workbook.xml.rels"])}
    sheets = {}
    for sheet in book.findall("s:sheets/s:sheet", NS):
        target = relationships[sheet.get("{" + NS["r"] + "}id")]
        name = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        tree = ET.fromstring(parts[name])
        cells = {}
        for cell in tree.findall("s:sheetData/s:row/s:c", NS):
            value = cell.findtext("s:v", default="", namespaces=NS)
            if cell.get("t") == "s":
                value = strings[int(value)]
            elif cell.get("t") == "inlineStr":
                value = "".join(cell.find("s:is", NS).itertext())
            cells[cell.get("r")] = dict(value=value, formula=cell.findtext("s:f", default="", namespaces=NS), style=cell.get("s", "0"))
        sheets[sheet.get("name")] = dict(tree=tree, cells=cells)
    return sheets


def plain_word(parts: dict[str, bytes]) -> str:
    return "\n".join("".join(p.itertext()) for p in ET.fromstring(parts["word/document.xml"]).findall(".//w:p", NS))


def frozen_office_baseline(directory: Path) -> bool:
    return all(hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected
               for name, expected in T9A_OFFICE_HASHES.items())


def template_set_issues(root: Path) -> list[str]:
    directory = root / "docs/deliverables"
    if not directory.is_dir():
        return ["T7 requires all five approved Office templates"]
    issues = []
    if {p.name for p in directory.iterdir()} != set(FILES):
        issues.append("docs/deliverables/ must contain exactly the five approved Office templates")
    try:
        plan = (root / TEST_PLAN).read_text(encoding="utf-8")
        definitions = approved_tests(plan)
        if hashlib.sha256(plan.encode("utf-8")).hexdigest() == T9D4_PLAN_SHA256:
            if not frozen_office_baseline(directory):
                issues.append("Test Plan transition permits only the byte-frozen published Office baseline")
            published_plan = subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{T9D1_PUBLICATION}:{TEST_PLAN}"],
                encoding="utf-8", stderr=subprocess.PIPE)
            definitions = approved_tests(published_plan)
        all_workbooks = {}
        for filename, expected in SHEETS.items():
            parts = package_parts(directory / filename)
            data = workbook_data(parts)
            all_workbooks[filename] = data
            if tuple(data) != expected:
                issues.append(f"{filename}: incorrect worksheet inventory/order")
            styles = ET.fromstring(parts["xl/styles.xml"])
            if any(n.get("val") != "Segoe UI" for n in styles.findall("s:fonts/s:font/s:name", NS)):
                issues.append(f"{filename}: spreadsheet fonts must use Segoe UI")
            theme = ET.fromstring(parts["xl/theme/theme1.xml"])
            if any(n.get("typeface") != "Segoe UI" for n in theme.iter() if "typeface" in n.attrib):
                issues.append(f"{filename}: theme fonts must use Segoe UI")
            tables = [ET.fromstring(v) for k, v in parts.items() if k.startswith("xl/tables/") and k.endswith(".xml")]
            if len(tables) != len(expected) or len({t.get("name") for t in tables}) != len(tables):
                issues.append(f"{filename}: missing or duplicate named tables")
            if any(t.find("s:autoFilter", NS) is None for t in tables):
                issues.append(f"{filename}: table filters are missing")
            for sheet_name, sheet in data.items():
                tree, cells = sheet["tree"], sheet["cells"]
                pane = tree.find("s:sheetViews/s:sheetView/s:pane", NS)
                if pane is None or pane.get("state") != "frozen" or pane.get("ySplit") != "7" or pane.get("xSplit") != "2":
                    issues.append(f"{filename}:{sheet_name}: frozen headers/identifiers missing")
                headers = {a[:-1]: c["value"] for a, c in cells.items() if re.fullmatch(r"[A-Z]+7", a)}
                for address, c in cells.items():
                    match = re.fullmatch(r"([A-Z]+)([0-9]+)", address)
                    if not match or int(match[2]) < 8:
                        continue
                    col = match[1]
                    if col in BLANK_COLUMNS[sheet_name] and c["value"] and not c["formula"]:
                        issues.append(f"{filename}:{sheet_name}: actual/evidence/date fields must be blank")
                    if c["formula"] and sheet_name != "Resource Allocation":
                        issues.append(f"{filename}:{sheet_name}: unexpected calculation")
                    label = headers.get(col)
                    if label in {"Status", "Engineering status"} and sheet_name != "Issue Log" and c["value"] != "NOT TESTED":
                        issues.append(f"{filename}:{sheet_name}: shell status records an outcome")
                    if label == "Owner decision" and c["value"] != "PENDING":
                        issues.append(f"{filename}: owner UAT must remain PENDING")
                    if c["value"].startswith(("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#NUM!")):
                        issues.append(f"{filename}:{sheet_name}: cached formula error")
                for col, label in headers.items():
                    if label not in {"Status", "Engineering status", "Owner decision"}:
                        continue
                    approved = OWNER_DECISIONS if label == "Owner decision" else ISSUE_STATUSES if sheet_name == "Issue Log" else STATUSES
                    validations = tree.findall("s:dataValidations/s:dataValidation", NS)
                    matching = [n for n in validations if n.get("sqref", "").startswith(col + "8:") and n.findtext("s:formula1", default="", namespaces=NS).strip('"') == approved]
                    if not matching or any(n.get("showErrorMessage") != "1" for n in matching) or tree.find("s:conditionalFormatting", NS) is None:
                        issues.append(f"{filename}:{sheet_name}: status dropdown/conditional formatting missing")
                visible = "\n".join(c["value"] for c in cells.values())
                if re.search(r"\b(?:R[0-9]{2}|T[0-9]{2}|S[0-9]{2})\b|six (?:security )?zones|six standard users|two-tier|twenty.event|twelve application|two automation", visible, re.I):
                    issues.append(f"{filename}:{sheet_name}: obsolete enterprise target or ID")
        cases = all_workbooks[FILES[2]]["Test Cases"]["cells"]
        expected_rows = []
        for t in definitions:
            expected_rows.append([t["id"], t["requirement"], "OVERALL", t["title"] + "\n" + t["scope"] + "\n" + t["method"], t["expected"], t["second"]])
            expected_rows.extend([[t["id"], t["requirement"], f'{t["id"]}.{i:02}', action, expectation, detail] for i, (action, expectation, detail) in enumerate(SUBCHECKS[t["id"]], 1)])
        actual_ids = [c["value"] for a, c in cases.items() if re.fullmatch(r"C(?:[89]|[1-9][0-9]+)", a)]
        if actual_ids != [r[2] for r in expected_rows]:
            issues.append("Test Cases: ten tests and all mandatory subchecks must occur once in approved order")
        for rn, expected in enumerate(expected_rows, 8):
            if [cases.get(f"{col}{rn}", {}).get("value", "") for col in "ABCDEF"] != expected:
                issues.append(f"Test Cases: {expected[0]}/{expected[2]} differs from approved test plan/subchecks")
        coverage = all_workbooks[FILES[2]]["Requirements Coverage"]["cells"]
        assignment = (root / "docs/assignments/PROJECT-ASSIGNMENT.md").read_text(encoding="utf-8")
        required = re.findall(r"^\| (FWR-\d{2}) \| ([^|]+) \| FWT-\d{2} \|$", assignment, re.M)
        if len(required) != 10:
            raise ValueError("Missing approved requirements")
        owners = ["01", "01", "02", "02", "02", "02", "03", "03", "03", "03, 04, 05"]
        for rn, ((rid, required_result), owner) in enumerate(zip(required, owners), 8):
            if rid == "FWR-02" and required_result.strip() == T9B_FWR02:
                if not frozen_office_baseline(directory):
                    issues.append("FWR-02 transition permits only the byte-frozen published Office baseline; package alignment requires its approved scope")
                required_result = T9A_FWR02
            expected = [rid, required_result.strip(), rid.replace("FWR", "FSC"), rid.replace("FWR", "FWT"), rid.replace("FWR", "FAC"), owner]
            if [coverage.get(f"{col}{rn}", {}).get("value") for col in "ABCDEF"] != expected:
                issues.append(f"Requirements Coverage: {rid} traceability differs from approved assignment")
        resource = all_workbooks[FILES[0]]["Resource Allocation"]["cells"]
        if {a: c["formula"] for a, c in resource.items() if c["formula"]} != RESOURCE_FORMULAS:
            issues.append("Resource Allocation: approved simple totals/input guards changed")
        for name, expected in (("Virtual Machines", ["OPNsense", "DC1", "WIN1", "APP1"]), ("Network Zones", ["Management", "Corporate", "Restricted"])):
            cells = all_workbooks[FILES[0]][name]["cells"]
            values = [c["value"] for a, c in cells.items() if re.fullmatch(r"A(?:[89]|[1-9][0-9]+)", a)]
            if values != expected:
                issues.append(f"{name}: approved four-VM/three-zone baseline changed")
        flows = all_workbooks[FILES[0]]["Allowed Network Flows"]["cells"]
        architecture = (root / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        approved_flows = re.findall(r"^\| (FF-\d{2}) \| ([^|]+) \| ([^|]+) \|$", architecture, re.M)
        if len(approved_flows) != 8:
            raise ValueError("Missing approved flows")
        for rn, expected in enumerate(approved_flows, 8):
            if [flows.get(f"{c}{rn}", {}).get("value") for c in "ABC"] != [v.strip() for v in expected]:
                issues.append("Allowed Network Flows: approved permission/enforcement changed")
        events = all_workbooks[FILES[2]]["Security Events"]["cells"]
        categories = ["Directory logon success", "One directory logon failure", "Application allow", "Authenticated application denial", "Firewall denial"]
        if [events.get(f"B{r}", {}).get("value") for r in range(8, 13)] != categories:
            issues.append("Security Events: five approved event categories missing")
        for filename, prefix, count in ((FILES[2], "A", 7), (FILES[2], "B", 10)):
            name = "Automation Verification" if prefix == "A" else "Backup & Restore"
            cells = all_workbooks[filename][name]["cells"]
            if [cells.get(f"A{r}", {}).get("value") for r in range(8, 8 + count)] != [f"{prefix}{i:02}" for i in range(1, count + 1)]:
                issues.append(f"{name}: approved exercise check fields missing")
        for filename in (FILES[1], FILES[4]):
            parts = package_parts(directory / filename)
            word_text = plain_word(parts)
            document = ET.fromstring(parts["word/document.xml"])
            if "Blank template" not in word_text or "[Enter" not in word_text or document.find(".//w:pStyle[@w:val='Title']", NS) is None:
                issues.append(f"{filename}: editable template title/answer areas missing")
            headings = ["".join(p.itertext()) for p in document.findall(".//w:body/w:p", NS) if p.find("w:pPr/w:pStyle[@w:val='Heading1']", NS) is not None]
            if headings != [f"{i} {s}" for i, s in enumerate(WORD_SECTIONS[filename], 1)]:
                issues.append(f"{filename}: required Word heading styles/sections missing")
            if document.find(".//w:headerReference", NS) is None or document.find(".//w:footerReference", NS) is None:
                issues.append(f"{filename}: header/footer missing")
            footer = b"".join(v for k, v in parts.items() if re.fullmatch(r"word/footer\d+\.xml", k))
            if b"PAGE" not in footer or b"NUMPAGES" not in footer:
                issues.append(f"{filename}: page numbering missing")
            for name, raw in parts.items():
                if not name.startswith("word/"):
                    continue
                tree = ET.fromstring(raw)
                for node in tree.findall(".//w:rFonts", NS):
                    if any(value != "Segoe UI" for key, value in node.attrib.items() if key.rsplit("}", 1)[-1] in {"ascii", "hAnsi", "eastAsia", "cs"}):
                        issues.append(f"{filename}: Word fonts must use Segoe UI")
            tables = [[["".join(c.itertext()) for c in tr.findall("w:tc", NS)] for tr in t.findall("w:tr", NS)] for t in document.findall(".//w:body/w:tbl", NS)]
            blank_columns = {0: (2,), 1: (1, 2), 2: (2,), 3: (1,)} if filename == FILES[1] else {0: (1,), 1: (1,), 2: (1,), 3: (2, 3)}
            for index, columns in blank_columns.items():
                if any(record[c] for record in tables[index][1:] for c in columns):
                    issues.append(f"{filename}: actual/score/evidence answer cells must be blank")
            if filename == FILES[1]:
                contexts = ["ava /reports/", "ava /maintenance/", "eli /reports/", "eli /maintenance/", "uma /reports/", "uma /maintenance/"]
                outcomes = ["Allow", "Deny", "Allow", "Allow", "Deny", "Deny"]
                expected_cases = [[f"C{i:02}", context, outcome, f"FWT-03.{i+3:02}"] for i, (context, outcome) in enumerate(zip(contexts, outcomes), 1)]
                if tables[4][1:] != expected_cases:
                    issues.append(f"{filename}: six approved application cases/record references changed")
            if filename == FILES[4] and tables[3] != [["Assessment area", "Maximum", "Score", "Evidence / evaluator note"]] + [[title, str(score), "", ""] for title, score in RUBRIC] + [["TOTAL", "100", "", ""]]:
                issues.append(f"{filename}: approved 100-point rubric/blank scores changed")
            if re.search(r"\b(?:R[0-9]{2}|T[0-9]{2}|S[0-9]{2})\b|six (?:security )?zones|two-tier|twenty.event|twelve application|two automation", word_text, re.I):
                issues.append(f"{filename}: obsolete enterprise target or ID")
    except (OSError, BadZipFile, ET.ParseError, ValueError, KeyError, IndexError, TypeError, subprocess.CalledProcessError):
        issues.append("Office template structure/approved plan traceability could not be verified")
    return sorted(set(issues))


def main() -> int:
    from validate_docs import public_content_issues
    issues = template_set_issues(ROOT)
    for filename in FILES:
        issues.extend(package_issues(ROOT, "docs/deliverables/" + filename, public_content_issues))
    if issues:
        print(f"FAIL: {len(set(issues))} Office template finding(s)")
        for issue in sorted(set(issues)):
            print("- " + issue)
        return 1
    print("PASS: five editable blank Office packages; 14 worksheets; FWR-01 to FWR-10; ten FWT tests/91 mandatory subchecks; exact approved outcomes; blank actuals/evidence; separate pending UAT; 100-point rubric.")
    if T9B_FWR02 in (ROOT / "docs/assignments/PROJECT-ASSIGNMENT.md").read_text(encoding="utf-8"):
        print("BASELINE: FWR-02 checks byte-frozen published Office content; physical-firewall alignment remains deferred to T9E, not validated here.")
    if hashlib.sha256((ROOT / TEST_PLAN).read_text(encoding="utf-8").encode("utf-8")).hexdigest() == T9D4_PLAN_SHA256:
        print("BASELINE: Test Cases preserves the exact published workbook rows against the prior Test Plan. The revised plan is checked separately; workbook wording awaits T9E.")
    print("LIMITS: native opening/editing/recalculation and visual review require separate observations; owner UAT remains PENDING.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
