# ============================================================================
# FILE: utils/export.py
# ============================================================================
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def export_to_markdown(results: dict) -> str:
    """
    Converts the research results dictionary into a formatted Markdown string.

    Args:
        results (dict): The dictionary containing research results.

    Returns:
        str: A string in Markdown format.
    """
    query = results.get('query', 'N/A')
    summary = results.get('summary', 'No summary provided.')
    sources = results.get('sources', [])

    md_content = f"# Research Report: {query}\n\n"
    md_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    md_content += "## Summary\n"
    md_content += f"{summary}\n\n"

    if sources:
        md_content += "## Sources\n"
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'No Title')
            url = source.get('url', '#')
            md_content += f"{i}. [{title}]({url})\n"

    return md_content

def export_to_pdf(results: dict) -> bytes:
    """
    Converts the research results dictionary into a PDF file.

    Args:
        results (dict): The dictionary containing research results.

    Returns:
        bytes: The content of the generated PDF file.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab library is not installed. Please run 'pip install reportlab'.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    story = []

    # Title
    story.append(Paragraph(f"Research Report: {results.get('query', 'N/A')}", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # Summary
    story.append(Paragraph("Summary", styles['h2']))
    story.append(Paragraph(results.get('summary', 'No summary provided.'), styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # Sources
    if results.get('sources'):
        story.append(Paragraph("Sources", styles['h2']))
        for source in results.get('sources', []):
            story.append(Paragraph(f"- <link href='{source.get('url')}'>{source.get('title')}</link>", styles['BodyText']))

    doc.build(story)
    return buffer.getvalue()