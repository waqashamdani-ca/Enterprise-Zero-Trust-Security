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
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, LongTable, PageBreak, PageTemplate,
    Paragraph, Spacer, TableStyle, XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents

MANIFEST = "docs/documentation-manifest.json"
ALIASES = {
    "docs/DECISIONS.md": "docs/governance/DECISIONS.md",
    "docs/RISKS.md": "docs/governance/RISKS.md",
}
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
        if not name.endswith(".md") or name.lower().startswith("reports/"):
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
    markdown_report = name.lower().startswith("reports/") and name.endswith(".md")
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


def parse_diagram(raw: str) -> tuple[dict[str, str], list[tuple[str, str, str, bool]]]:
    nodes, edges = {}, []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "flowchart TB":
            continue
        node = re.fullmatch(r"(\w+)\[([^]]+)\]", line)
        edge = re.fullmatch(r"(\w+)\s+-->\s+(\w+)", line)
        dotted = re.fullmatch(r"(\w+)\s+-\.\s*(.*?)\s*\.->\s+(\w+)", line)
        if node:
            nodes[node[1]] = node[2]
        elif edge:
            edges.append((edge[1], edge[2], "", False))
        elif dotted:
            edges.append((dotted[1], dotted[3], dotted[2], True))
        else:
            raise ValueError("Unsupported Mermaid syntax; review before publication")
    if set(nodes) != {"Admin", "Mgmt", "FW", "ID", "USR", "APP", "LOG", "RA", "ROOT", "WAN", "EXT", "HOME"}:
        raise ValueError("Architecture nodes changed; review the vector layout")
    if any(a not in nodes or b not in nodes for a, b, _, _ in edges):
        raise ValueError("Mermaid edge references an undefined node")
    return nodes, edges


class ArchitectureFigure(Flowable):
    def __init__(self, raw: str):
        super().__init__()
        self.nodes, self.edges = parse_diagram(raw)
        self.width, self.height = CONTENT_WIDTH, 490

    def draw(self):
        canvas = self.canv
        layout = {
            "Admin": (252, 455, 300, 38), "Mgmt": (252, 393, 300, 38), "FW": (252, 331, 300, 38),
            "ID": (50, 232, 94, 72), "USR": (151, 232, 94, 72), "APP": (252, 232, 94, 72),
            "LOG": (353, 232, 94, 72), "RA": (454, 232, 94, 72),
            "ROOT": (112, 129, 186, 44), "HOME": (112, 60, 186, 44),
            "WAN": (390, 129, 190, 44), "EXT": (390, 51, 190, 38),
        }
        canvas.saveState()
        for start, end, label, dotted in self.edges:
            x1, y1, w1, h1 = layout[start]
            x2, y2, _, h2 = layout[end]
            points = [(x1, y1 - h1 / 2), (x2, y2 + h2 / 2)]
            if start == "FW" and end == "WAN":
                points = [(x1 + w1 / 2, y1), (502, y1), (502, y2 + h2 / 2 + 12), (x2, y2 + h2 / 2 + 12), (x2, y2 + h2 / 2)]
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
                canvas.setDash()
                style = ParagraphStyle("edge", fontName="Vera", fontSize=7.1, leading=9, textColor=colors.HexColor("#40576a"))
                paragraph = Paragraph(html.escape(normalize(label)), style)
                width = 92 if start == "FW" else 135
                px, py = (408, 279) if start == "FW" else (245, 78)
                _, height = paragraph.wrap(width, 60)
                paragraph.drawOn(canvas, px, py)
        canvas.setDash()
        for node, label in self.nodes.items():
            x, y, width, height = layout[node]
            canvas.setStrokeColor(colors.HexColor("#718391"))
            canvas.setFillColor(colors.HexColor("#eef3f7" if node not in {"ROOT", "HOME"} else "#f1f1f1"))
            canvas.roundRect(x - width / 2, y - height / 2, width, height, 4, stroke=1, fill=1)
            style = ParagraphStyle("node", fontName="Vera", fontSize=8.1 if width < 100 else 8.8, leading=10.5, alignment=TA_CENTER)
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
        self.destinations = {}
        frame = Frame(MARGIN, 51, CONTENT_WIDTH, HEIGHT - 115, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="standard", frames=[frame], onPage=self.page_furniture))

    def page_furniture(self, canvas, document):
        canvas.saveState()
        canvas.setFont("Vera", 7.8)
        canvas.setFillColor(colors.HexColor("#475c6c"))
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
            self.canv.addOutlineEntry(flowable.getPlainText(), flowable._anchor, flowable._level - 1, closed=flowable._level > 2)
            if flowable._level == 2:
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page, flowable._anchor))


