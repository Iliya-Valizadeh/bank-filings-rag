from bank_filings_rag import generate


def test_empty_context_refuses_without_calling_the_model(monkeypatch):
    # A key is set, so the only thing stopping a model call is the refusal path.
    monkeypatch.setattr(generate, "GEMINI_API_KEY", "set-but-must-not-be-used")

    def fail(*_, **__):
        raise AssertionError("the model must not be called with no context")

    import google.genai
    monkeypatch.setattr(google.genai, "Client", fail)
    for chunks in ([], [{"page": 3, "text": "   "}]):
        res = generate.answer("What was net income?", chunks)
        assert res["answer"] == generate.REFUSAL
        assert res["llm"] is False and res["cited_pages"] == []


def test_without_api_key_returns_evidence_and_pages(monkeypatch):
    monkeypatch.setattr(generate, "GEMINI_API_KEY", "")
    chunks = [{"page": 23, "text": "Net income 16,240"}, {"page": 7, "text": "$16.2 billion"}]
    res = generate.answer("What was net income?", chunks)
    assert res["llm"] is False
    assert res["cited_pages"] == [7, 23]


def test_prompt_labels_every_excerpt_with_its_page():
    prompt = generate.build_prompt("q", [{"page": 5, "text": "a"}, {"page": 9, "text": "b"}])
    assert "[p. 5] a" in prompt and "[p. 9] b" in prompt
    assert "do not guess" in prompt
