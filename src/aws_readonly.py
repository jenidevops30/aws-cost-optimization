from __future__ import annotations

"""Optional, read-only AWS observation helpers.

No mutating AWS APIs are exposed here. Credentials are resolved by boto3's
standard credential chain; nothing is stored in the repository.
"""

from typing import Any


def _client(service_name: str, region: str):
    import boto3

    return boto3.client(service_name, region_name=region)


def get_ec2_inventory(region: str) -> list[dict[str, Any]]:
    """Return a compact EC2 inventory using DescribeInstances only."""
    client = _client("ec2", region)
    paginator = client.get_paginator("describe_instances")
    result: list[dict[str, Any]] = []
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                result.append(
                    {
                        "instance_id": instance.get("InstanceId"),
                        "instance_type": instance.get("InstanceType"),
                        "state": instance.get("State", {}).get("Name"),
                        "az": instance.get("Placement", {}).get("AvailabilityZone"),
                        "architecture": instance.get("Architecture"),
                        "launch_time": str(instance.get("LaunchTime", "")),
                    }
                )
    return result


def get_rds_inventory(region: str) -> list[dict[str, Any]]:
    """Return a compact RDS inventory using DescribeDBInstances only."""
    client = _client("rds", region)
    paginator = client.get_paginator("describe_db_instances")
    result: list[dict[str, Any]] = []
    for page in paginator.paginate():
        for db in page.get("DBInstances", []):
            result.append(
                {
                    "identifier": db.get("DBInstanceIdentifier"),
                    "class": db.get("DBInstanceClass"),
                    "engine": db.get("Engine"),
                    "status": db.get("DBInstanceStatus"),
                    "multi_az": db.get("MultiAZ"),
                    "storage_gb": db.get("AllocatedStorage"),
                }
            )
    return result


def get_readonly_summary(region: str) -> dict[str, Any]:
    """Collect inventory without changing AWS resources."""
    return {
        "region": region,
        "ec2": get_ec2_inventory(region),
        "rds": get_rds_inventory(region),
    }
