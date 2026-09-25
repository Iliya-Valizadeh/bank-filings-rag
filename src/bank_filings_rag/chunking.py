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
            chunk = " ".join(words[start : start + size])
            if chunk.strip():
                out.append((chunk, rec["page"]))
    return _wrap(out, f"fixed_w{size}_o{overlap}")


def paragraph(pages, min_chars=200, max_chars=1200):
    """Pack the page's layout blocks (see ingest.load_blocks) into chunks up to max_chars.

    The first version split pypdf text on blank lines. pypdf emits none on this PDF, so
    every page came out as a single chunk (249 chunks for 250 pages) and the strategy was
    whole-page splitting under another name. It now needs the layout blocks and fails
    loudly without them, rather than falling back to whole pages without saying so.
    """
    out = []
    for rec in pages:
        if "blocks" not in rec:
            raise ValueError("paragraph chunking needs layout blocks: use ingest.load_pages")
        buf = ""
        for para in [p.strip() for p in rec["blocks"] if p.strip()]:
            if len(buf) + len(para) + 1 <= max_chars:
                buf = (buf + "\n" + para).strip()
            else:
                if buf:
                    out.append((buf, rec["page"]))
                buf = para
        if not buf:
            continue
        # A short leftover joins the previous chunk from the same page instead of being
        # dropped (the first version dropped it, losing page footers and short answers).
        if len(buf) < min_chars and out and out[-1][1] == rec["page"]:
            out[-1] = (out[-1][0] + "\n" + buf, rec["page"])
        else:
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
