"""Answer generation with page-level citations (free-tier Gemini, google-genai SDK).

Fail-closed: if no API key, returns the retrieved evidence so the pipeline is still
demonstrable and testable without spending anything.
"""
from __future__ import annotations
from .config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM = (
    "You answer questions about a bank's annual report using ONLY the provided excerpts. "
    "Cite the page number(s) in parentheses after each claim, e.g. (p. 42). "
    "If the excerpts do not contain the answer, say so — do not guess."
)


def build_prompt(question: str, chunks: list[dict]) -> str:
    ctx = "\n\n".join(f"[p. {c['page']}] {c['text']}" for c in chunks)
    return f"{SYSTEM}\n\nEXCERPTS:\n{ctx}\n\nQUESTION: {question}\n\nANSWER (with page citations):"


def answer(question: str, chunks: list[dict]) -> dict:
    prompt = build_prompt(question, chunks)
    cited_pages = sorted({c["page"] for c in chunks})
    if not GEMINI_API_KEY:
        return {"answer": "[no API key — showing retrieved evidence only]",
                "cited_pages": cited_pages, "chunks": chunks, "llm": False}
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return {"answer": resp.text, "cited_pages": cited_pages, "chunks": chunks, "llm": True}
