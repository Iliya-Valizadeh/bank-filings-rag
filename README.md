# Bank Filings Analyst: question answering over RBC's annual report

Ask a question about RBC's 2024 Annual Report and get an answer back with the page number
it came from. The report runs to 250 pages, so finding a single figure by hand means
knowing where to look before you start.

Two things mattered to me more than the chatbot part.

**Every answer has to be checkable.** The system gives the page each claim came from, so
you can open the report and see for yourself. If the pages it pulled do not actually
contain the answer, it says so instead of writing something that sounds right.

**Retrieval has to be measured.** Asking a model a question is the easy half. The hard
half is getting the right page in front of it to begin with, and you cannot tell how
often that works without checking. So I wrote an answer key by hand and used it to
compare three ways of splitting the report.

> **Status:** Working end to end. Splitting the report one page at a time finds the
> correct page in the top 5 results 4 times out of 10. Cutting it into fixed 180-word
> chunks finds it 1 time out of 10. That is measured on a 10-question answer key, which
> is small, so the result points in a direction rather than settling anything. Full table
> in reports/chunking_comparison.md.

## Why the embeddings run locally

The text is turned into vectors on my own machine with sentence-transformers instead of
being sent to a hosted API.

RBC's annual report is public, so nothing here needed protecting. I built it this way
because a bank running the same thing over its own internal documents could not send
them to an outside service, and I wanted a design that already held up under that
constraint rather than one that would have to be rebuilt to meet it. Running the model
locally also costs nothing.

## Why the answers cite pages

The page number is attached to the text at the first step, when the PDF is read, and
carried through every stage after it. That is the only reason a citation is available at
the end. It also means the model is told to answer from the supplied pages and to admit
when they do not cover the question, which is the behaviour a bank would need before
trusting anything like this over its own filings.

## How it works

```
RBC 2024 Annual Report (PDF)
  ingest.py        read the text out page by page, keep the page number
  chunking.py      split it three different ways so they can be compared
  embed_index.py   turn each piece into a vector, store them in FAISS
  retrieve.py      for a question, fetch the 5 closest pieces
  generate.py      hand those to Gemini, with instructions to cite pages and not guess
  eval/            score the retrieval against the hand-written answer key
```

## The experiment

Three ways of cutting up the report, the same 10 questions, the same scoring.

| How the report was split | Pieces | Right page in top 5 | MRR | Median time |
|---|---|---|---|---|
| Fixed 180-word chunks, 40-word overlap | 1355 | 0.10 | 0.10 | 15.5 ms |
| Paragraphs | 249 | 0.40 | 0.27 | 14.6 ms |
| One whole page at a time | 250 | 0.40 | 0.27 | 17.6 ms |

MRR is mean reciprocal rank. If the right page comes back first it scores 1, second 0.5,
third 0.33, and so on. It rewards putting the right page near the top rather than just
somewhere in the list.

**Why whole pages win.** A number in a financial report only means something next to its
label. The figure 16,240 is unfindable on its own; it is findable when Net income sits in
the same piece of text. Cutting the report into 180-word windows separates figures from
the headings that name them and often slices a table down the middle. Keeping a page
whole keeps the number with its label, and the citation comes free, because the page is
already the thing being retrieved.

**Something I did not expect.** The paragraph strategy produced 249 pieces for 250 pages,
which means it was doing the same job as whole-page splitting. pypdf does not put blank
lines between paragraphs on this PDF, so there was nothing for it to split on. How well
the chunking worked turned out to depend on how cleanly the text came out of the PDF in
the first place. I would not have found that if I had picked one strategy instead of
comparing three.

## Example

```
$ python -m src.ask --pdf data/raw/rbc_2024.pdf "What was RBC's net income in fiscal 2024?"

In fiscal 2024, RBC generated record earnings of $16.2 billion (p. 7).
Pro forma with the HSBC Canada acquisition, estimated net income would have been
$16.6 billion (p. 195); HSBC contributed $453 million since its March 28, 2024
acquisition date (p. 7, 195).

Cited pages: [7, 49, 59, 87, 195] | LLM used: True
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add a free Gemini API key (optional; runs without it)
# download the filing -> data/raw/rbc_2024.pdf  (see data/README.md)
python -m eval.evaluate --pdf data/raw/rbc_2024.pdf
```

## What I know is weak

- The answer key is 10 questions. That is too few to draw a firm conclusion from, and
  expanding it to 20 or 30 is the first thing on the list.
- Getting the right page 4 times out of 10 is not good enough to rely on. The questions
  are short and specific and the report is dense, but that is an explanation, not an
  excuse.
- Searching on meaning alone misses questions built around exact terms like CET1 or ROE.
  Adding keyword search alongside it is the change I would make first.
- The embedding model is a small one. A larger one would likely move the numbers.
- Tables lose their headers when the text is extracted, which is a known weak spot for
  filings specifically.
- The search index checks every vector one by one. That is exact and fine at 250 to 1,355
  pieces, and it would need replacing well before this reached a serious document set.

## Roadmap

- [x] Ingest, three chunking strategies, embedding and index, retrieval, cited generation
- [x] Evaluation harness (hit@k, MRR, latency) and the hand-written answer key
- [x] Chunking comparison run over RBC's 2024 report; see reports/chunking_comparison.md
- [ ] Expand the answer key to 20-30 questions
- [ ] Add keyword search alongside the meaning-based search and re-run the comparison

## Author

Iliya Valizadeh, BSc Data Science, York University.
GitHub: [Iliya-Valizadeh](https://github.com/Iliya-Valizadeh)
