# Evaluation methodology

Measuring retrieval quality is the point of this project. Anyone can wire an LLM to a
PDF; the question worth answering is how often the right evidence actually comes back.

## Gold Q&A set (`gold_qa.jsonl`)
10 hand-written question/answer pairs about the filing. Each records the **source
page(s)** where the answer actually appears. These pages are the ground truth for
retrieval, filled in by reading the document rather than generated.

Ten questions is a small set and the error bars on hit@k are correspondingly wide, so
treat the numbers as directional. Expanding to 20-30 is the first item on the roadmap.
The labels come from the filing itself rather than from the retriever's output, so no
chunking strategy can be tuned to them.

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
