"""Scoring functions for retrieval, kept separate so they can be tested on toy examples."""

from __future__ import annotations

import numpy as np


def normalize(text: str) -> str:
    """Collapse runs of whitespace, so line breaks from PDF extraction do not block a match."""
    return " ".join(text.split()).lower()


def hit_and_rank(hits, gold_pages) -> tuple[int, float]:
    """Strict score: (1, 1/rank) for the first hit on a gold page, else (0, 0)."""
    gold = set(gold_pages)
    for rank, h in enumerate(hits, start=1):
        if h["page"] in gold:
            return 1, 1.0 / rank
    return 0, 0.0


def contains_answer(text: str, answer_any) -> bool:
    t = normalize(text)
    return any(normalize(a) in t for a in answer_any)


def lenient_hit(hits, gold_pages, answer_any) -> int:
    """1 if a retrieved chunk is on a gold page OR contains one of the answer strings.

    The answer key lists the page(s) I checked, but the same figure often appears on
    other pages too (net income 16,240 is on 13 pages). A chunk from one of those pages
    has the answer even though the strict score counts it as a miss. Questions with no
    answer strings (answer_any is None) fall back to the strict score.
    """
    if hit_and_rank(hits, gold_pages)[0]:
        return 1
    if not answer_any:
        return 0
    return int(any(contains_answer(h["text"], answer_any) for h in hits))


def bootstrap_ci(values, n_boot=1000, seed=0) -> tuple[float, float]:
    """95% percentile interval for the mean, resampling questions with replacement."""
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), (n_boot, len(v)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)
