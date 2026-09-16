from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _query(instance_id: str, metric_name: str, period: int, stat: str, query_id: str) -> dict[str, Any]:
    return {"Id": query_id, "MetricStat": {"Metric": {"Namespace": "AWS/EC2", "MetricName": metric_name, "Dimensions": [{"Name": "InstanceId", "Value": instance_id}]}, "Period": period, "Stat": stat}, "ReturnData": True}


def get_ec2_utilization(instance_ids: list[str], start: datetime, end: datetime, *, region: str, period: int = 300, client=None) -> list[dict[str, Any]]:
    """Read EC2 CPU/network metrics through CloudWatch GetMetricData only."""
    if end <= start:
        raise ValueError("end must be after start")
    if period < 60 or period % 60:
        raise ValueError("period must be at least 60 seconds and a multiple of 60")
    if not instance_ids:
        return []
    if client is None:
        import boto3
        client = boto3.client("cloudwatch", region_name=region)
    results: list[dict[str, Any]] = []
    for instance_id in instance_ids:
        response = client.get_metric_data(
            MetricDataQueries=[
                _query(instance_id, "CPUUtilization", period, "Average", "cpuavg"),
                _query(instance_id, "CPUUtilization", period, "Maximum", "cpumax"),
                _query(instance_id, "NetworkIn", period, "Sum", "networkin"),
                _query(instance_id, "NetworkOut", period, "Sum", "networkout"),
            ],
            StartTime=start.astimezone(timezone.utc),
            EndTime=end.astimezone(timezone.utc),
            ScanBy="TimestampDescending",
        )
        by_id = {item.get("Id"): item for item in response.get("MetricDataResults", [])}
        def values(metric_id: str) -> list[float]:
            return [float(v) for v in by_id.get(metric_id, {}).get("Values", [])]
        cpu_avg, cpu_max = values("cpuavg"), values("cpumax")
        network_in, network_out = values("networkin"), values("networkout")
        results.append({
            "instance_id": instance_id,
            "cpu_average_pct": round(sum(cpu_avg) / len(cpu_avg), 2) if cpu_avg else None,
            "cpu_max_pct": round(max(cpu_max), 2) if cpu_max else None,
            "network_in_bytes": round(sum(network_in), 2) if network_in else None,
            "network_out_bytes": round(sum(network_out), 2) if network_out else None,
            "cpu_datapoints": len(cpu_avg),
            "mode": "analysis-only",
        })
    return results
