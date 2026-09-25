import pytest

from src import chunking
from src.retrieve import RETRIEVERS, build_index, tokenize


def test_tokenize_keeps_figures_and_acronyms_whole():
    assert tokenize("CET1 ratio of 13.2%, net income $16,240") == [
        "cet1", "ratio", "of", "13.2", "net", "income", "16,240"]


@pytest.mark.parametrize("kind", RETRIEVERS)
@pytest.mark.parametrize("k", [1, 2, 3])
def test_search_returns_k_items_with_pages(pages, encoder, kind, k):
    index = build_index(kind, chunking.whole_page(pages), encoder=encoder)
    hits = index.search("CET1 ratio", k=k)
    assert len(hits) == k
    assert all("page" in h and "score" in h for h in hits)


@pytest.mark.parametrize("kind", RETRIEVERS)
def test_k_larger_than_index_returns_everything_once(pages, encoder, kind):
    index = build_index(kind, chunking.whole_page(pages), encoder=encoder)
    hits = index.search("net income", k=50)
    assert len(hits) == len(pages)
    assert len({h["chunk_id"] for h in hits}) == len(pages)


@pytest.mark.parametrize("kind", RETRIEVERS)
def test_exact_term_question_finds_its_page(pages, encoder, kind):
    index = build_index(kind, chunking.whole_page(pages), encoder=encoder)
    assert index.search("What was the CET1 ratio?", k=1)[0]["page"] == 21
