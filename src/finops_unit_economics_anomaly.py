from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class UnitEconomicsAnomalyEvidence:
    period: str
    workload: str
    cost: float
    units: float

    def __post_init__(self) -> None:
        if self.cost < 0 or self.units < 0:
            raise ValueError("cost and units must be non-negative")
        if not self.period.strip() or not self.workload.strip():
            raise ValueError("period and workload are required")

def _unit_cost(record: UnitEconomicsAnomalyEvidence) -> float | None:
    return None if record.units == 0 else record.cost / record.units

def anomaly_rows(records: Iterable[UnitEconomicsAnomalyEvidence], threshold: float = 0.25) -> list[dict[str, object]]:
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    grouped: dict[str, list[UnitEconomicsAnomalyEvidence]] = {}
    for record in records:
        grouped.setdefault(record.workload, []).append(record)
    rows: list[dict[str, object]] = []
    for workload, items in grouped.items():
        ordered = sorted(items, key=lambda r: r.period)
        history: list[float] = []
        for record in ordered:
            current = _unit_cost(record)
            baseline = sum(history) / len(history) if history else None
            deviation = None if current is None or baseline in (None, 0) else (current - baseline) / baseline
            rows.append({
                "period": record.period,
                "workload": workload,
                "cost": record.cost,
                "units": record.units,
                "unit_cost": current,
                "baseline_unit_cost": baseline,
                "relative_deviation": deviation,
                "anomaly_review": bool(deviation is not None and abs(deviation) >= threshold),
                "evidence_status": "available" if current is not None else "unavailable",
            })
            if current is not None:
                history.append(current)
    return sorted(rows, key=lambda r: (str(r["period"]), str(r["workload"])))
