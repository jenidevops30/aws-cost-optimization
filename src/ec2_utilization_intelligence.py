from __future__ import annotations

from typing import Any


def correlate_cost_and_utilization(cost_rows: list[dict[str, Any]], utilization_rows: list[dict[str, Any]], *, low_cpu_pct: float = 10.0, high_cpu_pct: float = 80.0) -> list[dict[str, Any]]:
    """Combine resource cost and CloudWatch evidence without pricing inference."""
    utilization = {str(row["instance_id"]): row for row in utilization_rows if row.get("instance_id")}
    output: list[dict[str, Any]] = []
    for row in cost_rows:
        instance_id = str(row.get("resource_id") or "")
        if not instance_id:
            continue
        metrics = utilization.get(instance_id)
        if not metrics:
            output.append({**row, "utilization_status": "not-available", "signals": ()})
            continue
        cpu = metrics.get("cpu_average_pct")
        signals: list[str] = []
        if cpu is not None and cpu < low_cpu_pct:
            signals.append("low-average-cpu-review")
        if cpu is not None and cpu >= high_cpu_pct:
            signals.append("high-average-cpu")
        if metrics.get("cpu_max_pct") is not None and metrics["cpu_max_pct"] >= high_cpu_pct:
            signals.append("high-peak-cpu")
        output.append({**row, "cpu_average_pct": cpu, "cpu_max_pct": metrics.get("cpu_max_pct"), "network_in_bytes": metrics.get("network_in_bytes"), "network_out_bytes": metrics.get("network_out_bytes"), "cpu_datapoints": metrics.get("cpu_datapoints", 0), "utilization_status": "available" if metrics.get("cpu_datapoints", 0) else "no-cpu-data", "signals": tuple(signals), "mode": "analysis-only"})
    return output
