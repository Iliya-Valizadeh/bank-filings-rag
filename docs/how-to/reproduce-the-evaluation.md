# How to reproduce the evaluation numbers

Every number in the [README](../../README.md) comes from `make eval`. Here is how to
run it yourself.

## 1. Get the report

The PDF is not committed to this repo. Download RBC's 2024 Annual Report and save it
as `data/raw/rbc_2024.pdf`. See [data/README.md](../../data/README.md) for the exact
link and file size.

## 2. Install the extra packages dense search needs

```bash
uv sync --extra embed
```

`make demo`, `make lint` and `make test` do not need this extra. Only dense and
[hybrid search](../glossary.md#hybrid-search) do, since they load `sentence-transformers` and `torch`.

## 3. Run the evaluation

```bash
make eval
```

This runs every combination of [chunking](../glossary.md#chunk) (fixed words,
paragraphs, whole pages) and search (dense, [BM25](../glossary.md#bm25), hybrid)
against the [answer key](../glossary.md#answer-key), and writes:

- `reports/eval_results.json`: every question, every setup, the pages retrieved
- `reports/chunking_comparison.md`: the summary table with intervals
- `reports/metrics.json`: the headline and [baseline](../glossary.md#baseline) numbers, read by `CLAIMS.md`
- `reports/figures/hit_at_5.png`: the headline chart

## 4. Check nothing moved

Hit rates and [MRR](../glossary.md#mrr) come out identical on every run, since nothing
in the pipeline is randomized except the [bootstrap](../glossary.md#bootstrap), which uses a fixed seed. Search
time varies from run to run by a few milliseconds; the README and `reports/metrics.json`
both leave timing out of the numbers that must match.
