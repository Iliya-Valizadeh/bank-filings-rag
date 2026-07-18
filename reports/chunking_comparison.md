# Chunking comparison

Retrieval quality by chunking strategy (k=5) on the 10-question gold set over RBC's 2024
Annual Report (250 pages). Metric = does the top-5 retrieved set include a chunk from the
gold source page. Embeddings: `all-MiniLM-L6-v2`; index: FAISS flat (cosine).

| Strategy | #chunks | hit@5 | MRR | median latency (ms) |
|----------|---------|-------|-----|---------------------|
| fixed_words (180w / 40 overlap) | 1355 | 0.10 | 0.10 | 15.5 |
| paragraph (split on blank lines) | 249 | 0.40 | 0.27 | 14.6 |
| **whole_page** | 250 | **0.40** | **0.27** | 17.6 |

## Findings

1. **Fine-grained windows retrieve 4x worse.** Fixed 180-word chunks score hit@5 0.10 vs
   0.40 for page-level chunks. For factual figures in a financial report, a value is only
   retrievable when it stays next to the label/table header that gives it meaning —
   "$16,240" is invisible to a dense retriever unless "Net income" travels with it.
   Splitting into small windows fragments the number from its context and retrieval fails.
2. **"Paragraph" degenerates to page-level on this PDF.** pypdf's text extraction does not
   emit blank-line paragraph breaks, so the paragraph strategy produced ~one chunk per
   page (249) and matches whole_page exactly. A useful reminder that chunking quality is
   bounded by extraction quality.
3. **Latency is not the deciding factor** (~15 ms/query for a FAISS flat index at this
   scale) — retrieval quality is.

## Honest limitations & next steps

Absolute hit@5 of 0.40 is modest — expected for short factual questions against dense
financial prose with a small embedding model. Next improvements:
- Stronger embeddings (`bge-base`, `e5-large`).
- **Hybrid retrieval** (dense + BM25); financial questions are keyword-heavy ("CET1",
  "ROE"), where lexical matching helps.
- Table-aware chunking that keeps rows attached to their headers.
