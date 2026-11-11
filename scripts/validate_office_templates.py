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
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
try:
    from office_template_contract import FILES, SHEETS, STATUSES, OWNER_DECISIONS, ISSUE_STATUSES, WORD_SECTIONS, OFFICE03_TABLES, RUBRIC, office03_test_rows
except ModuleNotFoundError:
    from scripts.office_template_contract import FILES, SHEETS, STATUSES, OWNER_DECISIONS, ISSUE_STATUSES, WORD_SECTIONS, OFFICE03_TABLES, RUBRIC, office03_test_rows
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
FORMULAS = {"IF", "COUNT", "SUM"}
TEST_PLAN = "docs/testing/TEST-PLAN.md"

# Preserve the T9D.1 publication reference for historical regression checks.
# The LF-normalized T9D.4 source supplies the current worksheet definitions.
T9D1_PUBLICATION = "2852dbd8b5e85bf7e306650e6e73013860dfec4c"
T9D4_PLAN_SHA256 = "fdc664297e107b8f90179a4bb5da0e30bea8d91220067466ead9d78ff664e900"

# The prior FWR-02 wording remains part of the historical release checks.
T9B_FWR02 = "Verify the prepared Dell/Proxmox host, physical HP/OPNsense firewall, three workload VMs and three zones; deny unlisted flows, restrict administration, retain console recovery and confirm measured capacity fits."
T9A_FWR02 = "Run one host, four VMs and three zones; deny unlisted flows, restrict administration, retain console recovery and confirm measured capacity fits."
T9A_OFFICE_HASHES = {
    FILES[0]: "33a0a1ac1204c308b89cff131463d7c75f7ef804aeeef4d61073993f790b26c0",
    FILES[1]: "5ff8ce00c7d83d530643cdbb8c32c6f1ccb8b9e9f9fd26f7dbc80c60824d4d54",
    FILES[2]: "1281d20065d0c74e06e8e2490c81b99086f030b94af57fa75e465cda10e866ec",
    FILES[3]: "084423d2c1daa47a23a8fe9bc2afb0cbc02866e6d0fca836050ead604fd368ae",
    FILES[4]: "6e5622322ab962e03b159e31d4d5b1098d89de656fb7151ac09c24b7f53100c6",
}
T9E1_OFFICE01_SHA256 = "2359a415a4e9ab0f7abbf9065171e70f35de93273e82fc0637ba87443302f541"
T9E2_OFFICE02_SHA256 = "06ad5f5d7387c183cec61330539163ef51483ccc4afd50ec4586626392d035b9"
T9E3_OFFICE03_SHA256 = "bef697f6e1aff26af97f2d2ba86e66cbf49b904b48a8e488397f7e3cf1454177"

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
    "C8": "SUM('Virtual Machines'!D8:D10)", "C9": "SUM('Virtual Machines'!E8:E10)",
    "C10": "SUM('Virtual Machines'!F8:F10)",
    "D8": "IF(COUNT('Virtual Machines'!G8:G10)<3,\"\",SUM('Virtual Machines'!G8:G10))",
    "D9": "IF(COUNT('Virtual Machines'!H8:H10)<3,\"\",SUM('Virtual Machines'!H8:H10))",
    "D10": "IF(COUNT('Virtual Machines'!I8:I10)<3,\"\",SUM('Virtual Machines'!I8:I10))",
    "C16": "SUM(C10,C12:C15)", "D16": 'IF(COUNT(D10,D12:D15)<5,"",SUM(D10,D12:D15))',
}
OFFICE01_EVIDENCE = {
    "Hardware & Readiness": ("I", 17),
    "Virtual Machines": ("L", 10),
    "Network Zones": ("H", 10),
    "Allowed Network Flows": ("G", 15),
    "Resource Allocation": ("G", 19),
}

OFFICE02_TABLE_SIZES = ((5, 3), (6, 3), (4, 3), (6, 2), (7, 5), (5, 3))


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


