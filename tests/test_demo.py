"""`make demo` must run with no downloads, no keys, and no network call.

These tests exercise the real demo module against the small committed PDF
(data/demo/demo_filing.pdf), the same file `make demo` uses.
"""

import ast
import inspect

from bank_filings_rag import demo


def test_run_finds_every_made_up_page():
    rows = demo.run()
    assert len(rows) == len(demo.DEMO_QUESTIONS)
    assert all(r["hit"] for r in rows)
    assert [r["top_page"] for r in rows] == [1, 2, 3, 4]


def test_main_warns_the_output_is_a_smoke_test_and_returns_zero(capsys):
    assert demo.main() == 0
    out = capsys.readouterr().out
    assert "made up" in out
    assert "keyword-only" in out
    assert "smoke test" in out


def test_source_never_imports_generate_or_the_embedding_model():
    # generate.py holds the Gemini call; embed_index.py/sentence_transformers/torch
    # load the embedding model. This checks the actual import statements (an AST
    # walk), not a sys.modules check: other test files import those modules too, and
    # pytest collects every test file (importing it) before any test runs, so
    # sys.modules is not a reliable signal here. The real proof that the demo needs
    # neither is that `make demo` runs with the `embed` extra not installed at all
    # (verified locally and in CI).
    forbidden = {"generate", "embed_index", "sentence_transformers", "torch"}
    names = set()
    for node in ast.walk(ast.parse(inspect.getsource(demo))):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
            names.update(a.name for a in node.names)
    assert names.isdisjoint(forbidden)
