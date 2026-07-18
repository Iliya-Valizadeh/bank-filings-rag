"""Evaluation harness — the differentiator of this project.

Measures, for each chunking strategy:
  - Retrieval hit@k : does the retrieved top-k include a chunk from a gold source page?
  - MRR             : mean reciprocal rank of the first correct-page chunk
  - median latency  : per-query retrieval time

Run:  python -m eval.evaluate --pdf data/raw/rbc_2024.pdf
Produces reports/chunking_comparison.md.
"""
from __future__ import annotations
import argparse, json, time, statistics
from pathlib import Path

from src.config import EMBED_MODEL, TOP_K, REPORTS
from src import ingest, chunking
from src.embed_index import VectorIndex


def load_gold(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    return [r for r in rows if r.get("source_pages")]  # only graded once pages filled


def hit_and_rank(hits, gold_pages):
    gold = set(gold_pages)
    for rank, h in enumerate(hits, start=1):
        if h["page"] in gold:
            return 1, 1.0 / rank
    return 0, 0.0


def evaluate(pdf_path, k=TOP_K):
    pages = ingest.load_pages(pdf_path)
    gold = load_gold(Path(__file__).parent / "gold_qa.jsonl")
    if not gold:
        raise SystemExit("No graded gold questions yet — fill source_pages in gold_qa.jsonl.")

    rows = []
    for name, fn in chunking.STRATEGIES.items():
        chunks = fn(pages)
        index = VectorIndex(EMBED_MODEL).build(chunks)
        hits_at_k, rr, lat = [], [], []
        for q in gold:
            t0 = time.perf_counter()
            res = index.search(q["question"], k=k)
            lat.append(time.perf_counter() - t0)
            h, r = hit_and_rank(res, q["source_pages"])
            hits_at_k.append(h); rr.append(r)
        rows.append({
            "strategy": name, "n_chunks": len(chunks),
            f"hit@{k}": sum(hits_at_k) / len(gold),
            "mrr": statistics.mean(rr),
            "median_latency_ms": round(statistics.median(lat) * 1000, 1),
        })
    return rows


def write_report(rows, k):
    REPORTS.mkdir(exist_ok=True)
    lines = ["# Chunking comparison\n",
             f"Retrieval quality by chunking strategy (k={k}), on the gold Q&A set.\n",
             f"| Strategy | #chunks | hit@{k} | MRR | median latency (ms) |",
             "|----------|---------|--------|-----|---------------------|"]
    for r in rows:
        lines.append(f"| {r['strategy']} | {r['n_chunks']} | {r[f'hit@{k}']:.2f} | "
                     f"{r['mrr']:.2f} | {r['median_latency_ms']} |")
    (REPORTS / "chunking_comparison.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("-k", type=int, default=TOP_K)
    a = ap.parse_args()
    write_report(evaluate(a.pdf, a.k), a.k)
