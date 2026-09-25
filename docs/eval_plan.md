# Evaluation plan (written after the results)

I wrote this page on 2026-09-25, from the git history. It is not a plan made in
advance. The results already existed when I wrote it. Each choice below cites the
commit that first fixed it, and says whether that commit came before, with or after
the first results.

The first results are in commit `5ec3c84` (2026-07-17). That commit holds the search
code, the scoring code, the first 10 questions and a table of results, all at once. So
git cannot show that any choice in it came before I saw a number.

## Question

How often does the search put the right page of RBC's 2024 Annual Report in its top 5
results, and which way of splitting the report and which kind of search does best?

## Data and split

The data is one PDF, RBC's 2024 Annual Report, and a hand-built [answer key](glossary.md#answer-key),
[eval/gold_qa.jsonl](../eval/gold_qa.jsonl). The [datasheet](../DATASHEET.md) describes
the key.

Nothing is trained, so there is no training set. There is also no held-out set. The
same questions are used to pick the best setup and to report its score. That is a
real weakness, listed in [whats_weak.md](whats_weak.md).

## Main metric

The share of questions where a page from the answer key is in the top 5 results
([hit@5](glossary.md#hit5)). A hit counts only when the retrieved page is one the key lists. This is the
strict score. The headline uses only the questions I checked by reading the report.

Each score gets a 95% [confidence interval](glossary.md#confidence-interval) from a
percentile [bootstrap](glossary.md#bootstrap): resample the questions with replacement
1,000 times and take the middle 95% of the means.

## Baseline

The [baseline](glossary.md#baseline) is the first version of the system: fixed
180-word chunks with meaning-based (dense) search. The headline compares it with whole
pages and [hybrid search](glossary.md#hybrid-search), on the same questions.

## What counts as success

No bar was set in advance, and none is set now. Setting one today, with the numbers in
view, would not mean anything.

## When each choice was fixed

| Choice | Commit | Date | Compared with the first results |
|---|---|---|---|
| Pages are 1-based PDF page numbers, used for both the key and the search | `5ec3c84` | 2026-07-17 | same commit |
| Top 5 results (k = 5) | `5ec3c84` | 2026-07-17 | same commit |
| [Strict hit](glossary.md#strict-hit)@k: a hit only on a page the key lists | `5ec3c84` | 2026-07-17 | same commit |
| [MRR](glossary.md#mrr) (mean reciprocal rank) and median search time | `5ec3c84` | 2026-07-17 | same commit |
| Three ways to split the report: fixed 180-word windows with 40 words of overlap, paragraphs, whole pages | `5ec3c84` | 2026-07-17 | same commit |
| The first 10 questions | `5ec3c84` | 2026-07-17 | same commit |
| Paragraphs split on PyMuPDF layout blocks, not blank lines | `5160c6e` | 2026-09-24 | after |
| Keyword search ([BM25](glossary.md#bm25)) and hybrid search ([reciprocal rank fusion](glossary.md#reciprocal-rank-fusion)) | `1f4db7f` | 2026-09-24 | after |
| [Lenient hit](glossary.md#lenient-hit): a hit also when a retrieved [chunk](glossary.md#chunk) contains an answer string | `d78553a` | 2026-09-24 | after |
| Bootstrap intervals: 1,000 resamples of the questions, seed 0 | `d78553a` | 2026-09-24 | after |
| 20 more questions (30 in all), with a `verified` flag on each | `8b69b7b` | 2026-09-24 | after the first results; same minute as the first 30-question results |
| Headline on hand-checked questions only; a second table for all 30 | `8e12f28` | 2026-09-24 | after |
| Every split paired with every search (dense, BM25, hybrid) | `8e12f28` | 2026-09-24 | after |
| The best setup is the highest hit@5 on all 30 questions, ties broken by MRR | `8e12f28` | 2026-09-24 | after |
| The command-line tool uses whole pages with hybrid search | `4b14b5d` | 2026-09-24 | after |
| A stricter answer-key check: label and figure in the same passage | `a2d0688` | 2026-09-25 | after |
| Q28 and Q29 read by hand, making 12 hand-checked questions | `e1f89c9` | 2026-09-25 | after |

Commits `d78553a`, `8b69b7b` and `8e12f28` share one timestamp. Git cannot show
whether I ran the 30-question evaluation before I committed the 20 new questions.

## Choices made after results were seen

Most choices here came after the first results. The ones that could move the headline
most are these.

The 20 new questions. They came after the 10-question results were known. Their pages
were proposed by me and checked by a script, not by reading. So they could lean
toward pages the search finds easily. The headline leaves out the 18 that are still
checked only by script.

The move from 10 to 12 hand-checked questions. I read Q28 and Q29 because the stricter
answer-key check in `a2d0688` could not confirm them. That reason comes from the
answer key, not from the search results. The whole-page hybrid setup finds both. So
its count went from 5 of the first 10 to 7 of 12 when they joined the headline set.
The baseline also finds both.

The lenient score. It was added two months after the first results, and it gives
higher numbers than the strict score. It is reported next to the strict score and is
never the headline.

Hybrid search and the choice of the best setup. Both came after the first results,
and the best setup was picked on the same questions it is scored on.

## What would change the conclusion

- Reading the 18 questions still checked only by script. A wrong page there moves the
  30-question table.
- More hand-checked questions. With 12, one question moves hit@5 by about 0.08 (1 divided by 12), and the intervals of the top setups overlap. <!-- not-a-claim -->
- A held-out set of new questions, written after the best setup was fixed.
- An [embedding](glossary.md#embedding) model with a longer input window. The current one reads only the top of
  each page, which hurts whole-page [dense search](glossary.md#dense-search) the most.
- A second report, from RBC or another bank.

## The claim that the strict score came first

The README says: "The strict score is the headline because I defined it before I saw
any results." The history does not support this. The strict score first appears in
`5ec3c84`, the same commit as the first results table. The README sentence itself was
added in `a73f82d` on 2026-09-24, two months later.

What the history does show is weaker. The strict score was the only score when the
first results came out. The lenient score came later, after those results were known.
The strict score also gives the lower number, so making it the headline does not
flatter the results. The README rewrite should say this instead.

## Changes to this plan

None yet.
