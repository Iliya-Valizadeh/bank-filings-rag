# 0003: Whole pages as the unit for search and citation

Date: 2026-09-25. Status: accepted.

I wrote this record on 2026-09-25, from the git history. The decision was first made in
commit `5ec3c84` on 2026-07-17 and confirmed in `4b14b5d` on 2026-09-24.

## Context

The report must be cut into pieces before search. Small pieces can match a question
closely. But a number in a financial report only means something next to its label,
and small pieces can split the two.

The first commit, `5ec3c84`, tried three ways on the first 10 questions: fixed
180-word windows with 40 words of overlap, paragraphs, and whole pages. Fixed windows
scored far lower than the other two. Whole pages and paragraphs tied, and the command
line tool took whole pages as "the winning strategy".

That tie was not a real result. The paragraph splitter looked for blank lines, and
pypdf puts none in this report. So each page came out as one paragraph, and the
experiment compared whole pages with themselves. Commit `5160c6e` fixed this by using
the layout blocks that PyMuPDF finds. The splitter now stops with an error if the
blocks are missing, instead of falling back to whole pages without a word.

Commit `8e12f28` then ran each way of splitting with each kind of search (dense,
keyword and hybrid) on all 30 questions. Whole pages scored highest with every kind of
search. On the 12 hand-checked questions they scored highest or tied. The full table is
in [reports/chunking_comparison.md](../../reports/chunking_comparison.md).

## Options

- Fixed windows. Many small pieces, but a figure often ends up apart from its label.
- Paragraphs from layout blocks. Closer to how the report is written, but a table row
  can still land apart from its header.
- Whole pages. Label and figure stay together, and the page is also the unit cited in
  every answer. But a page is often longer than the [embedding](../glossary.md#embedding) model can read.
- Short pieces for the vectors, while still returning and citing whole pages. Never
  tried. The README names it as the first fix to try.

## Decision

Whole pages. They kept labels next to figures, they scored at least as well as the
other two ways on the questions I have, and they match the page citations.

## Consequences

- The dense vector for a page mostly describes its top part, because the model reads
  only the first 256 word pieces (see ADR 0002).
- The choice was made on the same questions it is scored on. There is no held-out set.
- On the 12 hand-checked questions the intervals of the setups overlap, so the ranking
  of the three ways to split is a direction, not a proof.
- Tables lose their column headers when the text is pulled from the PDF. Whole pages
  do not fix that.
