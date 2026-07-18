# Evaluation methodology

The point of this project is not a chatbot — it is measuring retrieval quality
rigorously, the way a bank AI team would before trusting a RAG system.

## Gold Q&A set (`gold_qa.jsonl`)
20–30 hand-written question/answer pairs about the filing. Each records the **source
page(s)** where the answer actually appears. These pages are the ground truth for
retrieval — filled in by reading the document, not generated.

> Note: pages are 1-based **PDF page indices** (as produced by `ingest.py`), used
> consistently for both the gold labels and retrieval — so the metric is internally exact.

## Metrics
- **hit@k** — fraction of questions for which the top-k retrieved chunks include a chunk
  from a gold source page. The headline retrieval-quality number.
- **MRR** — mean reciprocal rank of the first correct-page chunk; rewards ranking the
  right evidence higher, not just including it.
- **Median latency** — per-query retrieval time.

## Chunking comparison (the experiment)
We run the identical eval across several chunking strategies (`src/chunking.py`:
fixed-word windows, paragraph packing, whole-page) and report hit@k / MRR **before vs
after**. The deliverable is the table in `reports/chunking_comparison.md` plus a short
written interpretation of *why* the winning strategy wins.

## Answer quality (secondary)
Generation is graded lightly: does the answer cite the correct page(s) and avoid claims
not supported by the retrieved excerpts (the prompt is fail-closed on missing evidence).
