import re
import string
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

def extract_text_from_pdf(path):
    try:
        return pdf_extract_text(path)
    except Exception:
        return ""

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def extract_text_from_file(path):
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    if path.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    return ""

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()