from src.aws_budgets import BudgetRecord, summarize_budgets


def test_budget_summary_handles_missing_values():
    records = [BudgetRecord("x", "COST", None, None, None, "MONTHLY", None, None, "insufficient-evidence")]
    result = summarize_budgets(records)
    assert result["budget_count"] == 1
    assert result["limits_usd"] == 0
    assert result["actual_usd"] == 0
    assert result["forecast_usd"] == 0
