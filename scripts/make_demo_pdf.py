"""Build the small made-up PDF that `make demo` runs against.

Decision and rules: docs/decisions/0001-adopting-the-house-standard.md, section 4.

The four pages below are invented text in the style of an annual report. They are not
from any real bank or filing. Each page carries one fact that no other page repeats, so
BM25 keyword search (see src/bank_filings_rag/retrieve.py) can tell the pages apart
without an embedding model.

Run:  uv run python scripts/make_demo_pdf.py
Writes data/demo/demo_filing.pdf. The file is committed, so `make demo` needs nothing
from outside the repo.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "demo" / "demo_filing.pdf"

PAGES = [
    "Overview\n\n"
    "Example Bank is a made-up company used only to test this demo. It is not a real "
    "bank and these figures are not real. For the made-up year, Example Bank reported "
    "net income of $42 million, up from $31 million the year before.",
    "Risk factors\n\n"
    "Credit risk remains Example Bank's largest made-up risk category. The common "
    "equity tier 1 (CET1) ratio was 11.4 percent at year end, a made-up figure used "
    "only to test keyword search.",
    "Segment results\n\n"
    "The retail banking segment generated made-up revenue of $210 million for the "
    "year. The commercial banking segment generated made-up revenue of $95 million.",
    "Governance\n\n"
    "The board of directors has nine made-up members, chaired by Jane Example. The "
    "board met eight times during the made-up year.",
]


def build(out_path: Path = OUT_PATH) -> Path:
    doc = pymupdf.open()
    for text in PAGES:
        page = doc.new_page()
        page.insert_textbox(pymupdf.Rect(72, 72, 500, 700), text, fontsize=12)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    doc.close()
    return out_path


if __name__ == "__main__":
    p = build()
    print(f"Wrote {p} ({p.stat().st_size} bytes, {len(PAGES)} pages).")
