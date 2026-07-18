"""Demo CLI: ask a question over the filing, get a page-cited answer.

Uses the winning chunking strategy (whole_page). Fail-closed: without a GEMINI_API_KEY
it prints the retrieved evidence + pages instead of an LLM answer.

Run:
  python -m src.ask --pdf data/raw/rbc_2024.pdf "What was RBC's net income in 2024?"
"""
from __future__ import annotations
import argparse
from .config import EMBED_MODEL, TOP_K
from . import ingest, chunking
from .embed_index import VectorIndex
from .pipeline import ask as ask_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("question")
    ap.add_argument("-k", type=int, default=TOP_K)
    a = ap.parse_args()

    pages = ingest.load_pages(a.pdf)
    chunks = chunking.whole_page(pages)          # winning strategy from the eval
    index = VectorIndex(EMBED_MODEL).build(chunks)
    res = ask_pipeline(index, a.question, k=a.k)

    print("\nQUESTION:", a.question)
    print("\nANSWER:\n" + res["answer"])
    print("\nCited pages:", res["cited_pages"], "| LLM used:", res["llm"])


if __name__ == "__main__":
    main()
