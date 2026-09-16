from __future__ import annotations

from typing import Any

GIB = 1024 ** 3


def build_rds_intelligence(
    inventory: list[dict[str, Any]],
    utilization_rows: list[dict[str, Any]],
    *,
    low_cpu_pct: float = 10.0,
    high_cpu_pct: float = 80.0,
    low_free_storage_pct: float = 20.0,
    low_free_storage_gib: float = 20.0,
) -> list[dict[str, Any]]:
    """Correlate RDS inventory with CloudWatch evidence without price inference."""
    metrics = {str(row["db_identifier"]): row for row in utilization_rows if row.get("db_identifier")}
    output: list[dict[str, Any]] = []

    for db in inventory:
        identifier = str(db.get("identifier") or "")
        if not identifier:
            continue
        metric = metrics.get(identifier)
        row = {
            "db_identifier": identifier,
            "db_class": db.get("class"),
            "engine": db.get("engine"),
            "status": db.get("status"),
            "multi_az": db.get("multi_az"),
            "allocated_storage_gb": db.get("storage_gb"),
            "utilization_status": "not-available",
            "signals": (),
            "mode": "analysis-only",
        }
        if not metric:
            output.append(row)
            continue

        signals: list[str] = []
        cpu = metric.get("cpu_average_pct")
        if cpu is not None and cpu < low_cpu_pct:
            signals.append("low-average-cpu-review")
        if cpu is not None and cpu >= high_cpu_pct:
            signals.append("high-average-cpu")
        if metric.get("cpu_max_pct") is not None and metric["cpu_max_pct"] >= high_cpu_pct:
            signals.append("high-peak-cpu")

        free_storage = metric.get("free_storage_bytes_average")
        allocated = db.get("storage_gb")
        if free_storage is not None:
            free_gib = free_storage / GIB
            row["free_storage_gib_average"] = round(free_gib, 2)
            if free_gib < low_free_storage_gib:
                signals.append("low-free-storage-review")
            if allocated:
                free_pct = (free_gib / float(allocated)) * 100
                row["free_storage_pct_of_allocated"] = round(free_pct, 2)
                if free_pct < low_free_storage_pct:
                    signals.append("low-free-storage-percent-review")

        row.update({
            "cpu_average_pct": cpu,
            "cpu_max_pct": metric.get("cpu_max_pct"),
            "connections_average": metric.get("connections_average"),
            "read_iops_average": metric.get("read_iops_average"),
            "write_iops_average": metric.get("write_iops_average"),
            "cpu_datapoints": metric.get("cpu_datapoints", 0),
            "utilization_status": "available" if metric.get("cpu_datapoints", 0) else "no-cpu-data",
            "signals": tuple(signals),
        })
        output.append(row)
    return output
