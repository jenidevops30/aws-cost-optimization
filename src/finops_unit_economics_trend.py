from __future__ import annotations

from typing import Iterable


def unit_cost_trend(records: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for record in records:
        units = float(record["units"])
        cost = float(record["cost"])
        rows.append({
            **record,
            "cost_per_unit": None if units == 0 else cost / units,
        })
    return sorted(rows, key=lambda row: (str(row["period"]), str(row["workload"]), str(row["unit_name"])))


def unit_cost_change(previous: dict[str, object], current: dict[str, object]) -> float | None:
    previous_units = float(previous["units"])
    current_units = float(current["units"])
    if previous_units == 0 or current_units == 0:
        return None
    previous_cost_per_unit = float(previous["cost"]) / previous_units
    current_cost_per_unit = float(current["cost"]) / current_units
    if previous_cost_per_unit == 0:
        return None
    return (current_cost_per_unit - previous_cost_per_unit) / previous_cost_per_unit * 100
