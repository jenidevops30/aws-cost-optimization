from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReconciliationEvidence:
    dimension: str
    source_a_total: float
    source_b_total: float
    tolerance: float = 0.0

    def __post_init__(self) -> None:
        if not self.dimension.strip():
            raise ValueError("dimension is required")
        if self.source_a_total < 0 or self.source_b_total < 0 or self.tolerance < 0:
            raise ValueError("totals and tolerance must be non-negative")

def reconciliation_row(evidence: ReconciliationEvidence) -> dict[str, object]:
    difference = evidence.source_a_total - evidence.source_b_total
    relative_difference = None if evidence.source_a_total == 0 else difference / evidence.source_a_total
    status = "matched" if abs(difference) <= evidence.tolerance else "mismatch"
    return {
        "dimension": evidence.dimension,
        "source_a_total": evidence.source_a_total,
        "source_b_total": evidence.source_b_total,
        "difference": difference,
        "relative_difference": relative_difference,
        "tolerance": evidence.tolerance,
        "reconciliation_status": status,
    }

def reconciliation_summary(rows: list[dict[str, object]]) -> dict[str, int]:
    return {
        "dimensions": len(rows),
        "matched": sum(r["reconciliation_status"] == "matched" for r in rows),
        "mismatch": sum(r["reconciliation_status"] == "mismatch" for r in rows),
    }
