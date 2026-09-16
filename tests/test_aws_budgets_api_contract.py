from pathlib import Path


def test_budget_module_uses_read_only_describe_api():
    source = Path("src/aws_budgets.py").read_text(encoding="utf-8")
    assert "describe_budgets" in source
    assert "CreateBudget" not in source
    assert "ModifyBudget" not in source
    assert "DeleteBudget" not in source
