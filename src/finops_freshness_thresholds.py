from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

@dataclass(frozen=True)
class FreshnessEvidence:
    dataset: str
    observed_at: str
    max_age_hours: float
    record_count: int

    def __post_init__(self) -> None:
        if not self.dataset.strip() or not self.observed_at.strip():
            raise ValueError("dataset and observed_at are required")
        if self.max_age_hours < 0:
            raise ValueError("max_age_hours must be non-negative")
        if self.record_count < 0:
            raise ValueError("record_count must be non-negative")

def freshness_rows(records: Iterable[FreshnessEvidence], now: datetime | None = None) -> list[dict[str, object]]:
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    rows = []
    for r in sorted(records, key=lambda x: x.dataset):
        observed = datetime.fromisoformat(r.observed_at.replace("Z", "+00:00"))
        age_hours = max(0.0, (reference - observed).total_seconds() / 3600)
        fresh = r.record_count > 0 and age_hours <= r.max_age_hours
        rows.append({
            "dataset": r.dataset,
            "observed_at": r.observed_at,
            "record_count": r.record_count,
            "age_hours": age_hours,
            "max_age_hours": r.max_age_hours,
            "freshness_status": "fresh" if fresh else "stale",
        })
    return rows

def freshness_summary(rows: Iterable[dict[str, object]]) -> dict[str, int]:
    values = list(rows)
    return {
        "datasets": len(values),
        "fresh": sum(v["freshness_status"] == "fresh" for v in values),
        "stale": sum(v["freshness_status"] == "stale" for v in values),
    }
