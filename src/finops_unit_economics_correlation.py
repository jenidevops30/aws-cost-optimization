from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class UnitCostCorrelationEvidence:
    period: str
    workload: str
    unit_name: str
    cost: float
    units: float
    supporting_signal: float | None = None
    signal_name: str | None = None

    def __post_init__(self) -> None:
        if self.cost < 0 or self.units < 0:
            raise ValueError("cost and units must be non-negative")
        if not self.workload.strip() or not self.unit_name.strip():
            raise ValueError("workload and unit_name are required")
        if self.supporting_signal is not None and not self.signal_name:
            raise ValueError("signal_name is required when supporting_signal is supplied")


def cost_per_unit(record: UnitCostCorrelationEvidence) -> float | None:
    if record.units == 0:
        return None
    return record.cost / record.units


def correlation_rows(records: Iterable[UnitCostCorrelationEvidence]) -> list[dict[str, object]]:
    rows = []
    for record in sorted(records, key=lambda item: (item.period, item.workload)):
        rows.append({
            "period": record.period,
            "workload": record.workload,
            "unit_name": record.unit_name,
            "cost": record.cost,
            "units": record.units,
            "cost_per_unit": cost_per_unit(record),
            "supporting_signal": record.supporting_signal,
            "signal_name": record.signal_name,
            "evidence_status": "available" if record.supporting_signal is not None else "unavailable",
        })
    return rows
