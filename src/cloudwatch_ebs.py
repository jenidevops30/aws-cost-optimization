from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _query(volume_id: str, metric_name: str, period: int, stat: str, query_id: str) -> dict[str, Any]:
    return {
        "Id": query_id,
        "MetricStat": {
            "Metric": {
                "Namespace": "AWS/EBS",
                "MetricName": metric_name,
                "Dimensions": [{"Name": "VolumeId", "Value": volume_id}],
            },
            "Period": period,
            "Stat": stat,
        },
        "ReturnData": True,
    }


def get_ebs_metrics(
    volume_ids: list[str],
    start: datetime,
    end: datetime,
    *,
    region: str,
    period: int = 300,
    client=None,
) -> list[dict[str, Any]]:
    """Read EBS CloudWatch evidence with GetMetricData only."""
    if end <= start:
        raise ValueError("end must be after start")
    if period < 60 or period % 60:
        raise ValueError("period must be at least 60 seconds and a multiple of 60")
    if not volume_ids:
        return []
    if client is None:
        import boto3
        client = boto3.client("cloudwatch", region_name=region)

    metrics = [
        ("VolumeReadOps", "Average", "read_ops"),
        ("VolumeWriteOps", "Average", "write_ops"),
        ("VolumeReadBytes", "Average", "read_bytes"),
        ("VolumeWriteBytes", "Average", "write_bytes"),
        ("VolumeQueueLength", "Average", "queue"),
        ("VolumeIdleTime", "Average", "idle_time"),
    ]
    results: list[dict[str, Any]] = []
    for volume_id in volume_ids:
        response = client.get_metric_data(
            MetricDataQueries=[_query(volume_id, name, period, stat, query_id) for name, stat, query_id in metrics],
            StartTime=start.astimezone(timezone.utc),
            EndTime=end.astimezone(timezone.utc),
            ScanBy="TimestampDescending",
        )
        by_id = {item.get("Id"): item for item in response.get("MetricDataResults", [])}

        def values(metric_id: str) -> list[float]:
            return [float(value) for value in by_id.get(metric_id, {}).get("Values", [])]

        rows = {metric_id: values(metric_id) for _, _, metric_id in metrics}
        results.append({
            "volume_id": volume_id,
            "read_ops_average": round(sum(rows["read_ops"]) / len(rows["read_ops"]), 4) if rows["read_ops"] else None,
            "write_ops_average": round(sum(rows["write_ops"]) / len(rows["write_ops"]), 4) if rows["write_ops"] else None,
            "read_bytes_average": round(sum(rows["read_bytes"]) / len(rows["read_bytes"]), 2) if rows["read_bytes"] else None,
            "write_bytes_average": round(sum(rows["write_bytes"]) / len(rows["write_bytes"]), 2) if rows["write_bytes"] else None,
            "queue_length_average": round(sum(rows["queue"]) / len(rows["queue"]), 4) if rows["queue"] else None,
            "idle_time_average": round(sum(rows["idle_time"]) / len(rows["idle_time"]), 4) if rows["idle_time"] else None,
            "read_ops_datapoints": len(rows["read_ops"]),
            "write_ops_datapoints": len(rows["write_ops"]),
            "mode": "analysis-only",
        })
    return results
