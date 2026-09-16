from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .aws_resilience import aws_client, observe


def _query(db_identifier: str, metric_name: str, period: int, stat: str, query_id: str) -> dict[str, Any]:
    return {"Id": query_id, "MetricStat": {"Metric": {"Namespace": "AWS/RDS", "MetricName": metric_name, "Dimensions": [{"Name": "DBInstanceIdentifier", "Value": db_identifier}]}, "Period": period, "Stat": stat}, "ReturnData": True}


def get_rds_utilization(db_identifiers: list[str], start: datetime, end: datetime, *, region: str, period: int = 300, client=None) -> list[dict[str, Any]]:
    """Read RDS utilization evidence through CloudWatch GetMetricData only."""
    if end <= start:
        raise ValueError("end must be after start")
    if period < 60 or period % 60:
        raise ValueError("period must be at least 60 seconds and a multiple of 60")
    if not db_identifiers:
        return []
    if client is None:
        client = aws_client("cloudwatch", region)
    results: list[dict[str, Any]] = []
    for db_identifier in db_identifiers:
        response = observe(lambda: client.get_metric_data(
            MetricDataQueries=[
                _query(db_identifier, "CPUUtilization", period, "Average", "cpuavg"),
                _query(db_identifier, "CPUUtilization", period, "Maximum", "cpumax"),
                _query(db_identifier, "DatabaseConnections", period, "Average", "connections"),
                _query(db_identifier, "FreeStorageSpace", period, "Average", "freestorage"),
                _query(db_identifier, "ReadIOPS", period, "Average", "readiops"),
                _query(db_identifier, "WriteIOPS", period, "Average", "writeiops"),
            ],
            StartTime=start.astimezone(timezone.utc),
            EndTime=end.astimezone(timezone.utc),
            ScanBy="TimestampDescending",
        ))
        by_id = {item.get("Id"): item for item in response.get("MetricDataResults", [])}
        def values(metric_id: str) -> list[float]:
            return [float(value) for value in by_id.get(metric_id, {}).get("Values", [])]
        cpu_avg, cpu_max = values("cpuavg"), values("cpumax")
        connections, free_storage = values("connections"), values("freestorage")
        read_iops, write_iops = values("readiops"), values("writeiops")
        results.append({
            "db_identifier": db_identifier,
            "cpu_average_pct": round(sum(cpu_avg) / len(cpu_avg), 2) if cpu_avg else None,
            "cpu_max_pct": round(max(cpu_max), 2) if cpu_max else None,
            "connections_average": round(sum(connections) / len(connections), 2) if connections else None,
            "free_storage_bytes_average": round(sum(free_storage) / len(free_storage), 2) if free_storage else None,
            "read_iops_average": round(sum(read_iops) / len(read_iops), 2) if read_iops else None,
            "write_iops_average": round(sum(write_iops) / len(write_iops), 2) if write_iops else None,
            "cpu_datapoints": len(cpu_avg),
            "mode": "analysis-only",
        })
    return results
