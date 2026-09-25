import pytest

from src import chunking


@pytest.mark.parametrize("name", list(chunking.STRATEGIES))
def test_every_chunk_keeps_a_real_page_number(pages, name):
    chunks = chunking.STRATEGIES[name](pages)
    valid = {p["page"] for p in pages}
    assert chunks
    assert all(c["page"] in valid for c in chunks)
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)


@pytest.mark.parametrize("name", list(chunking.STRATEGIES))
def test_chunk_text_comes_from_its_own_page(pages, name):
    text = {p["page"]: " ".join(p["text"].split()) for p in pages}
    for c in chunking.STRATEGIES[name](pages):
        first_words = " ".join(c["text"].split()[:3])
        assert first_words in text[c["page"]]


def test_no_text_is_dropped_by_paragraph_chunking(pages):
    chunks = chunking.paragraph(pages, min_chars=200, max_chars=300)
    for p in pages:
        joined = " ".join(c["text"] for c in chunks if c["page"] == p["page"])
        for block in p["blocks"]:
            assert block in joined


def test_paragraph_splits_on_blocks_not_blank_lines(pages):
    # pypdf text has no blank lines here, like the real report. The old chunker returned
    # one chunk per page; with blocks, a small max_chars must give more chunks than pages.
    assert len(chunking.paragraph(pages, max_chars=100)) > len(pages)


def test_paragraph_refuses_pages_without_blocks(pages):
    with pytest.raises(ValueError):
        chunking.paragraph([{"page": 1, "text": "no blocks here"}])
