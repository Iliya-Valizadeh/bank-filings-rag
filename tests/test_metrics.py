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


def test_label_and_figure_check_needs_them_in_the_same_block():
    from eval.check_gold import label_figure_gap
    blocks = ["Net income $ 729 $ 549", "Total revenue 1,729"]
    assert label_figure_gap(blocks, ["Net income"], ["729"]) == 13
    assert label_figure_gap(["Net income $ 5", "Revenue 729"], ["Net income"], ["729"]) is None
    assert label_figure_gap(["Total revenue 1,729"], ["Total revenue"], ["729"]) is None
    assert label_figure_gap(["CET1 ratio was 13.2%, down"], ["CET1 ratio"], ["13.2%"]) == 15
    # A footnote marker after a year must not hide a phrase figure.
    assert label_figure_gap(["NZBA ... net-zero emissions by 20503."], ["NZBA"],
                            ["net-zero emissions by 2050"]) is not None
