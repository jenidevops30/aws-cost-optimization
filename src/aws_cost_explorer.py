from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

import boto3


@dataclass(frozen=True)
class CostExplorerRecord:
    billing_period: str
    service: str
    region: str
    cost: float
    currency: str = "USD"
    source: str = "aws-cost-explorer"
    resource_id: str | None = None


def _client():
    return boto3.client("ce", region_name="us-east-1")


def _month(value: str) -> str:
    return value[:7]


def _parse_results(results: Iterable[dict]) -> list[CostExplorerRecord]:
    records: list[CostExplorerRecord] = []
    for period in results:
        billing_period = _month(period["TimePeriod"]["Start"])
        for group in period.get("Groups", []):
            keys = group.get("Keys", [])
            service = keys[0] if keys else "Uncategorized"
            amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
            unit = group.get("Metrics", {}).get("UnblendedCost", {}).get("Unit", "USD")
            records.append(CostExplorerRecord(billing_period, service, "ALL", amount, unit))
    return records


def _parse_resource_results(results: Iterable[dict]) -> list[CostExplorerRecord]:
    records: list[CostExplorerRecord] = []
    for period in results:
        billing_period = _month(period["TimePeriod"]["Start"])
        for group in period.get("Groups", []):
            keys = group.get("Keys", [])
            resource_id = keys[0] if keys else None
            if not resource_id:
                continue
            amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
            unit = group.get("Metrics", {}).get("UnblendedCost", {}).get("Unit", "USD")
            records.append(CostExplorerRecord(
                billing_period=billing_period,
                service="EC2",
                region="ALL",
                cost=amount,
                currency=unit,
                source="aws-cost-explorer-resource",
                resource_id=resource_id,
            ))
    return records


def get_service_costs(start: date, end: date, *, client=None) -> list[CostExplorerRecord]:
    if end <= start:
        raise ValueError("end must be after start")
    ce = client or _client()
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return _parse_results(response.get("ResultsByTime", []))


def get_ec2_resource_costs(start: date, end: date, *, client=None) -> list[CostExplorerRecord]:
    """Read daily EC2 resource costs; never mutates AWS resources."""
    if end <= start:
        raise ValueError("end must be after start")
    ce = client or _client()
    response = ce.get_cost_and_usage_with_resources(
        TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Elastic Compute Cloud - Compute"]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "RESOURCE_ID"}],
    )
    return _parse_resource_results(response.get("ResultsByTime", []))
