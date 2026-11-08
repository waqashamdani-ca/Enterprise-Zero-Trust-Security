#!/usr/bin/env python3
"""Offline documentation and focused public-publication checks; Python 3.11+.

This tool inspects files only. It never installs dependencies, connects to the
lab, fetches external links, or prints a suspected credential value. It is not
a complete secret detector; a manual staged-content/history review is required.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from validate_office_templates import package_issues, template_set_issues
except ModuleNotFoundError:  # Importlib-based focused tests run from repo root.
    from scripts.validate_office_templates import package_issues, template_set_issues


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", "AGENTS.md", ".gitignore", ".gitattributes",
    ".github/workflows/documentation.yml",
    "docs/assignments/PROJECT-ASSIGNMENT.md", "docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md",
    "docs/lab-guides/reference/01-Prepared-Infrastructure.md",
    "docs/lab-guides/reference/02-Windows-Directory-and-Policy.md",
    "docs/lab-guides/reference/03-Linux-Network-and-Host-Policy.md",
    "docs/lab-guides/reference/04-HTTPS-and-Application-Roles.md",
    "docs/lab-guides/reference/05-Tailscale-Policy.md",
    "docs/lab-guides/reference/06-Logs-Automation-and-Test-Tools.md",
    "docs/lab-guides/reference/07-Backup-and-Recovery.md",
    "docs/architecture/ARCHITECTURE.md", "docs/security/SECURITY-REQUIREMENTS.md",
    "docs/testing/TEST-PLAN.md", "docs/testing/ACCEPTANCE-CRITERIA.md",
    "docs/governance/DECISIONS.md", "docs/governance/RISKS.md", "docs/final-report/FINAL-REPORT.md",
    "docs/governance/REFERENCES.md", "infrastructure/README.md",
    "configurations/README.md", "scripts/validate_docs.py",
    "tests/test_validate_docs.py", "evidence/README.md",
    "docs/reports/README.md", "docs/reports/INDEX.md", "docs/reports/T1-Report.md",
    "docs/README.md", "docs/guides/GLOSSARY.md", "docs/governance/DOCUMENTATION-BUILD.md",
    "scripts/build_docs.py", "tests/test_build_docs.py", "requirements-docs.txt",
    "docs/documentation-manifest.json",
)
REQUIRED_DIRS = (
    ".github/workflows", "docs", "infrastructure", "configurations",
    "scripts", "tests", "evidence", "docs/reports",
    "docs/assignments", "docs/lab-guides", "docs/architecture", "docs/security",
    "docs/testing", "docs/governance", "docs/final-report", "docs/guides",
)
GUIDE_TRANSITION = "docs/governance/HISTORICAL-REQUIREMENT-TRANSITION.md"
PREPARED_REFERENCE = "docs/lab-guides/reference/01-Prepared-Infrastructure.md"
WINDOWS_REFERENCE = "docs/lab-guides/reference/02-Windows-Directory-and-Policy.md"
LINUX_REFERENCE = "docs/lab-guides/reference/03-Linux-Network-and-Host-Policy.md"
HTTPS_REFERENCE = "docs/lab-guides/reference/04-HTTPS-and-Application-Roles.md"
TAILSCALE_REFERENCE = "docs/lab-guides/reference/05-Tailscale-Policy.md"
MONITORING_REFERENCE = "docs/lab-guides/reference/06-Logs-Automation-and-Test-Tools.md"
RECOVERY_REFERENCE = "docs/lab-guides/reference/07-Backup-and-Recovery.md"
PHASE_TITLES = (
    "Prepared Infrastructure", "Identity and Endpoint Security", "Zero Trust Access Controls",
    "Monitoring, Automation and Recovery", "Validation and Final Submission",
)
RUBRIC_WEIGHTS = (
    ("Infrastructure and Network Security", 25), ("Identity and Access Controls", 25),
    ("Security Monitoring and Operations", 20), ("Testing and Recovery", 20),
    ("Documentation and Final Submission", 10),
)
ORDERED_HARDWARE = (
    "Xeon W-2145", "Samsung 1 TB SSD", "Sabrent PCIe adapter",
    "Intel I350-T4 NIC", "GL.iNet Beryl AX", "TP-Link managed switch",
)
PDF_MANIFEST = "docs/documentation-manifest.json"
PDF_ALIASES = {
    "docs/DECISIONS.md", "docs/RISKS.md", "docs/docs/DECISIONS.md", "docs/docs/RISKS.md",
    "docs/docs/README.md", "docs/docs/final-report/FINAL-REPORT.md",
    "docs/evidence/BOOTSTRAP-VALIDATION.md", "docs/docs/documentation-manifest.json",
}
REPORT_PREFIXES = ("docs/reports/", "reports/")
# Optional, byte-frozen archives already published at the T3 baseline. These
# exceptions never admit new report PDFs or require a current Markdown pairing.
REPORT_ARCHIVE_BASELINE = "d1b575761c090c35dac535ec331a1e32f9bd5fe6"
ARCHIVED_REPORT_PDFS = {
    "docs/reports/README.pdf": "8dac0d69a194a43a550f086e409cb763245bbd583d9e1e1fe94db6bb933d6567",
    "docs/reports/T1-Addendum-001-Reporting-Governance.pdf": "e684fa1f73c0cf8aa9029dc0ae13c2fbab3bb1c26a77ae5a00925d5d5f3bde56",
    "docs/reports/T1-Report.pdf": "c42f42e0b548c0996a66f6431da09fcf85995dd5e0841b9358e58f01fb206dd9",
    "docs/reports/T2-Report.pdf": "36ec642bee80564ac9e50bb5c24900211f70908d5a2fb29d6c51f26d2d6e5856",
    "docs/reports/T3-Report.pdf": "4ab8ce03f2009e8cfbfe44c4b9803780043f3b7203b7373cb0f1aa64e3a8ab5d",
}
# Owner-authorized T4 relocation is a path-only exception, never a content waiver.
REPORT_MIGRATION_BASELINE = "0d28d105a517606e7a0a1cdaf4939f166b2f3a53"
MIGRATED_REPORT_FILES = {
    **ARCHIVED_REPORT_PDFS,
    "docs/reports/README.md": "b1db4ef489bd607171966fc5dc1f81778374b95cd3a3946018f09220add2e7ed",
    "docs/reports/T1-Addendum-001-Reporting-Governance.md": "792d74c5dd486cb1ceea0a639d46d585f6b3576402476624125cfd3239c0689e",
    "docs/reports/T1-Report.md": "428c869a9c4c3d2d5b7e03881b719a264690e515256214514b25fe2c46a4fca6",
    "docs/reports/T2-Report.md": "6ffbf30e74f5456c7b2b4f78555722a98dfabac97475367fd16adbe84e8c9dab",
    "docs/reports/T3-Addendum-001-Markdown-Only-Reporting.md": "502cee8541f417263e008a9205e71c7cab27fcca05e1ad9d8067e140a2289ea8",
    "docs/reports/T3-Report.md": "e5542bbdef113b8debc45150dc33b78586105c7492227ea4e3c8033e1135f761",
}
REPORT_SECTIONS = (
    "A. Task Information", "B. Implementation Summary",
    "C. Testing and Validation", "D. Security and Quality Review",
    "E. GitHub Operations", "F. Outstanding Issues",
    "G. Completion Status", "H. Next Task",
)
REPORT_NAME = re.compile(r"docs/reports/T([1-9][0-9]*)-Report\.md")
# Explicit owner-authorized companions; no T7 allocation or other lettered tasks.
COMPANION_REPORTS = {"docs/reports/T6A-Report.md": ("T6A", 6),
                     "docs/reports/T6B-Report.md": ("T6B", 6)}
# Explicit owner-approved interim publication; no general draft-report waiver.
T9_UMBRELLA_REPORT = "docs/reports/T9-Report.md"
ADDENDUM_NAME = re.compile(r"docs/reports/T([1-9][0-9]*)-Addendum-([0-9]{3})-[A-Za-z0-9-]+\.md")
ASSIGNMENT_HEADINGS = (
    "Project Overview", "Learning Objectives", "Lab Environment", "Project Activities",
    "Required Deliverables", "Evaluation Rubric", "Completion Criteria",
)
ASSIGNMENT_COMPATIBILITY_ANCHORS = {
    "project-objectives", "project-scope", "technologies-and-resources",
    "expected-deliverables", "implementation-approach", "success-criteria",
    "what-you-will-build", "project-requirements", "four-week-implementation-plan",
    "evaluation-criteria", "references",
}
DELIVERABLE_FILENAMES = (
    "01-Lab-Environment-and-Architecture.xlsx",
    "02-Identity-and-Zero-Trust-Implementation.docx",
    "03-Security-Monitoring-and-Testing.xlsx",
    "04-Troubleshooting-and-Lessons.xlsx",
    "05-Final-Project-Submission.docx",
)
ALLOWED_EXTENSIONS = {".md", ".py", ".yml", ".yaml"}
ALLOWED_SPECIAL_NAMES = {".gitignore", ".gitattributes"}
PRIVATE_PARTS = {
    ".private", "private", "local", "secrets", "credentials", "inventories",
    "raw", "unsanitized", ".aws", ".azure", ".ssh", ".kube", ".terraform",
}
PRIVATE_NAME = re.compile(
    r"(^\.env($|\.)|^id_(rsa|ed25519)|\.(private|local)\.|"
    r"(^|[-_.])(credentials?|secrets?|tokens?|passwords?|inventor(y|ies)|backups?)($|[-_.]))",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    ("private-key material", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("cloud access identifier", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Tailscale key", re.compile(r"\btskey-(?:auth|api)-[A-Za-z0-9_-]{20,}\b")),
    ("chat service token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("authorization credential", re.compile(r"\b(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]{24,}", re.I)),
    ("credential in URL", re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.I)),
    ("assigned secret", re.compile(
        r"\b(?:password|passwd|pwd|client_secret|access_token|refresh_token|api_key)"
        r"[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_+/=.-]{12,}[\"']", re.I,
    )),
)
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6 = re.compile(r"(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}(?:%[\w.-]+)?(?![\w:])")
DOCUMENTATION_NETWORKS = tuple(map(ipaddress.ip_network, (
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32",
)))
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)]+)(?:\s+[\"'][^\"']*[\"'])?\)")
REFERENCE = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", re.M)
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+\s*)?$", re.M)


def candidate_paths(root: Path) -> list[str]:
    """Include ignored files if tracked; also inspect proposed nonignored files."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others",
         "--exclude-standard", "-z"],
        capture_output=True, check=True,
    )
    return sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})


