from __future__ import annotations

from typing import Any


def get_alb_inventory(region: str, *, client=None) -> list[dict[str, Any]]:
    """Return read-only ALB inventory using ELBv2 DescribeLoadBalancers."""
    import boto3

    elbv2 = client or boto3.client("elbv2", region_name=region)
    paginator = elbv2.get_paginator("describe_load_balancers")
    result: list[dict[str, Any]] = []
    for page in paginator.paginate():
        for lb in page.get("LoadBalancers", []):
            result.append({
                "load_balancer_arn": lb.get("LoadBalancerArn"),
                "name": lb.get("LoadBalancerName"),
                "type": lb.get("Type"),
                "scheme": lb.get("Scheme"),
                "state": (lb.get("State") or {}).get("Code"),
                "dns_name": lb.get("DNSName"),
                "vpc_id": lb.get("VpcId"),
                "availability_zones": [z.get("ZoneName") for z in lb.get("AvailabilityZones", []) if z.get("ZoneName")],
                "mode": "analysis-only",
            })
    return result


def build_alb_intelligence(
    inventory: list[dict[str, Any]],
    metric_rows: list[dict[str, Any]],
    *,
    low_request_count: float = 1.0,
    high_response_time_seconds: float = 1.0,
    high_processed_bytes: float = 1_000_000_000.0,
) -> list[dict[str, Any]]:
    """Correlate ALB inventory with CloudWatch evidence without savings claims."""
    metrics = {str(row.get("load_balancer_arn")): row for row in metric_rows if row.get("load_balancer_arn")}
    output: list[dict[str, Any]] = []
    for lb in inventory:
        arn = str(lb.get("load_balancer_arn") or "")
        if not arn:
            continue
        metric = metrics.get(arn)
        row = {**lb, "metrics_status": "not-available", "signals": ()}
        if not metric:
            output.append(row)
            continue
        requests = metric.get("request_count_average")
        processed = metric.get("processed_bytes_average")
        response_time = metric.get("target_response_time_average")
        signals: list[str] = []
        if requests is not None and requests < low_request_count:
            signals.append("low-request-activity-review")
        if processed is not None and processed >= high_processed_bytes:
            signals.append("high-processed-bytes-review")
        if response_time is not None and response_time >= high_response_time_seconds:
            signals.append("high-target-response-time-review")
        if lb.get("state") != "active":
            signals.append("non-active-load-balancer-review")
        row.update({**metric, "metrics_status": "available", "signals": tuple(signals)})
        output.append(row)
    return output
