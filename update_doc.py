"""Build the Vietnamese FocusStudy presentation and handover PDF from Markdown."""
from __future__ import annotations

import html
import os
import re
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        PageBreak,
    )
except ImportError as exc:
    raise SystemExit(
        "Thiếu ReportLab. Cài dependency tài liệu bằng: "
        "python -m pip install -r requirements-docs.txt"
    ) from exc


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "docs" / "BAO_CAO_THUYET_TRINH.md"
OUTPUT = ROOT / "docs" / "BAO_CAO_THUYET_TRINH_BAN_MOI.pdf"
FALLBACK_OUTPUT = ROOT / "docs" / "BAO_CAO_THUYET_TRINH.pdf"

INK = colors.HexColor("#243B32")
GREEN = colors.HexColor("#315B47")
MUTED = colors.HexColor("#64756C")
PALE = colors.HexColor("#EEF3E9")
GRID = colors.HexColor("#D7E0D5")


def register_vietnamese_fonts() -> tuple[str, str, str]:
    candidates = [
        (
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\arialbd.ttf"),
            Path(r"C:\Windows\Fonts\ariali.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf"),
        ),
    ]
    for regular, bold, italic in candidates:
        if regular.is_file() and bold.is_file() and italic.is_file():
            pdfmetrics.registerFont(TTFont("FocusSans", str(regular)))
            pdfmetrics.registerFont(TTFont("FocusSans-Bold", str(bold)))
            pdfmetrics.registerFont(TTFont("FocusSans-Italic", str(italic)))
            pdfmetrics.registerFontFamily(
                "FocusSans",
                normal="FocusSans",
                bold="FocusSans-Bold",
                italic="FocusSans-Italic",
                boldItalic="FocusSans-Bold",
            )
            return "FocusSans", "FocusSans-Bold", "FocusSans-Italic"
    raise RuntimeError(
        "Không tìm thấy font Unicode có hỗ trợ tiếng Việt. "
        "Cài Arial, DejaVu Sans hoặc Liberation Sans rồi chạy lại."
    )


def inline_markup(text: str, regular_font: str) -> str:
    token = re.compile(
        r"(\*\*.+?\*\*|`.+?`|\*.+?\*|\[[^\]]+\]\([^)]+\))"
    )
    chunks: list[str] = []
    position = 0
    for match in token.finditer(text):
        chunks.append(html.escape(text[position : match.start()], quote=False))
        value = match.group(0)
        if value.startswith("**"):
            chunks.append(f"<b>{html.escape(value[2:-2], quote=False)}</b>")
        elif value.startswith("`"):
            chunks.append(
                f'<font name="{regular_font}">'
                f"{html.escape(value[1:-1], quote=False)}</font>"
            )
        elif value.startswith("*"):
            chunks.append(f"<i>{html.escape(value[1:-1], quote=False)}</i>")
        else:
            link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", value)
            if link:
                label, href = link.groups()
                chunks.append(
                    f'<link href="{html.escape(href, quote=True)}" '
                    f'color="#315B47">{html.escape(label, quote=False)}</link>'
                )
            else:
                chunks.append(html.escape(value, quote=False))
        position = match.end()
    chunks.append(html.escape(text[position:], quote=False))
    return "".join(chunks).replace("\n", "<br/>")


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


