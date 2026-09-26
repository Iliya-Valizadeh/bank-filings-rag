"""Demo CLI: ask a question over the filing, get a page-cited answer.

Uses the best configuration from the evaluation: whole-page chunks with hybrid
(dense + BM25) retrieval. Fail-closed: without a GEMINI_API_KEY
it prints the retrieved evidence + pages instead of an LLM answer.

Run:
  python -m src.ask --pdf data/raw/rbc_2024.pdf "What was RBC's net income in 2024?"
"""

from __future__ import annotations

import argparse

from . import chunking, ingest
from .config import EMBED_MODEL, TOP_K
from .pipeline import ask as ask_pipeline
from .retrieve import build_index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("question")
    ap.add_argument("-k", type=int, default=TOP_K)
    a = ap.parse_args()

    pages = ingest.load_pages(a.pdf, with_blocks=False)
    chunks = chunking.whole_page(pages)  # best configuration in the eval
    index = build_index("hybrid", chunks, EMBED_MODEL)
    res = ask_pipeline(index, a.question, k=a.k)

    print("\nQUESTION:", a.question)
    print("\nANSWER:\n" + res["answer"])
    print("\nCited pages:", res["cited_pages"], "| LLM used:", res["llm"])


if __name__ == "__main__":
    main()