def office02_issues(word_text: str, tables: list[list[list[str]]]) -> list[str]:
    """Check the reviewed recording structure and key control boundaries."""
    issues = []
    directory = [
        ["ava", "Standard analyst; LabReaders"],
        ["eli", "Standard engineer; LabReaders and LabMaintainers"],
        ["uma", "Standard unassigned user, none of the three AD role groups"],
        ["Separate privileged admin", "LabAdmins; approved infrastructure rights only"],
    ]
    app_roles = [
        ["ava", "LabReaders"],
        ["eli", "LabReaders and LabMaintainers"],
        ["uma", "No reader or maintenance role"],
    ]
    if [row[:2] for row in tables[0][1:]] != directory or [row[:2] for row in tables[2][1:]] != app_roles:
        issues.append("approved directory or Apache group memberships changed")

    contexts = ["ava /reports/", "ava /maintenance/", "eli /reports/", "eli /maintenance/", "uma /reports/", "uma /maintenance/"]
    outcomes = ["Allow", "Deny", "Allow", "Allow", "Deny", "Deny"]
    expected_cases = [[f"C{i:02}", context, outcome, f"FWT-03.{i+3:02}"] for i, (context, outcome) in enumerate(zip(contexts, outcomes), 1)]
    if [row[:4] for row in tables[4][1:]] != expected_cases:
        issues.append("six approved application cases/record references changed")
    if tables[4][0][4] != "Evidence ID":
        issues.append("application evidence field missing")

    prompts = {
        "approved three-workload architecture": (
            "bare-metal OPNsense on the HP desktop", "exactly three workload VMs",
            "DC1 and WIN1 share Corporate. APP1 is in Restricted. Management is the third zone.",
        ),
        "stage approval or Office 03 evidence ledger": (
            "stage approval references and dates", "Office 03 > Test Cases and Evidence Index",
            "second observation", "Office 04 > Issue Log",
        ),
        "endpoint enforcement attribution": (
            "Match same-zone traffic to Windows host rules.",
            "known-listening denial to the APP1 rule and log or counter.", "Use HP evidence for routed traffic.",
        ),
        "independent Apache roles": (
            "passwords distinct from AD and manually mapped groups",
            "AD single sign-on and automatic role synchronization are excluded.",
        ),
        "Tailscale access boundary": (
            "APP1 TCP 443-only grant", "one approved existing remote client",
            "subnet routes, exit nodes, Tailscale SSH, Funnel, Serve and sharing are off.",
            "Exclude DC1, WIN1, Proxmox and OPNsense.",
        ),
        "remote denial attribution": (
            "known-listening wrong-port control and denial",
            "Match each denial to effective grants, device state, independent APP1 host rules or Apache roles and logs.",
        ),
        "revocation evidence": (
            "separate AD change and both change times", "grant and exact device authorization removal times",
            "new network requests from existing authenticated and fresh sessions",
            "cache or connection-state handling", "denial and elapsed times against a separate clock",
            "Deny maintenance, allow reports", "Link failures, retests and rollback.",
        ),
    }
    if any(
        f"{series}-{number:02}" not in word_text
        for number in range(3, 7)
        for series in ("FWR", "FSC", "FWT", "FAC")
    ):
        issues.append("required FWR/FSC/FWT/FAC-03 through -06 references missing")
    for label, required in prompts.items():
        if any(fragment not in word_text for fragment in required):
            issues.append(f"{label} changed or missing")
    if word_text.count("[Enter your response.]") != 6 or len(re.findall(
        r"\[Insert a sanitized [^\n]+ screenshot and an evidence ID\.\]", word_text
    )) != 4:
        issues.append("answer or screenshot/evidence prompts missing")

    return issues


