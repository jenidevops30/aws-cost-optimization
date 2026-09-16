from src.aws_budgets import _status


def test_budget_thresholds():
    assert _status({"BudgetLimit": {"Amount": "100"}, "CalculatedSpend": {"ActualSpend": {"Amount": "79"}}}) == "within-limit"
    assert _status({"BudgetLimit": {"Amount": "100"}, "CalculatedSpend": {"ActualSpend": {"Amount": "80"}}}) == "near-limit"
    assert _status({"BudgetLimit": {"Amount": "100"}, "CalculatedSpend": {"ForecastedSpend": {"Amount": "100"}}}) == "over-budget"
