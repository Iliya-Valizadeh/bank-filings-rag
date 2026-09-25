# Explanation

Background and reasons. This page says why the project works the way it does. The
tutorial and how-to guides say what to type.

## Why measure retrieval instead of the written answer

The first version of this project answered questions and named a page for each one,
and it looked like it worked. Reading the answers alone could not say how often the
named page was actually right. So the project became about measuring that: an
[answer key](glossary.md#answer-key) with a known page for each question, and a
score that counts how often the search puts that page in the top results. Writing an
answer is a separate, later step that this project does not score; see
[docs/whats_weak.md](whats_weak.md).

## Why whole pages, not smaller chunks

A number in a financial report means little without the label or row that names it.
Small [chunks](glossary.md#chunk), such as fixed windows of words, can separate a
figure from its label. A [whole page](glossary.md#whole-page) keeps them together, and a page is also the unit
the system cites to the reader. [ADR 0003](decisions/0003-whole-pages-as-the-unit.md)
has the fuller record, including the fixed-window and paragraph setups it was
compared against.

## Why hybrid search

Meaning-based ([dense](glossary.md#dense-search)) search matches a question to a page
with a similar idea, but the [embedding](glossary.md#embedding) model used here reads
only the first 256 [word pieces](glossary.md#word-piece) of a page, so it can miss an
answer further down. Keyword search ([BM25](glossary.md#bm25)) reads the whole page
and matches exact terms such as "CET1" well, but misses a question phrased with
different words than the report uses. [Hybrid search](glossary.md#hybrid-search) runs
both and merges the two ranked lists with
[reciprocal rank fusion](glossary.md#reciprocal-rank-fusion), so a page that either
search finds gets credit. [ADR 0005](decisions/0005-hybrid-search-with-rank-fusion.md)
has the fuller record.

## Why local embeddings

Turning text into [embeddings](glossary.md#embedding) and searching them both run on
my own machine, not a hosted service. RBC's report is public, so nothing here needed
protecting, but a bank running the same pipeline over its own filings could not send
them to an outside service. Building the search half to already work under that rule
was the point, even though the project still calls a hosted model,
Gemini, to write the final answer. [ADR 0002](decisions/0002-local-embeddings.md) has
the fuller record.

## Choices and their costs

- Two ways of scoring a hit, strict and lenient, trade certainty for coverage: the
  strict score can undercount a real hit if a figure repeats on another page, and the
  lenient score can over-count a coincidence. [ADR 0004](decisions/0004-two-ways-of-scoring-a-hit.md)
  explains why the strict score stays the headline.
- The headline uses only the 12 questions checked by hand, not all 30, because the 18
  others were proposed after the first results and confirmed by a script, not by
  reading. [ADR 0006](decisions/0006-headline-on-hand-checked-questions.md) explains
  the trade: fewer questions, but each one is trusted more.
- `docs/eval_plan.md` was written after the results existed, which is weaker than
  writing it first. It says so in its own title, and traces every choice to the
  commit that made it, so a reader can see for themselves what came before the first
  results and what came after.
