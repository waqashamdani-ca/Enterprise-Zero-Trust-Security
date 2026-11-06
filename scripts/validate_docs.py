#!/usr/bin/env python3
"""Offline documentation and focused public-publication checks; Python 3.11+.

This tool inspects files only. It never installs dependencies, connects to the
lab, fetches external links, or prints a suspected credential value. It is not
a complete secret detector; a manual staged-content/history review is required.
"""

from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", "AGENTS.md", ".gitignore", ".gitattributes",
    ".github/workflows/documentation.yml",
    "docs/PROJECT-ASSIGNMENT.md", "docs/LAB-IMPLEMENTATION-GUIDE.md",
    "docs/ARCHITECTURE.md", "docs/SECURITY-REQUIREMENTS.md",
    "docs/TEST-PLAN.md", "docs/ACCEPTANCE-CRITERIA.md",
    "docs/DECISIONS.md", "docs/RISKS.md", "docs/FINAL-REPORT.md",
    "docs/REFERENCES.md", "infrastructure/README.md",
    "configurations/README.md", "scripts/validate_docs.py",
    "tests/test_validate_docs.py", "evidence/README.md",
)
REQUIRED_DIRS = (
    ".github/workflows", "docs", "infrastructure", "configurations",
    "scripts", "tests", "evidence",
)
STAGE_FIELDS = (
    "Prerequisites", "Procedures", "Proposed commands", "Expected outcome",
    "Verification", "Rollback", "Completion criteria",
)
ASSIGNMENT_HEADINGS = (
    "Description and background", "Enterprise scenario and business case",
    "Purpose, objectives, and learning goals", "Measurable technical requirements",
    "Scope, exclusions, assumptions, and constraints",
    "Prerequisites and dependencies", "Expected architecture and trust boundaries",
    "Technologies and implementation alternatives",
    "Security requirements and threat model", "Standards alignment",
    "Deliverables and final outcomes", "Testing and acceptance",
    "100-point evaluation rubric", "GitHub publication requirements",
    "Evidence-backed resume achievement objectives", "Authoritative references",
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
    return used


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
    if path.suffix.lower() not in ALLOWED_EXTENSIONS and path.name not in ALLOWED_SPECIAL_NAMES:
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


def structure_issues(root: Path, paths: list[str]) -> list[str]:
    issues = []
    for relative in REQUIRED_FILES:
        if relative not in paths or not (root / relative).is_file():
            issues.append(f"required file missing from publication set: {relative}")
    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            issues.append(f"required directory missing: {relative}")
    return issues


def completeness_issues(texts: dict[str, str]) -> list[str]:
    issues: list[str] = []
    assignment = texts.get("docs/PROJECT-ASSIGNMENT.md", "")
    titles = {match[2] for match in HEADING.finditer(strip_fences(assignment)[0])}
    for title in ASSIGNMENT_HEADINGS:
        if title not in titles:
            issues.append(f"assignment missing required section: {title}")
    required_ids = {f"R{number:02d}" for number in range(1, 17)}
    assignment_ids = re.findall(r"^\|\s*(R\d{2})\s*\|", assignment, re.M)
    if set(assignment_ids) != required_ids or len(assignment_ids) != 16:
        issues.append("assignment must declare R01–R16 exactly once")
    rubric = assignment.partition("## 100-point evaluation rubric")[2].split("\n## ", 1)[0]
    scores = re.findall(r"^\|[^|]+\|\s*(\d+)\s*\|", rubric, re.M)
    if not scores or sum(map(int, scores)) != 100:
        issues.append("assignment rubric must total exactly 100 points")
    guide = texts.get("docs/LAB-IMPLEMENTATION-GUIDE.md", "")
    sections = re.split(r"^## Stage ([A-L])[^\n]*\n", guide, flags=re.M)
    stage_parts = iter(sections[1:])
    stages = list(zip(stage_parts, stage_parts))
    if [letter for letter, _ in stages] != list("ABCDEFGHIJKL"):
        issues.append("guide must contain stages A–L exactly once in order")
    for letter, section in stages:
        for field in STAGE_FIELDS:
            if not re.search(rf"^### {re.escape(field)}\s*$", section, re.M):
                issues.append(f"stage {letter} missing field: {field}")
    plan = texts.get("docs/TEST-PLAN.md", "")
    test_ids = re.findall(r"^### (T\d{2})\b", plan, re.M)
    if test_ids != [f"T{number:02d}" for number in range(21)]:
        issues.append("test plan must declare T00–T20 exactly once in order")
    coverage = plan.partition("## Coverage index")[2]
    covered = re.findall(r"^\|\s*(R\d{2})\s*\|\s*([^|]+)\|", coverage, re.M)
    if {rid for rid, _ in covered} != required_ids or len(covered) != 16:
        issues.append("test coverage index must map every requirement exactly once")
    for rid, tests in covered:
        referenced = re.findall(r"\bT\d{2}\b", tests)
        if not referenced or not set(referenced).issubset(set(test_ids)):
            issues.append(f"{rid}: invalid or missing primary test mapping")
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


def main() -> int:
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
    if issues:
        print(f"FAIL: {len(issues)} finding(s)")
        for issue in sorted(set(issues)):
            print(f"- {issue}")
        return 1
    markdown_count = sum(path.endswith(".md") for path in paths)
    print(f"PASS: {len(paths)} public candidate files; {markdown_count} Markdown files.")
    print("PASS: structure, local links/anchors, stage fields, R01–R16/T00–T20 coverage, rubric, workflow, focused publication scan.")
    print("LIMITS: manual content/history/metadata review required; no external-link or operational-security verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
