from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .cost_engine import CostRecord


@dataclass(frozen=True)
class Anomaly:
    period: str
    service: str
    cost: float
    baseline: float
    change_pct: float
    severity: str


@dataclass(frozen=True)
class Opportunity:
    service: str
    current_cost: float
    baseline_cost: float
    potential_monthly_saving: float
    rationale: str
    confidence: str


def detect_anomalies(records: list[CostRecord], threshold_pct: float = 30.0) -> list[Anomaly]:
    grouped: dict[tuple[str, str], float] = {}
    periods_by_service: dict[str, list[str]] = {}
    for record in records:
        grouped[(record.billing_period, record.service)] = grouped.get((record.billing_period, record.service), 0.0) + record.cost
        periods_by_service.setdefault(record.service, []).append(record.billing_period)

    anomalies: list[Anomaly] = []
    for service, periods in periods_by_service.items():
        ordered = sorted(set(periods))
        for index, period in enumerate(ordered):
            if index == 0:
                continue
            current = grouped[(period, service)]
            previous = grouped[(ordered[index - 1], service)]
            if previous == 0:
                continue
            change_pct = ((current - previous) / previous) * 100
            if abs(change_pct) >= threshold_pct:
                severity = "high" if abs(change_pct) >= 75 else "medium"
                anomalies.append(Anomaly(period, service, current, previous, change_pct, severity))
    return sorted(anomalies, key=lambda item: abs(item.change_pct), reverse=True)


def savings_opportunities(records: list[CostRecord]) -> list[Opportunity]:
    by_service: dict[str, list[float]] = {}
    for record in records:
        by_service.setdefault(record.service, []).append(record.cost)

    opportunities: list[Opportunity] = []
    for service, values in by_service.items():
        if len(values) < 2:
            continue
        current = values[-1]
        baseline = mean(values[:-1])
        if current <= baseline or baseline == 0:
            continue
        saving = current - baseline
        opportunities.append(
            Opportunity(
                service=service,
                current_cost=current,
                baseline_cost=baseline,
                potential_monthly_saving=saving,
                rationale="Latest period is above the available historical baseline; validate usage, sizing, and commitment options before acting.",
                confidence="analysis-only",
            )
        )
    return sorted(opportunities, key=lambda item: item.potential_monthly_saving, reverse=True)
