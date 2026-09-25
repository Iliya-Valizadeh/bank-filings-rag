# 0004: Two ways of scoring a hit, with the strict one as the headline

Date: 2026-09-25. Status: accepted.

I wrote this record on 2026-09-25, from the git history. The strict score dates from
commit `5ec3c84` (2026-07-17). The lenient score dates from `d78553a` (2026-09-24).

## Context

The [answer key](../glossary.md#answer-key) lists the page or pages where each answer appears. A search result is a
"hit" if one of its top 5 pages is right. The question is what "right" means.

The first commit, `5ec3c84`, had one rule: a hit only when a retrieved page is one the
key lists. This is the strict score. The first results table used it.

Two months later, commit `d78553a` added a second rule and wrote down why in
`eval/metrics.py`. The same figure often appears on more than one page. RBC's net
income, for example, is printed on 13 pages. A search that returns one of those other
pages has found the answer, but the strict score calls it a miss. The lenient score
also counts a hit when any retrieved piece contains one of the question's answer
strings. Questions 8 and 10 have no answer strings, so they use the strict rule.

## Options

- Strict only. Simple and hard to game, but it undercounts real hits.
- Lenient only. Closer to what a reader would call a success, but it depends on the
  answer strings I chose. A short figure could also appear in an unrelated passage and
  count as a hit.
- Both, with one of them as the headline.

## Decision

Report both, with the strict score as the headline.

The README gives the reason as "because I defined it before I saw any results." The
history does not support that. The strict score first appears in the same commit as the
first results. The reasons the history does support are these. The strict score was
the only score when the first results came out. The lenient score was added after
those results were known. The strict score gives the lower number, so the headline
does not flatter the results.

## Consequences

- The README sentence about defining the strict score first must be rewritten in the
  README task. The [eval plan](../eval_plan.md) records the same finding.
- The gap between the two scores shows how much the strict score undercounts. It is
  not a measure of search quality on its own.
- The lenient score is only as good as the answer strings in
  [eval/gold_qa.jsonl](../../eval/gold_qa.jsonl). No check confirms that a matched
  string is the answer and not the same figure used elsewhere.
