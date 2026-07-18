"""Embed chunks with a local sentence-transformers model and build a FAISS index.

Local embeddings on purpose: a bank cannot ship confidential filings to a
third-party embedding API, so this mirrors a realistic in-house setup (and costs $0).
"""
from __future__ import annotations
import numpy as np


class VectorIndex:
    def __init__(self, embed_model: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(embed_model)
        self.chunks: list[dict] = []
        self._index = None

    def build(self, chunks: list[dict]):
        import faiss
        self.chunks = chunks
        vecs = self.model.encode(
            [c["text"] for c in chunks], normalize_embeddings=True,
            show_progress_bar=True, batch_size=64,
        ).astype("float32")
        self._index = faiss.IndexFlatIP(vecs.shape[1])  # cosine via normalized dot
        self._index.add(vecs)
        return self

    def search(self, query: str, k=5) -> list[dict]:
        q = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, idx = self._index.search(q, k)
        hits = []
        for score, i in zip(scores[0], idx[0]):
            c = dict(self.chunks[i]); c["score"] = float(score)
            hits.append(c)
        return hits
