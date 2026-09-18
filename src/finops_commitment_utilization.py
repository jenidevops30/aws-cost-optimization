from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CommitmentUtilizationEvidence:
    period: str
    commitment_type: str
    committed_value: float
    utilized_value: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.commitment_type not in {"reserved-instance", "savings-plan"}:
            raise ValueError("unsupported commitment_type")
        if self.committed_value < 0 or self.utilized_value < 0:
            raise ValueError("utilization values must be non-negative")
        if self.utilized_value > self.committed_value:
            raise ValueError("utilized_value cannot exceed committed_value")


def utilization_percent(record: CommitmentUtilizationEvidence) -> float | None:
    if record.committed_value == 0:
        return None
    return record.utilized_value / record.committed_value * 100


def aggregate_utilization(records: Iterable[CommitmentUtilizationEvidence]) -> list[dict[str, object]]:
    totals: dict[tuple[str, str], list[float]] = {}
    for record in records:
        key = (record.period, record.commitment_type)
        committed, utilized = totals.setdefault(key, [0.0, 0.0])
        totals[key] = [committed + record.committed_value, utilized + record.utilized_value]
    rows = []
    for (period, commitment_type), (committed, utilized) in sorted(totals.items()):
        rows.append({
            "period": period,
            "commitment_type": commitment_type,
            "committed_value": committed,
            "utilized_value": utilized,
            "unused_value": committed - utilized,
            "utilization_pct": None if committed == 0 else utilized / committed * 100,
        })
    return rows


def utilization_review_flags(record: CommitmentUtilizationEvidence) -> list[str]:
    pct = utilization_percent(record)
    if pct is None:
        return ["no-committed-value"]
    if pct == 0:
        return ["no-utilization"]
    if pct < 50:
        return ["low-utilization-review"]
    return []
