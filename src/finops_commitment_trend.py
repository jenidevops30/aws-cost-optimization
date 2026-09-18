from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CommitmentTrendEvidence:
    period: str
    commitment_type: str
    eligible_spend: float
    covered_spend: float
    committed_value: float
    utilized_value: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.commitment_type not in {"reserved-instance", "savings-plan"}:
            raise ValueError("unsupported commitment_type")
        values = (
            self.eligible_spend,
            self.covered_spend,
            self.committed_value,
            self.utilized_value,
        )
        if any(value < 0 for value in values):
            raise ValueError("commitment values must be non-negative")
        if self.covered_spend > self.eligible_spend:
            raise ValueError("covered_spend cannot exceed eligible_spend")
        if self.utilized_value > self.committed_value:
            raise ValueError("utilized_value cannot exceed committed_value")


def _pct(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator * 100


def commitment_trend(records: Iterable[CommitmentTrendEvidence]) -> list[dict[str, object]]:
    rows = []
    for record in sorted(records, key=lambda item: (item.period, item.commitment_type)):
        rows.append({
            "period": record.period,
            "commitment_type": record.commitment_type,
            "coverage_pct": _pct(record.covered_spend, record.eligible_spend),
            "utilization_pct": _pct(record.utilized_value, record.committed_value),
            "uncovered_spend": record.eligible_spend - record.covered_spend,
            "unused_value": record.committed_value - record.utilized_value,
        })
    return rows


def coverage_utilization_gap(record: CommitmentTrendEvidence) -> float | None:
    coverage = _pct(record.covered_spend, record.eligible_spend)
    utilization = _pct(record.utilized_value, record.committed_value)
    if coverage is None or utilization is None:
        return None
    return coverage - utilization


def trend_review_flags(record: CommitmentTrendEvidence) -> list[str]:
    coverage = _pct(record.covered_spend, record.eligible_spend)
    utilization = _pct(record.utilized_value, record.committed_value)
    if coverage is None:
        return ["coverage-unavailable"]
    if utilization is None:
        return ["utilization-unavailable"]
    flags: list[str] = []
    if coverage < 50:
        flags.append("low-coverage-review")
    if utilization < 50:
        flags.append("low-utilization-review")
    if coverage >= 50 and utilization < 50:
        flags.append("coverage-utilization-mismatch")
    return flags
