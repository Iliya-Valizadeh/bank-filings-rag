# ML Test Score self-assessment

This page scores this repo against the ML Test Score, a checklist from
[Breck et al. (Google, 2017)][breck]. I scored it on 2026-09-25. The scoring rule is
the one in the `ds-project-standard` template, ADR 0004. No point is given that the
code does not earn.

## In plain words

Google wrote a list of 28 tests for a machine learning system. <!-- not-a-claim -->
A system should pass them before people rely on it.
This page checks this repo against that list. The repo's total is zero, the lowest
level. It is a search tool that runs on my machine. Nothing runs as a live
service, so nothing is watched while in use.

## How the scoring works

The paper gives each test a score:

- none: the test is not done
- half a point: the test is done by hand, and the result is written down
- one point: the test is automated and runs again on every change

A section's score is the sum of its seven tests. The overall score is the lowest of
the four section scores, so one weak section pulls the whole system down. The paper
reads an overall score of zero as closer to a research project than a production
system.

Following template ADR 0004, a test earns one point only after CI (continuous
integration, the checks GitHub runs on every push) has run it on GitHub. The test step
passed in CI run `36197187202`, on commit `f0f065e`. That run failed later, at the docs
checks, which do not affect these tests.

Two more rules I applied. A test that is automated but covers only part of what the
paper asks earns half a point, not one. Tests that do not apply, such as the serving
tests, score none, as the paper does.

## What is scored

There is no trained model here. The system splits RBC's 2024 Annual Report into
pieces, finds the pieces that best match a question, and sends them to a hosted model
to write an answer. I treat the search setup (how the report is split, and which kind
of search is used) as the "model". The code is in `src/bank_filings_rag/`, the scoring
is in `eval/`, and the tests are in `tests/`.

## Summary

| Section | Score out of 7 |
|---|---|
| Features and data | one and a half points |
| Model development | half a point |
| Infrastructure | two and a half points |
| Monitoring | none |
| Overall (the lowest section) | 0 |

One test earns a full point. Seven earn half a point each. The other twenty earn
nothing.

## Tests for features and data

| # | Test | Score | Evidence or gap |
|---|---|---|---|
| 1 | Feature expectations are captured in a schema | none | No schema lists the fields of a page or of the [answer key](glossary.md#answer-key). The paragraph splitter stops if a page has no layout blocks, but that is one check, not a schema |
| 2 | All features are beneficial | half | `make eval` runs [dense search](glossary.md#dense-search), keyword search and the hybrid of the two, so each signal is scored alone and together. It is run by hand, since it needs the PDF, and the results are committed in `reports/` |
| 3 | No feature's cost is too much | half | `make eval` records the median search time for each setup in `reports/chunking_comparison.md`. Run by hand, on one machine |
| 4 | Features adhere to meta-level requirements | none | The rule that indexing and search run locally ([ADR 0002](decisions/0002-local-embeddings.md)) is not checked by any test |
| 5 | The data pipeline has appropriate privacy controls | none | The report is public, so no control was needed here. Answer writing sends the top pages to Gemini. A test checks that no call is made without a key or with nothing retrieved, but that is not a privacy control |
| 6 | New features can be added quickly | none | Not measured |
| 7 | All input feature code is tested | half | CI runs tests on the splitters (page numbers survive, no text is dropped, paragraphs use layout blocks) and on the tokenizer. Parts of `ingest.py`, which reads the PDF, are not run by any test |

## Tests for model development

| # | Test | Score | Evidence or gap |
|---|---|---|---|
| 1 | Model specs are reviewed and checked in | none | The code is in git, but no second person has reviewed it |
| 2 | Offline and online metrics correlate | none | There is no live use, so there is no online metric |
| 3 | All hyperparameters have been tuned | none | Three ways of splitting were compared. The window size, the overlap, k and the fusion settings were not tuned ([ADR 0005](decisions/0005-hybrid-search-with-rank-fusion.md)) |
| 4 | The impact of model staleness is known | none | Only one year's report is used. Nothing tests a newer report against an older setup |
| 5 | A simpler model is not better | half | `make eval` scores the [baseline](glossary.md#baseline) (fixed chunks, dense search) and each kind of search alone next to the chosen setup, with [bootstrap](glossary.md#bootstrap) intervals. Run by hand. On the 12 hand-checked questions the intervals overlap, so this points in a direction but does not settle it |
| 6 | Model quality is sufficient on important data slices | none | Each question has a `kind` (for example `table` or `multi_page`), but no score is reported per kind |
| 7 | The model is tested for considerations of inclusion | none | The data describes a company, not people. Nothing checks this |

## Tests for infrastructure

| # | Test | Score | Evidence or gap |
|---|---|---|---|
| 1 | Training is reproducible | half | Nothing is trained, and building the index has no random step. During the retrofit a rerun of `make eval` matched the earlier results exactly, apart from timings (commit `f0f065e`). That was done by hand. No CI job reruns it, since it needs the PDF, and the [embedding](glossary.md#embedding) model's revision is not pinned |
| 2 | Model specs are unit tested | one point | CI runs tests on all three kinds of search with a fake encoder (k results, pages kept, an exact-term question finds its page) and on the scoring code with toy data (hit@k, [MRR](glossary.md#mrr), [lenient hit](glossary.md#lenient-hit), bootstrap) |
| 3 | The ML pipeline is integration tested | half | A CI test runs the demo end to end on a small made-up PDF: read, split into pages, keyword search, then hit@k and MRR. It does not cover dense or [hybrid search](glossary.md#hybrid-search), and no test runs `eval/evaluate.py` |
| 4 | Model quality is validated before serving | none | There is no serving step. Nothing blocks a change that lowers [hit@5](glossary.md#hit5) |
| 5 | The model is debuggable | half | `reports/eval_results.json` keeps, for every question, the pages retrieved and the top text. [reports/error_analysis.md](../reports/error_analysis.md) follows each miss of the best setup by hand |
| 6 | Models are canaried before serving | none | There is no serving step |
| 7 | Serving models can be rolled back | none | There is no serving step |

## Monitoring tests

| # | Test | Score | Evidence or gap |
|---|---|---|---|
| 1 | Dependency changes result in notification | none | Versions are pinned in `uv.lock`, but nothing reports new releases |
| 2 | Data invariants hold for inputs | none | There are no live inputs to check |
| 3 | Training and serving are not skewed | none | There is no serving step |
| 4 | Models are not too stale | none | There is no serving step |
| 5 | Models are numerically stable | none | Nothing checks for missing or infinite values in the vectors or scores |
| 6 | Computing performance has not regressed | none | Search time is recorded by `make eval` but never compared with an earlier run |
| 7 | Prediction quality has not regressed | none | No test compares a fresh run with the committed numbers. A test checks only that the committed results name the documented headline and [baseline](glossary.md#baseline) setups |

## What would raise the score

- A CI job that reruns the evaluation on a small public PDF and fails if hit@5 drops.
  That would touch infrastructure test 4 and monitoring test 7.
- Scores per question kind in `make eval` (model development test 6).
- A test for the rule that indexing makes no network call (features and data test 4).
- Dependabot or a similar tool for new package releases (monitoring test 1).

[breck]: https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/
