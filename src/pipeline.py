"""End-to-end: question -> retrieve -> cited answer."""
from __future__ import annotations
from .retrieve import retrieve
from .generate import answer


def ask(index, question: str, k=5) -> dict:
    hits = retrieve(index, question, k=k)
    return answer(question, hits)
