from __future__ import annotations

import os
from typing import Any


def configured_region() -> str:
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"


def get_region_inventory(region: str) -> dict[str, Any]:
    """Return read-only infrastructure inventory for one AWS region."""
    from src.aws_readonly import get_readonly_summary

    return get_readonly_summary(region)


def inventory_frame(summary: dict[str, Any]):
    import pandas as pd

    rows = []
    for item in summary.get("ec2", []):
        rows.append({
            "resource_type": "EC2",
            "identifier": item.get("instance_id"),
            "size": item.get("instance_type"),
            "status": item.get("state"),
            "architecture": item.get("architecture"),
            "availability_zone": item.get("az"),
            "engine": "",
            "multi_az": "",
            "storage_gb": "",
        })
    for item in summary.get("rds", []):
        rows.append({
            "resource_type": "RDS",
            "identifier": item.get("identifier"),
            "size": item.get("class"),
            "status": item.get("status"),
            "architecture": "",
            "availability_zone": "",
            "engine": item.get("engine"),
            "multi_az": item.get("multi_az"),
            "storage_gb": item.get("storage_gb"),
        })
    return pd.DataFrame(rows)
