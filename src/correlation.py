from __future__ import annotations

from collections import defaultdict
from typing import Any


def correlate_costs_to_inventory(
    records: list[Any],
    ec2_inventory: list[dict[str, Any]],
    rds_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Correlate service-level billing with observed resource inventory.

    Billing exports in this project are service-level, so this function never
    invents per-resource costs. It reports the observed aggregate service cost
    alongside resource counts and explicitly marks the correlation level.
    """
    service_cost: defaultdict[str, float] = defaultdict(float)
    for record in records:
        service_cost[str(record.service).upper()] += float(record.cost)

    ec2_count = len(ec2_inventory)
    rds_count = len(rds_inventory)
    rows: list[dict[str, Any]] = []

    if ec2_count:
        rows.append(
            {
                "service": "EC2",
                "observed_resources": ec2_count,
                "aggregate_cost": round(service_cost.get("EC2", 0.0), 2),
                "cost_scope": "service-level",
                "confidence": "medium",
                "evidence": "Billing service total + read-only EC2 inventory",
            }
        )

    if rds_count:
        rows.append(
            {
                "service": "RDS",
                "observed_resources": rds_count,
                "aggregate_cost": round(service_cost.get("RDS", 0.0), 2),
                "cost_scope": "service-level",
                "confidence": "medium",
                "evidence": "Billing service total + read-only RDS inventory",
            }
        )

    return rows
