# Tutorial

This page walks you through one full run of bank-filings-rag, from a fresh clone to
the demo output. You need `uv`, `make`, and the Python version named in
`pyproject.toml`. `uv` can install that Python for you.

## Step 1: get the code

```bash
git clone https://github.com/Iliya-Valizadeh/bank-filings-rag.git
cd bank-filings-rag
```

## Step 2: install

```bash
make setup
```

## Step 3: run the demo

```bash
make demo
```

The demo needs no download and no API key. It searches a short, made-up PDF (not
RBC's report) with keyword search only, and prints, for a few made-up questions,
which made-up page it found. Its first printed line says the pages are made up and
the numbers are a smoke test, not a result. It shows that the code runs end to end.

## Step 4: run the real evaluation (optional)

This step needs RBC's 2024 Annual Report, which is not committed to the repo (see
[data/README.md](../data/README.md) for how to get it).

```bash
make eval
```

This rebuilds every number in the [README](../README.md): it splits the report three
ways, searches it with three retrievers, scores every combination against the
[answer key](glossary.md#answer-key), and writes
[reports/metrics.json](../reports/metrics.json) and
[reports/chunking_comparison.md](../reports/chunking_comparison.md).

## Step 5: ask a question (optional)

With the report downloaded, and a Gemini API key in `.env` if you want a written
answer rather than just the retrieved pages:

```bash
uv run --extra embed python -m bank_filings_rag.ask --pdf data/raw/rbc_2024.pdf \
  "What was RBC's net income in fiscal 2024?"
```

This uses the best setup from the evaluation: whole pages with
[hybrid search](glossary.md#hybrid-search). It prints the pages it cited, and, with a
key set, an answer written from those pages.
