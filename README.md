# Bank Filings Analyst — RAG over RBC's Annual Report

Retrieval-augmented Q&A over RBC's 2024 annual report, 250 pages. Embeddings run locally,
so the filing never leaves the machine. Every answer cites the page its evidence came
from, and the generator is fail-closed: when the retrieved excerpts do not contain the
answer, it says so instead of guessing.

The part worth reading is the evaluation harness. A hand-labelled gold set scored on
hit@k and MRR, run identically across three chunking strategies, so the choice between
them rests on a measurement.

> **Status:** Complete end to end. Ingest, chunking, local embeddings, FAISS retrieval
> and cited generation all run. Measured result: whole-page chunking retrieves the
> correct page four times as often as fixed 180-word windows (hit@5 0.40 vs 0.10), on a
> 10-question gold set built by hand from the filing. Every figure in this repo is
> produced by the harness in eval/ and written to reports/chunking_comparison.md.

## Why this design

- **Local embeddings, on purpose.** A bank can't send confidential filings to a
  third-party embedding API. `sentence-transformers` runs in-house and costs $0 — this
  mirrors a realistic bank setup, not a demo shortcut.
- **Citations to the page.** Every answer cites the page(s) its evidence came from, and
  the generator is fail-closed: if the retrieved excerpts don't contain the answer, it
  says so instead of guessing.
- **Evaluation is the deliverable, not the chatbot.** Anyone can wire an LLM to a PDF.
  The value is proving *how well retrieval works* and *which chunking strategy wins, and
  why*.

## Architecture

```
PDF (annual report)
  └─ ingest.py        per-page text (page numbers kept for citations)
       └─ chunking.py  competing strategies: fixed-word / paragraph / whole-page
            └─ embed_index.py  sentence-transformers → FAISS (cosine)
                 └─ retrieve.py  top-k chunks for a query
                      └─ generate.py  Gemini (free tier) answer WITH page citations
eval/  gold Q&A set → hit@k, MRR, latency → chunking comparison table
```

## Evaluation (the core)

See [`eval/README.md`](eval/README.md). In short: a hand-built gold Q&A set with the true
source page for each answer; retrieval scored by **hit@k** and **MRR**; the identical eval
run across chunking strategies to produce a **before/after comparison**
(`reports/chunking_comparison.md`) plus a cost/latency table.

## Example: a cited answer

```
$ python -m src.ask --pdf data/raw/rbc_2024.pdf "What was RBC's net income in fiscal 2024?"

In fiscal 2024, RBC generated record earnings of $16.2 billion (p. 7).
Pro forma with the HSBC Canada acquisition, estimated net income would have been
$16.6 billion (p. 195); HSBC contributed $453 million since its March 28, 2024
acquisition date (p. 7, 195).

Cited pages: [7, 49, 59, 87, 195] | LLM used: True
```

The generator answers **only** from retrieved excerpts and cites a page for each claim;
if the evidence doesn't contain the answer it says so rather than guessing (fail-closed).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add a free Gemini API key (optional; runs without it)
# download the filing -> data/raw/rbc_2024.pdf  (see data/README.md)
python -m eval.evaluate --pdf data/raw/rbc_2024.pdf
```

## Roadmap

- [x] Repo skeleton, chunking strategies, embedding/index, retrieval, cited generation
- [x] Evaluation harness (hit@k, MRR, latency) + gold Q&A template
- [x] Ingest RBC 2024 report (250 pages); gold Q&A filled with real figures + source pages
- [x] Chunking comparison run (whole_page wins, hit@5 0.40 vs 0.10); see reports/chunking_comparison.md
- [x] Cited generation via Gemini free tier (fail-closed, page citations) — see Example
- [ ] Expand gold set to 20-30 Q&A; try hybrid (dense + BM25) retrieval

## Author
Iliya Valizadeh — BSc Data Science, York University. GitHub: [Iliya-Valizadeh](https://github.com/Iliya-Valizadeh)
