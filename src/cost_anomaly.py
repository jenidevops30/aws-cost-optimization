from __future__ import annotations

from datetime import date
from typing import Any

from .aws_resilience import aws_client, observe


def get_cost_anomalies(start: date, end: date, *, region: str = "us-east-1", monitor_arn: str | None = None, max_results: int = 100, client=None) -> list[dict[str, Any]]:
    """Read AWS Cost Anomaly Detection findings; never modifies billing controls."""
    if end <= start:
        raise ValueError("end must be after start")
    if not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100")
    ce = client or aws_client("ce", region)
    result: list[dict[str, Any]] = []
    next_token: str | None = None
    while True:
        request: dict[str, Any] = {"DateInterval": {"StartDate": start.isoformat(), "EndDate": end.isoformat()}, "MaxResults": max_results}
        if monitor_arn:
            request["MonitorArn"] = monitor_arn
        if next_token:
            request["NextPageToken"] = next_token
        response = observe(lambda: ce.get_anomalies(**request))
        for anomaly in response.get("Anomalies", []):
            impact = anomaly.get("Impact", {}) or {}
            result.append({
                "anomaly_id": anomaly.get("AnomalyId"),
                "monitor_arn": anomaly.get("MonitorArn"),
                "anomaly_start": anomaly.get("AnomalyStartDate"),
                "anomaly_end": anomaly.get("AnomalyEndDate"),
                "estimated_impact_usd": float(impact.get("TotalImpact", 0) or 0),
                "actual_spend_usd": float(impact.get("TotalActualSpend", 0) or 0),
                "root_causes": [
                    {"service": cause.get("Service"), "region": cause.get("Region"), "usage_type": cause.get("UsageType"), "linked_account": cause.get("LinkedAccount")}
                    for cause in (anomaly.get("RootCauses", []) or [])
                ],
                "mode": "analysis-only",
            })
        next_token = response.get("NextPageToken")
        if not next_token:
            return result


def summarize_anomalies(anomalies: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce deterministic summary statistics from returned anomaly evidence."""
    impacts = [float(item.get("estimated_impact_usd", 0) or 0) for item in anomalies]
    services = sorted({str(cause.get("service")) for item in anomalies for cause in item.get("root_causes", []) if cause.get("service")})
    return {"anomaly_count": len(anomalies), "total_estimated_impact_usd": round(sum(impacts), 2), "max_estimated_impact_usd": round(max(impacts), 2) if impacts else 0.0, "affected_services": services, "mode": "analysis-only"}
