# Bank Filings Analyst — RAG over RBC's Annual Report

A retrieval-augmented Q&A system over a bank's public annual report, built the way a bank
AI team would actually ship it: **local embeddings** (no confidential document leaves the
machine), **page-level source citations** on every answer, and — the real point — a
**rigorous evaluation harness** that measures retrieval quality and compares chunking
strategies with numbers, not vibes.

> **Status:** Scaffolding, evaluation design, and a real 10-question gold Q&A set (built
> from RBC's 2024 report) and the chunking comparison complete (whole_page retrieves
> 4x better than fixed windows). LLM answer step is the remaining piece. Metrics tables are produced by the harness in
> `eval/` — nothing is reported here until it has been measured.

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
- [ ] Cost/latency table; short demo

## Author
Iliya Valizadeh — BSc Data Science, York University. GitHub: [Iliya-Valizadeh](https://github.com/Iliya-Valizadeh)
