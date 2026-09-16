from __future__ import annotations

from src.aws_budgets import get_budgets, summarize_budgets


class FakeBudgets:
    def __init__(self):
        self.calls = []

    def describe_budgets(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return {
                "Budgets": [{
                    "BudgetName": "monthly",
                    "BudgetType": "COST",
                    "BudgetLimit": {"Amount": "100", "Unit": "USD"},
                    "CalculatedSpend": {
                        "ActualSpend": {"Amount": "75.5", "Unit": "USD"},
                        "ForecastedSpend": {"Amount": "85", "Unit": "USD"},
                    },
                    "TimeUnit": "MONTHLY",
                    "TimePeriod": {"Start": "2026-09-01", "End": "2026-10-01"},
                }],
                "NextToken": "next",
            }
        return {
            "Budgets": [{
                "BudgetName": "quarterly",
                "BudgetType": "COST",
                "BudgetLimit": {"Amount": "200", "Unit": "USD"},
                "CalculatedSpend": {"ActualSpend": {"Amount": "210", "Unit": "USD"}},
                "TimeUnit": "QUARTERLY",
            }]
        }


def test_get_budgets_paginates_and_preserves_spend():
    client = FakeBudgets()
    records = get_budgets("123456789012", client=client)
    assert [r.name for r in records] == ["monthly", "quarterly"]
    assert records[0].forecast_usd == 85.0
    assert records[0].status == "near-limit"
    assert records[1].status == "over-budget"
    assert client.calls[1]["NextToken"] == "next"


def test_summary_is_deterministic():
    client = FakeBudgets()
    summary = summarize_budgets(get_budgets("123456789012", client=client))
    assert summary == {
        "budget_count": 2,
        "over_budget_count": 1,
        "near_limit_count": 1,
        "limits_usd": 300.0,
        "actual_usd": 285.5,
        "forecast_usd": 85.0,
        "mode": "analysis-only",
    }


def test_missing_limit_is_insufficient_evidence():
    client = FakeBudgets()
    client.describe_budgets = lambda **kwargs: {"Budgets": [{"BudgetName": "unknown"}]}
    record = get_budgets("123456789012", client=client)[0]
    assert record.status == "insufficient-evidence"
