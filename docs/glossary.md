# Glossary

Each technical term has a heading and one plain sentence. Link a term to its heading
the first time it appears in each file. `make check-docs` checks this.

## Baseline

A simple method, such as the first version of a system, that a new method must beat
to be worth using.

## Bootstrap

A way to see how much a number could change: draw many new samples from the test
rows, with repeats allowed, and compute the number again on each one.

## Confidence interval

A range around a measured number that shows how much the number could move if the
test were run again on new questions.

## Chunk

One piece of a document after it has been split up for search. This project tries
three ways to split a report: fixed-length windows of words, paragraphs, and whole
pages.

## Whole page

A way of splitting a report where each page is its own chunk. A page keeps a number
next to the heading or row label that names it, which a smaller chunk can separate.

## Embedding

A list of numbers that stands for the meaning of a piece of text. Two pieces of text
with a similar meaning get embeddings that point in a similar direction.

## Dense search

Search that compares the embedding of the question with the embedding of each chunk,
and returns the chunks whose meaning is closest to the question.

## BM25

A keyword search method. It scores a chunk higher when it contains the question's
exact words, and lower for words that appear in most chunks anyway. It does not use
embeddings.

## Hybrid search

Search that runs dense search and BM25 on the same question, then merges the two
ranked lists into one. This project merges them with reciprocal rank fusion.

## Reciprocal rank fusion

A way to merge two ranked lists into one, using only each chunk's rank in each list,
not its raw score. A chunk at rank *r* in a list gets 1 divided by (a constant plus
*r*) from that list, and its scores from both lists are added together. Using rank
instead of raw score avoids having to match up two different scoring scales.

## Word piece

A small piece of a word that a language model reads one at a time. Long or rare words
are often split into more than one word piece. A model that reads only the first *n*
word pieces of a page ignores the rest of it.

## hit@5

The share of questions where a page from the answer key is in the top 5 search
results.

## Strict hit

A hit counted only when a retrieved page is exactly one of the pages the answer key
lists for that question.

## Lenient hit

A hit counted when a retrieved chunk contains the answer's text, even if that page is
not one the answer key lists. The same figure or fact can appear on more than one
page of a report.

## MRR

Mean reciprocal rank. For each question, take 1 divided by the rank of the first
correct page in the results (0 if none of the top results are correct), then average
that across all questions. A question answered at rank 1 scores higher than one
answered at rank 5.

## Answer key

The hand-built list of questions and the page or pages that hold each answer, used to
score search results.
