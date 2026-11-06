#!/usr/bin/env python3
"""Offline checks for the eight approved blank T5 Office packages.

This is a bounded package/content check, not a native Office renderer or a
complete secret detector. It never opens external links or executes formulas.
"""
from __future__ import annotations

import hashlib
import subprocess
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
# T6 preserves legacy shells; T7 alone may migrate their historical contract.
LEGACY_TEST_PLAN_REF = "b838c00bc7d4478251662fc2086059d38a2c7ffd"
LEGACY_TEST_PLAN_SHA256 = "c01a987e29cfcfe637d5f25bbdbd8fecef526ae8175c0a6f9f3b604063e27811"
FILES = (
    "01-Lab-Environment.xlsx", "02-Architecture-and-Network-Design.docx",
    "03-Identity-and-Access-Management.xlsx", "04-Zero-Trust-Implementation.docx",
    "05-Security-Monitoring.xlsx", "06-Testing-and-Validation.xlsx",
    "07-Troubleshooting-and-Lessons.xlsx", "08-Final-Lab-Submission.docx",
)
SHEETS = {
    FILES[0]: ("Hardware Inventory", "Virtual Machines", "Software and Versions", "Setup Checklist", "Resource Allocation"),
    FILES[2]: ("Test Identities", "Groups and Roles", "Access Matrix", "Authentication Policies", "Privileged Access", "Endpoint Baselines", "Revocation Timing", "Access Verification"),
    FILES[4]: ("Log Sources", "Security Events", "Detection Rules", "Alerts and Investigations", "Monitoring Coverage", "Clock Checks", "Retention Sizing", "Observed Results"),
    FILES[5]: ("Test Catalog", "Case Register", "Requirement Coverage", "Recovery Measurements", "Evidence Index", "Engineering Review", "Owner UAT", "Scope Exceptions"),
    FILES[6]: ("Issue Log",),
}
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
STATUSES = "Not Started,In Progress,Pass,Fail,Blocked,Not Applicable"
FORMULAS = {"IF", "COUNT", "SUM", "ISNUMBER", "ABS", "ROUND"}
WORD_SECTIONS = {
    FILES[1]: ("Architecture overview", "Business and security objectives", "Logical architecture diagram", "Network zones", "Physical topology diagram", "Access and segmentation", "Network design decisions", "Design verification", "Limitations and conclusions"),
    FILES[3]: ("Implementation overview", "Observed results limitations and conclusions"),
    FILES[7]: ("Executive summary", "Project objectives", "Architecture summary", "Implementation summary", "Requirements coverage", "Testing results", "Security findings", "Limitations", "Lessons learned", "Final conclusions", "Supporting deliverables", "Publication and repository record", "Rubric assessment"),
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


def template_set_issues(root: Path) -> list[str]:
    directory = root / "docs/deliverables"
    if not directory.exists():
        return ["T5 requires all eight approved Office templates"]
    issues = []
    if {p.name for p in directory.iterdir()} != set(FILES):
        issues.append("docs/deliverables/ must contain exactly the eight approved Office templates")
    try:
        for filename, expected in SHEETS.items():
            parts = package_parts(directory / filename)
            data = workbook_data(parts)
            if tuple(data) != expected:
                issues.append(f"{filename}: incorrect worksheet inventory/order")
            styles = ET.fromstring(parts["xl/styles.xml"])
            if any(n.get("val") != "Segoe UI" for n in styles.findall("s:fonts/s:font/s:name", NS)):
                issues.append(f"{filename}: spreadsheet fonts must use Segoe UI")
            tables = [ET.fromstring(v) for k, v in parts.items() if k.startswith("xl/tables/") and k.endswith(".xml")]
            if len(tables) != len(expected) or len({t.get("name") for t in tables}) != len(tables):
                issues.append(f"{filename}: missing or duplicate named tables")
            if any(t.find("s:autoFilter", NS) is None for t in tables):
                issues.append(f"{filename}: table filters are missing")
            for sheet_name, sheet in data.items():
                tree, cells = sheet["tree"], sheet["cells"]
                if tree.find("s:sheetViews/s:sheetView/s:pane", NS) is None:
                    issues.append(f"{filename}:{sheet_name}: frozen headers missing")
                headers = {a: c["value"] for a, c in cells.items() if re.fullmatch(r"[A-Z]+7", a)}
                for address, label in headers.items():
                    col = address[:-1]
                    column = [c for a, c in cells.items() if re.fullmatch(col + r"(?:[89]|[1-9][0-9]+)", a)]
                    if label == "Status" and any(c["value"] != "Not Started" for c in column):
                        issues.append(f"{filename}:{sheet_name}: shell status records an outcome")
                    if re.search(r"actual|observed|evidence reference|issue reference|executed UTC|ret(e|est)|review date|decision date|explicit confirmation", label, re.I):
                        if any(c["value"] and not c["formula"] for c in column):
                            issues.append(f"{filename}:{sheet_name}: actual/evidence fields must be blank")
                if sheet_name == "Owner UAT" and any(c["value"] != "Pending" for a, c in cells.items() if re.fullmatch(r"D(?:[89]|[1-9][0-9]+)", a)):
                    issues.append(f"{filename}: owner UAT must remain Pending")
                if any(c["value"].startswith(("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#NUM!")) for c in cells.values()):
                    issues.append(f"{filename}:{sheet_name}: cached formula error")
                if any(label == "Status" for label in headers.values()):
                    lists = [n.findtext("s:formula1", default="", namespaces=NS).strip('"') for n in tree.findall("s:dataValidations/s:dataValidation", NS)]
                    if STATUSES not in lists or tree.find("s:conditionalFormatting", NS) is None:
                        issues.append(f"{filename}:{sheet_name}: status dropdown/conditional formatting missing")
            if filename == FILES[5]:
                catalog = data["Test Catalog"]["cells"]
                raw_plan = subprocess.check_output(
                    ["git", "-C", str(ROOT), "show",
                     LEGACY_TEST_PLAN_REF + ":docs/testing/TEST-PLAN.md"],
                    stderr=subprocess.PIPE,
                )
                if hashlib.sha256(raw_plan).hexdigest() != LEGACY_TEST_PLAN_SHA256:
                    raise ValueError("Legacy test-plan integrity mismatch")
                plan = raw_plan.decode("utf-8")
                definitions = re.findall(r"### (T\d{2}) — (.*?)\n(.*?)(?=\n### |\n## Coverage index)", plan, re.S)
                if [tid for tid, _, _ in definitions] != [f"T{i:02}" for i in range(21)]:
                    raise ValueError("Legacy test-plan definitions unavailable")
                ids = [catalog.get(f"A{r}", {}).get("value") for r in range(8, 29)]
                if ids != [f"T{i:02}" for i in range(21)]:
                    issues.append(f"{filename}: T00-T20 definitions missing or reordered")
                for row, (tid, title, body) in enumerate(definitions, 8):
                    expected_result = re.search(r"- Expected: (.*?)\n", body)[1].replace("**", "")
                    second = re.search(r"- Independent observation: (.*?)(?:\n|$)", body)[1].replace("**", "")
                    scope = re.search(r"- (?:Future scope|Scope): (.*?)\n", body)[1]
                    if [catalog.get(f"{c}{row}", {}).get("value") for c in "DEFG"] != [title, scope, expected_result, second]:
                        issues.append(f"{filename}: {tid} differs from the approved test plan")
                coverage = data["Requirement Coverage"]["cells"]
                if [coverage.get(f"A{r}", {}).get("value") for r in range(8, 24)] != [f"R{i:02}" for i in range(1, 17)]:
                    issues.append(f"{filename}: R01-R16 coverage is incomplete")
            if filename == FILES[2]:
                matrix = data["Access Matrix"]["cells"]
                if [matrix.get(f"A{r}", {}).get("value") for r in range(8, 20)] != [f"C{i:02}" for i in range(1, 13)]:
                    issues.append(f"{filename}: twelve T12 cases missing")
            if filename == FILES[4]:
                events = data["Security Events"]["cells"]
                if [events.get(f"A{r}", {}).get("value") for r in range(8, 28)] != [f"E{i:02}" for i in range(1, 21)]:
                    issues.append(f"{filename}: twenty event recording fields missing")
        for filename in (FILES[1], FILES[3], FILES[7]):
            parts = package_parts(directory / filename)
            text = plain_word(parts)
            document = ET.fromstring(parts["word/document.xml"])
            if "Blank template" not in text or "[Enter" not in text or document.find(".//w:pStyle[@w:val='Title']", NS) is None:
                issues.append(f"{filename}: editable template title/answer areas missing")
            if document.find(".//w:headerReference", NS) is None or document.find(".//w:footerReference", NS) is None:
                issues.append(f"{filename}: header/footer missing")
            footer = b"".join(v for k, v in parts.items() if re.fullmatch(r"word/footer\d+\.xml", k))
            if b"PAGE" not in footer or b"NUMPAGES" not in footer:
                issues.append(f"{filename}: page numbering missing")
            if filename == FILES[3] and any(f"Stage {s} " not in text for s in "ABCDEFGHIJKL"):
                issues.append(f"{filename}: stages A-L incomplete")
            if any(section not in text for section in WORD_SECTIONS[filename]):
                issues.append(f"{filename}: required submission sections missing")
    except (OSError, subprocess.CalledProcessError, BadZipFile, ET.ParseError, ValueError, KeyError, IndexError, TypeError):
        issues.append("Office template structure/traceability could not be verified")
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
    print("PASS: eight legacy T5 editable-package shells; 30 worksheets; pinned R01-R16/T00-T20; blank actual/evidence fields; bounded OOXML publication review.")
    print("LIMITS: native opening/editing/recalculation and visual review require separate observations; owner UAT remains PENDING.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
