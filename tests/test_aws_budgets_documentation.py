from pathlib import Path


def test_budget_docs_reference_governance():
    for name in ("README.md", "PROJECT.md", "IMPLEMENTATION.md"):
        text = Path(name).read_text(encoding="utf-8")
        assert "Budget" in text
