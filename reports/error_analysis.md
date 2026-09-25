# Error analysis

Configuration: whole-page chunks + hybrid retrieval (dense + BM25, reciprocal rank
fusion). This is the best row in `reports/chunking_comparison.md` on all 30 questions:
21 of 30 hits in the top 5, so 9 misses.

The retrieved pages come from `reports/eval_results.json`. Word-piece positions come from
`notebooks/01_explore.ipynb`. The causes are my reading of those pages. Of questions 11
to 30, only Q28 and Q29 are checked by hand so far (see `eval/gold_check.md`).

Background that explains most of this: the embedding model reads only the first 256 word
pieces of any text. A median page here is 981 word pieces, and 96% of pages are longer
than 256. So a whole-page vector mostly describes the top quarter of the page. BM25
reads the whole page.

| Q | Question (short) | Answer-key page | Top 5 retrieved | Cause |
|---|---|---|---|---|
| 1 | Reported net income | 23 | 12, 7, 87, 9, 61 | Answer on another page. p. 7 (CEO letter) says "record earnings of $16.2 billion", so the lenient score counts it. Every page mentions net income, and p. 23 is a long table that neither retriever ranks first. |
| 5 | Total assets | 23 | 12, 63, 10, 8, 165 | Past the embedding window. The figure is at word piece 835 of p. 23. p. 63 also has 2,171,582, so the lenient score counts it. |
| 7 | Number of employees | 4 | 14, 3, 7, 6, 10 | Answer on another page. p. 6 (CEO letter) also has "98,000", so the lenient score counts it. p. 4 is a 700-character infographic that doesn't rank well in either retriever. |
| 8 | Reportable segments | 23 | 239, 8, 24, 46, 240 | Answer key too narrow. p. 24 describes the segments and the Q4 2024 split of Personal & Commercial Banking into two segments. p. 240 is the segment note. Both answer the question, but the key lists only p. 23. |
| 10 | Where are top and emerging risks discussed | 66 | 8, 74, 108, 7, 9 | Past the embedding window, and fusion lost the keyword hit. The heading is at word piece 790 of p. 66, below text about structured entities. BM25 alone finds p. 66 in the top 5. Dense doesn't, and after fusion it drops out of the top 5. |
| 12 | Bank-wide net interest margin | 23 | 50, 9, 40, 49, 88 | Term collision. "NIM" appears in every segment table. The retriever returns segment pages (p. 40 has Personal Banking's NIM of 2.43%) instead of the bank-wide 1.54%, which is at word piece 479 of p. 23. |
| 19 | Total price paid for HSBC Canada | 25, 194 | 195, 7, 63, 237, 43 | Off by one page, and past the window. p. 195 is the next page of the same acquisition note. On p. 25 the figure is at word piece 1,177, under an economic outlook section. |
| 22 | Insurance segment net income | 54 | 216, 164, 239, 7, 23 | Term collision and answer on another page. "Insurance" pulls in the insurance-contract accounting notes (p. 164, 216). p. 23 does have "Insurance 729 549", so the lenient score counts it. |
| 25 | Auditor and engagement partner | 145 | 11, 10, 143, 17, 7 | Off by two pages, and past the window. p. 143 is the first page of the same auditor's report. The partner's name is at the end of p. 145 (word piece 1,031). |

## Patterns

- Five of the nine misses have the answer past word piece 256 on the answer-key page
  (Q5, 10, 12, 19, 25). Being past the window doesn't guarantee a miss: Q11, 13, 14,
  18, 26 and 27 are also past it and were still found. For Q13, 14 and 26 the top of
  the page is about the same topic (the LCR, the NSFR, the Chair's letter), so the dense
  vector still matches. Q18 was found on its other answer-key page, p. 31. For Q11 and
  Q27 only BM25 found the page, and fusion kept it.
- Four of the nine retrieved a page that does contain the answer (Q1, 5, 7, 22). The
  strict score understates retrieval. This is why the comparison table also reports
  lenient hit@5 (0.83 for this configuration on all 30).
- Two retrieved a neighbouring page in the right section (Q19, 25). Returning page
  ranges instead of single pages, or indexing overlapping two-page windows, would
  probably fix both.
- Two are term collisions (Q12, 22). A word in the question also appears all over the
  report in another sense.

## What I would try next, in order

1. Split long pages into pieces under 256 word pieces for the dense side, but keep the
   whole page as the unit that gets cited. This targets the largest group of misses.
2. Weight BM25 more heavily in the fusion, or use it when the question contains an
   acronym. Q10 shows fusion can throw away a correct keyword hit.
3. Accept neighbouring pages of a gold page as a separate, labelled metric, to measure
   how often retrieval lands in the right section.

## Changes to the answer key since this analysis

Q8's answer text used to list "Personal & Commercial Banking" as one segment. The report
says (p. 23 footnote 5 and p. 24) that from Q4 2024 it is two segments, Personal Banking
and Commercial Banking, and the answer text now says so. Q7's answer now notes that
98,000+ is a headcount (p. 4) and that p. 23 gives 94,838 full-time equivalents. Neither
page changed, and neither edit changes any score: Q8 has no answer strings, and Q7's
answer strings are the same.