def strip_fences(content: str) -> tuple[str, bool]:
    output: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in content.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if not fence_char and marker:
            fence_char, fence_length = marker[1][0], len(marker[1])
            output.append("")
        elif fence_char:
            if (marker and marker[1][0] == fence_char
                    and len(marker[1]) >= fence_length and not marker[2].strip()):
                fence_char = ""
            output.append("")
        else:
            output.append(line)
    return "\n".join(output), not fence_char


def heading_anchors(content: str) -> set[str]:
    visible, _ = strip_fences(content)
    used: set[str] = set()
    for match in HEADING.finditer(visible):
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match[2])
        title = re.sub(r"<[^>]+>", "", title).lower().replace("`", "")
        base = re.sub(r"[^\w -]", "", title).replace(" ", "-")
        anchor, suffix = base, 0
        while anchor in used:
            suffix += 1
            anchor = f"{base}-{suffix}"
        used.add(anchor)
    used.update(re.findall(r'^<a id="([a-z][a-z0-9-]*)"></a>\s*$', visible, re.M))
    return used


def retired_t5_link(root: Path, relative: str, content: str, destination: Path) -> bool:
    """Verify retired targets only for the byte-frozen T5 report snapshot.

    Open that report at this revision for working GitHub relative navigation.
    Current source links must resolve normally; this is not a missing-link waiver.
    """
    if relative != "docs/reports/T5-Report.md" or hashlib.sha256(content.encode("utf-8")).hexdigest() != "3c686c0c308e42eea3524a1077d389925cf18439a5a742e578f0c50b8aceb78d":
        return False
    old_names = {
        "01-Lab-Environment.xlsx", "02-Architecture-and-Network-Design.docx",
        "03-Identity-and-Access-Management.xlsx", "04-Zero-Trust-Implementation.docx",
        "05-Security-Monitoring.xlsx", "06-Testing-and-Validation.xlsx",
        "07-Troubleshooting-and-Lessons.xlsx", "08-Final-Lab-Submission.docx",
    }
    name = destination.relative_to(root.resolve()).as_posix()
    if name not in {"docs/deliverables/" + n for n in old_names}:
        return False
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e",
             "6f5352bb6d5e2eca37ac2384703367543530b952:" + name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        return result.returncode == 0
    except OSError:
        return False


