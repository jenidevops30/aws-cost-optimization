from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CostRecord:
    billing_period: str
    service: str
    usage_type: str
    region: str
    cost: float
    currency: str = "USD"
    source: str = "csv"


def load_csv(path: str | Path) -> list[CostRecord]:
    records: list[CostRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"billing_period", "service", "usage_type", "region", "cost"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            records.append(
                CostRecord(
                    billing_period=row["billing_period"],
                    service=row["service"],
                    usage_type=row["usage_type"],
                    region=row["region"],
                    cost=float(row["cost"]),
                    currency=row.get("currency") or "USD",
                    source=row.get("source") or "csv",
                )
            )
    return records


def monthly_totals(records: list[CostRecord]) -> dict[str, float]:
    totals: defaultdict[str, float] = defaultdict(float)
    for record in records:
        totals[record.billing_period] += record.cost
    return dict(sorted(totals.items()))


def service_totals(records: list[CostRecord]) -> dict[str, float]:
    totals: defaultdict[str, float] = defaultdict(float)
    for record in records:
        totals[record.service] += record.cost
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def month_over_month(records: list[CostRecord]) -> list[dict[str, float | str | None]]:
    totals = monthly_totals(records)
    periods = list(totals)
    result: list[dict[str, float | str | None]] = []
    previous = None
    for period in periods:
        current = totals[period]
        change = None if previous is None else current - previous
        percent = None if previous in (None, 0) else (change / previous) * 100
        result.append({"period": period, "cost": current, "change": change, "change_pct": percent})
        previous = current
    return result
