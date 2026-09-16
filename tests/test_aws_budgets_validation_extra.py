from src.aws_budgets import _status


def test_missing_spend_is_insufficient_evidence():
    assert _status({"BudgetLimit": {"Amount": "100"}}) == "insufficient-evidence"
