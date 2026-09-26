"""Three retrievers with the same interface: build(chunks), then search(query, k).

- dense:  meaning-based search over sentence embeddings (embed_index.VectorIndex)
- bm25:   keyword search. Scores chunks by how often they contain the query's words,
          weighting rare words (like "CET1") more than common ones (like "RBC").
- hybrid: runs both and merges the two rankings with reciprocal rank fusion (RRF):
          each chunk scores sum(1 / (60 + rank)) over the lists it appears in. RRF only
          uses ranks, so the two very different score scales never need matching up.
"""

from __future__ import annotations

import re

from .config import TOP_K

_TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*")
RRF_K = 60  # the constant from Cormack et al. (2009); larger = flatter weighting
FUSION_DEPTH = 50  # how far down each list RRF looks


def tokenize(text: str) -> list[str]:
    """Lowercase words and numbers. Keeps '16,240' and '13.2' whole so figures can match."""
    return _TOKEN.findall(text.lower())


class BM25Index:
    def build(self, chunks: list[dict]):
        from rank_bm25 import BM25Okapi

        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])
        return self

    def search(self, query: str, k=5) -> list[dict]:
        scores = self._bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [dict(self.chunks[i], score=float(scores[i])) for i in order]


class HybridIndex:
    def __init__(self, dense, lexical):
        self.dense, self.lexical = dense, lexical

    def build(self, chunks: list[dict]):
        self.chunks = chunks
        self.dense.build(chunks)
        self.lexical.build(chunks)
        return self

    @classmethod
    def from_built(cls, dense, lexical):
        """Fuse two indexes that are already built over the same chunks."""
        h = cls(dense, lexical)
        h.chunks = dense.chunks
        return h

    def search(self, query: str, k=5) -> list[dict]:
        fused: dict[str, float] = {}
        by_id = {}
        for hits in (
            self.dense.search(query, FUSION_DEPTH),
            self.lexical.search(query, FUSION_DEPTH),
        ):
            for rank, h in enumerate(hits, start=1):
                fused[h["chunk_id"]] = fused.get(h["chunk_id"], 0.0) + 1.0 / (RRF_K + rank)
                by_id[h["chunk_id"]] = h
        order = sorted(fused, key=lambda cid: -fused[cid])[:k]
        return [dict(by_id[cid], score=fused[cid]) for cid in order]


def build_index(kind: str, chunks: list[dict], embed_model: str | None = None, encoder=None):
    from .embed_index import VectorIndex

    if kind == "dense":
        return VectorIndex(embed_model, encoder).build(chunks)
    if kind == "bm25":
        return BM25Index().build(chunks)
    if kind == "hybrid":
        return HybridIndex(VectorIndex(embed_model, encoder), BM25Index()).build(chunks)
    raise ValueError(f"unknown retriever: {kind}")


RETRIEVERS = ("dense", "bm25", "hybrid")


def retrieve(index, query: str, k: int = TOP_K) -> list[dict]:
    return index.search(query, k=k)
