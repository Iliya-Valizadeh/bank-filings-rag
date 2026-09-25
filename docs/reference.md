# Reference

Facts to look up: commands, files and settings.

## Make targets

| Target | What it does |
|---|---|
| `make setup` | Installs the pinned packages with `uv` |
| `make lint` | Runs ruff and mypy |
| `make test` | Runs pytest with a coverage report for `src/` and `eval/` |
| `make eval` | Runs the search and scoring over RBC's report, writes `reports/metrics.json` |
| `make demo` | Runs a short demo that needs no download and no key |
| `make check-docs` | Runs the claims, readability, AI-writing signs, link and README checks |
| `make all` | Runs every step above in order |

A full setup for `make eval` is `uv sync --extra embed`, since [dense search](glossary.md#dense-search) needs
torch and sentence-transformers. `make demo`, `make lint` and `make test` do not need
that extra.

## Output files

| File | What it holds |
|---|---|
| `reports/metrics.json` | The headline numbers, read by `CLAIMS.md` |
| `reports/chunking_comparison.md` | Every chunking and retriever combination, with intervals |
| `reports/error_analysis.md` | Every miss of the best setup, with a one-line cause |
| `reports/figures/hit_at_5.png` | The headline chart |
| `reports/eval_results.json` | Full per-question results, including retrieved pages |
| `eval/gold_check.md` | The two script checks on the [answer key](glossary.md#answer-key)'s proposed pages |

## Package (`src/bank_filings_rag/`)

| Module | What it does |
|---|---|
| `ingest.py` | Reads page text (pypdf) and layout blocks (PyMuPDF); keeps the page number |
| `chunking.py` | Fixed-word windows, paragraphs from layout blocks, or whole pages |
| `embed_index.py` | Local [embeddings](glossary.md#embedding) and a FAISS index |
| `retrieve.py` | Dense, [BM25](glossary.md#bm25) keyword, or [hybrid](glossary.md#hybrid-search) search |
| `pipeline.py` | Wires ingest, [chunk](glossary.md#chunk), retrieve and generate together for `ask.py` |
| `generate.py` | Calls Gemini with the top pages; refuses if nothing was retrieved |
| `ask.py` | Command-line tool: ask a question, get a cited answer |
| `demo.py` | Runs `make demo`: BM25 only, on a made-up PDF, no downloads |
| `config.py` | Shared constants, such as `TOP_K` |

## Evaluation (`eval/`)

| File | What it does |
|---|---|
| `gold_qa.jsonl` | The 30-question answer key |
| `check_gold.py` | Two script checks on the answer key's proposed pages |
| `metrics.py` | hit@k, [MRR](glossary.md#mrr), the lenient score, and [bootstrap](glossary.md#bootstrap) intervals |
| `evaluate.py` | Runs every chunking and retriever combination, writes `reports/` |
| `summarize.py` | Builds `reports/metrics.json` from `reports/eval_results.json` |

## The embedding model

[Dense search](glossary.md#dense-search) and [hybrid search](glossary.md#hybrid-search) use `sentence-transformers/all-MiniLM-L6-v2`, a
pretrained model I did not train. Its own model card is at
[huggingface.co/sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
This repo does not pin an exact revision of it; see
[docs/whats_weak.md](whats_weak.md).
