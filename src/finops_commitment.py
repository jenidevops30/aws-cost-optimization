from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CommitmentEvidence:
    period: str
    commitment_type: str
    service: str
    eligible_spend: float
    covered_spend: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.commitment_type not in {"reserved-instance", "savings-plan"}:
            raise ValueError("unsupported commitment_type")
        if self.eligible_spend < 0 or self.covered_spend < 0:
            raise ValueError("spend values must be non-negative")
        if self.covered_spend > self.eligible_spend:
            raise ValueError("covered_spend cannot exceed eligible_spend")


def coverage_percent(evidence: CommitmentEvidence) -> float | None:
    if evidence.eligible_spend == 0:
        return None
    return evidence.covered_spend / evidence.eligible_spend * 100


def aggregate_commitment_coverage(
    records: Iterable[CommitmentEvidence],
) -> list[dict[str, object]]:
    totals: dict[tuple[str, str], list[float]] = {}
    for record in records:
        key = (record.period, record.commitment_type)
        eligible, covered = totals.setdefault(key, [0.0, 0.0])
        eligible += record.eligible_spend
        covered += record.covered_spend
        totals[key] = [eligible, covered]

    result: list[dict[str, object]] = []
    for (period, commitment_type), (eligible, covered) in sorted(totals.items()):
        result.append(
            {
                "period": period,
                "commitment_type": commitment_type,
                "eligible_spend": eligible,
                "covered_spend": covered,
                "uncovered_spend": eligible - covered,
                "coverage_pct": None if eligible == 0 else covered / eligible * 100,
            }
        )
    return result


def commitment_review_flags(evidence: CommitmentEvidence) -> list[str]:
    coverage = coverage_percent(evidence)
    if coverage is None:
        return ["no-eligible-spend"]
    if coverage == 0:
        return ["no-covered-eligible-spend"]
    if coverage < 50:
        return ["low-coverage-review"]
    return []
