"""Chunking strategies — the object of the comparison experiment.

Each strategy takes per-page records and returns chunks that CARRY THEIR PAGE,
so every retrieved chunk can be cited to a page in the filing.

Chunk = {"chunk_id", "text", "page", "strategy"}.
"""
from __future__ import annotations


def _wrap(chunks_text_page, strategy):
    return [
        {"chunk_id": f"{strategy}-{i}", "text": t, "page": p, "strategy": strategy}
        for i, (t, p) in enumerate(chunks_text_page)
    ]


def fixed_words(pages, size=180, overlap=40):
    """Fixed-size windows over words, with overlap. Simple, strong baseline."""
    out = []
    for rec in pages:
        words = rec["text"].split()
        step = max(1, size - overlap)
        for start in range(0, len(words), step):
            chunk = " ".join(words[start:start + size])
            if chunk.strip():
                out.append((chunk, rec["page"]))
    return _wrap(out, f"fixed_w{size}_o{overlap}")


def paragraph(pages, min_chars=200, max_chars=1200):
    """Split on blank lines, then pack paragraphs up to max_chars."""
    out = []
    for rec in pages:
        buf = ""
        for para in [p.strip() for p in rec["text"].split("\n\n") if p.strip()]:
            if len(buf) + len(para) + 1 <= max_chars:
                buf = (buf + "\n" + para).strip()
            else:
                if buf:
                    out.append((buf, rec["page"]))
                buf = para
        if len(buf) >= min_chars or (buf and not out):
            out.append((buf, rec["page"]))
    return _wrap(out, f"paragraph_max{max_chars}")


def whole_page(pages):
    """One chunk per page. Coarse control condition."""
    return _wrap([(r["text"], r["page"]) for r in pages], "whole_page")


STRATEGIES = {
    "fixed_words": fixed_words,
    "paragraph": paragraph,
    "whole_page": whole_page,
}
