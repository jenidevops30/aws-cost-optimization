from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class AllocationRecord:
    billing_period: str
    account_id: str
    service: str
    cost: float
    region: str = ""
    allocation_key: str = ""


def classify_allocation(record: AllocationRecord) -> str:
    """Classify a cost record without inventing allocation evidence."""
    return "allocated" if record.allocation_key.strip() else "unallocated"


def allocation_totals(records: Iterable[AllocationRecord]) -> dict[str, float]:
    totals = {"allocated": 0.0, "unallocated": 0.0}
    for record in records:
        totals[classify_allocation(record)] += record.cost
    return totals


def allocation_quality(records: Iterable[AllocationRecord]) -> dict[str, float | int | None]:
    records = list(records)
    totals = allocation_totals(records)
    total = totals["allocated"] + totals["unallocated"]
    allocated_pct = None if total == 0 else (totals["allocated"] / total) * 100
    return {
        "record_count": len(records),
        "allocated_records": sum(classify_allocation(r) == "allocated" for r in records),
        "unallocated_records": sum(classify_allocation(r) == "unallocated" for r in records),
        "allocated_cost": totals["allocated"],
        "unallocated_cost": totals["unallocated"],
        "total_cost": total,
        "allocated_pct": allocated_pct,
    }


def unallocated_by_dimension(
    records: Iterable[AllocationRecord], dimension: str = "service"
) -> dict[str, float]:
    """Return unallocated spend by a safe, explicit dimension."""
    if dimension not in {"service", "account_id", "region", "billing_period"}:
        raise ValueError("unsupported allocation dimension")

    totals: dict[str, float] = {}
    for record in records:
        if classify_allocation(record) != "unallocated":
            continue
        key = str(getattr(record, dimension)) or "unknown"
        totals[key] = totals.get(key, 0.0) + record.cost
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def allocation_quality_from_mappings(
    rows: Iterable[Mapping[str, object]], allocation_field: str = "allocation_key"
) -> dict[str, float | int | None]:
    """Adapt normalized mapping rows without changing their source evidence."""
    records = [
        AllocationRecord(
            billing_period=str(row.get("billing_period", "")),
            account_id=str(row.get("account_id", "")),
            service=str(row.get("service", "")),
            cost=float(row.get("cost", 0) or 0),
            region=str(row.get("region", "")),
            allocation_key=str(row.get(allocation_field, "") or ""),
        )
        for row in rows
    ]
    return allocation_quality(records)
