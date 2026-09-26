DRAFT: Iliya to edit

# How the AI assistant was used

This page says which parts of the work were mine and which parts an AI coding assistant
wrote. The owner of the repo edits it and removes the draft line above.

## What I decided

The question (how often search finds the right page of RBC's report), the
[answer key](docs/glossary.md#answer-key)'s first 10 questions, the
[baseline](docs/glossary.md#baseline) (fixed chunks with
[dense search](docs/glossary.md#dense-search)), and the
choice to score retrieval instead of the written answer. TODO: Iliya to confirm this
list and add anything missing.

## What I checked

TODO: which parts of this retrofit I read line by line before committing: the two
README corrections (the eval-plan claim and the 30-question pass rate), the CLAIMS.md
rows against their sources, and the rewritten Diátaxis docs.

## What the AI assistant wrote

Claude, an AI coding assistant, is a co-author on the commit that added 20 of the 30
answer-key questions (`8b69b7b`). In this retrofit, an assistant drafted the ADRs,
`docs/eval_plan.md`, `docs/whats_weak.md`, `DATASHEET.md`, `docs/ml_test_score.md`,
the rewritten README, the glossary, the Diátaxis docs, and the `CLAIMS.md` rows, from
the repo's own git history and generated files. TODO: Iliya to confirm this is
complete and accurate, and to add anything the assistant did that isn't listed here.
