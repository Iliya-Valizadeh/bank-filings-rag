# How the retrieval was evaluated

A system like this can look fine in a demo and still fetch the wrong page most of the
time. The only way to tell which is happening is to write down the right answers first
and then check against them.

## The answer key (gold_qa.jsonl)

30 questions about RBC's 2024 Annual Report. Each records the page(s) where the answer
appears, plus a few answer strings (`answer_any`) used for checking.

- **Questions 1 to 10** I wrote and checked by reading the report: `"verified": true,
  "verified_by": "hand"`. Because the pages came from the report and not from the
  system's output, no chunking strategy could be tuned to match them.
- **Questions 11 to 30** I drafted to cover exact terms, segment tables, plain facts and
  answers that span two pages. They are `"verified": false, "verified_by": "script"`
  until I read each page myself.

`python -m eval.check_gold --pdf data/raw/rbc_2024.pdf` checks that each proposed page
contains one of the answer strings, and writes [gold_check.md](gold_check.md). It
catches a wrong page number. It can't catch a badly worded question or a wrong answer.

Pages are 1-based PDF page numbers, the same ones `src/ingest.py` produces.

## What gets measured

**hit@k**: the share of questions where a page from the answer key is in the top k
results. k = 5. This is the headline number.

**MRR** (mean reciprocal rank) also rewards position: 1 if the right page is first, 0.5
if second, 0.33 if third, and 0 if it isn't in the top k, averaged over questions.

**Lenient hit@k**: a hit when any retrieved chunk contains one of the answer strings,
even on a page the key doesn't list. The same figure is often printed on several pages,
so the strict score undercounts. Questions without answer strings (8 and 10) use the
strict score.

**Intervals**: 95% bootstrap intervals, from resampling the questions with replacement
1,000 times. On 10 questions they are wide, and the README says so.

**Median latency**: time for one search, including encoding the question. It varies by a
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
