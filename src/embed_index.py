"""Embed chunks with a local sentence-transformers model and build a FAISS index.

Local embeddings on purpose: a bank cannot ship confidential filings to a
third-party embedding API, so this mirrors a realistic in-house setup (and costs $0).

Note: all-MiniLM-L6-v2 reads at most 256 word pieces per text and ignores the rest.
A whole page here is ~4,700 characters (roughly 1,000 word pieces), so page-level
vectors only see the top of each page. See README, "What I know is weak".
"""
from __future__ import annotations
import numpy as np


class VectorIndex:
    def __init__(self, embed_model: str | None = None, encoder=None):
        """Pass either a sentence-transformers model name or any object with an
        `encode(texts, normalize_embeddings=True, **kw)` method (the tests use a fake)."""
        if encoder is None:
            from sentence_transformers import SentenceTransformer
            encoder = SentenceTransformer(embed_model)
        self.model = encoder
        self.chunks: list[dict] = []
        self._index = None

    def build(self, chunks: list[dict]):
        import faiss
        self.chunks = chunks
        vecs = np.asarray(self.model.encode(
            [c["text"] for c in chunks], normalize_embeddings=True,
            show_progress_bar=False, batch_size=64,
        ), dtype="float32")
        self._index = faiss.IndexFlatIP(vecs.shape[1])  # cosine via normalized dot
        self._index.add(vecs)
        return self

    def search(self, query: str, k=5) -> list[dict]:
        k = min(k, len(self.chunks))
        q = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype="float32")
        scores, idx = self._index.search(q, k)
        hits = []
        for score, i in zip(scores[0], idx[0]):
            c = dict(self.chunks[i]); c["score"] = float(score)
            hits.append(c)
        return hits