def link_issues(root: Path, relative: str, content: str) -> list[str]:
    visible, balanced = strip_fences(content)
    issues = [] if balanced else [f"{relative}: unclosed Markdown code fence"]
    targets = [match[1] for match in LINK.finditer(visible)]
    targets.extend(match[1] for match in REFERENCE.finditer(visible))
    for raw in targets:
        target = raw.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme:
            if parsed.scheme != "https":
                issues.append(f"{relative}: unsupported link scheme")
            elif not parsed.netloc:
                issues.append(f"{relative}: malformed HTTPS link")
            continue  # External references are intentionally not fetched by CI.
        if parsed.netloc or parsed.query or "\\" in target:
            issues.append(f"{relative}: invalid local link: {target}")
            continue
        decoded = unquote(parsed.path)
        path = ((root / relative).parent / decoded).resolve() if decoded else (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            issues.append(f"{relative}: local link escapes repository")
            continue
        if not path.is_file():
            if not parsed.fragment and retired_t5_link(root, relative, content, path):
                continue
            issues.append(f"{relative}: missing local link destination: {target}")
            continue
        if parsed.fragment and path.suffix.lower() == ".md":
            if unquote(parsed.fragment) not in heading_anchors(path.read_text(encoding="utf-8-sig")):
                issues.append(f"{relative}: missing heading anchor: {target}")
    # Check column counts within each ordinary pipe-delimited Markdown table.
    columns = None
    for number, line in enumerate(visible.splitlines(), 1):
        if line.startswith("|") and line.endswith("|"):
            count = len(re.split(r"(?<!\\)\|", line)) - 2
            if columns is not None and count != columns:
                issues.append(f"{relative}:{number}: inconsistent table columns")
            columns = count if columns is None else columns
        else:
            columns = None
    return issues


def public_content_issues(relative: str, content: str) -> list[str]:
    issues = []
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            issues.append(f"{relative}:{line}: possible {label}; value omitted")
    for pattern in (IPV4, IPV6):
        for match in pattern.finditer(content):
            try:
                address = ipaddress.ip_address(match[0].split("%", 1)[0])
            except ValueError:
                continue
            if not any(address.version == net.version and address in net for net in DOCUMENTATION_NETWORKS):
                line = content.count("\n", 0, match.start()) + 1
                issues.append(f"{relative}:{line}: non-documentation IP literal; value omitted")
    for match in EMAIL.finditer(content):
        domain = match[0].rsplit("@", 1)[1].lower()
        safe = domain in {"example.com", "example.net", "example.org", "users.noreply.github.com"}
        safe = safe or domain.endswith((".test", ".example", ".invalid"))
        if not safe:
            line = content.count("\n", 0, match.start()) + 1
            issues.append(f"{relative}:{line}: non-synthetic email; value omitted")
    return issues


def file_issues(root: Path, relative: str) -> tuple[list[str], str | None]:
    path = root / relative
    issues: list[str] = []
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        return [f"{relative}: symlink or path outside repository is not publishable"], None
    if not path.is_file():
        return [f"{relative}: missing/nonregular candidate file"], None
    if any(part.lower() in PRIVATE_PARTS for part in path.relative_to(root).parts):
        issues.append(f"{relative}: private directory in publication set")
    # These two exact owner-requested paths are technical documentation. They
    # still receive ordinary content scans and source/manifest/PDF validation;
    # no archive, neighboring filename or raw recovery artifact is admitted.
    recovery_documents = {RECOVERY_REFERENCE, RECOVERY_REFERENCE[:-3] + ".pdf"}
    if PRIVATE_NAME.search(path.name) and relative not in recovery_documents:
        issues.append(f"{relative}: sensitive filename in publication set")
    if path.suffix.lower() == ".pdf":
        return issues + generated_pdf_issues(root, relative), None
    if path.suffix.lower() in {".docx", ".xlsx"}:
        return issues + package_issues(root, relative, public_content_issues), None
    if (path.suffix.lower() not in ALLOWED_EXTENSIONS and path.name not in ALLOWED_SPECIAL_NAMES
            and relative not in {PDF_MANIFEST, "requirements-docs.txt", "docs/docs/documentation-manifest.json"}):
        issues.append(f"{relative}: unreviewed file type; extend policy only after artifact review")
    if path.stat().st_size > 1024 * 1024:
        return issues + [f"{relative}: exceeds 1 MiB public-text limit"], None
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (UnicodeError, OSError):
        return issues + [f"{relative}: cannot read as UTF-8 text"], None
    if "\0" in content:
        return issues + [f"{relative}: binary/NUL content is not publishable"], None
    return issues + public_content_issues(relative, content), content


def generated_pdf_issues(root: Path, relative: str) -> list[str]:
    """Require source-matched generated PDFs or an exact historical archive."""
    try:
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            return [f"{relative}: unsafe PDF path"]
        if relative.lower().startswith(REPORT_PREFIXES):
            expected = ARCHIVED_REPORT_PDFS.get(relative)
            if expected is None:
                return [f"{relative}: new report PDFs are prohibited; task reports must be Markdown only"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                return [f"{relative}: archived report PDF differs from frozen T3 artifact"]
            return []
        manifest = json.loads((root / PDF_MANIFEST).read_text(encoding="utf-8"))
        entries = [entry for entry in manifest["documents"] if entry["pdf"] == relative]
        if len(entries) != 1:
            return [f"{relative}: PDF not uniquely approved in generated manifest"]
        entry = entries[0]
        if entry["source"] != relative[:-4] + ".md":
            return [f"{relative}: invalid PDF/source pairing"]
        source = root / entry["source"]
        if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
            return [f"{relative}: unsafe PDF source"]
        data = path.read_bytes()
        if not data.startswith(b"%PDF-") or len(data) > 20 * 1024 * 1024:
            return [f"{relative}: invalid/oversized generated PDF"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["source_sha256"]:
            return [f"{relative}: generated PDF is stale relative to Markdown"]
        if hashlib.sha256(data).hexdigest() != entry["pdf_sha256"]:
            return [f"{relative}: PDF bytes differ from reviewed generated manifest"]
        return []
    except (OSError, KeyError, ValueError, TypeError):
        return [f"{relative}: PDF manifest/source cannot be verified"]


def pdf_inventory_issues(paths: list[str], texts: dict[str, str]) -> list[str]:
    try:
        manifest = json.loads(texts.get(PDF_MANIFEST, ""))
        entries = manifest["documents"]
        sources = [entry["source"] for entry in entries]
        expected = {name for name in texts if name.endswith(".md") and name not in PDF_ALIASES
                    and not name.lower().startswith(REPORT_PREFIXES)}
        if manifest.get("schema") != 1 or set(sources) != expected or len(sources) != len(expected):
            return ["generated PDF manifest must cover each maintained document outside docs/reports/ exactly once"]
        if any(entry["pdf"].lower().startswith(REPORT_PREFIXES) for entry in entries):
            return ["docs/reports/ must not appear in the generated PDF inventory"]
        if any(entry["pdf"] not in paths for entry in entries):
            return ["required generated PDF missing from publication set"]
        return []
    except (KeyError, ValueError, TypeError):
        return ["generated PDF inventory/manifest is missing or invalid"]


def structure_issues(root: Path, paths: list[str]) -> list[str]:
    issues = []
    for relative in REQUIRED_FILES:
        if relative not in paths or not (root / relative).is_file():
            issues.append(f"required file missing from publication set: {relative}")
    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            issues.append(f"required directory missing: {relative}")
    if (root / "reports").exists() or any(name.startswith("reports/") for name in paths):
        issues.append("legacy reports/ must be absent after migration; duplicate report locations are prohibited")
    return issues


def prepared_infrastructure_issues(guide: str, reference: str) -> list[str]:
    """Inspect the accepted compact procedures and their retained security detail."""
    issues = []
    intro, _, body = guide.partition("## Phase 1: Prepared Infrastructure\n")
    phase = body.partition("## Phase 2: Identity and Endpoint Security")[0]
    visible = re.sub(r'<a id="[a-z][a-z0-9-]*"></a>', '', intro + phase)
    if len(intro.split()) > 210 or len(phase.split()) > 850:
        issues.append("guide: introduction/Phase 1 exceed the compact writing budget")
    expected = ["A. Verify the lab equipment and VM resources", "B. Verify network zones and management access",
                "C. Verify isolation and required network access"]
    procedures = re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", phase, re.M | re.S)
    if [title for title, _ in procedures] != expected:
        issues.append("guide Phase 1: preserve exactly three prepared-infrastructure procedures")
    for title, section in procedures:
        if re.findall(r"^\*\*(WHERE|STEPS|CHECK|RECORD)\*\*$", section, re.M) != ["WHERE", "STEPS", "CHECK", "RECORD"]:
            issues.append(f"guide Phase 1 {title}: missing ordered sample labels")
        actions = [int(n) for n in re.findall(r"^(\d+)\. ", section, re.M)]
        if not 3 <= len(actions) <= 7 or actions != list(range(1, len(actions) + 1)):
            issues.append(f"guide Phase 1 {title}: require 3-7 sequential actions")
        if "Deliverable 01 >" not in section:
            issues.append(f"guide Phase 1 {title}: missing recording destination")
    for meaning in ("Dell Precision 5820", "HP desktop with physical OPNsense", "TP-Link TL-SG108E",
                    "GL.iNet Beryl AX", "Exactly three workload VMs", "DC1", "WIN1", "APP1",
                    "Management", "Corporate", "Restricted", "6 vCPU / 16 GiB RAM / 160 GiB",
                    "read-only stage A approval", "B (host), C (network) or D (firewall) approval",
                    "private network map", "backup/recovery", "original Windows disk", "second observations",
                    "FWR-01/FWR-02", "FWT-01/FWT-02", "Before Phase 2", "NOT TESTED",
                    "GUI inspection alone does not prove", "Never probe home or production"):
        if meaning not in phase:
            issues.append("guide Phase 1: missing prepared-design, approval, safety or evidence safeguard: " + meaning)
    for anchor in ("physical-map-and-proxmox-bridges", "management-access", "default-deny-and-allowed-flows",
                   "isolation-and-routing", "approved-active-checks", "console-recovery-and-rollback"):
        if "reference/01-Prepared-Infrastructure.md#" + anchor not in phase:
            issues.append("guide Phase 1: missing technical-reference navigation: " + anchor)
    if re.search(r"\b(?:virtual OPNsense|virtual firewall|four (?:baseline )?VMs|Install Proxmox|Install OPNsense|"
                 r"Ordered|Delivered|procurement|PLANNED|T9[A-F]?(?:\.[1-7])?)\b", visible, re.I):
        issues.append("guide introduction/Phase 1: obsolete installation, status or internal task language")
    if re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\bVLAN\s+\d+|\bvmbr\d+|^```", visible, re.M):
        issues.append("guide Phase 1: invented private mapping or executable block")
    if not reference:
        return issues + ["guide Phase 1: prepared technical reference is required"]
    if re.findall(r"^\| (FF-\d{2}) \|", reference, re.M) != [f"FF-{n:02d}" for n in range(1, 9)]:
        issues.append("prepared reference: preserve all eight FF restrictions in order")
    for meaning in ("stage A approval", "separate B, C and D approval", "PVID", "tagged/untagged",
                    "Workload bridges carry no Proxmox host IP", "sole inter-zone router", "one zone NIC",
                    "same-zone", "local_network", "management` IPSet", "anti-lockout", "floating/group/automatic",
                    "existing states", "NAT", "firewall-originated", "IPv4 and IPv6", "router advertisements",
                    "DHCPv6", "automatic/default routes", "independently isolated", "lab-owned mock",
                    "Never send test traffic to home or production", "second observation", "working allowed control",
                    "wrong password or stopped listener is insufficient", "System > Configuration > Backups",
                    "restore", "console", "original Windows disk", "supported second factor", "LabEditPath"):
        if meaning not in reference:
            issues.append("prepared reference: missing mandatory technical safeguard: " + meaning)
    for meaning in ("hardware revision", "selected software builds", "private mapping", "01 >", "03 >", "04 >",
                    "12 GiB host RAM", "80 GiB free storage", "320 GiB", "NOT TESTED", "owner UAT"):
        if meaning not in reference:
            issues.append("prepared reference: missing version, capacity or evidence detail: " + meaning)
    for match in re.finditer(r"^```[^\n]*\n.*?^```", reference, re.M | re.S):
        context = reference[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
        if not re.search(r"READ-ONLY|CONFIGURATION CHANGE|DESTRUCTIVE / HIGH-RISK", context):
            issues.append("prepared reference: command block needs a risk/target context")
    return issues


def identity_endpoint_issues(guide: str, windows: str, linux: str) -> list[str]:
    """Check Phase 2's actionable controls without executing any proposed command."""
    issues = []
    phase = guide.partition("## Phase 2: Identity and Endpoint Security\n")[2].partition("## Phase 3:")[0]
    expected = ["A. Verify or create the three workload VMs", "B. Configure DC1 and Active Directory",
                "C. Create lab users and groups, then join WIN1", "D. Apply Windows security policies",
                "E. Configure APP1 networking and host protection"]
    procedures = re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", phase, re.M | re.S)
    if [title for title, _ in procedures] != expected:
        issues.append("guide Phase 2: require exactly five identity/endpoint procedures")
    for title, section in procedures:
        if re.findall(r"^\*\*(WHERE|STEPS|CHECK|RECORD)\*\*$", section, re.M) != ["WHERE", "STEPS", "CHECK", "RECORD"]:
            issues.append(f"guide Phase 2 {title}: missing ordered sample labels")
        actions = [int(n) for n in re.findall(r"^(\d+)\. ", section, re.M)]
        if not 3 <= len(actions) <= 7 or actions != list(range(1, len(actions) + 1)):
            issues.append(f"guide Phase 2 {title}: require 3-7 sequential actions")
        if "**RECORD**\n\n**Deliverable " not in section or not re.search(r"mismatch|failure|On failure", section, re.I):
            issues.append(f"guide Phase 2 {title}: missing recording or recovery context")
    for meaning in ("FWR-03/FWR-04", "FWT-03/FWT-04", "Approvals: E", "F for endpoint", "private identity/network plan",
                    "original Windows disk", "physical", "Corporate", "Restricted", "Management",
                    "6 vCPU / 16 GiB / 160 GiB", "2 / 6 GiB / 64 GiB", "2 / 4 GiB / 32 GiB",
                    "missing guest only", "supported OS/build", "offline update/activation", "TPM 2.0",
                    "Promote this server", "approved functional levels", "DSRM", "SYSVOL", "NETLOGON",
                    "Role installation alone is insufficient", "ava", "eli", "uma", "LabReaders", "LabMaintainers", "LabAdmins",
                    "separate administrator only", "Member Of", "Members", "approved folder", "DC1-only DNS",
                    "ad.lab.test", "Domain Controllers", "Defender", "inbound **Block**", "FF-02", "same-zone",
                    "standard-user denial/admin control", "second observations", "atomic replacement",
                    "default-deny input/forward", "IPv4/IPv6", "Preserve other tables", "console recovery",
                    "Before Phase 3", "NOT TESTED", "six access cases and revocation"):
        if meaning not in phase:
            issues.append("guide Phase 2: missing identity/endpoint safeguard: " + meaning)
    visible = re.sub(r'<a id="[a-z][a-z0-9-]*"></a>', '', phase)
    if re.search(r"\b(?:four (?:baseline )?VMs|virtual (?:OPNsense|firewall)|internal-only bridge|vmbr\d+|VLAN\s+\d+|"
                 r"Ordered|Delivered|procurement|PLANNED|T9[A-F]?(?:\.[1-7])?)\b|\b(?:\d{1,3}\.){3}\d{1,3}\b|^```", visible, re.I | re.M):
        issues.append("guide Phase 2: obsolete mapping, execution status, internal language or command block")
    links = {
        WINDOWS_REFERENCE: ("vm-profiles-and-installation", "ad-ds-and-dns", "directory-verification",
                            "users-groups-and-permissions", "win1-domain-join-and-verification", "account-and-endpoint-policy",
                            "auditing-and-effective-policy", "scoped-service-ports", "privilege-and-protection-checks", "recovery-and-version-notes"),
        LINUX_REFERENCE: ("interface-and-backend-inspection", "netplan-configuration-and-rollback", "lab-only-time",
                          "nftables-policy", "initial-load-and-persistence", "verification-and-console-recovery"),
    }
    for name, anchors in links.items():
        for anchor in anchors:
            if name.removeprefix("docs/lab-guides/") + "#" + anchor not in phase:
                issues.append("guide Phase 2: missing technical-reference navigation: " + anchor)
    safeguards = {
        "Windows": (windows, ("Desktop Experience", "domain-capable", "approved functional levels", "DSRM", "private custody",
                              "Install-WindowsFeature", "Install-ADDSForest", "Get-ADForest", "Get-ADDomainController",
                              "SYSVOL,NETLOGON", "_ldap._tcp.dc._msdcs.ad.lab.test", "Root Hints", "no corporate/public",
                              "domain root", "minimum length/history/age/complexity", "lockout threshold/duration/reset",
                              "Domain/Private/Public", "Microsoft Defender", "Audit Kerberos Authentication Service",
                              "**DC audit GPO** to the **Domain Controllers** OU", "Remote IP address", "TCP/UDP 53", "TCP/UDP 88 and 464", "TCP/UDP 389",
                              "TCP 445", "TCP 135", "49152-65535", "UDP 123", "TCP 3268", "overlapping default rules",
                              "Test-ComputerSecureChannel -Verbose", "gpresult /scope computer /r", "Access Denied", "winning-setting",
                              "LabReaders", "LabMaintainers", "LabAdmins", "Domain Admins", "standard users", "snapshot",
                              "distinct passwords", "FWT-03.01-.03", "FWT-04", "NOT TESTED")),
        "Linux": (linux, ("APP1", "sudo/root", "F approval", "Restricted", "private recovery", "renderer/backend",
                           "renderer: networkd", "dhcp4: false", "dhcp6: false", "accept-ra: false", "addresses: [LAB_DC1_IP]",
                           "netplan generate", "netplan try --timeout 120", "rollback", "FallbackNTP=", "per-link",
                           "systemd-timesyncd", "table inet lab_host", "hook input priority 10; policy drop",
                           "hook forward priority 10; policy drop", "ip saddr { LAB_WIN1_IP, LAB_ADMIN_IP } tcp dport 443",
                           'iifname "tailscale0" counter drop', "before established traffic", "APP1-only",
                           "initial-load", "atomic", "delete table inet lab_host", 'include "/etc/nftables.conf"',
                           "sudo nft -c -f /root/lab-host-replace.nft", "preserving other tables", "ExecStart/ExecStop",
                           "approved reboot", "net.ipv6.conf.all.forwarding", "IPv4 and IPv6", "NOT TESTED", "console")),
    }
    for name, (text, meanings) in safeguards.items():
        for meaning in meanings:
            if meaning not in text:
                issues.append(f"{name} reference: missing identity/endpoint safeguard: " + meaning)
        for match in re.finditer(r"^```[^\n]*\n.*?^```", text, re.M | re.S):
            context = text[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
            if not re.search(r"READ-ONLY|CONFIGURATION CHANGE|DESTRUCTIVE / HIGH-RISK", context):
                issues.append(f"{name} reference: command block needs a risk/target context")
            if re.search(r"^\s*(?:sudo\s+)?nft\s+flush\s+ruleset\b", match.group(), re.M):
                issues.append(f"{name} reference: blanket firewall flush is prohibited")
    return issues


def access_control_issues(guide: str, https: str, tailscale: str) -> list[str]:
    """Inspect Phase 3 controls and conditional profiles without lab execution."""
    issues = []
    phase = guide.partition("## Phase 3: Zero Trust Access Controls\n")[2].partition("## Phase 4:")[0]
    expected = ["A. Create and verify HTTPS certificates", "B. Configure the Apache application and accounts",
                "C. Test the six application access cases", "D. Revoke an application permission",
                "E. Configure, test and revoke Tailscale access"]
    procedures = re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", phase, re.M | re.S)
    if [title for title, _ in procedures] != expected:
        issues.append("guide Phase 3: require exactly five access-control procedures")
    for title, section in procedures:
        if re.findall(r"^\*\*(WHERE|STEPS|CHECK|RECORD)\*\*$", section, re.M) != ["WHERE", "STEPS", "CHECK", "RECORD"]:
            issues.append(f"guide Phase 3 {title}: missing ordered sample labels")
        actions = [int(n) for n in re.findall(r"^(\d+)\. ", section, re.M)]
        if not 3 <= len(actions) <= 7 or actions != list(range(1, len(actions) + 1)):
            issues.append(f"guide Phase 3 {title}: require 3-7 sequential actions")
        if "**RECORD**\n\n**Deliverable " not in section or "On failure" not in section:
            issues.append(f"guide Phase 3 {title}: missing recording or recovery context")
    cases = re.findall(r"^\| (C\d{2}) \| (ava|eli|uma) \| (/\w+/) \| (ALLOW / 200|DENY / authenticated 403) \|$", phase, re.M)
    expected_cases = [(f"C{i:02d}", user, page, result) for i, (user, page, result) in enumerate((
        ("ava", "/reports/", "ALLOW / 200"), ("ava", "/maintenance/", "DENY / authenticated 403"),
        ("eli", "/reports/", "ALLOW / 200"), ("eli", "/maintenance/", "ALLOW / 200"),
        ("uma", "/reports/", "DENY / authenticated 403"), ("uma", "/maintenance/", "DENY / authenticated 403")), 1)]
    if cases != expected_cases:
        issues.append("guide Phase 3: preserve all six exact application account/path/status decisions")
    for meaning in ("Approvals: G", "H for Apache", "I for remote", "E also covers", "FWR-03/05/06",
                    "FWT-03/FWT-05/FWT-06", "365-day", "90-day", "encrypted CA key", "serverAuth",
                    "remaining validity", "untrusted rejection", "No home/production trust changes",
                    "separate test accounts", "manually assigned roles", "single sign-on or automatic synchronization",
                    "LabReaders: ava eli", "LabMaintainers: eli", "no fourth app administrator", "TCP 443 only",
                    "fresh browser context per user", "valid application credentials", "actual server request",
                    "Apache logs", "401", "FWT-03.01-.03", ".10-.13", "separate observer clock",
                    "AD membership does not update Apache", "reader permission stays", "Restore permissions only",
                    "revocation-time SLA", "independently isolated", "explicit deny-all", "additive grant/ACL",
                    "MFA", "subnet routes", "Tailscale SSH", "Funnel", "Serve", "public sharing",
                    "FF-03", "FF-06", "no DC1, WIN1, Proxmox or OPNsense", "working positive controls",
                    "closed port or broken DNS is insufficient", "Phase 5 mock dependency", "remove the client grant",
                    "exact device authorization", "existing browser and a fresh context", "observed denial time",
                    "cache/connection-state treatment", "OPNsense alone cannot prove", "second observations", "NOT TESTED"):
        if meaning not in phase:
            issues.append("guide Phase 3: missing access-control safeguard: " + meaning)
    if "```" in phase:
        issues.append("guide Phase 3: detailed commands belong in the linked technical references")
    for name, content in ((HTTPS_REFERENCE, https), (TAILSCALE_REFERENCE, tailscale)):
        if not content:
            issues.append("guide Phase 3: technical reference is required: " + name)
        links = re.findall(re.escape(name.split("docs/lab-guides/")[1]) + r"#([a-z0-9-]+)", phase)
        if not links or any(anchor not in heading_anchors(content) for anchor in links):
            issues.append("guide Phase 3: technical-reference navigation must reach exact headings")
        for match in re.finditer(r"^```[^\n]*\n.*?^```", content, re.M | re.S):
            context = content[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
            if not re.search(r"READ-ONLY|CONFIGURATION CHANGE|DESTRUCTIVE / HIGH-RISK", context):
                issues.append("Phase 3 reference: command block needs a risk/target context")
    required = {
        "HTTPS": (https, ("rsa:3072", "-days 365", "rsa:2048 -noenc", "-days 90", "umask 077",
                          "-purpose sslserver", "-verify_hostname app.ad.lab.test", "subjectAltName=DNS:app.ad.lab.test",
                          "basicConstraints=critical,CA:FALSE", "extendedKeyUsage=serverAuth", "remaining validity",
                          "-B -c /etc/labapp/users ava", "-c creates or overwrites", "root-only, mode 0600",
                          "mode **0640**", "AuthzSendForbiddenOnFailure On", "AuthMerging Off",
                          "Syntax OK", "sudo ss -lntp", "no single sign-on or automatic AD synchronization",
                          "There is no revocation-time SLA", "no CRL/OCSP", "LabReaders: ava eli")),
        "Tailscale": (tailscale, ("before Internet connectivity", "MFA and recovery", "before enrollment",
                                 "--accept-routes=false --accept-dns=false --ssh=false", "not grant every device",
                                 "Windows route/DNS defaults", "no direct physical/zone route", "hosts",
                                 "before established traffic", "forward chain drops", "both IPv4/IPv6",
                                 "unauthorized **uma**", "distinct", "known-listening", "working positive control",
                                 "Remove", "Keep APP1 intact", "fresh connection/context", "separate observer clock",
                                 "do not blindly restore", "NOT TESTED")),
    }
    for name, (content, meanings) in required.items():
        for meaning in meanings:
            if meaning not in content:
                issues.append(f"{name} reference: missing access-control safeguard: " + meaning)
    groups = re.findall(r"^```text\n(LabReaders:[^`]+)```", https, re.M)
    if groups != ["LabReaders: ava eli\nLabMaintainers: eli\n"]:
        issues.append("HTTPS reference: preserve exact manual application group mapping")
    apache = "\n".join(re.findall(r"^```apache\n(.*?)^```", https, re.M | re.S))
    for path, role in (("/srv/labapp/reports", "LabReaders"), ("/srv/labapp/maintenance", "LabMaintainers")):
        if not re.search(r'<Directory "' + re.escape(path) + r'">\s*Require group ' + role + r'\s*</Directory>', apache):
            issues.append("HTTPS reference: exact per-page group authorization is required")
    if "Require valid-user" in apache or "Require all denied" not in apache or "Listen 80" in apache:
        issues.append("HTTPS reference: deny-by-default HTTPS must not become a generic user allow")
    try:
        policies = [json.loads(block) for block in re.findall(r"^```json\n(.*?)^```", tailscale, re.M | re.S)]
    except ValueError:
        policies = []
    if policies != [{"acls": [], "grants": [], "ssh": []},
                    {"acls": [], "grants": [{"src": ["LAB_REMOTE_OVERLAY_IP"], "dst": ["LAB_APP_OVERLAY_IP"], "ip": ["tcp:443"]}], "ssh": []}]:
        issues.append("Tailscale reference: require explicit deny-all then the single exact client/APP1 tcp:443 grant")
    return issues


def monitoring_recovery_issues(guide: str, logs: str, recovery: str) -> list[str]:
    """Check Phase 4's instruction/security contract without executing lab code."""
    issues = []
    phase = guide.partition("## Phase 4: Monitoring, Automation and Recovery\n")[2].partition("## Phase 5:")[0]
    expected = ["A. Collect five security events", "B. Investigate one denied-access event",
                "C. Run the capacity-summary automation", "D. Back up APP1 and restore it in isolation"]
    procedures = re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", phase, re.M | re.S)
    if [title for title, _ in procedures] != expected:
        issues.append("guide Phase 4: require exactly four monitoring/automation/recovery procedures")
    for title, section in procedures:
        if re.findall(r"^\*\*(WHERE|STEPS|CHECK|RECORD)\*\*$", section, re.M) != ["WHERE", "STEPS", "CHECK", "RECORD"]:
            issues.append(f"guide Phase 4 {title}: missing ordered sample labels")
        actions = [int(n) for n in re.findall(r"^(\d+)\. ", section, re.M)]
        # Recovery deliberately has nine actions to retain critical dependencies.
        maximum = 9 if title.startswith("D. ") else 7
        if not 3 <= len(actions) <= maximum or actions != list(range(1, len(actions) + 1)):
            issues.append(f"guide Phase 4 {title}: missing sequential bounded actions")
        if "Deliverable 03 >" not in section or "failure" not in section.lower() and "On failure" not in section:
            issues.append(f"guide Phase 4 {title}: missing exact recording or recovery context")
    events = re.findall(r"^\| (E\d{2}) ([^|]+)\|", phase, re.M)
    if [(event, label.strip()) for event, label in events] != [
            ("E01", "Directory authentication success"), ("E02", "Directory authentication failure"),
            ("E03", "Application access allowed"), ("E04", "Application access denied"),
            ("E05", "Firewall access denied")]:
        issues.append("guide Phase 4: preserve five distinct security event categories")
    visible = re.sub(r'<a id="[a-z][a-z0-9-]*"></a>', '', phase)
    for meaning in ("physical OPNsense", "three workload VMs", "J approval", "explicit L", "E/H/I",
                    "known-listening", "lockout", "source/observer UTC", "second observations",
                    "one working allowed control", "incorrect credentials", "broken DNS", "stopped service", "network failure",
                    "WIN1/ad.lab.test", "outside Git", "WIN1-capacity.json", "successfully a second time",
                    "invalid-target", "invalid-output-path", "both safe rejections", "before/after",
                    "BLOCKED", "NOT TESTED", "private isolation plan", "encrypted", "separate recovery key",
                    "unused temporary ID", "manifest", "Keep the original off", "every restored NIC",
                    "automatic startup", "stop and disable copied Tailscale", "before temporary changes",
                    "no new bridge/VLAN/NIC/port mapping or firewall bypass", "ava /reports/", "ava /maintenance/",
                    "actual elapsed time", "lock/detach", "stored separately", "B01-B10", "AD/CA/host/physical-firewall",
                    "Before Phase 5", "Engineering results and owner acceptance are separate"):
        if meaning.lower() not in phase.lower():
            issues.append("guide Phase 4: missing operational safeguard: " + meaning)
    if re.search(r"^```|\bvmbr\d+\b|\bVLAN\s+\d+|\b(?:\d{1,3}\.){3}\d{1,3}\b", visible, re.M):
        issues.append("guide Phase 4: detailed commands/private topology belong outside the concise guide")
    if re.search(r"\b(?:T9[A-F]?(?:\.[1-7])?|procurement|PLANNED|IN PROGRESS)\b", visible):
        issues.append("guide Phase 4: internal task or execution-status language")
    if not logs or not recovery:
        return issues + ["guide Phase 4: both technical references are required"]
    for name, reference in ((MONITORING_REFERENCE, logs), (RECOVERY_REFERENCE, recovery)):
        if "reference/" + name.rsplit("/", 1)[1] + "#" not in phase:
            issues.append("guide Phase 4: direct technical-reference heading links are required")
        for match in re.finditer(r"^```[^\n]*\n.*?^```", reference, re.M | re.S):
            context = reference[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
            if not re.search(r"READ-ONLY|CONFIGURATION CHANGE|DESTRUCTIVE / HIGH-RISK", context):
                issues.append("Phase 4 reference: command block needs a risk/target context")
    scripts = [body for _, body in re.findall(r"^```([^\n]*)\n(.*?)^```", logs, re.M | re.S)
               if body.startswith("param([Parameter(Mandatory)]")]
    if len(scripts) != 1 or hashlib.sha256(scripts[0].encode()).hexdigest() != "a0520fd9c143f407b53e395faeef7399b17525cbd16139b05d33bd24bfcce7ce":
        issues.append("monitoring reference: complete WIN1 capacity script must remain identical to approved baseline")
    for meaning in ("Audit Kerberos Authentication Service", "Domain Controllers", "4768", "4771", "one deliberately wrong-password attempt",
                    "lockout margin", "cached", "Live View", "floating/group/automatic", "States", "event-time",
                    "/var/log/apache2/labapp-access.log", "/var/log/apache2/labapp-error.log", "tail -n 40",
                    "/etc/logrotate.d/apache2", "source UTC minus observer UTC", "retention", "raw", "private originals",
                    "E01", "E02", "E03", "E04", "E05", "who", "working allowed control", "second observation",
                    "incorrect credentials", "broken DNS", "stopped service", "network failure", "401", "403",
                    "junctions/symlinks/reparse points", "not a canonical-path", "execution-policy bypass", "No remote execution",
                    "second time successfully", "Get-Item", "WIN1-INVALID-TEST", "unchanged hash/mtime", "A01", "A07",
                    "FWT-07", "FWT-08", "reference-only extraction", "deferred Phase 5 dependency", "FWR/FWT-01/02/06",
                    "TCP CONNECTED", "NO TCP CONNECTION", "MOCK_PROTECTED", "LAB_ADMIN_IP", "tcp dport 8443",
                    "never a real protected address", "Keep the vendor TCP-443-only grant unchanged"):
        if meaning.lower() not in logs.lower():
            issues.append("monitoring reference: missing event/automation/deferred-tool safeguard: " + meaning)
    for meaning in ("Operational procedure: BLOCKED pending private design", "owner-selected encrypted storage backend",
                    "WIN1 -> physical HP OPNsense -> restored APP1", "not a verified physical connection recipe",
                    "No fixed bridge, VLAN, NIC or port mapping", "is_mountpoint", "findmnt --mountpoint", "lsblk", "storage.cfg",
                    "compression", "recovery-key access", "recovery key separately", "off-compute", "both** AD and application",
                    "LabMaintainers", "revoked state", "/srv/labapp", "/etc/apache2", "/etc/labapp", "app.key", "app.crt", "lab-ca.crt",
                    "older manifests", "new unused path", "separate protected storage", "before backup", "included disk",
                    "original APP1", "sole archive", "Keep **Start after restore** and **Live restore** off", "Start at boot: No",
                    "unused temporary", "every NIC", "original remains stopped", "disable --now tailscaled", "is-active tailscaled",
                    "is-enabled tailscaled", "sha256sum -c", "before** temporary", "physical HP firewall on the routed test path",
                    "Do not connect them directly on a shared bridge", "LAB_RESTORE_CLIENT_IP", "LAB_RESTORE_APP_IP",
                    "TCP 443", "earlier tailscale0 drop", "unrelated tables", "default denies", "IPv6", "independent observer clock",
                    "immediately before confirming Restore", "only when", "HTTP 200", "HTTP 403", "HTTP 401", "separate observations",
                    "Disconnect every restored NIC first", "before original startup", "unmount, lock and detach", "B01-B03", "B04-B07",
                    "B06", "B07", "B08", "B09", "B10", "NOT TESTED", "no enterprise", "AD/CA/host/physical-firewall",
                    "Version-specific", "24.04", "no disk-format"):
        if meaning.lower() not in recovery.lower():
            issues.append("recovery reference: missing backup/isolation/evidence safeguard: " + meaning)
    if re.search(r"\bvmbr\d+\b|disconnect OPNsense.{0,30}NIC|OPNsense.s vmbr|\bVLAN\s+\d+", phase + recovery, re.I):
        issues.append("Phase 4 recovery: obsolete virtual-firewall or invented topology instruction")
    return issues


def completeness_issues(texts: dict[str, str]) -> list[str]:
    """Validate the approved focused specification; never execute lab content."""
    issues: list[str] = []
    assignment = texts.get("docs/assignments/PROJECT-ASSIGNMENT.md", "")
    guide = texts.get("docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md", "")
    issues.extend(prepared_infrastructure_issues(guide, texts.get(PREPARED_REFERENCE, "")))
    issues.extend(identity_endpoint_issues(guide, texts.get(WINDOWS_REFERENCE, ""), texts.get(LINUX_REFERENCE, "")))
    issues.extend(access_control_issues(guide, texts.get(HTTPS_REFERENCE, ""), texts.get(TAILSCALE_REFERENCE, "")))
    issues.extend(monitoring_recovery_issues(guide, texts.get(MONITORING_REFERENCE, ""), texts.get(RECOVERY_REFERENCE, "")))
    plan = texts.get("docs/testing/TEST-PLAN.md", "")
    titles = tuple(match[2] for match in HEADING.finditer(strip_fences(assignment)[0]) if match[1] == "##")
    if titles != ASSIGNMENT_HEADINGS:
        issues.append("assignment must contain the seven required sections exactly once in order")
    required_ids = [f"FWR-{number:02d}" for number in range(1, 11)]
    assignment_ids = re.findall(r"^\|\s*(FWR-\d{2})\s*\|", assignment, re.M)
    if assignment_ids != required_ids:
        issues.append("assignment must declare FWR-01 through FWR-10 exactly once in order")
    for number in range(1, 11):
        row = re.search(rf"^\|\s*FWR-{number:02d}\s*\|[^\n]+$", assignment, re.M)
        if not row or re.findall(r"FWT-\d{2}", row[0]) != [f"FWT-{number:02d}"]:
            issues.append(f"FWR-{number:02d}: wrong primary test mapping")
    rubric = assignment.partition("## Evaluation Rubric")[2].split("\n## ", 1)[0]
    weights = [(title.strip(), int(score)) for title, score in
               re.findall(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", rubric, re.M)]
    if weights != list(RUBRIC_WEIGHTS) or sum(score for _, score in weights) != 100:
        issues.append("assignment rubric must match approved five categories/weights and total 100 points")
    deliverables = assignment.partition("## Required Deliverables")[2].split("\n## ", 1)[0]
    names = re.findall(r"^\|\s*`([^`]+)`\s*\|", deliverables, re.M)
    if tuple(names) != DELIVERABLE_FILENAMES:
        issues.append("assignment must declare the five approved unique T7 deliverable filenames in order")
    mapped = set()
    for row in deliverables.splitlines():
        match = re.match(r"\|\s*`([^`]+)`\s*\|([^|]+)\|$", row)
        if match:
            mapped.update(re.findall(r"\bFWR-\d{2}\b", match[2]))
    if mapped != set(required_ids):
        issues.append("assignment deliverables must cover all FWR-01 through FWR-10 requirements")
    if "`docs/deliverables/`" not in deliverables:
        issues.append("assignment must state the docs/deliverables/ submission location")
    if "available as blank templates" not in deliverables:
        issues.append("assignment: template availability must remain explicit")
    if "available as blank templates" not in guide:
        issues.append("guide: template availability must remain explicit")
    if re.search(r"\b(?:T6[AB]?|T7|Codex)\b", guide):
        issues.append("guide: internal task jargon belongs in reports")
    aliases = set(re.findall(r'^<a id="([a-z][a-z0-9-]*)"></a>\s*$', assignment, re.M))
    if aliases != ASSIGNMENT_COMPATIBILITY_ANCHORS:
        issues.append("assignment: preserve compatibility anchors for existing links")
    if re.search(r"\b(?:T[0-9]+[A-F]?|Codex|A-L)\b", assignment):
        issues.append("assignment: internal task/stage jargon must stay in the guide/report")
    for meaning in ("separate test accounts", "manually assigned roles", "removing an application role", "single sign-on"):
        if meaning not in assignment.lower():
            issues.append("assignment: preserve separate application identity/revocation/SSO limits")
    environment = assignment.partition("## Lab Environment")[2].split("\n## ", 1)[0].lower()
    for meaning in ("prepared environment", "proxmox and physical opnsense", "three security boundaries",
                    "restricted management", "sufficient resources", "host reserves", "temporary restore",
                    "home/production isolation", "required network flows and denials", "console recovery",
                    "backup and recovery", "original windows disk", "data and services",
                    "owner approval covering changes, validation and rollback"):
        if meaning not in environment:
            issues.append("assignment: preserve concise hardware readiness/data/safety controls")
    for meaning in ("keep uplinks disconnected", "independent isolation", "lab-owned mock targets",
                    "never probe them", "separate lab identities", "credential reuse",
                    "corporate microsoft 365", "pe-dap", "customer data", "hosting integration"):
        if meaning not in assignment.lower():
            issues.append("assignment: preserve isolation and protected-network safeguards")
    for component in ("Dell Precision 5820 with Proxmox VE", "HP desktop with physical OPNsense",
                      "TP-Link TL-SG108E", "GL.iNet Beryl AX", "exactly three workload",
                      "6 vCPU / 16 GiB RAM / 160 GiB virtual disks"):
        if component not in assignment:
            issues.append("assignment: preserve approved physical firewall and three-workload architecture")
    if re.search(r"\b(?:four[- ](?:VMs?|virtual machines)|virtual OPNsense|PLANNED|NOT TESTED|UAT PENDING|"
                 r"[Oo]rdered|[Dd]elivered|[Pp]rocurement)\b", assignment):
        issues.append("assignment: obsolete topology, procurement or execution status belongs outside the assignment")
    guide_files = guide.partition("## Required lab deliverables")[2].split("\n## ", 1)[0]
    if tuple(re.findall(r"^\|\s*`([^`]+)`\s*\|", guide_files, re.M)) != DELIVERABLE_FILENAMES:
        issues.append("guide must match the five approved filenames")
    phases = re.split(r"^## Phase (\d): ([^\n]+)\n", guide, flags=re.M)
    phase_rows = [tuple(phases[i:i + 3]) for i in range(1, len(phases), 3)]
    if [(n, title) for n, title, _ in phase_rows] != [(str(i), t) for i, t in enumerate(PHASE_TITLES, 1)]:
        issues.append("guide must contain the five approved phases exactly once in order")
    for number, _, section in phase_rows:
        if number in {"1", "2", "3", "4"}:
            if f"**Before Phase {int(number) + 1}:**" not in section:
                issues.append(f"phase {number} missing field: checkpoint and recovery")
        elif not re.search(rf"^### Phase {number} checkpoint and recovery\s*$", section, re.M):
            issues.append(f"phase {number} missing field: checkpoint and recovery")
        for field in (() if number in {"1", "2", "3", "4"} else ("**Outcome:**", "Approvals:", "Test")):
            if field not in section:
                issues.append(f"phase {number} missing field: {field}")
        expected_tests = {"1": (1, 2), "2": (3, 4), "3": (3, 5, 6),
                          "4": (7, 8, 9), "5": (10,)}.get(number, ())
        for test in expected_tests:
            if f"FWT-{test:02d}" not in section:
                issues.append(f"phase {number}: missing existing test mapping")
    for meaning in ("each stage A-L", "original Windows disk", "backup/recovery",
                    "independently isolated", "lab-owned mocks", "separate test accounts",
                    "manually assigned roles", "NOT TESTED", "PENDING"):
        if meaning not in guide:
            issues.append("guide: preserve stage approval, readiness, isolation and identity safeguards")
    for match in re.finditer(r"^```[^\n]*\n.*?^```", guide, re.M | re.S):
        context = guide[:match.start()].rstrip().rsplit("\n\n", 1)[-1]
        if not re.search(r"READ-ONLY|CONFIGURATION CHANGE|DESTRUCTIVE / HIGH-RISK", context):
            issues.append("guide: command/configuration block needs a risk/target context")
    procedures = re.findall(r"^### Step (\d+) - [^\n]+\n(.*?)(?=^### |^## |\Z)", guide, re.M | re.S)
    if [int(n) for n, _ in procedures] != list(range(24, 28)):
        issues.append("guide: preserve downstream numbered procedures 24-27 in order")
    for number, body in procedures:
        for field in ("**Purpose and location:**", "**Check", "**If it fails:**"):
            if field not in body:
                issues.append(f"guide procedure {number}: missing instructional context {field}")
        if not re.search(r"^1\. ", body, re.M):
            issues.append(f"guide procedure {number}: missing numbered actions")
    lines = strip_fences(guide)[0].splitlines()
    for previous, line in zip(lines, lines[1:]):
        if re.match(r"^\d+\. ", line) and previous.strip() and not re.match(r"^\d+\. ", previous):
            issues.append("guide: a numbered action after prose needs a blank line to render as a list")
    transition = texts.get(GUIDE_TRANSITION, "")
    if GUIDE_TRANSITION.split("/")[-1] not in guide:
        issues.append("guide: historical appendix navigation is required")
    if set(re.findall(r"\bR\d{2}\b", transition)) != {f"R{i:02d}" for i in range(1, 17)}:
        issues.append("appendix historical requirement transition must preserve all R01-R16 IDs")
    if set(re.findall(r"\bT\d{2}\b", transition)) != {f"T{i:02d}" for i in range(21)}:
        issues.append("appendix historical test transition must preserve all T00-T20 IDs")
    test_ids = re.findall(r"^### (FWT-\d{2})\b", plan, re.M)
    if test_ids != [f"FWT-{number:02d}" for number in range(1, 11)]:
        issues.append("test plan must declare FWT-01 through FWT-10 exactly once in order")
    chunks = re.split(r"^### (FWT-\d{2})[^\n]*\n", plan, flags=re.M)
    pairs = iter(chunks[1:])
    for tid, section in zip(pairs, pairs):
        for field in ("Objective and method", "Expected result and pass/fail criteria", "Second observation"):
            if f"**{field}:**" not in section:
                issues.append(f"{tid}: missing test field {field}")
        for field in ("Actual result", "Evidence reference"):
            value = re.search(rf"^\|\s*{field}\s*\|([^|]*)\|", section, re.M)
            if not value or value[1].strip():
                issues.append(f"{tid}: planned {field.lower()} must be present and empty")
        if not re.search(r"^\|\s*Verdict\s*\|\s*NOT TESTED\s*\|", section, re.M):
            issues.append(f"{tid}: planned verdict must be NOT TESTED")
    app_cases = plan.partition("## Six application access cases")[2].split("\n## ", 1)[0]
    outcomes = re.findall(r"^\|\s*(C\d{2})\s*\|[^\n]+\|\s*(Allow|Deny)\s*\|", app_cases, re.M)
    if outcomes != [(f"C{i:02d}", result) for i, result in enumerate(("Allow", "Deny", "Allow", "Allow", "Deny", "Deny"), 1)]:
        issues.append("test plan must retain six approved meaningful application access cases")
    controls = texts.get("docs/security/SECURITY-REQUIREMENTS.md", "")
    acceptance = texts.get("docs/testing/ACCEPTANCE-CRITERIA.md", "")
    if re.findall(r"^\|\s*(FSC-\d{2})\s*\|", controls, re.M) != [f"FSC-{i:02d}" for i in range(1, 11)]:
        issues.append("security must declare ten focused controls")
    if re.findall(r"^\|\s*(FAC-\d{2})\s*\|", acceptance, re.M) != [f"FAC-{i:02d}" for i in range(1, 11)]:
        issues.append("acceptance must declare ten focused criteria")
    for number in range(1, 11):
        row = re.search(rf"^\|\s*FSC-{number:02d}\s*\|[^\n]+$", controls, re.M)
        if (not row or re.findall(r"FWR-\d{2}", row[0]) != [f"FWR-{number:02d}"]
                or re.findall(r"FWT-\d{2}", row[0]) != [f"FWT-{number:02d}"]):
            issues.append(f"FSC-{number:02d}: invalid security requirement/test mapping")
    coverage = plan.partition("## Coverage index")[2]
    rows = [line.strip().strip("|").split("|") for line in coverage.splitlines() if re.match(r"^\|\s*FWR-", line)]
    if [row[0].strip() for row in rows] != required_ids:
        issues.append("test coverage index must map every focused requirement exactly once")
    for row in rows:
        rid = row[0].strip()
        number = rid[-2:]
        expected = (f"FSC-{number}", f"FWT-{number}", f"FAC-{number}")
        if len(row) != 6 or tuple(cell.strip() for cell in row[2:5]) != expected:
            issues.append(f"{rid}: invalid architecture/control/test/acceptance mapping")
        elif not row[1].strip() or not re.fullmatch(r"0[1-5](?:, 0[1-5])*", row[5].strip()):
            issues.append(f"{rid}: missing architecture or future deliverable mapping")
    workflow = texts.get(".github/workflows/documentation.yml", "")
    if not re.search(r"permissions:\s*\n\s+contents: read\s*\n", workflow):
        issues.append("workflow must declare contents: read")
    if "persist-credentials: false" not in workflow:
        issues.append("workflow must disable persistent checkout credentials")
    uses = re.findall(r"^\s+uses:\s*(\S+)", workflow, re.M)
    if not uses or any(not re.fullmatch(r"actions/checkout@[0-9a-f]{40}", action) for action in uses):
        issues.append("documentation workflow must use a full-SHA-pinned official checkout")
    if re.search(r"pull_request_target|secrets\.|write-all|contents:\s*write", workflow):
        issues.append("documentation workflow contains privileged execution or credentials")
    return issues


def report_issues(texts: dict[str, str], require_finalized: bool = False,
                  allow_t9_draft: bool = False) -> list[str]:
    issues = []
    if allow_t9_draft:
        umbrella = texts.get(T9_UMBRELLA_REPORT, "")
        visible_umbrella, _ = strip_fences(umbrella)
        if (not require_finalized
                or re.findall(r"^Report state: (DRAFT|FINALIZED)$", visible_umbrella, re.M) != ["DRAFT"]
                or not re.search(r"^\|\s*Umbrella status\s*\|\s*IN PROGRESS\s*\|$",
                                 visible_umbrella, re.M)):
            issues.append("T9 draft exception requires --require-finalized and the single DRAFT, IN PROGRESS T9 umbrella report")
    numbers = []
    addenda: dict[int, list[int]] = {}
    for name, content in texts.items():
        if not name.startswith("docs/reports/") or name in {"docs/reports/README.md", "docs/reports/INDEX.md"}:
            continue
        report = REPORT_NAME.fullmatch(name)
        addendum = ADDENDUM_NAME.fullmatch(name)
        companion = COMPANION_REPORTS.get(name)
        if not report and not addendum and not companion:
            issues.append(f"{name}: invalid task-report/addendum filename")
            continue
        number = companion[1] if companion else int((report or addendum)[1])
        expected_id = companion[0] if companion else f"T{number}"
        if companion:
            parent = texts.get(f"docs/reports/T{number}-Report.md", "")
            if not re.search(r"^Report state: FINALIZED$", parent, re.M):
                issues.append(f"{expected_id}: companion requires its finalized parent task report")
        elif report:
            numbers.append(number)
        else:
            addenda.setdefault(number, []).append(int(addendum[2]))
        visible, _ = strip_fences(content)
        headings = [match[2] for match in HEADING.finditer(visible) if len(match[1]) == 2]
        required = [heading for heading in headings if heading in REPORT_SECTIONS]
        if required != list(REPORT_SECTIONS):
            issues.append(f"{name}: required report sections A–H must occur once in order")
        task_id = re.search(r"^\|\s*Task ID\s*\|\s*(T[1-9][0-9]*[A-Z]?)(?=\s|/|\|)", visible, re.M)
        if not task_id or task_id[1] != expected_id:
            issues.append(f"{name}: missing/mismatched Task ID row")
        states = re.findall(r"^Report state: (DRAFT|FINALIZED)$", visible, re.M)
        if len(states) != 1:
            issues.append(f"{name}: exactly one DRAFT/FINALIZED state marker required")
        elif require_finalized and states[0] != "FINALIZED" and not (allow_t9_draft and name == T9_UMBRELLA_REPORT):
            issues.append(f"{name}: report must be finalized before task completion/merge")
    if not numbers or sorted(numbers) != list(range(1, max(numbers, default=0) + 1)):
        issues.append("task report numbers must be unique and sequential starting at T1")
    for parent, sequence in addenda.items():
        if parent not in numbers:
            issues.append(f"T{parent}: addendum has no parent task report")
        if sorted(sequence) != list(range(1, max(sequence) + 1)):
            issues.append(f"T{parent}: addendum numbers must be unique/sequential starting at 001")
    return issues


def finalized_history_issues(root: Path, texts: dict[str, str]) -> list[str]:
    """Compare both historical report locations with the canonical current bytes."""
    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)

    if git("rev-parse", "--is-shallow-repository").strip() == b"true":
        return ["report immutability requires complete Git history (fetch-depth: 0)"]
    frozen: dict[str, set[str]] = {}
    objects: dict[str, bytes] = {}
    for commit in git("log", "--all", "--format=%H", "--", "reports", "docs/reports").decode().splitlines():
        seen = set()
        for entry in git("ls-tree", "-r", "-z", commit, "--", "reports", "docs/reports").split(b"\0"):
            if not entry:
                continue
            metadata, raw_name = entry.split(b"\t", 1)
            name = raw_name.decode("utf-8")
            if name.startswith("reports/"):
                name = "docs/" + name  # T4 permits relocation, never a renamed basename.
            if not (REPORT_NAME.fullmatch(name) or ADDENDUM_NAME.fullmatch(name) or name in COMPANION_REPORTS):
                continue
            if name in seen:
                return [f"{name}: duplicate report locations in committed history"]
            seen.add(name)
            _, kind, oid = metadata.decode().split()
            if kind != "blob":
                return [f"{name}: unexpected report object in history"]
            if oid not in objects:
                objects[oid] = git("cat-file", "blob", oid)
            content = objects[oid]
            if re.search(rb"^Report state: FINALIZED$", content, re.M):
                frozen.setdefault(name, set()).add(hashlib.sha256(content).hexdigest())
    issues = []
    for name, hashes in frozen.items():
        if len(hashes) != 1:
            issues.append(f"{name}: finalized report was changed in committed history")
        elif name not in texts or not (root / name).is_file():
            issues.append(f"{name}: finalized report deleted or renamed")
        elif hashlib.sha256((root / name).read_bytes()).hexdigest() not in hashes:
            issues.append(f"{name}: finalized report modified; use a separate addendum")
    return issues


def report_migration_issues(root: Path) -> list[str]:
    """Freeze the complete owner-requested migration, including its old index."""
    issues = []
    for name, expected in MIGRATED_REPORT_FILES.items():
        path = root / name
        if not path.is_file():
            issues.append(f"{name}: missing migrated historical file")
        elif path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            issues.append(f"{name}: migrated historical file differs from frozen pre-T4 bytes")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-finalized", action="store_true", help="Reject draft reports before task completion or merge")
    parser.add_argument("--allow-t9-draft", action="store_true",
                        help="With --require-finalized, allow only the owner-authorized in-progress T9 umbrella draft for interim publication; never T9F completion")
    args = parser.parse_args()
    try:
        paths = candidate_paths(ROOT)
    except (OSError, subprocess.CalledProcessError):
        print("FAIL: Git file inventory unavailable; initialize/inspect Git before validation.")
        return 1
    issues = structure_issues(ROOT, paths)
    texts: dict[str, str] = {}
    for relative in paths:
        findings, content = file_issues(ROOT, relative)
        issues.extend(findings)
        if content is not None:
            texts[relative] = content
            if relative.endswith(".md"):
                issues.extend(link_issues(ROOT, relative, content))
    issues.extend(completeness_issues(texts))
    issues.extend(pdf_inventory_issues(paths, texts))
    issues.extend(report_issues(texts, args.require_finalized, args.allow_t9_draft))
    issues.extend(report_migration_issues(ROOT))
    if (ROOT / "docs/reports/T5-Report.md").exists() or (ROOT / "docs/deliverables").exists():
        issues.extend(template_set_issues(ROOT))
    try:
        issues.extend(finalized_history_issues(ROOT, texts))
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        issues.append("report immutability history could not be verified; inspect Git before completion")
    if issues:
        print(f"FAIL: {len(issues)} finding(s)")
        for issue in sorted(set(issues)):
            print(f"- {issue}")
        return 1
    markdown_count = sum(path.endswith(".md") for path in paths)
    print(f"PASS: {len(paths)} public candidate files; {markdown_count} Markdown files.")
    print("PASS: structure, local links/anchors and verified frozen T5 snapshot targets, five phase fields, FWR/FWT/FSC/FAC coverage, rubric, workflow, focused publication scan.")
    print("PASS: task-report numbering, A–H structure, and committed finalized-report preservation.")
    if args.allow_t9_draft:
        print("EXCEPTION: only the DRAFT, IN PROGRESS T9 umbrella report is permitted for interim publication; T9 completion is not verified.")
    print("PASS: docs/reports/ migration, eleven historical file hashes, Markdown-only reporting, and source/hash-matched document PDFs.")
    print("LIMITS: manual content/history/metadata review required; no external-link or operational-security verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
