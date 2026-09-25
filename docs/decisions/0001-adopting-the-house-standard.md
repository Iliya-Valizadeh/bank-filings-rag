# 0001: Adopting the house standard

Date: 2026-09-25. Status: accepted.

## Context

This repo was built before my house standard existed. The standard now lives in the
`ds-project-standard` template (tag `v1.0`). It expects a `src/<package>/` layout,
`pyproject.toml` with `uv.lock`, a Makefile with seven targets, a
`reports/metrics.json`, docs checks in CI, and a `make demo` that needs no downloads or
keys.

The repo today has a flat `src/` folder that is imported as `src`, and an `eval/`
folder with the scoring code and the [answer key](../glossary.md#answer-key) (`eval/gold_qa.jsonl`). Pins live in
`requirements.txt` (full run, with a CPU-only torch installed by hand from PyTorch's own
package index) and `requirements-ci.txt` (tests only, no torch). The Makefile has only
`eval` and `test`. CI runs ruff and pytest.

Three things set this repo apart:

- The numbers live in `reports/eval_results.json`. There is no `reports/metrics.json`.
- The search uses a pretrained [embedding](../glossary.md#embedding) model (`sentence-transformers/all-MiniLM-L6-v2`).
  Its weights download on first use. I did not train it.
- `src/generate.py` calls Gemini, which needs a paid key. It must stay out of the demo,
  the evaluation and CI.

The source PDF (`data/raw/rbc_2024.pdf`, RBC's annual report) is not committed.

The rule for this work is that no number changes. Before any change, I copied
`reports/eval_results.json` and a list of every number in `README.md` into a folder
outside the repo. The last step of the retrofit diffs against that copy.

This record makes each adoption choice once, so the later steps only carry it out.

## Decisions

### 1. How to adopt the template

Options:

- Hand-copy the files I need. This gives full control and no example code to remove.
  But the repo gets no `.copier-answers.yml`, so `copier update` can never bring in
  later fixes to `tools/`. The checks would drift from the template over time.
- Run `copier copy` into this repo. This brings the example project's code along, and
  some files clash with files I already have.

Decision: run `copier copy --trust --vcs-ref v1.0 gh:Iliya-Valizadeh/ds-project-standard .`
on the branch, with these flags:

- `--exclude` for `src/**`, `tests/**` and `reports/**`, so the template's worked
  example never enters the repo.
- `--skip` for `README.md`. Its text is mine, and a later step rewrites it against the
  saved number list.
- Every other clash (`Makefile`, `pyproject.toml`, `.gitignore`,
  `.github/workflows/ci.yml`) takes the template's version first. Then the repo's own
  content goes back in by hand, in the same commit: the two `eval` commands, the PDF
  and index ignore rules, and the ruff notes.

Why: the answers file is the only thing that lets `tools/` stay in sync with one source.
Taking the template's version of the shared files as the base keeps future
`copier update` diffs small. A source of `gh:` rather than a local path means the
answers file works on any machine.

`copier update` does not remember `--exclude`. Without the same flags, an update would
add the example code back. So `docs/how-to/` gets a page with the exact update command,
flags included.

### 2. Folder layout

Options:

- Keep the flat `src/`. No file moves. But the code then imports a package literally
  named `src`, which works only from the repo root. The template's build settings,
  coverage settings and Makefile all expect `src/<package>/`, so every one of them
  would need a local override. Each `copier update` would fight those overrides again.
- Move to `src/bank_filings_rag/`.

Decision: move. The move is one commit that does only two things: `git mv` of each file,
and rewriting `from src` imports to `from bank_filings_rag`. The same rewrite covers
`eval/`, `tests/` and the import lines of `notebooks/01_explore.ipynb`. The notebook is
not re-run, so its saved outputs stay as they are.

`eval/` stays where it is. It holds the answer key and the scripts that score the
search, which is a different job from the package. Because it stays a folder at the
root, pytest keeps `pythonpath = ["."]` so the tests can import `eval.metrics`.

Why: an import rename cannot change a number, and the final metrics diff proves it.
The flat layout would cost a small amount forever. The move costs one reviewed commit
once.

### 3. Pinned packages and the CPU-only torch

Decision:

- The packages the tests and the demo need go into `[project] dependencies` with the
  same `==` versions as `requirements.txt`. That includes `google-genai`. Installing the
  client costs nothing, and it makes no call without a key. The tests need it, because
  `tests/test_generate.py` checks that no call goes out.
- torch, sentence-transformers and transformers become an optional extra `embed`, at
  the same versions. Only `make eval` needs them. CI never installs them, as it does
  not today.
- torch comes from PyTorch's CPU package index through uv:

  ```toml
  [[tool.uv.index]]
  name = "pytorch-cpu"
  url = "https://download.pytorch.org/whl/cpu"
  explicit = true

  [tool.uv.sources]
  torch = [{ index = "pytorch-cpu", marker = "sys_platform != 'darwin'" }]
  ```

  `explicit = true` means only torch comes from that index, so no other package can be
  picked up from it by accident. On macOS the normal torch package is already CPU-only,
  so the marker leaves macOS on the default index. The pin `torch==2.14.0` also matches
  the index's `2.14.0+cpu` build, which is the build in my local `.venv`.
- Every Makefile target that needs the model runs `uv run --extra embed`. No target then
  depends on what an earlier target happened to install.
- The dev tools come from the template's `dev` group, and `uv.lock` pins them.
- The old files move with `git mv` to `docs/archive/`, not deleted.

The old files pin only direct packages. A fresh lock could pick newer versions of the
packages underneath them, and those can shift results. My local `.venv` is the
environment that made the committed numbers. So the adoption step saves its
`pip freeze` output to `docs/archive/` too, compares `uv.lock` against it, and adds a
`[tool.uv] constraint-dependencies` entry for each package whose version differs.

### 4. What `make demo` runs

Two things block a demo on the real data. The PDF is RBC's report, and the repo does not
share it. The dense and [hybrid search](../glossary.md#hybrid-search) both need the embedding model, which means a
download. Committing the weights would put a large binary in git. A fake encoder in the
demo would print "hybrid" results that mean nothing.

Decision: `make demo` runs `python -m bank_filings_rag.demo` on a small made-up PDF.
A committed script (`scripts/make_demo_pdf.py`) builds the PDF with PyMuPDF, which the
repo already uses. Its pages are short, invented texts in the style of an annual report.
The PDF is committed too, so the demo needs nothing from outside the repo. The demo then
runs the real code path: `load_pages`, whole-page splitting, and keyword search ([BM25](../glossary.md#bm25)).
It prints the top pages for a few fixed questions. It also scores them against a tiny
made-up answer key with the repo's own hit@k and [MRR](../glossary.md#mrr) code.

Rules for the demo:

- The first line it prints says the pages are made up, the search is keyword-only, and
  the numbers are a smoke test, not results.
- It never imports `generate.py` and never loads the embedding model.
- It writes nothing to `reports/`.
- CI runs it with `HF_HUB_OFFLINE=1` set, so any accidental model download fails loudly
  instead of passing quietly.

### 5. What `make all` does when the data is missing

Options: skip `eval` with a warning, or fail.

Decision: fail. The `eval` target first checks for `data/raw/rbc_2024.pdf`. If the file
is missing, it prints the path and points to `data/README.md`, then exits with an
error.

Why: `make all` is the promise that every number was just regenerated. If it skipped
`eval` and still passed, it would say "all good" without regenerating anything. CI is not
affected, because CI runs `lint`, `test`, `check-docs` and `demo` one by one, and none of
those needs the PDF. `make eval` itself may download the embedding model. The "no
downloads" rule is for the demo only.

### 6. Which numbers count for "no number changed"

Decision: the final diff counts every value in `reports/eval_results.json` except the
timing keys: `median_ms` in each `verified` and `all` block, and `ms` in each
per-question row. The README already says latency varies from run to run. The diff
includes the retrieved page lists and the `top_text` strings, which must match exactly.
It also counts every number in the saved list from `README.md`. A number may move to
another file during the rewrite, but its value may not change.

The README says hit rates and MRR come out the same on every run. So any change to a
counted value, even in the last digit, is written under "Numbers changed" in the status
file with its cause. It does not pass silently.

### 7. The shape of `reports/metrics.json`

Decision: a committed script, `eval/summarize.py`, builds `reports/metrics.json` from
`reports/eval_results.json`. It is the last step of `make eval`, so the two files cannot
drift apart. It copies values; it does not recompute them. The shape:

```json
{
  "about": "Built by eval/summarize.py from reports/eval_results.json. Do not edit by hand.",
  "k": 5,
  "n_questions": {"verified": 12, "all": 30},
  "interval": {"method": "percentile_bootstrap", "resamples": 1000, "level": 0.95},
  "headline": {
    "question_set": "verified",
    "metric": "hit_at_k",
    "model": {"strategy": "whole_page", "retriever": "hybrid",
              "value": 0.58, "ci_low": 0.33, "ci_high": 0.83},
    "baseline": {"strategy": "fixed_words", "retriever": "dense",
                 "value": 0.25, "ci_low": 0.0, "ci_high": 0.5}
  },
  "results": [
    {"strategy": "whole_page", "retriever": "hybrid", "n_chunks": 250,
     "verified": {"hit_at_k": {"value": 0.58, "ci_low": 0.33, "ci_high": 0.83},
                  "mrr": {"...": "..."}, "lenient_hit_at_k": {"...": "..."}},
     "all": {"...": "..."}}
  ]
}
```

The values above only show the shape and are rounded for reading. The script writes
the full values from `eval_results.json`, so the `interval` block must match what
`eval/evaluate.py` actually does. The script leaves out the timing keys, so
`metrics.json` itself is the same on every run.

The headline is whole pages with hybrid search, on the questions I checked by hand.
The [baseline](../glossary.md#baseline) is the first version: fixed-size chunks with [dense search](../glossary.md#dense-search), on the same
questions. This is the comparison the README already leads with. I am not picking a new
headline now that I have seen all the rows.

The README also quotes counts worked out from the per-question rows. One example: hybrid
found some questions that dense missed, and the reverse. `eval/summarize.py` computes
those too, so `CLAIMS.md` can point every number at `metrics.json`. The script does not
add a [bootstrap](../glossary.md#bootstrap) interval for the gap between two setups. `eval_results.json` has none,
and adding one would be a new result. It becomes a `roadmap` issue.

### 8. `has_model` and `has_dataset`

Decision: `has_model: false`, `has_dataset: true`.

A model card documents a model its author trained: its training data, its intended
use, and how it performs across groups. I did not train the embedding model. A card
from me would either repeat its authors' card or make things up. Instead,
`docs/reference.md` names the model, links its authors' card, and records the exact
model revision in my local cache. The code does not pin that revision today. That goes
into `docs/whats_weak.md`. Pinning it in code is a change to `src/`, so it waits until
it can be shown not to move any number.

The answer key is a dataset I built by hand, so it gets a short `DATASHEET.md`: who
wrote the questions, how pages were checked, which questions I checked by reading, and
its known gaps.

### 9. The coverage bar

The template asks for 80% coverage of `src/`, but only for new repos. <!-- not-a-claim -->

Options:

- 80% now. <!-- not-a-claim -->
  `eval/evaluate.py` and index building need the PDF and the model, or heavy mocking.
  Tests written only to reach a number would say less than an honest lower bar.
- No bar. Coverage could then fall without anyone noticing.
- A floor that only goes up.

Decision: after the layout move, measure coverage of `bank_filings_rag` and `eval`
together, round it down to a whole percent, and set that as `--cov-fail-under`. It is
never lowered. `eval` counts because `eval/metrics.py` is the code that turns search
results into the headline numbers. A bug there changes a claim. Each new module added in
this phase, such as `demo.py` and `eval/summarize.py`, must reach 80% on its own in the <!-- not-a-claim -->
coverage report. A `roadmap` issue tracks raising the total to 80%. <!-- not-a-claim -->

### 10. The eval plan, written after the results

The standard wants `docs/eval_plan.md` committed before the results. That can't happen
here: the results exist.

Decision: the file is titled "Evaluation plan (written after the results)". Its first
paragraph says it was written on 2026-09-25 from the git history, and that it is not a
plan made in advance. Each choice cites the commit that first fixed it: the set of
questions, the ones checked by hand, hit@k, MRR, the strict and lenient scores, and the
bootstrap. Each also says whether that commit came before or after the first commit
that reported results. Choices made after results were seen, such as adding hand checks
to more questions, get their own section.

The README's "How I worked" links the file with the same label. The ML Test Score
self-score gives no credit for a plan written in advance.

The README says the strict score is the headline "because I defined it before I saw
any results." The eval plan step must check that against the history. If the history
does not show it, the review step changes that sentence.

### 11. Lint and type settings <!-- not-a-claim -->

Decision: use the template's ruff rules. `ruff format` runs once, in its own commit,
and that commit's hash goes into `.git-blame-ignore-revs`. Lint findings are fixed only
when the fix cannot change behavior. Any other finding gets a per-rule ignore with a
one-line reason. mypy runs on `src/` and `eval/` in its default mode with
`check_untyped_defs`, not in strict mode. It ignores missing type stubs for packages
that ship none, and for the `embed` packages that CI does not install. Strict mode
becomes a `roadmap` issue.

Why: strict mode would mean annotating every function in code that already works. That
is a large diff with a real chance of a mistake, and it would not change any claim.

## Consequences

- `copier update` can sync `tools/` from one source, as long as it uses the flags on the
  how-to page.
- Every command in the docs changes from `src.` to `bank_filings_rag.`. The README
  rewrite must catch all of them.
- A full setup for `make eval` is `uv sync --extra embed`. The Makefile and the tutorial
  must both say so.
- The lockfile may pin a transitive package newer than my local `.venv`. The freeze
  comparison in decision 3 is there to catch that before the metrics diff does.
- `make all` fails on a fresh clone until the PDF is downloaded. That is on purpose, and
  the error message says what to do.
- The demo shows that the code runs, not that the search works. The README must not
  present demo output as a result.
- The coverage floor, the non-strict mypy setting and the unpinned model revision are
  weaker than the standard. All three go into `docs/whats_weak.md` and the ML Test Score
  self-score.
