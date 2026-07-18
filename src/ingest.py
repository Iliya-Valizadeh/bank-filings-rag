"""Load a filing PDF into per-page text (page numbers preserved for citations)."""
from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader


def load_pages(pdf_path: str | Path) -> list[dict]:
    """Return [{'page': 1-based int, 'text': str}, ...]."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i, "text": text})
    return pages


if __name__ == "__main__":
    import sys
    pgs = load_pages(sys.argv[1])
    print(f"{len(pgs)} non-empty pages; first page chars: {len(pgs[0]['text'])}")
