#!/usr/bin/env python3
"""Build deterministic public PDF editions from reviewed Markdown sources.

No network, lab access, shell execution, or external rendering service is used.
Install requirements-docs.txt in a documentation environment; see the build guide.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.metadata
import io
import json
import math
from pathlib import Path
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEPENDENCIES = ROOT / "local" / "pdf-deps"
if LOCAL_DEPENDENCIES.is_dir():
    sys.path.insert(0, str(LOCAL_DEPENDENCIES))

import mistune
import reportlab
from pypdf import PdfReader, PdfWriter
from pygments import lex
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.token import Comment, Keyword, Name, Number, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, LongTable, PageBreak, PageTemplate,
    Paragraph, Spacer, TableStyle, XPreformatted, KeepTogether, Table,
)
from reportlab.platypus.tableofcontents import TableOfContents

MANIFEST = "docs/documentation-manifest.json"
ALIASES = {
    "docs/DECISIONS.md": "docs/governance/DECISIONS.md",
    "docs/RISKS.md": "docs/governance/RISKS.md",
    "docs/docs/DECISIONS.md": "docs/governance/DECISIONS.md",
    "docs/docs/RISKS.md": "docs/governance/RISKS.md",
    "docs/docs/README.md": "docs/README.md",
    "docs/docs/final-report/FINAL-REPORT.md": "docs/final-report/FINAL-REPORT.md",
    "docs/docs/documentation-manifest.json": "docs/documentation-manifest.json",
    "docs/evidence/BOOTSTRAP-VALIDATION.md": "evidence/BOOTSTRAP-VALIDATION.md",
}
REPORT_PREFIXES = ("docs/reports/", "reports/")
ASSIGNMENT = "docs/assignments/PROJECT-ASSIGNMENT.md"
GUIDE = "docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md"
PREPARED_REFERENCE = "docs/lab-guides/reference/01-Prepared-Infrastructure.md"
WINDOWS_REFERENCE = "docs/lab-guides/reference/02-Windows-Directory-and-Policy.md"
LINUX_REFERENCE = "docs/lab-guides/reference/03-Linux-Network-and-Host-Policy.md"
HTTPS_REFERENCE = "docs/lab-guides/reference/04-HTTPS-and-Application-Roles.md"
TAILSCALE_REFERENCE = "docs/lab-guides/reference/05-Tailscale-Policy.md"
ACCESS_REFERENCES = {HTTPS_REFERENCE, TAILSCALE_REFERENCE}
MONITORING_REFERENCE = "docs/lab-guides/reference/06-Logs-Automation-and-Test-Tools.md"
RECOVERY_REFERENCE = "docs/lab-guides/reference/07-Backup-and-Recovery.md"
OPERATIONS_REFERENCES = {MONITORING_REFERENCE, RECOVERY_REFERENCE}
TECHNICAL_REFERENCES = {PREPARED_REFERENCE, WINDOWS_REFERENCE, LINUX_REFERENCE} | ACCESS_REFERENCES | OPERATIONS_REFERENCES
ARCHITECTURE = "docs/architecture/ARCHITECTURE.md"
SECURITY = "docs/security/SECURITY-REQUIREMENTS.md"
TEST_PLAN = "docs/testing/TEST-PLAN.md"
PACKAGES = ("reportlab", "pypdf", "mistune", "Pygments", "pillow", "charset-normalizer")
REPOSITORY = "https://github.com/waqashamdani-ca/enterprise-zero-trust-security"
WIDTH, HEIGHT = letter
MARGIN = 54
CONTENT_WIDTH = WIDTH - 2 * MARGIN
MARKDOWN = mistune.create_markdown(renderer="ast", plugins=["table"])
TYPOGRAPHY = str.maketrans({
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u00a0": " ", "\u2192": "->", "\u2190": "<-", "\u2194": "<->",
})


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return text.translate(TYPOGRAPHY)


def discover_sources(root: Path = ROOT) -> list[str]:
    sources = []
    # Respect Git ignore rules: private/local notes must never become an
    # automatic documentation source simply because they end with .md.
    inventory = subprocess.check_output(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    for name in sorted(set(inventory.decode("utf-8").split("\0")) - {""}):
        if not name.endswith(".md") or name.lower().startswith(REPORT_PREFIXES):
            continue
        path = root / name
        if not path.is_file():
            continue  # A staged deletion is not a current source.
        relative = path.relative_to(root)
        if any(part in {".git", "local", "tmp", "node_modules", ".venv", ".venv-docs"} for part in relative.parts):
            continue
        name = relative.as_posix()
        if name not in ALIASES:
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Unsafe documentation source path")
            sources.append(name)
    return sorted(sources)


def register_fonts() -> None:
    if "Vera" in pdfmetrics.getRegisteredFontNames():
        return
    font_dir = Path(reportlab.__file__).parent / "fonts"
    for name, filename in (("Vera", "Vera.ttf"), ("Vera-Bold", "VeraBd.ttf"),
                           ("Vera-Italic", "VeraIt.ttf"), ("Vera-BoldItalic", "VeraBI.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily("Vera", normal="Vera", bold="Vera-Bold", italic="Vera-Italic", boldItalic="Vera-BoldItalic")


def toolchain() -> dict[str, str]:
    return {package: importlib.metadata.version(package) for package in PACKAGES}


def renderer_fingerprint() -> str:
    font_dir = Path(reportlab.__file__).parent / "fonts"
    data = Path(__file__).read_bytes() + json.dumps(toolchain(), sort_keys=True).encode()
    for name in ("Vera.ttf", "VeraBd.ttf", "VeraBI.ttf", "VeraIt.ttf"):
        data += (font_dir / name).read_bytes()
    return digest(data)


def plain(tokens: list[dict]) -> str:
    return "".join(token.get("raw", "") if "children" not in token else plain(token["children"]) for token in tokens)


def anchor_for(title: str, used: set[str]) -> str:
    base = re.sub(r"[^\w -]", "", title.lower().replace("`", "")).replace(" ", "-")
    anchor, index = base, 0
    while anchor in used:
        index += 1
        anchor = f"{base}-{index}"
    used.add(anchor)
    return anchor


def resolve_link(source: str, target: str, sources: set[str]) -> str:
    parsed = urlsplit(target)
    if parsed.scheme:
        if parsed.scheme != "https":
            raise ValueError("Unsupported public PDF link scheme")
        return target
    if parsed.netloc or parsed.query:
        raise ValueError("Invalid relative PDF link")
    name = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path))) if parsed.path else source
    if name.startswith("../") or name.startswith("/"):
        raise ValueError("PDF link escapes repository")
    name = ALIASES.get(name, name)
    if name == source and parsed.fragment:
        return "#" + unquote(parsed.fragment)
    markdown_report = name.lower().startswith(REPORT_PREFIXES) and name.endswith(".md")
    if name.endswith(".md") and not markdown_report:
        if name not in sources:
            raise ValueError(f"Unknown PDF source link from {source}: {name}")
        name = name[:-3] + ".pdf"
    url = REPOSITORY + "/blob/main/" + name
    fragment_prefix = "#" if markdown_report else "#nameddest="
    return url + (fragment_prefix + parsed.fragment if parsed.fragment else "")


def inline(tokens: list[dict], source: str, sources: set[str]) -> str:
    result = []
    for token in tokens:
        kind = token["type"]
        child = inline(token.get("children", []), source, sources)
        raw = html.escape(normalize(token.get("raw", "")))
        if kind == "text":
            result.append(raw)
        elif kind == "strong":
            result.append("<b>" + child + "</b>")
        elif kind == "emphasis":
            result.append("<i>" + child + "</i>")
        elif kind == "codespan":
            result.append('<font name="Courier" size="8.2">' + raw + "</font>")
        elif kind == "link":
            url = html.escape(resolve_link(source, token["attrs"]["url"], sources), quote=True)
            result.append(f'<a href="{url}" color="#164b73">{child}</a>')
        elif kind in {"softbreak", "linebreak"}:
            result.append(" " if kind == "softbreak" else "<br/>")
        elif kind == "inline_html":
            if not token.get("raw", "").startswith("<!--"):
                raise ValueError("Unreviewed inline HTML in Markdown")
        elif kind == "image":
            raise ValueError("Images require an explicitly reviewed asset renderer")
        else:
            result.append(child or raw)
    return "".join(result)


def parse_diagram(raw: str) -> tuple[dict[str, str], list[tuple[str, str, str, bool]], dict]:
    nodes, edges, boundaries = {}, [], {}
    current = None
    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "flowchart TB":
            continue
        node = re.fullmatch(r"(\w+)\[([^]]+)\]", line)
        boundary = re.fullmatch(r"subgraph (\w+)\[([^]]+)\]", line)
        edge = re.fullmatch(r"(\w+)\s+-->\s+(\w+)", line)
        dotted = re.fullmatch(r"(\w+)\s+-\.\s*(.*?)\s*\.->\s+(\w+)", line)
        if boundary:
            if current or boundary[1] in boundaries:
                raise ValueError("Unsupported Mermaid boundary nesting/duplication")
            current = boundary[1]
            boundaries[current] = (boundary[2], [])
        elif line == "end":
            if current is None:
                raise ValueError("Unsupported Mermaid boundary ending")
            current = None
        elif node:
            if node[1] in nodes:
                raise ValueError("Duplicate Mermaid node")
            nodes[node[1]] = node[2]
            if current:
                boundaries[current][1].append(node[1])
        elif edge:
            edges.append((edge[1], edge[2], "", False))
        elif dotted:
            edges.append((dotted[1], dotted[3], dotted[2], True))
        else:
            raise ValueError("Unsupported Mermaid syntax; review before publication")
    if current:
        raise ValueError("Unclosed Mermaid boundary")
    if set(nodes) != {"Admin", "Mgmt", "FW", "Switch", "Host", "Corp", "App", "Remote", "WAN", "HOME"}:
        raise ValueError("Architecture nodes changed; review the vector layout")
    expected = {"Management": ("Management boundary", ["Admin", "Mgmt"]),
                "Corporate": ("Corporate boundary", ["Corp"]),
                "Restricted": ("Restricted boundary", ["App"])}
    if boundaries != expected:
        raise ValueError("Architecture boundaries changed; review the vector layout")
    if any(a not in nodes or b not in nodes for a, b, _, _ in edges):
        raise ValueError("Mermaid edge references an undefined node")
    return nodes, edges, boundaries


class ArchitectureFigure(Flowable):
    def __init__(self, raw: str):
        super().__init__()
        self.nodes, self.edges, self.boundaries = parse_diagram(raw)
        self.width, self.height = CONTENT_WIDTH, 530

    def draw(self):
        canvas = self.canv
        layout = {
            "WAN": (252, 522, 300, 38), "FW": (252, 456, 300, 38),
            "Switch": (252, 390, 300, 38), "Host": (252, 324, 300, 38),
            "Corp": (119, 236, 210, 50), "App": (385, 236, 210, 50),
            "Mgmt": (119, 127, 210, 42), "Admin": (119, 64, 210, 34),
            "Remote": (385, 128, 210, 40), "HOME": (385, 54, 210, 40),
        }
        routes = {
            ("Remote", "App"): [(385, 148), (385, 211)],
            ("Host", "Corp"): [(252, 305), (252, 236), (224, 236)],
            ("Host", "App"): [(252, 305), (252, 236), (280, 236)],
            ("Admin", "Mgmt"): [(119, 81), (119, 106)],
            ("Mgmt", "FW"): [(14, 134), (2, 134), (2, 456), (102, 456)],
            ("Mgmt", "Host"): [(14, 120), (7, 120), (7, 324), (102, 324)],
        }
        labels = {
            ("Remote", "App"): (396, 170, 96),
            ("Mgmt", "FW"): (14, 416, 82),
            ("Mgmt", "Host"): (14, 294, 82),
            ("WAN", "FW"): (264, 482, 205),
        }
        canvas.saveState()
        canvas.translate(0, -18)
        frames = {"Management": (12, 34, 214, 130), "Corporate": (12, 199, 214, 88),
                  "Restricted": (278, 199, 214, 88)}
        for key, (label, _) in self.boundaries.items():
            x, y, width, height = frames[key]
            canvas.setFillColor(colors.HexColor("#f7f9fb"))
            canvas.setStrokeColor(colors.HexColor("#183b56"))
            canvas.roundRect(x, y, width, height, 5, stroke=1, fill=1)
            canvas.setFillColor(colors.HexColor("#183b56"))
            canvas.setFont("Vera-Bold", 8.5)
            canvas.drawString(x + 9, y + height - 12, label)
        for start, end, label, dotted in self.edges:
            x1, y1, _, h1 = layout[start]
            x2, y2, _, h2 = layout[end]
            points = routes.get((start, end), [(x1, y1 - h1 / 2), (x2, y2 + h2 / 2)])
            canvas.setStrokeColor(colors.HexColor("#56758c"))
            canvas.setLineWidth(0.9)
            canvas.setDash(3, 3) if dotted else canvas.setDash()
            for a, b in zip(points, points[1:]):
                canvas.line(*a, *b)
            a, b = points[-2:]
            angle = math.atan2(b[1] - a[1], b[0] - a[0])
            arrow = canvas.beginPath()
            arrow.moveTo(*b)
            for offset in (2.65, -2.65):
                arrow.lineTo(b[0] + 5 * math.cos(angle + offset), b[1] + 5 * math.sin(angle + offset))
            arrow.close()
            canvas.setFillColor(colors.HexColor("#56758c"))
            canvas.drawPath(arrow, fill=1, stroke=0)
            if label:
                if (start, end) not in labels:
                    raise ValueError("Diagram label route needs review")
                px, py, width = labels[start, end]
                style = ParagraphStyle("edge", fontName="Vera", fontSize=7.6, leading=9.4,
                                       textColor=colors.HexColor("#40576a"))
                paragraph = Paragraph(html.escape(normalize(label)), style)
                _, height = paragraph.wrap(width, 40)
                paragraph.drawOn(canvas, px, py)
        canvas.setDash()
        for node, label in self.nodes.items():
            x, y, width, height = layout[node]
            canvas.setStrokeColor(colors.HexColor("#718391"))
            canvas.setFillColor(colors.HexColor("#eef3f7" if node != "HOME" else "#f1f1f1"))
            canvas.roundRect(x - width / 2, y - height / 2, width, height, 4, stroke=1, fill=1)
            style = ParagraphStyle("node", fontName="Vera", fontSize=8.8, leading=10.5, alignment=TA_CENTER)
            paragraph = Paragraph(html.escape(normalize(label)), style)
            _, ph = paragraph.wrap(width - 12, height - 8)
            if ph > height - 8:
                raise ValueError("Diagram label does not fit")
            paragraph.drawOn(canvas, x - width / 2 + 6, y - ph / 2)
        canvas.restoreState()


class Document(BaseDocTemplate):
    def __init__(self, stream, title: str, source: str, source_hash: str):
        super().__init__(stream, pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=64, bottomMargin=51, title=normalize(title),
                         author="HL-CYB-001 project", creator="HL-CYB-001 documentation builder",
                         subject=f"Source: {source}; SHA-256: {source_hash}",
                         invariant=1, pageCompression=1, allowSplitting=1)
        self.document_title, self.source_hash = normalize(title), source_hash
        self.is_assignment = source == ASSIGNMENT
        self.is_guide = source == GUIDE
        self.destinations = {}
        frame = Frame(MARGIN, 51, CONTENT_WIDTH, HEIGHT - 115, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="standard", frames=[frame], onPage=self.page_furniture))

    def page_furniture(self, canvas, document):
        canvas.saveState()
        canvas.setFont("Vera", 7.8)
        canvas.setFillColor(colors.HexColor("#475c6c"))
        if self.is_assignment:
            canvas.drawString(MARGIN, HEIGHT - 32, "HL-CYB-001 | Practical assignment")
            canvas.drawRightString(WIDTH - MARGIN, HEIGHT - 32, "Four-week lab")
        elif self.is_guide:
            canvas.drawString(MARGIN, HEIGHT - 32, "HL-CYB-001 | Lab implementation guide")
            canvas.drawRightString(WIDTH - MARGIN, HEIGHT - 32, "Four-week lab")
        else:
            canvas.drawString(MARGIN, HEIGHT - 29, "HL-CYB-001 | Enterprise Zero Trust Security Architecture")
            title = self.document_title
            while pdfmetrics.stringWidth(title, "Vera", 7.8) > CONTENT_WIDTH and len(title) > 5:
                title = title[:-2]
            canvas.drawString(MARGIN, HEIGHT - 41, title)
        canvas.setStrokeColor(colors.HexColor("#d9e0e5"))
        canvas.line(MARGIN, HEIGHT - 48, WIDTH - MARGIN, HEIGHT - 48)
        canvas.drawString(MARGIN, 27, "Source version " + self.source_hash[:12])
        canvas.drawRightString(WIDTH - MARGIN, 27, f"Page {document.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if hasattr(flowable, "_anchor"):
            self.canv.bookmarkPage(flowable._anchor)
            self.destinations[flowable._anchor] = self.page - 1
            for alias in getattr(flowable, "_aliases", ()):
                self.canv.bookmarkPage(alias)
                self.destinations[alias] = self.page - 1
            self.canv.addOutlineEntry(flowable.getPlainText(), flowable._anchor, flowable._level - 1, closed=flowable._level > 2)
            if flowable._level == 2:
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page, flowable._anchor))


class Builder:
    def __init__(self, source: str, sources: set[str]):
        register_fonts()
        self.source, self.sources = source, sources
        self.anchors: set[str] = set()
        self.pending_anchors: list[str] = []
        self.counters = [0] * 6
        self.table_count, self.figure_count = 0, 0
        self.section_title = "Document"
        self.style = ParagraphStyle("body", fontName="Vera", fontSize=9.3, leading=13.2, spaceAfter=7)
        self.cell_style = ParagraphStyle("cell", parent=self.style, fontSize=8.25, leading=10.8, spaceAfter=0)
        if source == ASSIGNMENT:
            self.style = ParagraphStyle("assignment-body", parent=self.style, fontSize=10, leading=13.4, spaceAfter=6)
            self.cell_style = ParagraphStyle("assignment-cell", parent=self.style, fontSize=9.0, leading=11.8, spaceAfter=0)
        elif source == GUIDE:
            self.style = ParagraphStyle("guide-body", parent=self.style, fontSize=10, leading=13.7, spaceAfter=6,
                                        allowWidows=0, allowOrphans=0)
            self.cell_style = ParagraphStyle("guide-cell", parent=self.style, fontSize=8.9, leading=11.7, spaceAfter=0)
        elif source == ARCHITECTURE:
            self.style = ParagraphStyle("architecture-body", parent=self.style, allowWidows=0, allowOrphans=0)
        self.code_style = ParagraphStyle("code", fontName="Courier", fontSize=7.9, leading=10.2,
                                        backColor=colors.HexColor("#f5f7f8"), borderColor=colors.HexColor("#d7dfe4"),
                                        borderWidth=0.4, borderPadding=6, leftIndent=7, rightIndent=7, spaceAfter=11)
        if source == GUIDE:
            self.code_style = ParagraphStyle("guide-code", parent=self.code_style, fontSize=8.8, leading=11.5)

    def heading(self, token: dict, cover: bool = False) -> Paragraph:
        level = token["attrs"]["level"]
        title = plain(token["children"])
        anchor = anchor_for(title, self.anchors)
        if level == 1:
            label = inline(token["children"], self.source, self.sources)
        else:
            self.counters[level - 2] += 1
            for index in range(level - 1, 6):
                self.counters[index] = 0
            label = ".".join(str(n) for n in self.counters[:level - 1]) + ". " + inline(token["children"], self.source, self.sources)
        sizes = {1: 24 if cover else 18, 2: 13.1, 3: 10.6, 4: 10, 5: 9.5, 6: 9.3}
        if self.source == ASSIGNMENT:
            sizes.update({1: 21, 2: 12.8})
        elif self.source == GUIDE:
            sizes.update({1: 20, 2: 13, 3: 10.6})
            if level >= 2:
                label = inline(token["children"], self.source, self.sources)
        style = ParagraphStyle("heading", parent=self.style, fontName="Vera-Bold", fontSize=sizes[level], leading=sizes[level] * 1.3,
                               textColor=colors.HexColor("#193e58"), spaceBefore=12 if level > 1 else 0,
                               spaceAfter=7, keepWithNext=1)
        paragraph = Paragraph(label, style)
        paragraph._anchor, paragraph._level = anchor, level
        paragraph._aliases = tuple(self.pending_anchors)
        self.pending_anchors.clear()
        if level == 2:
            self.section_title = normalize(title)
        return paragraph

    def code(self, raw: str, language: str) -> XPreformatted:
        try:
            lexer = get_lexer_by_name(language or "text")
        except Exception:
            lexer = TextLexer()
        lines, line = [], []
        def finish():
            nonlocal line
            limit = 88 if self.source == GUIDE else 98
            while len(line) > limit:
                split = max((i + 1 for i, (char, _) in enumerate(line[:limit]) if char == " "), default=limit)
                lines.append(line[:split])
                line = line[split:]
            lines.append(line)
            line = []
        for token, value in lex(normalize(raw).expandtabs(4), lexer):
            color = "#263746"
            for parent, tone in ((Comment, "#5d766b"), (Keyword, "#164b86"), (String, "#8d3f22"), (Number, "#76518a"), (Name.Function, "#205c6a")):
                if token in parent:
                    color = tone
                    break
            for char in value:
                if char == "\n":
                    finish()
                else:
                    line.append((char, color))
        if line:
            finish()
        markup = []
        for line in lines:
            segments, previous, text = [], None, ""
            for char, color in line:
                if color != previous and text:
                    segments.append(f'<font color="{previous}">{html.escape(text)}</font>')
                    text = ""
                previous = color
                text += char
            if text:
                segments.append(f'<font color="{previous}">{html.escape(text)}</font>')
            markup.append("".join(segments))
        return XPreformatted("\n".join(markup), self.code_style)

    def table(self, token: dict) -> list:
        head = token["children"][0]["children"]
        rows = [head] + [row["children"] for row in token["children"][1]["children"]]
        headers = [plain(cell["children"]) for cell in head]
        count = len(headers)
        if self.source == ARCHITECTURE and headers == ["Component", "Role and boundary"]:
            widths = [144, 360]
        elif self.source == ARCHITECTURE and headers == ["Zone", "Members and enforcement"]:
            widths = [105, 399]
        elif self.source == ARCHITECTURE and headers == ["Flow", "Source to destination", "Permission and enforcement owner"]:
            widths = [55, 150, 299]
        elif self.source == SECURITY and headers[0] == "Security ID":
            widths = [62, 349, 93]
        elif self.source == SECURITY and headers[0] == "Threat":
            widths = [126, 230, 148]
        elif self.source == TEST_PLAN and headers == ["Requirement", "Architecture component / flow",
                                                       "Security control", "Test", "Acceptance", "File"]:
            widths = [74, 192, 64, 50, 66, 58]
        elif self.source == ASSIGNMENT and headers == ["ID", "Required result", "Test"]:
            widths = [55, 389, 60]
        elif self.source == ASSIGNMENT and headers == ["Filename", "What to record"]:
            widths = [300, 204]
        elif self.source == ASSIGNMENT and headers == ["Week", "Phase and activities", "Checkpoint"]:
            widths = [48, 272, 184]
        elif self.source == ASSIGNMENT and headers[1] == "Points":
            widths = [194, 52, 258]
        elif self.source == GUIDE and headers == ["Filename", "Owning record"]:
            widths = [300, 204]
        elif self.source == GUIDE and headers == ["Phase", "Separate stage approvals", "Week"]:
            widths = [210, 254, 40]
        elif self.source == GUIDE and headers[0] in {"Earlier requirement", "Earlier tests"}:
            widths = [104, 118, 282]
        elif self.source == GUIDE and headers == ["Test / requirement", "What to do and compare"]:
            widths = [110, 394]
        elif self.source == GUIDE and headers == ["Private value", "Where it comes from"]:
            widths = [210, 294]
        elif self.source == GUIDE and headers == ["VM", "Zone / bridge", "vCPU", "RAM MiB", "Disk GiB"]:
            widths = [65, 205, 55, 90, 89]
        elif self.source == GUIDE and headers == ["Case", "App account", "Page", "Expected result"]:
            widths = [45, 75, 105, 279]
        elif self.source == GUIDE and headers == ["Event", "Approved action", "Source and expected observation"]:
            widths = [100, 200, 204]
        elif count == 2:
            widths = [62, 442] if max(len(plain(row[0]["children"])) for row in rows) < 12 else [133, 371]
        elif count == 3:
            widths = [144, 42, 318] if headers[1] == "Points" else ([58, 276, 170] if headers[0] in {"Stage", "Security ID"} else [205, 143, 156])
        elif count == 4:
            if headers[-1] == "Status":
                widths = [145, 140, 163, 56]
            elif headers[0] == "ID":
                widths = [52, 231, 153, 68] if headers[-1] == "Stage" else [52, 200, 137, 115]
            elif headers[:2] == ["Change", "Date"]:
                widths = [52, 70, 190, 192]
            else:
                widths = [117, 153, 139, 95]
        elif count == 5:
            widths = [70, 40, 62, 65, 267] if headers == ["VM", "vCPU", "RAM GiB", "Disk GiB", "Responsibility"] else [137, 66, 94, 141, 66]
        else:
            widths = [CONTENT_WIDTH / count] * count
        cells = []
        for row_number, row in enumerate(rows):
            values = []
            for column, cell in enumerate(row):
                if self.source in {ASSIGNMENT, GUIDE} and headers[0] == "Filename" and row_number and column == 0:
                    filename = plain(cell["children"])
                    style = ParagraphStyle("filename", parent=self.cell_style, splitLongWords=False)
                    if pdfmetrics.stringWidth(filename, style.fontName, style.fontSize) > widths[0] - 10:
                        raise ValueError("Deliverable filename must fit on one line")
                    values.append(Paragraph(html.escape(filename), style))
                else:
                    style = self.cell_style
                    if self.source == ASSIGNMENT and "Points" in headers and column == 1:
                        style = ParagraphStyle("points", parent=style, alignment=TA_RIGHT)
                    values.append(Paragraph(("<b>" if row_number == 0 else "") + inline(cell["children"], self.source, self.sources) + ("</b>" if row_number == 0 else ""), style))
            cells.append(values)
        test_record = self.source == TEST_PLAN and headers == ["Record", "Value"]
        keep_rows = self.source in TECHNICAL_REFERENCES | {
            ASSIGNMENT, GUIDE, ARCHITECTURE, SECURITY, TEST_PLAN, "docs/governance/DECISIONS.md", "docs/governance/RISKS.md",
        }
        table = LongTable(cells, colWidths=widths, repeatRows=1, splitByRow=1, splitInRow=int(not keep_rows),
                          hAlign="LEFT", spaceAfter=8 if test_record else 12)
        vertical_padding = 4 if self.source in {SECURITY, TEST_PLAN} else 5
        if test_record:
            vertical_padding = 2.5
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5edf3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fa")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c5d0d8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), vertical_padding), ("BOTTOMPADDING", (0, 0), (-1, -1), vertical_padding),
        ]))
        if self.source in {ASSIGNMENT, GUIDE}:
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f4")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),

                ("GRID", (0, 0), (-1, -1), 0, colors.white),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#849aa9")),
                ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#d9e0e5")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
        if self.source in {ASSIGNMENT, GUIDE} or test_record:
            if "Points" in headers:
                table.setStyle(TableStyle([("ALIGN", (1, 0), (1, -1), "RIGHT")]))
            table.wrap(CONTENT_WIDTH, HEIGHT)
            return [CondPageBreak(min(640, sum(table._rowHeights[:2]) + 12)), table]
        self.table_count += 1
        caption = Paragraph(f"Table {self.table_count}. {html.escape(self.section_title)}", ParagraphStyle("caption", parent=self.style, fontName="Vera-Italic", fontSize=8.3, leading=11, keepWithNext=0, spaceBefore=3, spaceAfter=4))
        # Keep enough room for caption/header/first row without asking a
        # multi-page table to stay together (which leaves near-empty pages).
        table.wrap(CONTENT_WIDTH, HEIGHT)
        _, caption_height = caption.wrap(CONTENT_WIDTH, HEIGHT)
        first_rows = sum(table._rowHeights[:2])
        return [CondPageBreak(min(640, first_rows + caption_height + 16)), caption, table]

    def blocks(self, tokens: list[dict], depth: int = 0) -> list:
        story = []
        for token_index, token in enumerate(tokens):
            kind = token["type"]
            if kind in {"paragraph", "block_text"}:
                style = self.style if not depth else ParagraphStyle("indented", parent=self.style, leftIndent=depth * 14)
                if self.source == ASSIGNMENT and len(token["children"]) == 1 and token["children"][0]["type"] == "strong":
                    style = ParagraphStyle("assignment-label", parent=style, keepWithNext=1)
                elif self.source == GUIDE and token["children"] and token["children"][0]["type"] == "strong":
                    following = next((t for t in tokens[token_index + 1:] if t["type"] != "blank_line"), {})
                    if following.get("type") == "block_code":
                        style = ParagraphStyle("guide-command-context", parent=style, keepWithNext=1)
                story.append(Paragraph(inline(token["children"], self.source, self.sources), style))
            elif kind == "heading":
                title = plain(token["children"])
                if token["attrs"]["level"] == 2 and (title.startswith(("Stage ", "Phase ")) or title == "Source preservation appendix"):
                    story.append(CondPageBreak(240) if self.source == GUIDE else PageBreak())
                story.append(self.heading(token))
            elif kind == "list":
                ordered = token.get("attrs", {}).get("ordered", False)
                start = token.get("attrs", {}).get("start", 1)
                for index, item in enumerate(token["children"]):
                    children = list(item["children"])
                    prefix = f"{start + index}. " if ordered else "- "
                    first = children.pop(0)
                    if first["type"] not in {"paragraph", "block_text"}:
                        raise ValueError("Unsupported list structure")
                    style = ParagraphStyle("list", parent=self.style, leftIndent=12 + 14 * depth, firstLineIndent=-10)
                    if self.source == ASSIGNMENT:
                        style.spaceAfter = 4
                        style.keepWithNext = index < len(token["children"]) - 1
                    elif self.source == GUIDE:
                        style.spaceAfter = 4
                    paragraph = Paragraph(prefix + inline(first["children"], self.source, self.sources), style)
                    following = self.blocks(children, depth + 1)
                    if (self.source == GUIDE and ordered) or self.source in {WINDOWS_REFERENCE, LINUX_REFERENCE} | ACCESS_REFERENCES | OPERATIONS_REFERENCES:
                        story.append(KeepTogether([paragraph, *following]))
                    else:
                        story.append(paragraph)
                        story.extend(following)
            elif kind == "table":
                table_parts = self.table(token)
                if story and hasattr(story[-1], "_anchor"):
                    heading = story.pop()
                    _, height = heading.wrap(CONTENT_WIDTH, HEIGHT)
                    needed = min(660, table_parts[0].height + height + heading.getSpaceBefore() + heading.getSpaceAfter())
                    story.extend([CondPageBreak(needed), heading, *table_parts[1:]])
                else:
                    story.extend(table_parts)
            elif kind == "block_code":
                language = token.get("attrs", {}).get("info", "").split(" ", 1)[0]
                if language == "mermaid":
                    self.figure_count += 1
                    story.append(ArchitectureFigure(token["raw"]))
                    story.append(Paragraph(f"Figure {self.figure_count}. Target physical and logical architecture; lines do not grant access.", ParagraphStyle("figure-caption", parent=self.style, fontName="Vera-Italic", fontSize=8.3)))
                else:
                    code = self.code(token["raw"], language)
                    if self.source == GUIDE:
                        context = []
                        if story and isinstance(story[-1], Paragraph) and story[-1].style.name == "guide-command-context":
                            context.append(story.pop())
                            context[0].keepWithNext = 0
                        story.append(KeepTogether([*context, code]))
                    else:
                        story.append(code)
            elif kind == "block_quote":
                story.extend(self.blocks(token["children"], depth + 1))
            elif kind in {"blank_line", "thematic_break"}:
                continue
            elif kind == "block_html" and self.source in {ASSIGNMENT, ARCHITECTURE, GUIDE, MONITORING_REFERENCE} and re.fullmatch(
                    r'(?:<a id="[a-z][a-z0-9-]*"></a>\s*)+', token.get("raw", "").strip()):
                self.pending_anchors.extend(re.findall(r'<a id="([a-z][a-z0-9-]*)"></a>', token["raw"]))
            elif kind == "block_html" and token.get("raw", "").lstrip().startswith("<!--"):
                continue
            else:
                raise ValueError(f"Unsupported Markdown block: {kind}")
        return story


class PreparedInfrastructureBuilder(Builder):
    """Accepted sample style for the guide and its technical references."""

    def __init__(self, source: str, sources: set[str]):
        super().__init__(source, sources)
        self.identity_phase = False
        self.compact_guide = False
        self.monitoring_phase = False
        self.style = ParagraphStyle("prepared-body", fontName="Vera", fontSize=10.5, leading=13.8,
                                    spaceAfter=5, allowWidows=0, allowOrphans=0,
                                    textColor=colors.HexColor("#28333e"))
        self.cell_style = ParagraphStyle("prepared-cell", parent=self.style, fontSize=9.5, leading=12.5,
                                         spaceAfter=0)

    def heading(self, token: dict, cover: bool = False) -> Paragraph:
        level = token["attrs"]["level"]
        title = plain(token["children"])
        size = {1: 21, 2: 13, 3: 11.2}.get(level, 10.5)
        style = ParagraphStyle("prepared-heading", parent=self.style, fontName="Vera-Bold",
                               fontSize=size, leading=size * 1.23, spaceBefore=8 if level > 1 else 0,
                               spaceAfter=6, keepWithNext=1, textColor=colors.HexColor("#16364f"))
        if self.source == GUIDE and self.compact_guide and level == 3:
            style.spaceBefore, style.spaceAfter = 6, 4
        paragraph = Paragraph(inline(token["children"], self.source, self.sources), style)
        paragraph._anchor, paragraph._level = anchor_for(title, self.anchors), level
        paragraph._aliases = tuple(self.pending_anchors)
        self.pending_anchors.clear()
        if level == 2:
            self.section_title = normalize(title)
        return paragraph

    def result_panel(self, label: str, token: dict) -> Table:
        label_style = ParagraphStyle("prepared-result-label", parent=self.style, fontName="Vera-Bold",
                                     fontSize=9.2, leading=12, spaceAfter=0,
                                     textColor=colors.HexColor("#16364f"))
        body_style = ParagraphStyle("prepared-result", parent=self.style, spaceAfter=0)
        compact = self.identity_phase or self.compact_guide
        panel = Table([[Paragraph(label, label_style),
                        Paragraph(inline(token["children"], self.source, self.sources), body_style)]],
                      colWidths=[65, CONTENT_WIDTH - 65], hAlign="LEFT",
                      spaceBefore=3 if compact else 5,
                      spaceAfter=4 if compact else 6)
        panel.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f3f5")),
            ("LINEBEFORE", (0, 0), (0, -1), 1.4, colors.HexColor("#16364f")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4 if compact else 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4 if compact else 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return panel

    def table(self, token: dict) -> list:
        if self.source == GUIDE and self.compact_guide:
            headers = tuple(plain(cell["children"]) for cell in token["children"][0]["children"])
            widths = {
                ("Case", "Account", "Page", "Expected HTTP result"): [44, 62, 142, 256],
                ("Event", "Action and matching source"): [180, 324],
                ("Test / requirement", "Purpose and main evidence"): [99, 405],
                ("Filename", "What to complete", "Main evidence source"): [240, 172, 92],
            }.get(headers)
            if widths:
                rows = [token["children"][0]["children"]] + [row["children"] for row in token["children"][1]["children"]]
                cells = [[Paragraph(("<b>" if n == 0 else "") + inline(cell["children"], self.source, self.sources)
                                    + ("</b>" if n == 0 else ""), self.cell_style) for cell in row]
                         for n, row in enumerate(rows)]
                table = Table(cells, colWidths=widths, hAlign="LEFT", spaceAfter=5)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f4")),
                    ("LINEBELOW", (0, 0), (-1, 0), .7, colors.HexColor("#849aa9")),
                    ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#d9e0e5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]))
                return [table]
        if self.source not in TECHNICAL_REFERENCES:
            return super().table(token)
        head = token["children"][0]["children"]
        if len(head) != 2:
            return super().table(token)
        rows = [head] + [row["children"] for row in token["children"][1]["children"]]
        widths = [CONTENT_WIDTH * .28, CONTENT_WIDTH * .72]
        cells = [[Paragraph(("<b>" if n == 0 else "") + inline(cell["children"], self.source, self.sources)
                             + ("</b>" if n == 0 else ""), self.cell_style) for cell in row]
                 for n, row in enumerate(rows)]
        table = LongTable(cells, colWidths=widths, repeatRows=1, splitByRow=1, splitInRow=0,
                          hAlign="LEFT", spaceAfter=9)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f4")),
            ("LINEBELOW", (0, 0), (-1, 0), .7, colors.HexColor("#8191a1")),
            ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#d9dfe5")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        table.wrap(CONTENT_WIDTH, HEIGHT)
        return [CondPageBreak(sum(table._rowHeights[:2]) + 12), table]

    def blocks(self, tokens: list[dict], depth: int = 0, keep_procedures: bool = True) -> list:
        phase = next((plain(t["children"]) for t in tokens if t["type"] == "heading"
                      and plain(t["children"]).startswith("Phase ")), "")
        if self.source == GUIDE and phase:
            self.identity_phase = phase.startswith("Phase 2:")
            self.monitoring_phase = phase.startswith("Phase 4:")
            self.compact_guide = phase.startswith(("Phase 3:", "Phase 4:", "Phase 5:"))
        tokens = [t for t in tokens if t["type"] != "blank_line"]
        story, i = [], 0
        while i < len(tokens):
            token = tokens[i]
            if (keep_procedures and self.source == PREPARED_REFERENCE and token["type"] == "heading"
                    and plain(token["children"]) == "Approved active checks"):
                end = next((n for n in range(i + 1, len(tokens)) if tokens[n]["type"] == "heading"
                            and tokens[n]["attrs"]["level"] <= 2), len(tokens))
                story.append(KeepTogether(self.blocks(tokens[i:end], depth, keep_procedures=False)))
                i = end
                continue
            if (keep_procedures and token["type"] == "heading" and token["attrs"]["level"] == 3
                    and re.match(r"[A-E]\. ", plain(token["children"]))):
                end = next((n for n in range(i + 1, len(tokens)) if tokens[n]["type"] == "heading"
                            and tokens[n]["attrs"]["level"] <= 3), len(tokens))
                # The phase checkpoint follows the procedure's RECORD panel;
                # it is not part of the procedure that must remain intact.
                if self.source == GUIDE and (plain(token["children"]).startswith("E. ")
                                            or self.monitoring_phase and plain(token["children"]).startswith("D. ")):
                    end = next((n for n in range(i + 1, end) if tokens[n]["type"] == "paragraph"
                                and plain(tokens[n]["children"]).startswith(("Before Phase 3:", "Before Phase 4:", "Before Phase 5:"))), end)
                parts = self.blocks(tokens[i:end], depth, keep_procedures=False)
                # Ordered actions already have their own KeepTogether. Flatten
                # them before wrapping the whole short procedure: nested
                # KeepTogether reports a sentinel height and forces page breaks.
                parts = [child for part in parts for child in
                         (part._content if isinstance(part, KeepTogether) else [part])]
                story.append(KeepTogether(parts))
                i = end
                continue
            if token["type"] == "paragraph":
                label = plain(token["children"]).strip()
                if (self.source in TECHNICAL_REFERENCES and i + 1 < len(tokens)
                        and tokens[i + 1]["type"] == "block_code"):
                    context = []
                    if story and hasattr(story[-1], "_anchor"):
                        context.append(story.pop())
                        context[0].keepWithNext = 0
                    story.append(KeepTogether([*context, *super().blocks(tokens[i:i + 2], depth)]))
                    i += 2
                    continue
                if label in {"CHECK", "RECORD"}:
                    if i + 1 >= len(tokens) or tokens[i + 1]["type"] != "paragraph":
                        raise ValueError("CHECK/RECORD must introduce an intact result paragraph")
                    story.append(self.result_panel(label, tokens[i + 1]))
                    i += 2
                    continue
                if label in {"WHERE", "STEPS"}:
                    if self.source == GUIDE and self.compact_guide and label == "WHERE":
                        if i + 1 >= len(tokens) or tokens[i + 1]["type"] != "paragraph":
                            raise ValueError("Compact WHERE must introduce a target paragraph")
                        location = '<b><font color="#16364f">WHERE</font></b>  ' + inline(tokens[i + 1]["children"], self.source, self.sources)
                        story.append(Paragraph(location, self.style))
                        i += 2
                        continue
                    style = ParagraphStyle("prepared-label", parent=self.style, fontName="Vera-Bold",
                                           fontSize=9.5, leading=12, spaceBefore=5, spaceAfter=3,
                                           keepWithNext=1, textColor=colors.HexColor("#16364f"))
                    story.append(Paragraph(label, style))
                    i += 1
                    continue
                if self.source in {WINDOWS_REFERENCE, LINUX_REFERENCE} | ACCESS_REFERENCES | OPERATIONS_REFERENCES:
                    context = []
                    if story and hasattr(story[-1], "_anchor"):
                        context.append(story.pop())
                        context[0].keepWithNext = 0
                    story.append(KeepTogether([*context, *super().blocks([token], depth)]))
                    i += 1
                    continue
            story.extend(super().blocks([token], depth))
            i += 1
        return story


def source_tokens(tokens: list[dict]) -> set[str]:
    chunks = []
    for token in tokens:
        if token["type"] in {"text", "codespan", "block_code"}:
            raw = token.get("raw", "")
            if token.get("attrs", {}).get("info") == "mermaid":
                nodes, edges, boundaries = parse_diagram(raw)
                raw = " ".join([*nodes.values(), *(label for _, _, label, _ in edges),
                                *(label for label, _ in boundaries.values())])
            chunks.append(normalize(raw))
        if "children" in token:
            chunks.extend(source_tokens(token["children"]))
    return set(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", " ".join(chunks).lower()))


def render_pdf(source: str, content: bytes, sources: set[str]) -> bytes:
    if source.lower().startswith(REPORT_PREFIXES):
        raise ValueError("Task reports are Markdown only; docs/reports/ is excluded from PDF generation")
    tokens = MARKDOWN(content.decode("utf-8"))
    if source in {ASSIGNMENT, ARCHITECTURE, GUIDE, MONITORING_REFERENCE}:
        for token in tokens:
            if token["type"] == "paragraph":
                raw = "".join("\n" if c["type"] == "softbreak" else c.get("raw", "")
                              for c in token.get("children", []))
                if re.fullmatch(r'(?:<a id="[a-z][a-z0-9-]*"></a>\s*)+', raw.strip()):
                    token.clear()
                    token.update(type="block_html", raw=raw)
    if not tokens or tokens[0]["type"] != "heading":
        raise ValueError(f"Document must start with a title: {source}")
    title = plain(tokens[0]["children"])
    builder = (PreparedInfrastructureBuilder(source, sources) if source in {GUIDE} | TECHNICAL_REFERENCES
               else Builder(source, sources))
    formal = source.startswith(("docs/assignments/", "docs/lab-guides/", "docs/architecture/", "docs/security/", "docs/testing/", "docs/final-report/"))
    story = []
    compact_sources = {ASSIGNMENT, GUIDE, ARCHITECTURE, SECURITY, TEST_PLAN} | TECHNICAL_REFERENCES
    if source in compact_sources:
        story.append(builder.heading(tokens[0]))
    elif formal:
        cover_status = ""
        if source.startswith(("docs/lab-guides/", "docs/architecture/", "docs/security/")):
            cover_status = "PLANNED - operational controls NOT TESTED"
        elif source.startswith("docs/final-report/"):
            cover_status = "TEMPLATE - no completed implementation results"
        story.extend([Spacer(1, 70), Paragraph("HL-CYB-001", builder.style), Spacer(1, 15), builder.heading(tokens[0], cover=True), Spacer(1, 15), Paragraph("Enterprise Zero Trust Security Architecture", builder.style), Paragraph("Document version " + digest(content)[:12], builder.style)])
        if cover_status:
            story.append(Paragraph(cover_status, builder.style))
        story.append(PageBreak())
    else:
        story.append(builder.heading(tokens[0]))
    if source == ARCHITECTURE:
        first_section = next(i for i, token in enumerate(tokens[1:], 1)
                             if token["type"] == "heading" and token["attrs"]["level"] == 2)
        story.extend(builder.blocks(tokens[1:first_section]))
        story.append(Paragraph("Guide contents" if source == GUIDE else "Contents", ParagraphStyle("guide-contents", parent=builder.style,
                               fontName="Vera-Bold", fontSize=11, leading=14, spaceBefore=6, spaceAfter=5)))
        contents = TableOfContents()
        contents.levelStyles = [ParagraphStyle("guide-toc", fontName="Vera", fontSize=9, leading=12, spaceBefore=0)]
        contents.tableStyle = TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                         ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                         ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                         ("TOPPADDING", (0, 0), (-1, -1), 0),
                                         ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])
        story.extend([contents, Spacer(1, 6)])
        if source == ARCHITECTURE:
            story.append(PageBreak())
        tokens = [tokens[0], *tokens[first_section:]]
    if source not in compact_sources and sum(token["type"] == "heading" and token["attrs"]["level"] == 2 for token in tokens) >= 6 and len(content.split()) >= 900:
        story.append(Paragraph("Contents", ParagraphStyle("contents-title", parent=builder.style, fontName="Vera-Bold", fontSize=17, leading=22, spaceAfter=14)))
        contents = TableOfContents()
        contents.levelStyles = [ParagraphStyle("toc", fontName="Vera", fontSize=9.3, leading=14, spaceBefore=4)]
        story.extend([contents, PageBreak()])
    if source in {ASSIGNMENT, GUIDE, TEST_PLAN}:
        # Keep short submission sections and individual test definitions intact.
        groups, current = [], []
        section_levels = {2, 3} if source == TEST_PLAN else {2}
        for token in tokens[1:]:
            if token["type"] == "heading" and token["attrs"]["level"] in section_levels and current:
                groups.append(current)
                current = []
            current.append(token)
        if current:
            groups.append(current)
        compact_sections = {"Project Requirements", "Required Deliverables",
                            "Four-Week Implementation Plan", "Evaluation Criteria"}
        if source == GUIDE:
            compact_sections = {"Required lab deliverables"}
        elif source == TEST_PLAN:
            compact_sections = {"Six application access cases", "Coverage index"}
        for group in groups:
            section = next((plain(t["children"]) for t in group if t["type"] == "heading"), "")
            blocks = builder.blocks(group)
            keep_test = source == TEST_PLAN and section.startswith("FWT-")
            story.extend([KeepTogether(blocks)] if keep_test or section in compact_sections else blocks)
    else:
        story.extend(builder.blocks(tokens[1:]))
    output = io.BytesIO()
    document = Document(output, title, source, digest(content))
    document.multiBuild(story)
    # Keep true named destinations as well as outlines/GoTo annotations so
    # other PDF editions can address the corresponding Markdown heading.
    reader = PdfReader(io.BytesIO(output.getvalue()))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    for anchor, page in document.destinations.items():
        writer.add_named_destination(anchor, page)
    finalized = io.BytesIO()
    writer.write(finalized)
    return finalized.getvalue()


def inspect_pdf(data: bytes, source: str, content: bytes, sources: set[str] | None = None) -> dict:
    reader = PdfReader(io.BytesIO(data), strict=True)
    if not reader.pages or reader.is_encrypted:
        raise ValueError(f"Invalid/encrypted PDF: {source}")
    all_text = []
    heading_names = {normalize(plain(token["children"])) for token in MARKDOWN(content.decode("utf-8")) if token["type"] == "heading"}
    links, internal = set(), 0
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if not text.strip() or not re.search(rf"Page\s+{number}\b", text):
            raise ValueError(f"Missing searchable text/footer in {source}, page {number}")
        lines = [line.strip() for line in text.splitlines()[2:] if line.strip()]
        lines = [line for line in lines if not re.fullmatch(r"(?:Page \d+|Source version [0-9a-f]{12})", line)]
        if lines and number < len(reader.pages) and not {"Contents", "Assignment contents"}.intersection(lines):
            last = re.sub(r"^\d+(?:\.\d+)*\.\s+", "", normalize(lines[-1]))
            if last in heading_names:
                raise ValueError(f"Orphan heading at page end: {source}, page {number}: {last}")
        all_text.append(normalize(text))
        for ref in page.get("/Annots", []):
            annotation = ref.get_object()
            action = annotation.get("/A", {})
            if action.get("/S") not in {None, "/URI", "/GoTo"} or "/AA" in annotation:
                raise ValueError("Active PDF annotation/action is not permitted")
            if action.get("/S") == "/URI":
                if not str(action["/URI"]).startswith("https://"):
                    raise ValueError("PDF external links must use HTTPS")
                links.add(str(action["/URI"]))
            elif annotation.get("/Dest") or action.get("/S") == "/GoTo":
                internal += 1
    root = reader.trailer["/Root"]
    if any(key in root for key in ("/OpenAction", "/AA")) or "/EmbeddedFiles" in root.get("/Names", {}):
        raise ValueError("Active content/attachments are not permitted in generated PDFs")
    expected = source_tokens(MARKDOWN(content.decode("utf-8")))
    actual = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", " ".join(all_text).lower()))
    # PDF extraction inserts layout line breaks, including inside long paths.
    # Check that a wrapped token's characters are present before calling it lost.
    compact = re.sub(r"\s+", "", " ".join(all_text).lower())
    missing = {token for token in expected - actual if token not in compact}
    coverage = (len(expected) - len(missing)) / max(1, len(expected))
    if coverage < 0.975:
        raise ValueError(f"PDF source text coverage {coverage:.3f} too low: {source}; missing {sorted(missing)[:12]}")
    if not reader.named_destinations:
        raise ValueError(f"Missing named heading navigation: {source}")
    for destination in reader.named_destinations.values():
        page = reader.get_destination_page_number(destination)
        if page is None or not 0 <= page < len(reader.pages):
            raise ValueError(f"Invalid named destination page: {source}")
    expected_links = set()
    def collect_links(tokens):
        for token in tokens:
            if token["type"] == "link":
                expected_links.add(resolve_link(source, token["attrs"]["url"], sources or {source}))
            collect_links(token.get("children", []))
    collect_links(MARKDOWN(content.decode("utf-8")))
    if any(url not in links for url in expected_links if not url.startswith("#")):
        raise ValueError(f"Missing preserved hyperlink in PDF: {source}")
    if any(url[1:] not in reader.named_destinations for url in expected_links if url.startswith("#")):
        raise ValueError(f"Missing source anchor destination in PDF: {source}")
    return {"pages": len(reader.pages), "text_token_coverage": round(coverage, 6), "source_tokens": len(expected),
            "uri_links": len(links), "internal_links": internal, "bookmarks": len(reader.named_destinations), "searchable": True}


def build(root: Path = ROOT, check: bool = False, rebuild_check: bool = False) -> dict:
    sources = discover_sources(root)
    names = set(sources)
    fingerprint = renderer_fingerprint()
    manifest_path = root / MANIFEST
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    old = {entry["source"]: entry for entry in previous.get("documents", [])}
    entries, generated, skipped = [], 0, 0
    for source in sources:
        content = (root / source).read_bytes()
        output = source[:-3] + ".pdf"
        path = root / output
        cached = old.get(source, {})
        current = (cached.get("source_sha256") == digest(content) and cached.get("renderer_sha256") == fingerprint
                   and path.is_file() and cached.get("pdf_sha256") == digest(path.read_bytes()))
        if check and not current:
            raise ValueError(f"Stale/missing generated PDF or manifest: {source}")
        if current:
            data = path.read_bytes()
            skipped += 1
        else:
            data = render_pdf(source, content, names)
            if not path.exists() or path.read_bytes() != data:
                path.write_bytes(data)
            generated += 1
        details = inspect_pdf(data, source, content, names)
        if rebuild_check and render_pdf(source, content, names) != data:
            raise ValueError(f"Fresh PDF bytes differ: {source}")
        entries.append({"source": source, "pdf": output, "source_sha256": digest(content), "pdf_sha256": digest(data),
                        "renderer_sha256": fingerprint, **details})
    manifest = {"schema": 1, "project": "HL-CYB-001", "source_of_truth": "Markdown", "toolchain": toolchain(),
                "aliases": ALIASES, "documents": entries}
    encoded = (json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode()
    if check:
        if not manifest_path.exists() or manifest_path.read_bytes() != encoded:
            raise ValueError("Documentation manifest is stale or does not match inspected PDFs")
    elif not manifest_path.exists() or manifest_path.read_bytes() != encoded:
        manifest_path.write_bytes(encoded)
    print(f"PASS: {len(entries)} source/PDF pairs; {sum(row['pages'] for row in entries)} pages; generated {generated}, unchanged {skipped}.")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing outputs/manifest without editing them")
    parser.add_argument("--rebuild-check", action="store_true", help="Also compare a fresh in-memory render byte-for-byte")
    args = parser.parse_args()
    try:
        build(check=args.check, rebuild_check=args.rebuild_check)
    except Exception as error:
        print(f"FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
