# How the retrieval was evaluated

A system like this can look fine in a demo and still fetch the wrong page most of the
time. The only way to tell which is happening is to write down the right answers first
and then check against them.

## The answer key (gold_qa.jsonl)

30 questions about RBC's 2024 Annual Report. Each records the page(s) where the answer
appears, plus a few answer strings (`answer_any`) used for checking.

Questions 1 to 10 I wrote and checked by reading the report. They are marked
`"verified": true, "verified_by": "hand"`. The pages came from the report, not from the
system's output, so no chunking strategy could be tuned to match them.

Questions 11 to 30 I drafted to cover exact terms, segment tables, plain facts and
answers that span two pages. They are marked `"verified": false, "verified_by": "script"`
until I read each page myself. Each also names a label and a figure (`check_label`,
`check_figure`) for the stricter check below.

`python -m eval.check_gold --pdf data/raw/rbc_2024.pdf` writes
[gold_check.md](gold_check.md). It runs two checks on the proposed pages. The first looks
for one of the answer strings anywhere on the page. The second, for questions 11 to 30,
looks for the label and the figure in the same layout block (a paragraph, heading or
table body, as PyMuPDF sees it), no more than 200 characters apart. That rules out a page
that happens to contain the number somewhere unrelated. 18 of the 20 pass the second
check, and Q28 and Q29 are marked for a read. Neither check can catch a badly worded
question or a wrong answer.

Pages are 1-based PDF page numbers, the same ones `src/ingest.py` produces.

## What gets measured

hit@k is the share of questions where a page from the answer key is in the top k
results. k = 5. This is the headline number.

MRR (mean reciprocal rank) also rewards position: 1 if the right page is first, 0.5
if second, 0.33 if third, and 0 if it isn't in the top k, averaged over questions.

Lenient hit@k counts a hit when any retrieved chunk contains one of the answer strings,
even on a page the key doesn't list. The same figure is often printed on several pages,
so the strict score undercounts. Questions without answer strings (8 and 10) use the
strict score.

The intervals are 95% bootstrap intervals, from resampling the questions with replacement
1,000 times. On 10 questions they are wide, and the README says so.

Median latency is the time for one search, including encoding the question. It varies by a
few milliseconds between runs.

## The comparison

Every chunking strategy in `src/chunking.py` (fixed-word windows, paragraphs from layout
blocks, whole pages) is paired with every retriever in `src/retrieve.py` (dense, BM25,
hybrid). The same questions and the same scoring are used for all nine pairs.

`python -m eval.evaluate --pdf data/raw/rbc_2024.pdf` writes
`reports/chunking_comparison.md`, `reports/eval_results.json` (per-question results) and
`reports/figures/hit_at_5.png`. Those files are entirely generated, so the numbers can't
drift from the code. Discussion lives in the main README and in
`reports/error_analysis.md`.

## Answer quality

Not measured. The prompt tells the model to cite pages and to say when the pages don't
cover the question, and it refuses without calling the model when nothing is retrieved.
Scoring the written answers is future work.
