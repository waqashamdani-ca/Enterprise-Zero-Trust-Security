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
PHASE_TITLES = (
    "Infrastructure and Network", "Identity and Endpoint Security", "Zero Trust Access Controls",
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
    "Project Overview", "Learning Objectives", "What You Will Build", "Project Requirements",
    "Required Deliverables", "Four-Week Implementation Plan", "Evaluation Criteria", "References",
)
ASSIGNMENT_COMPATIBILITY_ANCHORS = {
    "project-objectives", "project-scope", "technologies-and-resources",
    "expected-deliverables", "implementation-approach", "success-criteria",
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
    if PRIVATE_NAME.search(path.name):
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


def completeness_issues(texts: dict[str, str]) -> list[str]:
    """Validate the approved focused specification; never execute lab content."""
    issues: list[str] = []
    assignment = texts.get("docs/assignments/PROJECT-ASSIGNMENT.md", "")
    guide = texts.get("docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md", "")
    plan = texts.get("docs/testing/TEST-PLAN.md", "")
    titles = {match[2] for match in HEADING.finditer(strip_fences(assignment)[0])}
    for title in ASSIGNMENT_HEADINGS:
        if title not in titles:
            issues.append(f"assignment missing required section: {title}")
    required_ids = [f"FWR-{number:02d}" for number in range(1, 11)]
    assignment_ids = re.findall(r"^\|\s*(FWR-\d{2})\s*\|", assignment, re.M)
    if assignment_ids != required_ids:
        issues.append("assignment must declare FWR-01 through FWR-10 exactly once in order")
    for number in range(1, 11):
        row = re.search(rf"^\|\s*FWR-{number:02d}\s*\|[^\n]+$", assignment, re.M)
        if not row or re.findall(r"FWT-\d{2}", row[0]) != [f"FWT-{number:02d}"]:
            issues.append(f"FWR-{number:02d}: wrong primary test mapping")
    rubric = assignment.partition("## Evaluation Criteria")[2].split("\n## ", 1)[0]
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
    if re.search(r"\b(?:T6A?|T7|A-L)\b", assignment):
        issues.append("assignment: internal task/stage jargon must stay in the guide/report")
    for meaning in ("separate test accounts", "manually assigned roles", "removing an application role", "single sign-on"):
        if meaning not in assignment.lower():
            issues.append("assignment: preserve separate application identity/revocation/SSO limits")
    for meaning in ("existing and ordered hardware", "backup and recovery", "owner approval", "original windows disk", "not assumed delivered, installed or validated"):
        if meaning not in assignment.lower():
            issues.append("assignment: preserve concise hardware readiness/data/safety controls")
    if any(part in assignment for part in ORDERED_HARDWARE):
        issues.append("assignment: detailed procurement belongs in the guide")
    guide_files = guide.partition("## Required lab deliverables")[2].split("\n## ", 1)[0]
    if tuple(re.findall(r"^\|\s*`([^`]+)`\s*\|", guide_files, re.M)) != DELIVERABLE_FILENAMES:
        issues.append("guide must match the five approved filenames")
    phases = re.split(r"^## Phase (\d): ([^\n]+)\n", guide, flags=re.M)
    phase_rows = [tuple(phases[i:i + 3]) for i in range(1, len(phases), 3)]
    if [(n, title) for n, title, _ in phase_rows] != [(str(i), t) for i, t in enumerate(PHASE_TITLES, 1)]:
        issues.append("guide must contain the five approved phases exactly once in order")
    for number, _, section in phase_rows:
        if not re.search(rf"^### Phase {number} checkpoint and recovery\s*$", section, re.M):
            issues.append(f"phase {number} missing field: checkpoint and recovery")
        for field in ("**Outcome:**", "Approvals:", "Test"):
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
    if [int(n) for n, _ in procedures] != list(range(1, 28)):
        issues.append("guide: preserve the 27 numbered procedures in order")
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
    for label, content in (("guide", guide),):
        for status in ("Existing", "Ordered", "Delivered", "Installed", "Validated"):
            if not re.search(rf"\b{status}\b", content, re.I):
                issues.append(f"{label}: missing hardware status {status}")
        for part in ORDERED_HARDWARE:
            if part not in content:
                issues.append(f"{label}: missing confirmed ordered hardware item")
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
