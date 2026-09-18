from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class FinOpsEvidenceLineage:
    dataset: str
    period: str
    source: str
    observed_at: str
    record_count: int
    complete: bool = True

    def __post_init__(self) -> None:
        if not self.dataset.strip() or not self.period.strip() or not self.source.strip() or not self.observed_at.strip():
            raise ValueError("dataset, period, source, and observed_at are required")
        if self.record_count < 0:
            raise ValueError("record_count must be non-negative")

def lineage_rows(records: Iterable[FinOpsEvidenceLineage]) -> list[dict[str, object]]:
    rows=[]
    for r in sorted(records,key=lambda x:(x.dataset,x.period)):
        rows.append({
            "dataset":r.dataset,"period":r.period,"source":r.source,
            "observed_at":r.observed_at,"record_count":r.record_count,
            "complete":r.complete,
            "lineage_status":"available" if r.complete and r.record_count > 0 else "review",
        })
    return rows

def lineage_summary(records: Iterable[FinOpsEvidenceLineage]) -> dict[str,int]:
    rows=list(records)
    return {
        "datasets":len(rows),
        "available":sum(r.complete and r.record_count > 0 for r in rows),
        "review":sum(not (r.complete and r.record_count > 0) for r in rows),
    }
