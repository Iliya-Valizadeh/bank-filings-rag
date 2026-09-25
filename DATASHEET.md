# Datasheet: bank-filings-rag answer key

Short form of the datasheet from Gebru et al., "Datasheets for Datasets"
(https://arxiv.org/abs/1803.09010). It describes the answer key,
[eval/gold_qa.jsonl](eval/gold_qa.jsonl). The report it points into, RBC's 2024 Annual
Report, is not part of this repo (see [data/README.md](data/README.md)).

## In plain words

The answer key is a list of 30 questions about one bank report. For each question it
says which page has the answer. The search is scored by whether it finds that page. I
have read the page for 12 of the questions myself. A script checked the other 18. It is
small, and it covers one report.

## Motivation

The key exists to score the search in this repo. It lets `make eval` measure how often
the right page is in the top 5 results. It was made for this project and no other.

## Composition

One row is one question. There are 30 rows. Each row has these fields:

- `id`: the question number
- `question` and `answer`: the question, and the answer in words
- `source_pages`: the page or pages that hold the answer, as 1-based PDF page numbers
- `answer_any`: short strings, such as a figure, used by the lenient score. Questions 8
  and 10 have none
- `kind`: `original` for the first 10, then `exact_term`, `narrative`, `table` or
  `multi_page`
- `verified` and `verified_by`: whether a person read the page (`hand`) or only a
  script checked it (`script`)
- `check_label` and `check_figure`: a label and a figure for the stricter script check,
  on questions 11 to 30 only
- `notes`: free text

Most questions have one answer page. Seven have two.

## Collection

The first 10 questions came with the first commit, `5ec3c84` (2026-07-17). They were
written and checked by reading the report. The key did not record that until
`8b69b7b` added the `verified` flag.

Questions 11 to 30 came in `8b69b7b` (2026-09-24), after the first results were known.
Each had a proposed page. Claude, an AI assistant, is listed as co-author of that
commit. The new questions were picked to cover exact terms (PCL, NIM, LCR, NSFR, RWA),
segment tables, plain facts, and answers that span two pages.

## Checks

`eval/check_gold.py` runs two checks on each proposed page. The first looks for an
answer string anywhere on the page. 28 pass. Questions 8 and 10 have no answer strings,
so this check cannot run on them. The second looks for the label and
the figure in the same passage, close together. 18 of the 20 new questions pass it. The
other two, Q28 and Q29, were read by hand in `e1f89c9`. The results are in
[eval/gold_check.md](eval/gold_check.md).

The answer strings for the first 10 questions were added in `8b69b7b`, with the
lenient score. After that, the answer text changed for three questions: Q7 and Q8 in
`c24f6ac`, and Q29 in `e1f89c9`. No page number or answer string has changed since each
was first written. A comparison of every version of the file in git confirms this.

## Uses

It fits one use: scoring page retrieval over this one report. It does not fit scoring
answer quality, since the `answer` field is not compared with any output. It does not
fit other reports, other banks or other years.

## Known limits

- It is small. With 12 hand-checked questions, one question moves hit@5 by about 0.08.
- 18 questions are checked by script only. A script can catch a wrong page, but not a
  badly worded question or a wrong answer.
- The key lists one or two pages per question. The same figure often appears on other pages too, so
  the strict score undercounts. The lenient score is there to show by how much.
- The new questions were written after the first results were known. No second
  person has reviewed the key.
- Only 2 questions are marked as table questions, though much of a bank report is
  tables.

## Distribution and maintenance

The key is in this repo, under the repo's MIT license. The report's text is not copied
into it beyond short answer strings. I maintain it. When I read one of the 18
unread pages, the row changes to `"verified_by": "hand"` in its own commit, and the
[eval plan](docs/eval_plan.md) notes the change.
