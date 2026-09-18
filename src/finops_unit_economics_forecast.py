from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class UnitEconomicsForecastEvidence:
    period: str
    workload: str
    cost: float
    units: float

    def __post_init__(self) -> None:
        if self.cost < 0 or self.units < 0:
            raise ValueError("cost and units must be non-negative")
        if not self.period.strip() or not self.workload.strip():
            raise ValueError("period and workload are required")

def forecast_rows(records: Iterable[UnitEconomicsForecastEvidence]) -> list[dict[str, object]]:
    grouped: dict[str, list[UnitEconomicsForecastEvidence]] = {}
    for record in records:
        grouped.setdefault(record.workload, []).append(record)
    rows = []
    for workload, items in grouped.items():
        ordered = sorted(items, key=lambda r: r.period)
        costs = [r.cost / r.units for r in ordered if r.units > 0]
        forecast = sum(costs) / len(costs) if costs else None
        rows.append({
            "workload": workload,
            "observed_periods": len(costs),
            "historical_unit_cost_mean": forecast,
            "next_period_unit_cost_forecast": forecast,
            "evidence_status": "available" if forecast is not None else "unavailable",
            "forecast_method": "historical-mean",
            "confidence": "low" if len(costs) < 3 else "medium",
        })
    return sorted(rows, key=lambda r: str(r["workload"]))
