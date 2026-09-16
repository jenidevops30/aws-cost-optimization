from __future__ import annotations

from collections import defaultdict
from typing import Any


def attribute_resource_costs(cost_records: list[Any], inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return resource-level costs only when billing records contain a resource ID.

    Service-level costs are never divided across resources. Missing resource IDs
    are reported as unattributed so the output remains evidence-driven.
    """
    inventory_ids = {
        str(item.get("instance_id") or item.get("identifier"))
        for item in inventory
        if item.get("instance_id") or item.get("identifier")
    }
    resource_cost: defaultdict[str, float] = defaultdict(float)
    unattributed = 0.0

    for record in cost_records:
        resource_id = getattr(record, "resource_id", None)
        if resource_id:
            resource_cost[str(resource_id)] += float(record.cost)
        else:
            unattributed += float(record.cost)

    rows: list[dict[str, Any]] = []
    for resource_id, cost in sorted(resource_cost.items()):
        rows.append({
            "resource_id": resource_id,
            "cost": round(cost, 2),
            "inventory_match": resource_id in inventory_ids,
            "confidence": "high" if resource_id in inventory_ids else "medium",
            "cost_scope": "resource-level",
        })

    if unattributed:
        rows.append({
            "resource_id": None,
            "cost": round(unattributed, 2),
            "inventory_match": False,
            "confidence": "not-attributed",
            "cost_scope": "service-level-or-missing-resource-id",
        })

    return rows
