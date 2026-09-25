import pytest

from eval.metrics import bootstrap_ci, hit_and_rank, lenient_hit


def hits(*pages, text=""):
    return [{"page": p, "text": text} for p in pages]


def test_hit_and_rank_on_toy_examples():
    assert hit_and_rank(hits(23, 7, 9), [23]) == (1, 1.0)
    assert hit_and_rank(hits(7, 9, 23), [23]) == (1, pytest.approx(1 / 3))
    assert hit_and_rank(hits(7, 9), [23]) == (0, 0.0)
    assert hit_and_rank(hits(7, 21, 23), [21, 23]) == (1, 0.5)   # first gold page counts


def test_mrr_and_hit_rate_over_a_toy_set():
    results = [hit_and_rank(hits(1, 2), [1]), hit_and_rank(hits(2, 1), [1]),
               hit_and_rank(hits(2, 3), [1])]
    assert sum(h for h, _ in results) / 3 == pytest.approx(2 / 3)
    assert sum(r for _, r in results) / 3 == pytest.approx(0.5)


def test_lenient_hit_counts_the_answer_on_another_page():
    retrieved = [{"page": 7, "text": "record earnings of $16.2\nbillion"}]
    assert lenient_hit(retrieved, [23], ["16,240", "16.2 billion"]) == 1
    assert lenient_hit(retrieved, [23], ["2,171,582"]) == 0
    assert lenient_hit(retrieved, [23], None) == 0        # no strings: strict only


def test_bootstrap_ci_brackets_the_mean_and_is_degenerate_when_constant():
    lo, hi = bootstrap_ci([0, 1] * 10)
    assert lo < 0.5 < hi
    assert bootstrap_ci([1] * 10) == (1.0, 1.0)
