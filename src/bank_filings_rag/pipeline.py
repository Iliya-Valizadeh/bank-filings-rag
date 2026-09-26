"""End-to-end: question -> retrieve -> cited answer."""

from __future__ import annotations

from .generate import answer
from .retrieve import retrieve


def ask(index, question: str, k=5) -> dict:
    hits = retrieve(index, question, k=k)
    return answer(question, hits)
