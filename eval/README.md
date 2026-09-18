# How the retrieval was evaluated

A system like this can look fine in a demo and still fetch the wrong page most of the
time. The only way to tell which one is happening is to write down the right answers
first and then check against them.

## The answer key (gold_qa.jsonl)

10 questions about RBC's 2024 Annual Report, written by hand. Each one records the page
where the answer actually appears, found by reading the report rather than by asking the
system and believing it. This is what is usually called a gold set.

Ten questions is a small set and a single question moves the score by 0.1, so the results
point in a direction rather than settling the matter. Expanding to 20 or 30 is the first
item on the roadmap.

Because the pages came from the report itself and not from the system's output, no
chunking strategy could be tuned to match them.

> Pages are 1-based PDF page numbers, the same ones ingest.py produces, used for both the
> answer key and the retrieval, so the two always refer to the same page.

## What gets measured

**hit@k** is how often the right page turns up in the top k results. At k=5: out of the
10 questions, how many times was the correct page among the 5 pieces of text the system
fetched. This is the headline number.

**MRR**, mean reciprocal rank, also cares about position. If the right page comes back
first it scores 1, second 0.5, third about 0.33, and not at all scores 0. Averaged across
the questions, it rewards putting the right page near the top instead of merely somewhere
in the list.

**Median latency** is how long one search takes.

## The comparison

Each way of splitting the report in src/chunking.py (fixed-word windows, paragraph
packing, whole pages) gets its own index, and the same questions run against all of them
under the same scoring. The table lands in reports/chunking_comparison.md with a short
note on why the winner won. The harness writes that file itself, so the numbers in the
report cannot drift away from the code that produced them.

## Answer quality

Checked by hand, and lightly: does the answer cite the right page, and does it stay
inside what the retrieved pages actually say. The prompt tells the model to say it does
not know when those pages do not cover the question.
