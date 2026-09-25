# 0006: Headline numbers on hand-checked questions only

Date: 2026-09-25. Status: accepted.

I wrote this record on 2026-09-25, from the git history. The decision was made in
commits `8b69b7b` and `8e12f28` on 2026-09-24.

## Context

The first 10 questions were written and checked by reading the report. Ten questions
give very wide intervals. So commit `8b69b7b` added 20 more questions, each with a
proposed page.

A script, `eval/check_gold.py`, confirms that each proposed page contains the answer
text. The commit message says why that is not enough: it is "a script check, not a
reading". So every question got a `verified` flag and a `verified_by` field ("hand" or
"script"). The 20 new ones started as unverified.

Commit `a2d0688` added a stricter script check: the label and the figure must sit in
the same passage, close together. Two questions, Q28 and Q29, did not pass it. Iliya
read both pages, and commit `e1f89c9` marked them as checked by hand. That made 12.

## Options

- Headline on all 30. Narrower intervals, but 18 of the pages have never been read.
- Headline on the hand-checked questions only. Every page is confirmed, but the
  intervals are wide.
- No headline until all 30 are read.

## Decision

The headline uses only the hand-checked questions. A second table covers all 30 and
says how many are unread. The best setup is still picked on all 30, ties broken by
[MRR](../glossary.md#mrr), because the hand-checked set is too small to separate the setups. The code says
so in `best_config` in `eval/evaluate.py`.

## Consequences

- The headline intervals are wide. With 12 questions, one question moves [hit@5](../glossary.md#hit5) by
  about 0.08 (1 divided by 12). <!-- not-a-claim -->
- The best setup is chosen with the help of 18 unread questions and then scored on the
  12 read ones. Both sets were known when the choice was made.
- The headline set grows only when a page is read by hand, and each addition can move
  the headline. Adding Q28 and Q29 did: the headline setup found both. The
  [eval plan](../eval_plan.md) records this, and any future addition should be
  recorded the same way.
- A new hand-checked question should be picked for a reason that does not depend on the
  search results, as Q28 and Q29 were.
