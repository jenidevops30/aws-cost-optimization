from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _query(arn_suffix: str, metric_name: str, period: int, stat: str, query_id: str) -> dict[str, Any]:
    return {
        "Id": query_id,
        "MetricStat": {
            "Metric": {
                "Namespace": "AWS/ApplicationELB",
                "MetricName": metric_name,
                "Dimensions": [{"Name": "LoadBalancer", "Value": arn_suffix}],
            },
            "Period": period,
            "Stat": stat,
        },
        "ReturnData": True,
    }


def get_alb_metrics(load_balancers: list[dict[str, Any]], start: datetime, end: datetime, *, region: str, period: int = 300, client=None) -> list[dict[str, Any]]:
    """Read ALB metrics with CloudWatch GetMetricData only."""
    if end <= start:
        raise ValueError("end must be after start")
    if period < 60 or period % 60:
        raise ValueError("period must be at least 60 seconds and a multiple of 60")
    if not load_balancers:
        return []
    if client is None:
        import boto3
        client = boto3.client("cloudwatch", region_name=region)

    metrics = [
        ("RequestCount", "Sum", "request_count"),
        ("ProcessedBytes", "Sum", "processed_bytes"),
        ("ActiveConnectionCount", "Average", "active_connections"),
        ("NewConnectionCount", "Sum", "new_connections"),
        ("TargetResponseTime", "Average", "target_response_time"),
    ]
    output: list[dict[str, Any]] = []
    for lb in load_balancers:
        arn = lb.get("load_balancer_arn")
        if not arn:
            continue
        suffix = str(arn).split(":loadbalancer:", 1)[-1]
        response = client.get_metric_data(
            MetricDataQueries=[_query(suffix, name, period, stat, query_id) for name, stat, query_id in metrics],
            StartTime=start.astimezone(timezone.utc), EndTime=end.astimezone(timezone.utc), ScanBy="TimestampDescending",
        )
        by_id = {item.get("Id"): item for item in response.get("MetricDataResults", [])}
        def values(metric_id: str) -> list[float]:
            return [float(v) for v in by_id.get(metric_id, {}).get("Values", [])]
        rows = {qid: values(qid) for _, _, qid in metrics}
        avg = lambda values: round(sum(values) / len(values), 4) if values else None
        output.append({
            "load_balancer_arn": arn,
            "request_count_average": avg(rows["request_count"]),
            "processed_bytes_average": avg(rows["processed_bytes"]),
            "active_connections_average": avg(rows["active_connections"]),
            "new_connections_average": avg(rows["new_connections"]),
            "target_response_time_average": avg(rows["target_response_time"]),
            "request_datapoints": len(rows["request_count"]),
            "processed_bytes_datapoints": len(rows["processed_bytes"]),
            "mode": "analysis-only",
        })
    return output
