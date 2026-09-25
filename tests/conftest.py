"""Fixtures that need neither the PDF nor the embedding model, so the tests run in CI."""
import zlib

import numpy as np
import pytest

from src.retrieve import tokenize


class FakeEncoder:
    """Bag-of-words hashed into 64 dimensions. Crude, but texts that share words get
    similar vectors, which is all the retrieval tests need."""

    dim = 64

    def encode(self, texts, normalize_embeddings=True, **_):
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for i, t in enumerate(texts):
            for w in tokenize(t):
                out[i, zlib.crc32(w.encode()) % self.dim] += 1
        if normalize_embeddings:
            out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)
        return out


@pytest.fixture
def encoder():
    return FakeEncoder()


@pytest.fixture
def pages():
    """Three toy pages, with layout blocks as ingest.load_pages returns them."""
    blocks = {
        4: ["Royal Bank of Canada", "98,000+ employees in 29 countries", "Our purpose"],
        21: ["Capital strength", "CET1 ratio of 13.2%", "Return on equity 14.4%",
             ("A long paragraph " + "about capital management " * 30).strip()],
        23: ["Selected financial highlights", "Net income $ 16,240 $ 14,612",
             "Total assets $ 2,171,582"],
    }
    return [{"page": p, "text": "\n".join(b), "blocks": b} for p, b in blocks.items()]
