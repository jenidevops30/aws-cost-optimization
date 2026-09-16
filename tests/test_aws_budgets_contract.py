from pathlib import Path


def test_budget_collector_has_no_mutation_operations():
    source = Path("src/aws_budgets.py").read_text(encoding="utf-8")
    assert "describe_budgets" in source
    assert "create_budget" not in source.lower()
    assert "modify_budget" not in source.lower()
    assert "delete_budget" not in source.lower()
