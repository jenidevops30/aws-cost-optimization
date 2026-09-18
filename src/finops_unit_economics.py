from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class UnitEconomicsEvidence:
    period: str
    workload: str
    cost: float
    units: float
    unit_name: str
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.cost < 0 or self.units < 0:
            raise ValueError("cost and units must be non-negative")
        if not self.workload.strip() or not self.unit_name.strip():
            raise ValueError("workload and unit_name are required")


def cost_per_unit(record: UnitEconomicsEvidence) -> float | None:
    if record.units == 0:
        return None
    return record.cost / record.units


def aggregate_unit_economics(records: Iterable[UnitEconomicsEvidence]) -> list[dict[str, object]]:
    totals: dict[tuple[str, str, str], list[float]] = {}
    for record in records:
        key = (record.period, record.workload, record.unit_name)
        cost, units = totals.setdefault(key, [0.0, 0.0])
        totals[key] = [cost + record.cost, units + record.units]
    return [
        {"period": p, "workload": w, "unit_name": u, "cost": c, "units": n,
         "cost_per_unit": None if n == 0 else c / n}
        for (p, w, u), (c, n) in sorted(totals.items())
    ]


def unit_economics_review_flags(record: UnitEconomicsEvidence) -> list[str]:
    if record.units == 0:
        return ["unit-volume-unavailable"]
    if record.cost == 0:
        return ["zero-cost-review"]
    return []
