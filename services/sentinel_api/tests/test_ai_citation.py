from app.ai.context_builder import build_context, validate_citations


def test_citation_validation():
    supplied = ["ev1", "ev2"]
    answer = "Based on [ev1] and [ev999] evidence."
    valid, invalid = validate_citations(answer, supplied)
    assert "ev1" in valid
    assert "ev999" in invalid


def test_build_context_bounds():
    records = [
        {"id": f"r{i}", "type": "evidence", "content": "x" * 100} for i in range(1000)
    ]
    ctx = build_context("q", records, max_chars=500)
    assert len(ctx) <= 2000
    assert "SYSTEM:" in ctx
