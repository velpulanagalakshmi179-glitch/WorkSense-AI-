"""
Extraction helpers for uploaded files. Keeps PDF/DOCX/TXT parsing out of
the page files so pages only deal with UI + Groq calls.
"""
import io
from PyPDF2 import PdfReader
import docx


def extract_text(uploaded_file) -> str:
    """
    uploaded_file: a Streamlit UploadedFile object.
    Returns plain text, or raises ValueError for unsupported types.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return _extract_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return _extract_docx(uploaded_file)
    elif name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {name}. Use PDF, DOCX, or TXT.")


def _extract_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages).strip()


def _extract_docx(uploaded_file) -> str:
    # python-docx needs a file-like object; Streamlit's UploadedFile works directly.
    document = docx.Document(io.BytesIO(uploaded_file.read()))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def chunk_text(text: str, max_chars: int = 12000) -> list:
    """
    Naive chunker for long documents so a single Groq call doesn't blow
    past context limits. Splits on paragraph boundaries where possible.
    """
    if len(text) <= max_chars:
        return [text]
    chunks, current = [], []
    length = 0
    for para in text.split("\n"):
        if length + len(para) > max_chars and current:
            chunks.append("\n".join(current))
            current, length = [], 0
        current.append(para)
        length += len(para)
    if current:
        chunks.append("\n".join(current))
    return chunks