def office03_record_issues(data: dict[str, dict], tables: list[ET.Element]) -> list[str]:
    """Check the released recording tables, scope prompts and required blank fields."""
    issues = []
    by_name = {table.get("name"): table for table in tables}
    for index, (name, (reference, headers)) in enumerate(OFFICE03_TABLES.items(), 1):
        cells = data[name]["cells"]
        last_col, last_row = re.fullmatch(r"A7:([A-Z])(\d+)", reference).groups()
        columns = [chr(col) for col in range(ord("A"), ord(last_col) + 1)]
        table = by_name.get(f"Lab03Table{index}")
        if table is None or table.get("ref") != reference or table.find("s:autoFilter", NS) is None:
            issues.append(f"{name}: approved named table, range or filter changed")
        elif (table.find("s:autoFilter", NS).get("ref") != reference
              or tuple(c.get("name") for c in table.findall("s:tableColumns/s:tableColumn", NS)) != headers):
            issues.append(f"{name}: table filter range or recording headers changed")
        if tuple(cells.get(f"{col}7", {}).get("value") for col in columns) != headers:
            issues.append(f"{name}: required recording headers changed")
        if any(f"{col}{row}" not in cells for col in columns for row in range(8, int(last_row) + 1)):
            issues.append(f"{name}: required actual/evidence or other recording field missing")

    events = data["Security Events"]["cells"]
    categories = (
        "Directory logon success", "One directory logon failure", "Application allow",
        "Authenticated application denial", "Firewall denial",
    )
    if [(events.get(f"A{row}", {}).get("value"), events.get(f"B{row}", {}).get("value"))
        for row in range(8, 13)] != [(f"E{i:02}", category) for i, category in enumerate(categories, 1)]:
        issues.append("Security Events: five approved event categories missing")

    for name, prefix, count in (
        ("Denied Access Investigation", "I", 7), ("Automation Verification", "A", 7),
        ("Backup & Restore", "B", 10), ("Owner Acceptance", "U", 5),
    ):
        cells = data[name]["cells"]
        if [cells.get(f"A{row}", {}).get("value") for row in range(8, 8 + count)] != [
            f"{prefix}{i:02}" for i in range(1, count + 1)
        ]:
            issues.append(f"{name}: approved check fields missing or out of order")

    prompts = {
        "Security Events": {
            "A3": ("source and observer UTC", "second observation", "private custody"),
            "C8": ("DC1 Security", "Kerberos event"),
            "C9": ("DC1 Security", "lockout margin", "one safe wrong-password attempt"),
            "C10": ("APP1 Apache", "allowed authenticated application request"),
            "C11": ("APP1 Apache", "valid application credentials", "denied request"),
            "C12": ("Physical HP OPNsense", "effective rule", "log or counter"),
        },
        "Denied Access Investigation": {
            "A3": ("one approved denied lab-owned action", "working positive control", "event-time policy"),
            "B8": ("source, destination and service",),
            "B12": ("source log, state or counter",),
            "B13": ("second observation", "State limits"),
        },
        "Test Cases": {
            "A3": ("every mandatory child passes with verified evidence", "FAIL if any child fails",
                   "NOT TESTED otherwise", "NOT APPLICABLE cannot waive a mandatory check"),
        },
        "Automation Verification": {
            "A3": ("one local WIN1 disk-capacity summary", "approved standard user", "No unapproved elevation or writes"),
            "B9": ("WIN1/ad.lab.test target", "protected private output path"),
            "B10": ("First-run result", "independent OS/storage comparison"),
            "B11": ("Second successful run", "side effects"),
            "B12": ("invalid-target rejection",),
            "B13": ("invalid-path rejection",),
            "B14": ("before and after both runs and rejections",),
        },
        "Backup & Restore": {
            "A3": ("BLOCKED", "encrypted external-storage backend and unlock/recovery",
                   "exact isolated physical HP path", "disconnection, reconnection and rollback"),
            "B8": ("One approved full APP1 backup",),
            "B9": ("off-compute custody", "separate recovery-key access", "sole archive"),
            "B11": ("original APP1 off before backup and throughout", "unused temporary VM ID",
                    "all restored NICs disconnected and autostart off"),
            "B12": ("Tailscale stopped and disabled",),
            "B13": ("verified integrity and usable HTTPS", "independent clock"),
            "B14": ("authentic independently retained manifest", "approved execution-stage shell"),
            "B15": ("exact approved isolated WIN1-to-copy path through physical HP OPNsense", "both approvals",
                    "disconnect/reconnect and rollback checklist", "upstream and nonparticipants disconnected",
                    "narrow temporary settings", "matching HP and APP1 evidence"),
            "B16": ("reports allowed and maintenance denied", "trusted HTTPS"),
            "B17": ("Disconnect and stop the copy before rollback", "original APP1 final state"),
        },
        "Evidence Index": {
            "A3": ("exact requirement/test/check", "source system, operator, date/time",
                   "second observation and issue/retest", "private original custody", "reviewed sanitized reference"),
        },
        "Owner Acceptance": {
            "A3": ("91 mandatory results and their evidence", "critical safety failures",
                   "100-point rubric (25 / 25 / 20 / 20 / 10)", "user acceptance testing (UAT) separately",
                   "explicit confirmation reference", "Start PENDING"),
        },
    }
    for name, required in prompts.items():
        cells = data[name]["cells"]
        for address, phrases in required.items():
            if any(phrase not in cells.get(address, {}).get("value", "") for phrase in phrases):
                issues.append(f"{name}: {address} approved control or evidence prompt changed")

    return issues


