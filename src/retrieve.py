"""Thin retrieval wrapper around a built VectorIndex."""
from __future__ import annotations
from .config import TOP_K


def retrieve(index, query: str, k: int = TOP_K) -> list[dict]:
    return index.search(query, k=k)
