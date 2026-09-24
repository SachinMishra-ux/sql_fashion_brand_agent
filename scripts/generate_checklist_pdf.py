#!/usr/bin/env python3
"""
scripts/generate_checklist_pdf.py
Generates a beautifully formatted, publication-grade PDF from docs/master_project_checklist_and_roadmap.md
using ReportLab with custom styled checkboxes, badges, and clean page wrapping.
"""
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds running headers and footers with total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 11 * inch - 30, "Maison Luxé (STELLA) — Master End-to-End Project Checklist")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(40, 11 * inch - 34, 8.5 * inch - 40, 11 * inch - 34)

        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 25, page_text)
        self.drawString(40, 25, "Confidential — Maison Luxé Architecture & Deployment Runbook")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 36, 8.5 * inch - 40, 36)
        self.restoreState()


def build_pdf(md_file: Path, pdf_file: Path):
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14,
    )

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h3_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        spaceAfter=2,
    )

    code_style = ParagraphStyle(
        "InlineCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#e2e8f0"),
    )

    story = []

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    i = 0
    in_code_block = False
    code_lines = []

    def format_inline(text: str) -> str:
        # Convert markdown bold and code to ReportLab XML tags
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Fix escaped entities inside tags
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"`(.*?)`", r'<font face="Courier" color="#0f172a" backcolor="#f1f5f9"> \1 </font>', text)
        return text

    while i < len(lines):
        line = lines[i]

        # Handle fenced code blocks
        if line.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "\n".join(code_lines)
                code_p = Preformatted(code_text, code_style)
                code_table = Table([[code_p]], colWidths=[doc.width])
                code_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("CORNERPAD", (0, 0), (-1, -1), 4),
                ]))
                story.append(code_table)
                story.append(Spacer(1, 6))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Skip horizontal rules
        if line.strip() in ["---", "***", "___"]:
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Document Title
        if line.startswith("# "):
            title_text = line[2:].strip()
            # Clean leading emoji
            title_text = re.sub(r"^[^\w\s]+\s*", "", title_text)
            story.append(Paragraph(format_inline(title_text), title_style))
            i += 1
            continue

        # Subtitle
        if line.startswith("### "):
            sub_text = line[4:].strip()
            story.append(Paragraph(format_inline(sub_text), subtitle_style))
            i += 1
            continue

        # H2 Section Header
        if line.startswith("## "):
            h2_text = line[3:].strip()
            # Wrap section header in a nice banner
            banner_p = Paragraph(f"<b>{format_inline(h2_text)}</b>", ParagraphStyle(
                "Banner", parent=h2_style, fontSize=11, leading=14, textColor=colors.HexColor("#0f172a")
            ))
            t = Table([[banner_p]], colWidths=[doc.width])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ]))
            story.append(Spacer(1, 8))
            story.append(t)
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Checklist Item (Checked [x] or Unchecked [ ])
        if line.strip().startswith("- [x]") or line.strip().startswith("- [ ]"):
            is_checked = line.strip().startswith("- [x]")
            raw_text = line.strip()[5:].strip()
            task_formatted = format_inline(raw_text)

            if is_checked:
                badge_p = Paragraph('<font size="10" color="#15803d"><b>✓</b></font>', ParagraphStyle("B1", alignment=1))
                text_p = Paragraph(task_formatted, ParagraphStyle("T1", parent=body_style, fontSize=9, leading=12.5, textColor=colors.HexColor("#0f172a")))
                bg_color = colors.HexColor("#f0fdf4")
                border_color = colors.HexColor("#bbf7d0")
            else:
                badge_p = Paragraph('<font size="10" color="#b45309"><b>○</b></font>', ParagraphStyle("B2", alignment=1))
                text_p = Paragraph(task_formatted, ParagraphStyle("T2", parent=body_style, fontSize=9, leading=12.5, textColor=colors.HexColor("#0f172a")))
                bg_color = colors.HexColor("#fefce8")
                border_color = colors.HexColor("#fde047")

            item_table = Table([[badge_p, text_p]], colWidths=[24, doc.width - 24])
            item_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (0, 0), 2),
                ("RIGHTPADDING", (0, 0), (0, 0), 2),
                ("LEFTPADDING", (1, 0), (1, 0), 4),
                ("RIGHTPADDING", (1, 0), (1, 0), 6),
            ]))

            # Collect nested sub-bullets underneath this task
            sub_bullets = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- ") and not (lines[j].strip().startswith("- [x]") or lines[j].strip().startswith("- [ ]")):
                sub_text = lines[j].strip()[2:].strip()
                sub_p = Paragraph(f"• {format_inline(sub_text)}", bullet_style)
                sub_bullets.append(sub_p)
                j += 1

            if sub_bullets:
                card_elements = [item_table, Spacer(1, 2)] + sub_bullets + [Spacer(1, 4)]
                story.append(KeepTogether(card_elements))
                i = j
                continue
            else:
                story.append(item_table)
                story.append(Spacer(1, 4))
                i += 1
                continue

        # Standard sub-bullets
        if line.strip().startswith("- "):
            bullet_text = line.strip()[2:].strip()
            story.append(Paragraph(f"• {format_inline(bullet_text)}", bullet_style))
            i += 1
            continue

        # Blockquote or callout
        if line.startswith("> "):
            quote_text = line[2:].strip()
            quote_p = Paragraph(format_inline(quote_text), ParagraphStyle(
                "Callout", parent=body_style, fontSize=8.5, leading=12, textColor=colors.HexColor("#1e40af")
            ))
            q_table = Table([[quote_p]], colWidths=[doc.width])
            q_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBEFORE", (0, 0), (-1, -1), 3, colors.HexColor("#3b82f6")),
            ]))
            story.append(q_table)
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Plain paragraphs
        if line.strip():
            story.append(Paragraph(format_inline(line), body_style))

        i += 1

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ PDF successfully generated at: {pdf_file}")


if __name__ == "__main__":
    src_md = Path("docs/master_project_checklist_and_roadmap.md")
    dest_pdf = Path("docs/master_project_checklist_and_roadmap.pdf")
    build_pdf(src_md, dest_pdf)
