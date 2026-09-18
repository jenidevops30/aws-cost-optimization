from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class UnitEconomicsGovernanceEvidence:
    period: str
    workload: str
    observed_unit_cost: float | None
    forecast_unit_cost: float | None
    anomaly: bool = False

    def __post_init__(self) -> None:
        if not self.period.strip() or not self.workload.strip():
            raise ValueError("period and workload are required")
        for value in (self.observed_unit_cost, self.forecast_unit_cost):
            if value is not None and value < 0:
                raise ValueError("unit costs must be non-negative")

def governance_rows(records: Iterable[UnitEconomicsGovernanceEvidence]) -> list[dict[str, object]]:
    rows=[]
    for record in sorted(records,key=lambda x:(x.period,x.workload)):
        complete=record.observed_unit_cost is not None and record.forecast_unit_cost is not None
        error=None if not complete else record.observed_unit_cost-record.forecast_unit_cost
        rows.append({
            "period":record.period,"workload":record.workload,
            "observed_unit_cost":record.observed_unit_cost,
            "forecast_unit_cost":record.forecast_unit_cost,
            "forecast_error":error,
            "anomaly_review":record.anomaly,
            "evidence_status":"available" if complete else "unavailable",
            "governance_status":"review" if record.anomaly or not complete else "observed",
        })
    return rows

def governance_summary(records: Iterable[UnitEconomicsGovernanceEvidence]) -> dict[str,int]:
    rows=list(records)
    return {
        "records":len(rows),
        "available":sum(r.observed_unit_cost is not None and r.forecast_unit_cost is not None for r in rows),
        "unavailable":sum(r.observed_unit_cost is None or r.forecast_unit_cost is None for r in rows),
        "anomaly_reviews":sum(r.anomaly for r in rows),
    }