class Builder:
    def __init__(self, source: str, sources: set[str]):
        register_fonts()
        self.source, self.sources = source, sources
        self.anchors: set[str] = set()
        self.counters = [0] * 6
        self.table_count, self.figure_count = 0, 0
        self.section_title = "Document"
        self.style = ParagraphStyle("body", fontName="Vera", fontSize=9.3, leading=13.2, spaceAfter=7)
        self.cell_style = ParagraphStyle("cell", parent=self.style, fontSize=8.25, leading=10.8, spaceAfter=0)
        self.code_style = ParagraphStyle("code", fontName="Courier", fontSize=7.9, leading=10.2,
                                        backColor=colors.HexColor("#f5f7f8"), borderColor=colors.HexColor("#d7dfe4"),
                                        borderWidth=0.4, borderPadding=6, leftIndent=7, rightIndent=7, spaceAfter=11)

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
        style = ParagraphStyle("heading", parent=self.style, fontName="Vera-Bold", fontSize=sizes[level], leading=sizes[level] * 1.3,
                               textColor=colors.HexColor("#193e58"), spaceBefore=12 if level > 1 else 0,
                               spaceAfter=7, keepWithNext=1)
        paragraph = Paragraph(label, style)
        paragraph._anchor, paragraph._level = anchor, level
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
            while len(line) > 98:
                split = max((i + 1 for i, (char, _) in enumerate(line[:98]) if char == " "), default=98)
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
        if count == 2:
            widths = [62, 442] if max(len(plain(row[0]["children"])) for row in rows) < 12 else [133, 371]
        elif count == 3:
            widths = [144, 42, 318] if headers[1] == "Points" else ([45, 250, 209] if headers[0] in {"Stage", "Security ID"} else [205, 143, 156])
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
            widths = [137, 66, 94, 141, 66]
        else:
            widths = [CONTENT_WIDTH / count] * count
        cells = []
        for row_number, row in enumerate(rows):
            cells.append([Paragraph(("<b>" if row_number == 0 else "") + inline(cell["children"], self.source, self.sources) + ("</b>" if row_number == 0 else ""), self.cell_style) for cell in row])
        table = LongTable(cells, colWidths=widths, repeatRows=1, splitByRow=1, splitInRow=1, hAlign="LEFT", spaceAfter=12)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5edf3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fa")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c5d0d8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
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
        for token in tokens:
            kind = token["type"]
            if kind in {"paragraph", "block_text"}:
                style = self.style if not depth else ParagraphStyle("indented", parent=self.style, leftIndent=depth * 14)
                story.append(Paragraph(inline(token["children"], self.source, self.sources), style))
            elif kind == "heading":
                title = plain(token["children"])
                if token["attrs"]["level"] == 2 and (title.startswith("Stage ") or title == "Source preservation appendix"):
                    story.append(PageBreak())
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
                    story.append(Paragraph(prefix + inline(first["children"], self.source, self.sources), style))
                    story.extend(self.blocks(children, depth + 1))
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
                    story.append(Paragraph(f"Figure {self.figure_count}. Proposed logical architecture; paths remain policy-controlled.", ParagraphStyle("figure-caption", parent=self.style, fontName="Vera-Italic", fontSize=8.3)))
                else:
                    story.append(self.code(token["raw"], language))
            elif kind == "block_quote":
                story.extend(self.blocks(token["children"], depth + 1))
            elif kind in {"blank_line", "thematic_break"}:
                continue
            elif kind == "block_html" and token.get("raw", "").lstrip().startswith("<!--"):
                continue
            else:
                raise ValueError(f"Unsupported Markdown block: {kind}")
        return story


def source_tokens(tokens: list[dict]) -> set[str]:
    chunks = []
    for token in tokens:
        if token["type"] in {"text", "codespan", "block_code"}:
            raw = token.get("raw", "")
            if token.get("attrs", {}).get("info") == "mermaid":
                raw = " ".join(parse_diagram(raw)[0].values())
            chunks.append(normalize(raw))
        if "children" in token:
            chunks.extend(source_tokens(token["children"]))
    return set(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", " ".join(chunks).lower()))


def render_pdf(source: str, content: bytes, sources: set[str]) -> bytes:
    if source.lower().startswith("reports/"):
        raise ValueError("Task reports are Markdown only; reports/ is excluded from PDF generation")
    tokens = MARKDOWN(content.decode("utf-8"))
    if not tokens or tokens[0]["type"] != "heading":
        raise ValueError(f"Document must start with a title: {source}")
    title = plain(tokens[0]["children"])
    builder = Builder(source, sources)
    formal = source.startswith(("docs/assignments/", "docs/lab-guides/", "docs/architecture/", "docs/security/", "docs/testing/", "docs/final-report/"))
    story = []
    if formal:
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
    if sum(token["type"] == "heading" and token["attrs"]["level"] == 2 for token in tokens) >= 6 and len(content.split()) >= 900:
        story.append(Paragraph("Contents", ParagraphStyle("contents-title", parent=builder.style, fontName="Vera-Bold", fontSize=17, leading=22, spaceAfter=14)))
        contents = TableOfContents()
        contents.levelStyles = [ParagraphStyle("toc", fontName="Vera", fontSize=9.3, leading=14, spaceBefore=4)]
        story.extend([contents, PageBreak()])
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
        if lines and number < len(reader.pages) and "Contents" not in lines:
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
