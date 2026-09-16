from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class GovernanceSnapshot:
    latest_period: str | None
    latest_cost_usd: float | None
    previous_cost_usd: float | None
    month_over_month_pct: float | None
    forecast_usd: float | None
    forecast_confidence: str | None
    budget_count: int
    over_budget_count: int
    near_limit_count: int
    anomaly_count: int
    anomaly_impact_usd: float
    finding_count: int
    validation_status: str
    evidence_status: str
    mode: str = "analysis-only"


def build_governance_snapshot(
    monthly: Iterable[dict[str, Any]],
    budgets: Iterable[dict[str, Any]] = (),
    anomalies: Iterable[dict[str, Any]] = (),
    findings: Iterable[dict[str, Any]] = (),
    forecast: dict[str, Any] | None = None,
    validation: dict[str, Any] | None = None,
) -> GovernanceSnapshot:
    months = list(monthly)
    budget_rows = list(budgets)
    anomaly_rows = list(anomalies)
    finding_rows = list(findings)

    latest = months[-1] if months else {}
    previous = months[-2] if len(months) > 1 else {}
    latest_cost = _number(latest.get("cost"))
    previous_cost = _number(previous.get("cost"))
    mom = None
    if latest_cost is not None and previous_cost not in (None, 0):
        mom = round(((latest_cost - previous_cost) / previous_cost) * 100, 2)

    over = sum(1 for row in budget_rows if row.get("status") == "over-budget")
    near = sum(1 for row in budget_rows if row.get("status") == "near-limit")
    impact = sum(_number(row.get("estimated_impact_usd")) or 0.0 for row in anomaly_rows)

    validation_status = (validation or {}).get("validation_status", "not-provided")
    evidence_status = _evidence_status(months, budget_rows, anomaly_rows)
    return GovernanceSnapshot(
        latest_period=latest.get("period"),
        latest_cost_usd=latest_cost,
        previous_cost_usd=previous_cost,
        month_over_month_pct=mom,
        forecast_usd=_number((forecast or {}).get("projected_cost")),
        forecast_confidence=(forecast or {}).get("confidence"),
        budget_count=len(budget_rows),
        over_budget_count=over,
        near_limit_count=near,
        anomaly_count=len(anomaly_rows),
        anomaly_impact_usd=round(impact, 2),
        finding_count=len(finding_rows),
        validation_status=validation_status,
        evidence_status=evidence_status,
    )


def _number(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _evidence_status(months: list[dict[str, Any]], budgets: list[dict[str, Any]], anomalies: list[dict[str, Any]]) -> str:
    if not months:
        return "insufficient-evidence"
    if budgets or anomalies:
        return "multi-signal"
    return "cost-only"


def snapshot_to_dict(snapshot: GovernanceSnapshot) -> dict[str, Any]:
    return {field: getattr(snapshot, field) for field in snapshot.__dataclass_fields__}
