from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EC2CostInsight:
    instance_id: str
    instance_type: str
    architecture: str | None
    state: str | None
    cost: float
    monthly_share_pct: float
    signals: tuple[str, ...]
    confidence: str
    mode: str = "analysis-only"


def build_ec2_cost_insights(
    resource_costs: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
) -> list[EC2CostInsight]:
    """Correlate resource-level EC2 cost with observed inventory facts.

    No utilization or savings claim is inferred from cost alone. Signals are
    limited to observable architecture/state facts and cost concentration.
    """
    inventory_by_id = {
        str(item.get("instance_id")): item
        for item in inventory
        if item.get("instance_id")
    }
    attributed = [r for r in resource_costs if r.get("resource_id")]
    total = sum(float(r.get("cost", 0.0)) for r in attributed)
    insights: list[EC2CostInsight] = []

    for record in attributed:
        instance_id = str(record["resource_id"])
        item = inventory_by_id.get(instance_id)
        if not item:
            continue
        cost = float(record.get("cost", 0.0))
        share = (cost / total * 100) if total else 0.0
        signals: list[str] = []
        architecture = item.get("architecture")
        if architecture == "x86_64":
            signals.append("arm64-review")
        if item.get("state") == "stopped":
            signals.append("stopped-resource-review")
        if total and share >= 25.0:
            signals.append("high-cost-concentration")
        insights.append(
            EC2CostInsight(
                instance_id=instance_id,
                instance_type=str(item.get("instance_type") or "unknown"),
                architecture=architecture,
                state=item.get("state"),
                cost=round(cost, 2),
                monthly_share_pct=round(share, 2),
                signals=tuple(signals),
                confidence="high" if instance_id in inventory_by_id else "medium",
            )
        )
    return sorted(insights, key=lambda x: x.cost, reverse=True)
