# 0002: Local embeddings instead of a hosted embedding service

Date: 2026-09-25. Status: accepted.

I wrote this record on 2026-09-25, from the git history. The decision itself was made
in commit `5ec3c84` on 2026-07-17. This record explains it; it does not change it.

## Context

Search needs each piece of the report turned into a vector (a list of numbers that
stands for its meaning). A model does this. It can run on my own machine, or the text
can be sent to a hosted service that returns the vectors.

The first commit, `5ec3c84`, made the choice and wrote down the reason in
`embed_index.py`: "a bank cannot ship confidential filings to a third-party [embedding](../glossary.md#embedding)
API, so this mirrors a realistic in-house setup". It uses the small
`sentence-transformers/all-MiniLM-L6-v2` model and a FAISS index that compares the
question with every vector.

RBC's report is public, so nothing in this repo needed protecting. The rule was set
for the setting the project imitates: a bank searching its own internal documents.

## Options

The history names only the general alternative, "a third-party embedding API". It
does not name a specific service.

- A hosted service. Its models are often larger and read longer text. It costs money
  per call, and every page leaves the machine.
- A small local model. It is free and the text stays on the machine. It is weaker,
  and it reads only the first 256 word pieces of any text.

## Decision

A small local model. Indexing and search should work under the rule a bank would
apply to internal documents.

## Consequences

- The model's weights download on first use. `make eval` needs a network connection
  the first time. `make demo` avoids the model on purpose (ADR 0001, decision 4).
- The code names the model but not a fixed revision of it. If its authors publish a
  new revision, the dense and hybrid numbers could change without any change here.
  [whats_weak.md](../whats_weak.md) lists this.
- The model reads only the top of a long page. This hurts whole pages with dense
  search, and it is a large part of why keyword and [hybrid search](../glossary.md#hybrid-search) help. The README
  and `notebooks/01_explore.ipynb` give the numbers.
- The privacy rule covers indexing and search only. Answer writing still sends the
  top pages to Gemini, a hosted model. Commit `e555419` added that to the README.
  Replacing the generator would change `src/bank_filings_rag/generate.py` and none of
  the search code.
