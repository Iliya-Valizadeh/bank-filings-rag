"""`make demo`: runs with no downloads, no keys, and no network call.

Decision and rules: docs/decisions/0001-adopting-the-house-standard.md, section 4.

It searches a small made-up PDF (data/demo/demo_filing.pdf, built by
scripts/make_demo_pdf.py) with BM25 keyword search only. It never imports generate.py
(the Gemini call) and never builds the embedding index, so it needs nothing from
outside the repo. It writes nothing to reports/: the numbers below are a smoke test
that the code runs, not an evaluation result.
"""

from __future__ import annotations

from pathlib import Path

from eval.metrics import hit_and_rank

from . import chunking, ingest
from .retrieve import BM25Index

DEMO_PDF = Path(__file__).resolve().parents[2] / "data" / "demo" / "demo_filing.pdf"

# Made up to match scripts/make_demo_pdf.py's four pages. Not a real answer key.
DEMO_QUESTIONS = [
    {"id": "d1", "question": "What was net income?", "source_pages": [1]},
    {"id": "d2", "question": "What was the CET1 ratio?", "source_pages": [2]},
    {"id": "d3", "question": "What was retail banking segment revenue?", "source_pages": [3]},
    {"id": "d4", "question": "How many members does the board have?", "source_pages": [4]},
]


def run(pdf_path: Path = DEMO_PDF) -> list[dict]:
    pages = ingest.load_pages(pdf_path, with_blocks=False)
    chunks = chunking.whole_page(pages)
    index = BM25Index().build(chunks)
    rows = []
    for q in DEMO_QUESTIONS:
        hits = index.search(q["question"], k=5)
        hit, rr = hit_and_rank(hits, q["source_pages"])
        rows.append(
            {
                "id": q["id"],
                "question": q["question"],
                "top_page": hits[0]["page"] if hits else None,
                "hit": hit,
                "rr": rr,
            }
        )
    return rows


def main() -> int:
    print(
        "These pages are made up, the search is keyword-only (BM25), and the "
        "numbers below are a smoke test that the code runs, not a result."
    )
    rows = run()
    for r in rows:
        print(
            f"Q: {r['question']}\n  top page: {r['top_page']}  "
            f"hit: {bool(r['hit'])}  reciprocal rank: {r['rr']:.2f}"
        )
    n_hit = sum(r["hit"] for r in rows)
    print(f"\n{n_hit}/{len(rows)} demo questions found their made-up page.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
