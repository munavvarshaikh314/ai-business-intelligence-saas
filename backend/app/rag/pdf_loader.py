from pypdf import PdfReader
from typing import List, Dict
from app.rag.text_cleaner import clean_text


def load_pdf(file_path: str) -> List[Dict]:
    """
    Loads PDF page-wise:
    [
      { "page": 1, "text": "..." }
    ]
    """
    reader = PdfReader(file_path)
    pages = []

    for page_no, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = clean_text(text)

        if text.strip():
            pages.append({
                "page": page_no + 1,
                "text": text
            })

    return pages