"""
Export helpers for the Export Module — turns any text/dict content into
a downloadable PDF or TXT. Pages call these and pass the result to
st.download_button.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def export_to_txt(title: str, content: str) -> bytes:
    text = f"{title}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'-'*40}\n\n{content}"
    return text.encode("utf-8")


def export_to_pdf(title: str, content: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10, leading=14)

    story = [
        Paragraph(title, title_style),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 0.5*cm),
    ]
    # reportlab's Paragraph chokes on raw newlines/HTML-sensitive chars — sanitize per line.
    for line in content.split("\n"):
        safe = (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        if safe.strip():
            story.append(Paragraph(safe, body_style))
        else:
            story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
