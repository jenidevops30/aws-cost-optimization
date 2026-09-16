from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .cost_engine import CostRecord, monthly_totals


@dataclass(frozen=True)
class Forecast:
    forecast_period: str
    baseline_monthly_cost: float
    projected_cost: float
    confidence: str
    method: str = "historical-mean"
    mode: str = "analysis-only"


@dataclass(frozen=True)
class SavingsScenario:
    name: str
    baseline_cost: float
    saving_pct: float
    projected_cost: float
    projected_saving: float
    mode: str = "analysis-only"


def forecast_next_month(records: list[CostRecord], periods: int = 3) -> Forecast:
    totals = monthly_totals(records)
    if not totals:
        raise ValueError("At least one billing period is required")
    if periods < 1:
        raise ValueError("periods must be at least 1")

    values = list(totals.values())[-periods:]
    baseline = mean(values)
    confidence = "low" if len(values) < 3 else "medium"
    last_period = list(totals)[-1]
    year, month = (int(part) for part in last_period.split("-", 1))
    month += 1
    if month == 13:
        year += 1
        month = 1
    next_period = f"{year:04d}-{month:02d}"

    return Forecast(next_period, round(baseline, 2), round(baseline, 2), confidence)


def simulate_savings(records: list[CostRecord], saving_percentages: tuple[float, ...] = (10.0, 20.0, 30.0)) -> list[SavingsScenario]:
    totals = monthly_totals(records)
    if not totals:
        raise ValueError("At least one billing period is required")
    baseline = totals[list(totals)[-1]]
    scenarios: list[SavingsScenario] = []
    for pct in saving_percentages:
        if pct < 0 or pct > 100:
            raise ValueError("saving percentages must be between 0 and 100")
        projected = baseline * (1 - pct / 100)
        scenarios.append(SavingsScenario(
            name=f"{pct:.0f}% savings",
            baseline_cost=round(baseline, 2),
            saving_pct=pct,
            projected_cost=round(projected, 2),
            projected_saving=round(baseline - projected, 2),
        ))
    return scenarios
