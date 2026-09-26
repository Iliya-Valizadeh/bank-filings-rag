import json

from eval.summarize import build_metrics, main


def toy_eval_results():
    """A miniature eval_results.json: just the two configurations summarize.py
    treats specially (the headline and the baseline), so the shape logic can be
    checked without the full nine-way grid."""

    def block(hit, mrr, lenient, median_ms):
        return {
            "n": 4,
            "hit": hit,
            "hit_ci": [hit - 0.1, hit + 0.1],
            "mrr": mrr,
            "mrr_ci": [mrr - 0.1, mrr + 0.1],
            "lenient": lenient,
            "lenient_ci": [lenient - 0.1, lenient + 0.1],
            "median_ms": median_ms,
        }

    return {
        "k": 5,
        "n_verified": 4,
        "n_all": 10,
        "results": [
            {
                "strategy": "fixed_words",
                "retriever": "dense",
                "n_chunks": 100,
                "verified": block(0.25, 0.2, 0.5, 17.0),
                "all": block(0.3, 0.25, 0.4, 18.0),
                "per_question": [{"id": 1, "ms": 1.0}],
            },
            {
                "strategy": "whole_page",
                "retriever": "hybrid",
                "n_chunks": 20,
                "verified": block(0.75, 0.6, 0.9, 19.0),
                "all": block(0.8, 0.65, 0.85, 20.0),
                "per_question": [{"id": 1, "ms": 2.0}],
            },
        ],
    }


def test_build_metrics_has_the_top_level_shape():
    metrics = build_metrics(toy_eval_results())
    assert metrics["k"] == 5
    assert metrics["n_questions"] == {"verified": 4, "all": 10}
    assert metrics["interval"] == {
        "method": "percentile_bootstrap",
        "resamples": 1000,
        "level": 0.95,
    }
    assert "Do not edit by hand" in metrics["about"]


def test_headline_is_whole_page_hybrid_and_baseline_is_fixed_dense():
    metrics = build_metrics(toy_eval_results())
    headline = metrics["headline"]
    assert headline["question_set"] == "verified"
    assert headline["metric"] == "hit_at_k"
    assert headline["model"] == {
        "strategy": "whole_page",
        "retriever": "hybrid",
        "value": 0.75,
        "ci_low": 0.65,
        "ci_high": 0.85,
    }
    assert headline["baseline"] == {
        "strategy": "fixed_words",
        "retriever": "dense",
        "value": 0.25,
        "ci_low": 0.15,
        "ci_high": 0.35,
    }


def test_results_block_carries_every_configuration_without_timing_keys():
    metrics = build_metrics(toy_eval_results())
    assert len(metrics["results"]) == 2
    for row in metrics["results"]:
        assert set(row) == {"strategy", "retriever", "n_chunks", "verified", "all"}
        for question_set in (row["verified"], row["all"]):
            assert set(question_set) == {"hit_at_k", "mrr", "lenient_hit_at_k"}
            for score in question_set.values():
                assert set(score) == {"value", "ci_low", "ci_high"}

    dumped = json.dumps(metrics)
    assert "median_ms" not in dumped
    assert '"ms"' not in dumped


def test_main_writes_metrics_json_from_eval_results_json(tmp_path):
    eval_results_path = tmp_path / "eval_results.json"
    metrics_path = tmp_path / "metrics.json"
    eval_results_path.write_text(json.dumps(toy_eval_results()), encoding="utf-8")

    main(["--eval-results", str(eval_results_path), "--out", str(metrics_path)])

    written = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert written["headline"]["model"]["value"] == 0.75


def test_real_eval_results_json_produces_the_documented_headline():
    """Guards against the shape drifting from docs/decisions/0001-....md section 7,
    using the real, committed reports/eval_results.json (the file the ADR names)."""
    from bank_filings_rag.config import REPORTS

    path = REPORTS / "eval_results.json"
    if not path.exists():
        return  # only present once `make eval` has run at least once
    eval_results = json.loads(path.read_text(encoding="utf-8"))
    metrics = build_metrics(eval_results)
    headline = metrics["headline"]
    assert headline["model"]["strategy"] == "whole_page"
    assert headline["model"]["retriever"] == "hybrid"
    assert headline["baseline"]["strategy"] == "fixed_words"
    assert headline["baseline"]["retriever"] == "dense"
    assert 0 <= headline["model"]["value"] <= 1
