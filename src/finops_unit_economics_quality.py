from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class UnitEconomicsQualityEvidence:
    period: str
    workload: str
    unit_name: str
    cost: float
    units: float
    source: str | None = None

    def __post_init__(self) -> None:
        if self.cost < 0 or self.units < 0:
            raise ValueError("cost and units must be non-negative")
        if not self.period.strip() or not self.workload.strip() or not self.unit_name.strip():
            raise ValueError("period, workload, and unit_name are required")
        if self.units > 0 and not self.source:
            raise ValueError("source is required when unit volume is available")

def quality_rows(records: Iterable[UnitEconomicsQualityEvidence]) -> list[dict[str, object]]:
    rows = []
    for record in sorted(records, key=lambda item: (item.period, item.workload, item.unit_name)):
        rows.append({"period": record.period, "workload": record.workload, "unit_name": record.unit_name, "cost": record.cost, "units": record.units, "cost_per_unit": None if record.units == 0 else record.cost / record.units, "source": record.source, "evidence_status": "available" if record.units > 0 and record.source else "unavailable"})
    return rows

def quality_flags(records: Iterable[UnitEconomicsQualityEvidence]) -> list[str]:
    rows = list(records)
    if not rows:
        return ["no-evidence"]
    flags = []
    if any(record.units == 0 for record in rows): flags.append("zero-volume-evidence")
    if any(record.units > 0 and not record.source for record in rows): flags.append("missing-volume-source")
    if all(record.cost == 0 for record in rows): flags.append("zero-cost-evidence")
    return flags
