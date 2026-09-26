# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and each release matches a
git tag.

## [1.0.0] - 2026-09-26

### Added

- 2026-07-17: first version of the pipeline: PDF ingest, three chunking strategies,
  [dense search](docs/glossary.md#dense-search) over a local
  [embedding](docs/glossary.md#embedding) index, and cited generation with Gemini.
- 2026-09-24: [BM25](docs/glossary.md#bm25) keyword search and
  [hybrid search](docs/glossary.md#hybrid-search) with
  [reciprocal rank fusion](docs/glossary.md#reciprocal-rank-fusion); a
  [lenient hit](docs/glossary.md#lenient-hit) score alongside the strict one;
  [bootstrap](docs/glossary.md#bootstrap) confidence intervals; 20 more questions in
  the [answer key](docs/glossary.md#answer-key) (30 in total); an error analysis of
  every miss.
- 2026-09-25: a stricter, second check on the answer key's proposed pages
  (`eval/check_gold.py`); two more questions checked by hand, for 12 in total.
- 2026-09-25: adopted the `ds-project-standard` template (Makefile, CI, mypy,
  `reports/metrics.json`, docs checks). Moved the code to `src/bank_filings_rag/`.
  Added `make demo`, which runs on a made-up PDF with no downloads or keys.
- 2026-09-25: the judgment docs this template requires: `docs/eval_plan.md` (written
  after the results, and honest about that), ADRs 0001 to 0006, `docs/whats_weak.md`,
  `DATASHEET.md`, and `docs/ml_test_score.md`.

### Fixed

- 2026-09-25: the README said the [strict hit](docs/glossary.md#strict-hit) score was "defined before I saw any
  results." Git history does not support that; the strict score and the first
  results appeared in the same commit. Reworded to say what the history does show:
  the strict score was the only score at first, and it is the more careful of the two
  scores this project reports.
- 2026-09-25: the README said all 30 answer-key questions pass the first script
  check. The real number is 28 of 30; two questions have no short answer string for
  the script to look for.
