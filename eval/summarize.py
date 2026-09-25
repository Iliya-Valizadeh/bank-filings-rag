"""Build reports/metrics.json from reports/eval_results.json.

Decision and shape: docs/decisions/0001-adopting-the-house-standard.md, section 7.

This script copies values out of eval_results.json. It does not recompute anything,
so a claim in the docs can point straight at metrics.json and trust the number came
from the actual eval run, not from a script bug. It drops the timing keys
(`median_ms`, `ms`), because the README already says latency varies run to run and
those keys would make metrics.json change on every run even when nothing else did.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bank_filings_rag.config import REPORTS

EVAL_RESULTS = REPORTS / "eval_results.json"
METRICS = REPORTS / "metrics.json"

# The headline and baseline configurations. Fixed by the ADR: whole pages with
# hybrid search is the headline, fixed-size chunks with dense search is the
# baseline. Both are read on the "verified" (hand-checked) question set.
HEADLINE_STRATEGY = "whole_page"
HEADLINE_RETRIEVER = "hybrid"
BASELINE_STRATEGY = "fixed_words"
BASELINE_RETRIEVER = "dense"

# The bootstrap settings eval/metrics.py actually uses (bootstrap_ci: n_boot=1000,
# a 95% percentile interval). Recorded here, not recomputed, so a change to
# eval/metrics.py that is not reflected here would be caught by test_summarize.py.
INTERVAL = {"method": "percentile_bootstrap", "resamples": 1000, "level": 0.95}


def _score_block(question_set: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Pull hit@k, MRR and the lenient score (with their intervals) out of one
    verified/all block, leaving out n and the timing key (median_ms)."""
    lo, hi = question_set["hit_ci"]
    mrr_lo, mrr_hi = question_set["mrr_ci"]
    lenient_lo, lenient_hi = question_set["lenient_ci"]
    return {
        "hit_at_k": {"value": question_set["hit"], "ci_low": lo, "ci_high": hi},
        "mrr": {"value": question_set["mrr"], "ci_low": mrr_lo, "ci_high": mrr_hi},
        "lenient_hit_at_k": {
            "value": question_set["lenient"],
            "ci_low": lenient_lo,
            "ci_high": lenient_hi,
        },
    }


def _find_result(results: list[dict[str, Any]], strategy: str, retriever: str) -> dict[str, Any]:
    for r in results:
        if r["strategy"] == strategy and r["retriever"] == retriever:
            return r
    raise ValueError(f"No result for strategy={strategy!r} retriever={retriever!r}")


def build_metrics(eval_results: dict[str, Any]) -> dict[str, Any]:
    """Turn the raw eval_results.json dict into the metrics.json dict. Pure
    function of its input, so it is easy to test without touching disk."""
    results = eval_results["results"]
    headline_result = _find_result(results, HEADLINE_STRATEGY, HEADLINE_RETRIEVER)
    baseline_result = _find_result(results, BASELINE_STRATEGY, BASELINE_RETRIEVER)

    headline_scores = _score_block(headline_result["verified"])["hit_at_k"]
    baseline_scores = _score_block(baseline_result["verified"])["hit_at_k"]

    return {
        "about": (
            "Built by eval/summarize.py from reports/eval_results.json. Do not edit by hand."
        ),
        "k": eval_results["k"],
        "n_questions": {
            "verified": eval_results["n_verified"],
            "all": eval_results["n_all"],
        },
        "interval": dict(INTERVAL),
        "headline": {
            "question_set": "verified",
            "metric": "hit_at_k",
            "model": {
                "strategy": HEADLINE_STRATEGY,
                "retriever": HEADLINE_RETRIEVER,
                **headline_scores,
            },
            "baseline": {
                "strategy": BASELINE_STRATEGY,
                "retriever": BASELINE_RETRIEVER,
                **baseline_scores,
            },
        },
        "results": [
            {
                "strategy": r["strategy"],
                "retriever": r["retriever"],
                "n_chunks": r["n_chunks"],
                "verified": _score_block(r["verified"]),
                "all": _score_block(r["all"]),
            }
            for r in results
        ],
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval-results", type=Path, default=EVAL_RESULTS)
    ap.add_argument("--out", type=Path, default=METRICS)
    args = ap.parse_args(argv)

    eval_results = json.loads(args.eval_results.read_text(encoding="utf-8"))
    metrics = build_metrics(eval_results)
    args.out.write_text(json.dumps(metrics, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