class ReportDocument(BaseDocTemplate):
    def __init__(self, path: Path, styles: dict[str, ParagraphStyle]):
        super().__init__(
            str(path),
            pagesize=A4,
            leftMargin=19 * mm,
            rightMargin=19 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="FocusStudy — Báo cáo toàn diện giới thiệu và bàn giao kỹ thuật",
            author="FocusStudy",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="content",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(
            [
                PageTemplate(
                    id="report",
                    frames=frame,
                    onPage=lambda canvas, doc: self.draw_chrome(canvas, doc),
                )
            ]
        )
        self.styles = styles

    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name in ('FocusH2','FocusH3'):
            level=0 if flowable.style.name=='FocusH2' else 1
            title=flowable.getPlainText()
            if level == 1 and not re.match(r'^\d+\.\d+', title):
                return
            key='section-'+str(self.seq.nextf('heading'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=level,closed=False)
            self.notify('TOCEntry',(level,title,self.page,key))

    @staticmethod
    def draw_chrome(canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(19 * mm, height - 13 * mm, width - 19 * mm, height - 13 * mm)
        canvas.setFont("FocusSans", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(19 * mm, height - 10 * mm, "FOCUSSTUDY · BÁO CÁO TOÀN DIỆN")
        canvas.line(19 * mm, 13 * mm, width - 19 * mm, 13 * mm)
        canvas.drawString(19 * mm, 8.5 * mm, "Tài liệu prototype · cập nhật 28/10/2026")
        canvas.drawRightString(width - 19 * mm, 8.5 * mm, f"Trang {doc.page}")
        canvas.restoreState()


def create_styles() -> dict[str, ParagraphStyle]:
    regular, bold, italic = register_vietnamese_fonts()
    base = getSampleStyleSheet()
    return {
        "regular_font": regular,
        "body": ParagraphStyle(
            "FocusBody",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=10.1,
            leading=14.8,
            textColor=INK,
            spaceAfter=5,
            alignment=TA_LEFT,
            splitLongWords=1,
        ),
        "title": ParagraphStyle(
            "FocusTitle",
            parent=base["Title"],
            fontName=bold,
            fontSize=23,
            leading=29,
            textColor=GREEN,
            alignment=TA_CENTER,
            spaceBefore=35,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "FocusH1",
            parent=base["Heading1"],
            fontName=bold,
            fontSize=16,
            leading=20,
            textColor=GREEN,
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "FocusH2",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=15,
            leading=19,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "FocusH3",
            parent=base["Heading3"],
            fontName=bold,
            fontSize=11.5,
            leading=15,
            textColor=GREEN,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "FocusBullet",
            fontName=regular,
            fontSize=9.7,
            leading=14,
            textColor=INK,
            leftIndent=13,
            firstLineIndent=-9,
            spaceAfter=3,
            splitLongWords=1,
        ),
        "table": ParagraphStyle(
            "FocusTable",
            fontName=regular,
            fontSize=8.3,
            leading=11.5,
            textColor=INK,
            spaceAfter=0,
            splitLongWords=1,
        ),
        "table_header": ParagraphStyle(
            "FocusTableHeader",
            fontName=bold,
            fontSize=8.4,
            leading=11.5,
            textColor=colors.white,
            spaceAfter=0,
            splitLongWords=1,
        ),
        "code": ParagraphStyle(
            "FocusCode",
            fontName=regular,
            fontSize=8.4,
            leading=11.5,
            textColor=INK,
            leftIndent=5,
            rightIndent=5,
            spaceAfter=0,
            wordWrap="CJK",
            splitLongWords=1,
        ),
        "meta": ParagraphStyle(
            "FocusMeta",
            fontName=italic,
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
    }


def parse_markdown(text: str, styles: dict[str, ParagraphStyle]) -> list:
    lines = text.splitlines()
    story = []
    index = 0
    first_title = True
    regular_font = styles["regular_font"]

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped in ("---", "***"):
            index += 1
            continue

        if stripped.startswith('<!--'):
            while '-->' not in lines[index] and index+1<len(lines):index+=1
            index+=1;continue
        if stripped=='[TOC]':
            story.append(PageBreak())
            story.append(Paragraph('Mục lục',styles['h1']))
            toc=TableOfContents()
            toc.levelStyles=[ParagraphStyle('TOC0',fontName=regular_font,fontSize=9.5,leading=13.5,spaceBefore=5),ParagraphStyle('TOC1',fontName=regular_font,fontSize=8.5,leading=12,leftIndent=12)]
            story.extend([toc,PageBreak()]);index+=1;continue
        picture=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',stripped)
        if picture:
            label,relative=picture.groups();path=SOURCE.parent/relative
            if not path.is_file():raise FileNotFoundError(path)
            w,h=ImageReader(str(path)).getSize();factor=min(172*mm/w,190*mm/h)
            story.extend([Image(str(path),width=w*factor,height=h*factor),Paragraph(inline_markup(label,regular_font),styles['meta']),Spacer(1,8)])
            index+=1;continue

        if stripped.startswith("```"):
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            code = html.escape("\n".join(code_lines), quote=False).replace("\n", "<br/>")
            block = Paragraph(code or " ", styles["code"])
            wrapper = Table([[block]], colWidths=[172 * mm], hAlign="LEFT")
            wrapper.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), PALE),
                        ("BOX", (0, 0), (-1, -1), 0.4, GRID),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.extend([Spacer(1, 3), wrapper, Spacer(1, 7)])
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            raw_rows = [split_table_row(stripped)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw_rows.append(split_table_row(lines[index]))
                index += 1
            col_count = max(len(row) for row in raw_rows)
            rows = []
            for row_number, row in enumerate(raw_rows):
                row = row + [""] * (col_count - len(row))
                style = styles["table_header"] if row_number == 0 else styles["table"]
                rows.append([Paragraph(inline_markup(cell, regular_font), style) for cell in row])
            widths = [172 * mm / col_count] * col_count
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.extend([Spacer(1, 3), table, Spacer(1, 7)])
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            level, title = len(heading.group(1)), heading.group(2)
            if level == 2 and title.startswith('15. Manifest'):
                story.append(PageBreak())
            style = styles["title"] if level == 1 and first_title else styles[f"h{level}"]
            story.append(Paragraph(inline_markup(title, regular_font), style))
            if level == 1:
                first_title = False
            index += 1
            continue

        if stripped.startswith(">"):
            quote_text = stripped.lstrip("> ").strip()
            story.append(Paragraph(inline_markup(quote_text, regular_font), styles["meta"]))
            index += 1
            continue

        list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.+)$", line)
        if list_match:
            marker, content = list_match.group(2), list_match.group(3)
            bullet = f"{marker} " if marker.endswith(".") else "• "
            story.append(
                Paragraph(
                    f"<b>{html.escape(bullet)}</b>{inline_markup(content, regular_font)}",
                    styles["bullet"],
                )
            )
            index += 1
            continue

        story.append(Paragraph(inline_markup(stripped, regular_font), styles["body"]))
        index += 1
    return story


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Không tìm thấy nội dung báo cáo: {SOURCE}")
    try:
        styles = create_styles()
        story = parse_markdown(SOURCE.read_text(encoding="utf-8"), styles)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        temporary_output = OUTPUT.with_name(f".{OUTPUT.stem}.building.pdf")
        ReportDocument(temporary_output, styles).multiBuild(story)
        try:
            os.replace(temporary_output, OUTPUT)
            final_output = OUTPUT
        except PermissionError:
            os.replace(temporary_output, FALLBACK_OUTPUT)
            final_output = FALLBACK_OUTPUT
    except Exception as exc:
        raise SystemExit(f"Không thể tạo PDF báo cáo: {exc}") from exc
    print(f"Generated PDF: {final_output}")


if __name__ == "__main__":
    main()
