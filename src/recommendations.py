from __future__ import annotations

from typing import Any


def ec2_architecture_recommendations(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate evidence-gated EC2 review candidates.

    These are review candidates, not automatic rightsizing decisions. A
    recommendation is only emitted when inventory contains enough facts.
    """
    recommendations: list[dict[str, Any]] = []
    for item in inventory:
        instance_type = item.get("instance_type")
        architecture = item.get("architecture")
        instance_id = item.get("instance_id")
        if not instance_id or not instance_type:
            continue

        if architecture == "x86_64":
            recommendations.append(
                {
                    "resource": instance_id,
                    "category": "architecture-review",
                    "current": instance_type,
                    "action": "Review ARM64/Graviton-compatible alternatives",
                    "confidence": "low",
                    "evidence": ["EC2 instance architecture is x86_64"],
                    "status": "analysis-only",
                }
            )
    return recommendations


def rds_storage_review(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag RDS resources for storage review when storage evidence exists."""
    recommendations: list[dict[str, Any]] = []
    for item in inventory:
        identifier = item.get("identifier")
        storage = item.get("storage_gb")
        if not identifier or storage is None:
            continue
        recommendations.append(
            {
                "resource": identifier,
                "category": "storage-review",
                "current_storage_gb": storage,
                "action": "Review storage utilization before changing allocation",
                "confidence": "low",
                "evidence": ["RDS allocated storage is available"],
                "status": "analysis-only",
            }
        )
    return recommendations


def build_recommendations(
    ec2: list[dict[str, Any]], rds: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return ec2_architecture_recommendations(ec2) + rds_storage_review(rds)
