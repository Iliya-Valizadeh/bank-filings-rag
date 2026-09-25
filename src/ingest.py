"""Load a filing PDF into per-page text (page numbers preserved for citations).

Two extractors, used for different things:
- pypdf gives one plain string per page. The whole-page and fixed-word strategies use it.
- PyMuPDF gives the page's layout blocks: runs of text the PDF lays out together,
  which on this report are mostly paragraphs, headings and table bodies. The paragraph
  strategy uses these, because pypdf emits no blank lines on this PDF, so there is
  nothing in its output to split paragraphs on.
"""
from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader


def load_pages(pdf_path: str | Path, with_blocks: bool = True) -> list[dict]:
    """Return [{'page': 1-based int, 'text': str, 'blocks': [str, ...]}, ...]."""
    reader = PdfReader(str(pdf_path))
    blocks = load_blocks(pdf_path) if with_blocks else {}
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            rec = {"page": i, "text": text}
            if with_blocks:
                rec["blocks"] = blocks.get(i, [])
            pages.append(rec)
    return pages


def load_blocks(pdf_path: str | Path) -> dict[int, list[str]]:
    """Text blocks per 1-based page, in reading order (top to bottom, left to right)."""
    import pymupdf
    out = {}
    with pymupdf.open(str(pdf_path)) as doc:
        for i, page in enumerate(doc, start=1):
            # Each block is (x0, y0, x1, y1, text, block_no, block_type); type 0 is text.
            out[i] = [" ".join(b[4].split()) for b in page.get_text("blocks", sort=True)
                      if b[6] == 0 and b[4].strip()]
    return out


if __name__ == "__main__":
    import sys
    pgs = load_pages(sys.argv[1])
    n_blocks = sum(len(p["blocks"]) for p in pgs)
    print(f"{len(pgs)} non-empty pages; {n_blocks} layout blocks; "
          f"pages whose pypdf text has a blank line: {sum(chr(10) * 2 in p['text'] for p in pgs)}")
