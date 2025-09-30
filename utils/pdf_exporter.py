"""Utilities to convert markdown text into a styled PDF."""
from __future__ import annotations

import io
import re
from typing import Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    HRFlowable,
)


def _format_inline(text: str) -> str:
    """Convert markdown emphasis markers into simple reportlab markup."""
    escaped = escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\\1</b>", escaped)
    escaped = re.sub(r"\*(.+?)\*", r"<i>\\1</i>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<font face='Courier'>\\1</font>", escaped)
    return escaped


def markdown_to_pdf_bytes(markdown_text: str, title: Optional[str] = None) -> bytes:
    """Render markdown content into a PDF and return the bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
        title=title or "Research Report",
    )

    styles = getSampleStyleSheet()
    heading_styles = {
        1: ParagraphStyle("Heading1", parent=styles["Heading1"], spaceAfter=12),
        2: ParagraphStyle("Heading2", parent=styles["Heading2"], spaceAfter=10),
        3: ParagraphStyle("Heading3", parent=styles["Heading3"], spaceAfter=8),
    }
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=12,
    )
    list_style = ParagraphStyle(
        "Bullet",
        parent=styles["BodyText"],
        leftIndent=0,
        leading=14,
        spaceAfter=6,
    )

    elements = []
    if title:
        elements.append(Paragraph(escape(title), styles["Title"]))
        elements.append(HRFlowable(width="100%", color=colors.grey, thickness=1))
        elements.append(Spacer(1, 0.2 * inch))

    lines = markdown_text.splitlines()
    bullet_items = []

    def flush_bullets():
        nonlocal bullet_items
        if bullet_items:
            elements.append(
                ListFlowable(
                    [ListItem(Paragraph(item, list_style)) for item in bullet_items],
                    bulletType="bullet",
                    leftIndent=18,
                )
            )
            bullet_items = []
            elements.append(Spacer(1, 0.08 * inch))

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            flush_bullets()
            elements.append(Spacer(1, 0.12 * inch))
            continue

        if line.lstrip().startswith(('- ', '* ')):
            text = line.lstrip()[2:].strip()
            bullet_items.append(_format_inline(text))
            continue

        flush_bullets()

        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line[level:].strip()
            style = heading_styles.get(min(level, 3), heading_styles[3])
            elements.append(Paragraph(_format_inline(text), style))
            elements.append(Spacer(1, 0.08 * inch))
        else:
            elements.append(Paragraph(_format_inline(line.strip()), body_style))

    flush_bullets()

    def _footer(canvas, doc_):
        canvas.saveState()
        footer_text = f"Page {doc_.page}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(doc_.pagesize[0] - 0.75 * inch, 0.5 * inch, footer_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes