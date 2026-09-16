from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .aws_resilience import AWSObservationError, aws_client, observe, safe_error_message


@dataclass(frozen=True)
class BudgetRecord:
    name: str
    budget_type: str
    limit_usd: float | None
    actual_usd: float | None
    forecast_usd: float | None
    time_unit: str
    time_period_start: str | None
    time_period_end: str | None
    status: str
    mode: str = "analysis-only"


def _amount(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value.get("Amount", 0)), 2)
    except (AttributeError, TypeError, ValueError):
        return None


def _status(budget: dict[str, Any]) -> str:
    limit = _amount(budget.get("BudgetLimit"))
    spend = budget.get("CalculatedSpend") or {}
    actual = _amount(spend.get("ActualSpend"))
    forecast = _amount(spend.get("ForecastedSpend"))
    if limit is None or limit <= 0:
        return "insufficient-evidence"
    reference = forecast if forecast is not None else actual
    if reference is None:
        return "insufficient-evidence"
    ratio = reference / limit
    if ratio >= 1:
        return "over-budget"
    if ratio >= 0.8:
        return "near-limit"
    return "within-limit"


def get_budgets(account_id: str, region: str = "us-east-1", client=None) -> list[BudgetRecord]:
    if not account_id.strip():
        raise ValueError("account_id is required")
    client = client or aws_client("budgets", region)
    records: list[BudgetRecord] = []
    token = None
    try:
        while True:
            kwargs = {"AccountId": account_id}
            if token:
                kwargs["NextToken"] = token
            response = observe(lambda: client.describe_budgets(**kwargs))
            for budget in response.get("Budgets", []):
                period = budget.get("TimePeriod") or {}
                spend = budget.get("CalculatedSpend") or {}
                records.append(BudgetRecord(
                    name=str(budget.get("BudgetName", "unnamed")),
                    budget_type=str(budget.get("BudgetType", "UNKNOWN")),
                    limit_usd=_amount(budget.get("BudgetLimit")),
                    actual_usd=_amount(spend.get("ActualSpend")),
                    forecast_usd=_amount(spend.get("ForecastedSpend")),
                    time_unit=str(budget.get("TimeUnit", "UNKNOWN")),
                    time_period_start=period.get("Start"),
                    time_period_end=period.get("End"),
                    status=_status(budget),
                ))
            token = response.get("NextToken")
            if not token:
                break
    except AWSObservationError as exc:
        raise RuntimeError(safe_error_message(exc)) from exc
    return records


def summarize_budgets(records: list[BudgetRecord]) -> dict[str, Any]:
    return {
        "budget_count": len(records),
        "over_budget_count": sum(r.status == "over-budget" for r in records),
        "near_limit_count": sum(r.status == "near-limit" for r in records),
        "limits_usd": round(sum(r.limit_usd or 0 for r in records), 2),
        "actual_usd": round(sum(r.actual_usd or 0 for r in records), 2),
        "forecast_usd": round(sum(r.forecast_usd or 0 for r in records), 2),
        "mode": "analysis-only",
    }
