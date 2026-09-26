# 0005: Hybrid search that merges two ranked lists by rank

Date: 2026-09-25. Status: accepted.

I wrote this record on 2026-09-25, from the git history. The decision was made in
commit `1f4db7f` on 2026-09-24 and put into the command line tool in `4b14b5d` the same
day.

## Context

The first version used only meaning-based (dense) search. The first results report, in
commit `5ec3c84`, listed [hybrid search](../glossary.md#hybrid-search) as a next step. Its reason: financial questions
use exact terms such as "CET1" and "ROE", and keyword matching helps with those.

Commit `1f4db7f` added keyword search ([BM25](../glossary.md#bm25)) and a hybrid of the two. The two searches
give scores on very different scales. A dense score is a cosine similarity. A BM25 score
grows with how often rare words appear. They cannot be added directly.

## Options

The history does not record which other ways of merging were weighed. These are the
usual ones.

- [Dense search](../glossary.md#dense-search) only. What the first version did.
- Keyword search only. Good on exact terms, weak when the question uses other words
  than the page.
- A weighted sum of the two scores. It needs the scales matched first, and the weights
  need tuning.
- [Reciprocal rank fusion](../glossary.md#reciprocal-rank-fusion). Each piece scores 1/(60 + rank) for each list it appears in,
  and the scores are added. It uses only ranks, so the scales never need matching.

## Decision

Reciprocal rank fusion, with the constant 60 taken from Cormack et al. (2009) and each
list read to depth 50. Neither setting was tuned. `4b14b5d` made whole pages with
hybrid search the setup the command line tool uses, because it had the best [hit@5](../glossary.md#hit5) on
all 30 questions.

## Consequences

- Fusion can push a right keyword hit out of the top 5. Q10 in
  [reports/error_analysis.md](../../reports/error_analysis.md) is one case.
- The weights are untuned. Tuning them on these same questions would overfit, so it
  needs new questions first.
- On the 12 hand-checked questions, hybrid over whole pages beats dense over whole
  pages by one question. The intervals overlap. The case for hybrid rests mostly on the
  30-question table, which includes 18 questions I have not read.
- Hybrid search runs both searches, so it needs the [embedding](../glossary.md#embedding) model as well as the
  keyword index.
