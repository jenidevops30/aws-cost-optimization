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
            records.append(
                CostExplorerRecord(
                    billing_period=billing_period,
                    service=service,
                    region="ALL",
                    cost=amount,
                    currency=unit,
                )
            )
    return records


def get_service_costs(
    start: date,
    end: date,
    *,
    client=None,
) -> list[CostExplorerRecord]:
    """Read monthly unblended cost grouped by AWS service.

    Cost Explorer's end date is exclusive. This function performs no resource
    mutations and uses only the Cost Explorer read API.
    """
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
