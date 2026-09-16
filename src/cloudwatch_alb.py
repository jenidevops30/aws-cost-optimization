from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SUM_METRICS = {"RequestCount", "ProcessedBytes", "NewConnectionCount"}


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


def _collect_metric_results(client, queries: list[dict[str, Any]], start: datetime, end: datetime) -> dict[str, list[float]]:
    """Collect all GetMetricData pages so a window is not silently truncated."""
    collected: dict[str, list[float]] = {query["Id"]: [] for query in queries}
    next_token = None
    while True:
        request = {
            "MetricDataQueries": queries,
            "StartTime": start.astimezone(timezone.utc),
            "EndTime": end.astimezone(timezone.utc),
            "ScanBy": "TimestampDescending",
        }
        if next_token:
            request["NextToken"] = next_token
        response = client.get_metric_data(**request)
        for item in response.get("MetricDataResults", []):
            metric_id = item.get("Id")
            if metric_id in collected:
                collected[metric_id].extend(float(value) for value in item.get("Values", []))
        next_token = response.get("NextToken")
        if not next_token:
            return collected


def _aggregate(values: list[float], metric_name: str) -> float | None:
    if not values:
        return None
    if metric_name in SUM_METRICS:
        return round(sum(values), 4)
    return round(sum(values) / len(values), 4)


def get_alb_metrics(load_balancers: list[dict[str, Any]], start: datetime, end: datetime, *, region: str, period: int = 300, client=None) -> list[dict[str, Any]]:
    """Read ALB metrics with CloudWatch GetMetricData only.

    Sum metrics are aggregated across returned periods; Average metrics use the
    arithmetic mean of returned datapoints. Missing metrics remain unavailable.
    """
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
        queries = [_query(suffix, name, period, stat, query_id) for name, stat, query_id in metrics]
        rows = _collect_metric_results(client, queries, start, end)
        output.append({
            "load_balancer_arn": arn,
            "request_count_total": _aggregate(rows["request_count"], "RequestCount"),
            "processed_bytes_total": _aggregate(rows["processed_bytes"], "ProcessedBytes"),
            "active_connections_average": _aggregate(rows["active_connections"], "ActiveConnectionCount"),
            "new_connections_total": _aggregate(rows["new_connections"], "NewConnectionCount"),
            "target_response_time_average": _aggregate(rows["target_response_time"], "TargetResponseTime"),
            "request_datapoints": len(rows["request_count"]),
            "processed_bytes_datapoints": len(rows["processed_bytes"]),
            "mode": "analysis-only",
        })
    return output