def template_set_issues(root: Path) -> list[str]:
    directory = root / "docs/deliverables"
    if not directory.is_dir():
        return ["T7 requires all five approved Office templates"]
    issues = []
    if {p.name for p in directory.iterdir()} != set(FILES):
        issues.append("docs/deliverables/ must contain exactly the five approved Office templates")
    try:
        released_hashes = T9A_OFFICE_HASHES | {
            FILES[0]: T9E1_OFFICE01_SHA256, FILES[1]: T9E2_OFFICE02_SHA256, FILES[2]: T9E3_OFFICE03_SHA256,
        }
        for filename, expected in released_hashes.items():
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != expected:
                issues.append(f"{filename}: package differs from the approved release")
        plan = (root / TEST_PLAN).read_text(encoding="utf-8")
        if hashlib.sha256(plan.encode("utf-8")).hexdigest() != T9D4_PLAN_SHA256:
            issues.append("Test Cases: approved test plan source differs from the audited T9D.4 publication")
        expected_rows = office03_test_rows(plan)
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
            if filename == FILES[2]:
                issues.extend(office03_record_issues(data, tables))
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
            expected = [rid, required_result.strip(), rid.replace("FWR", "FSC"), rid.replace("FWR", "FWT"), rid.replace("FWR", "FAC"), owner]
            if [coverage.get(f"{col}{rn}", {}).get("value") for col in "ABCDEF"] != expected:
                issues.append(f"Requirements Coverage: {rid} traceability differs from approved assignment")
        office01 = all_workbooks[FILES[0]]
        resource = office01["Resource Allocation"]["cells"]
        if {a: c["formula"] for a, c in resource.items() if c["formula"]} != RESOURCE_FORMULAS:
            issues.append("Resource Allocation: approved simple totals/input guards changed")
        if [resource.get(a, {}).get("value") for a in ("C8", "C9", "C10", "C16")] != ["6", "16", "160", "320"]:
            issues.append("Resource Allocation: planned guest totals or Dell ledger differ from the approved budget")
        if any(resource.get(a, {}).get("value") for a in ("D8", "D9", "D10", "D16")):
            issues.append("Resource Allocation: cached actual totals must be blank")
        for name, expected in (("Virtual Machines", ["DC1", "WIN1", "APP1"]), ("Network Zones", ["Management", "Corporate", "Restricted"])):
            cells = office01[name]["cells"]
            values = [c["value"] for a, c in cells.items() if re.fullmatch(r"A(?:[89]|[1-9][0-9]+)", a)]
            if values != expected:
                issues.append(f"{name}: approved inventory or zone order changed")
        vm_cells = office01["Virtual Machines"]["cells"]
        allocations = (["Corporate", "2", "6", "64"], ["Corporate", "2", "6", "64"], ["Restricted", "2", "4", "32"])
        for row, expected in enumerate(allocations, 8):
            if [vm_cells.get(f"{col}{row}", {}).get("value") for col in "CDEF"] != expected:
                issues.append(f"Virtual Machines: approved zone or allocation changed at row {row}")
        for name, (col, last_row) in OFFICE01_EVIDENCE.items():
            cells = office01[name]["cells"]
            if (cells.get(f"{col}7", {}).get("value") != "Evidence reference"
                    or any(f"{col}{row}" not in cells for row in range(8, last_row + 1))):
                issues.append(f"{name}: required evidence field missing")
        flows = office01["Allowed Network Flows"]["cells"]
        architecture = (root / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        approved_flows = re.findall(r"^\| (FF-\d{2}) \| ([^|]+) \| ([^|]+) \|$", architecture, re.M)
        if len(approved_flows) != 8:
            raise ValueError("Missing approved flows")
        for rn, expected in enumerate(approved_flows, 8):
            if [flows.get(f"{c}{rn}", {}).get("value") for c in "ABC"] != [v.strip() for v in expected]:
                issues.append("Allowed Network Flows: approved permission/enforcement changed")
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
            if filename == FILES[1]:
                if len(tables) != len(OFFICE02_TABLE_SIZES) or any(
                    len(table) != rows or any(len(row) != columns for row in table)
                    for table, (rows, columns) in zip(tables, OFFICE02_TABLE_SIZES)
                ):
                    issues.append(f"{filename}: required tables or evidence cells missing")
                    continue
                issues.extend(f"{filename}: {finding}" for finding in office02_issues(word_text, tables))
                blank_columns = {0: (2,), 1: (1, 2), 2: (2,), 3: (1,), 4: (4,)}
            else:
                blank_columns = {0: (1,), 1: (1,), 2: (1,), 3: (2, 3)}
            for index, columns in blank_columns.items():
                if any(record[c] for record in tables[index][1:] for c in columns):
                    issues.append(f"{filename}: actual/score/evidence answer cells must be blank")
            if filename == FILES[4] and tables[3] != [["Assessment area", "Maximum", "Score", "Evidence / evaluator note"]] + [[title, str(score), "", ""] for title, score in RUBRIC] + [["TOTAL", "100", "", ""]]:
                issues.append(f"{filename}: approved 100-point rubric/blank scores changed")
            if re.search(r"\b(?:R[0-9]{2}|T[0-9]{2}|S[0-9]{2})\b|six (?:security )?zones|two-tier|twenty.event|twelve application|two automation", word_text, re.I):
                issues.append(f"{filename}: obsolete enterprise target or ID")
    except (OSError, BadZipFile, ET.ParseError, ValueError, KeyError, IndexError, TypeError):
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
    print("LIMITS: native opening/editing/recalculation and visual review require separate observations; owner UAT remains PENDING.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
