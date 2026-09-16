from __future__ import annotations

from typing import Any


def get_ebs_inventory(region: str) -> list[dict[str, Any]]:
    """Return EBS volume inventory using DescribeVolumes only."""
    import boto3

    client = boto3.client("ec2", region_name=region)
    paginator = client.get_paginator("describe_volumes")
    result: list[dict[str, Any]] = []
    for page in paginator.paginate():
        for volume in page.get("Volumes", []):
            attachments = volume.get("Attachments", [])
            result.append({
                "volume_id": volume.get("VolumeId"),
                "volume_type": volume.get("VolumeType"),
                "size_gb": volume.get("Size"),
                "state": volume.get("State"),
                "az": volume.get("AvailabilityZone"),
                "encrypted": volume.get("Encrypted"),
                "iops": volume.get("Iops"),
                "throughput_mibps": volume.get("Throughput"),
                "attachments": [item.get("InstanceId") for item in attachments if item.get("InstanceId")],
                "mode": "analysis-only",
            })
    return result


def build_ebs_intelligence(
    inventory: list[dict[str, Any]],
    metric_rows: list[dict[str, Any]],
    *,
    low_activity_ops: float = 1.0,
    high_queue_length: float = 1.0,
) -> list[dict[str, Any]]:
    """Correlate EBS inventory with operational evidence; never infer price savings."""
    metrics = {str(row["volume_id"]): row for row in metric_rows if row.get("volume_id")}
    output: list[dict[str, Any]] = []

    for volume in inventory:
        volume_id = str(volume.get("volume_id") or "")
        if not volume_id:
            continue
        metric = metrics.get(volume_id)
        row = {
            **volume,
            "utilization_status": "not-available",
            "signals": (),
            "mode": "analysis-only",
        }
        if not metric:
            output.append(row)
            continue

        read_ops = metric.get("read_ops_average")
        write_ops = metric.get("write_ops_average")
        queue = metric.get("queue_length_average")
        signals: list[str] = []
        if read_ops is not None and write_ops is not None and (read_ops + write_ops) < low_activity_ops:
            signals.append("low-activity-review")
        if queue is not None and queue >= high_queue_length:
            signals.append("high-queue-review")
        if volume.get("state") == "available" and not volume.get("attachments"):
            signals.append("unattached-volume-review")
        if volume.get("volume_type") == "gp2":
            signals.append("gp2-migration-review")

        row.update({
            "read_ops_average": read_ops,
            "write_ops_average": write_ops,
            "read_bytes_average": metric.get("read_bytes_average"),
            "write_bytes_average": metric.get("write_bytes_average"),
            "queue_length_average": queue,
            "idle_time_average": metric.get("idle_time_average"),
            "read_ops_datapoints": metric.get("read_ops_datapoints", 0),
            "write_ops_datapoints": metric.get("write_ops_datapoints", 0),
            "utilization_status": "available" if metric.get("read_ops_datapoints", 0) or metric.get("write_ops_datapoints", 0) else "no-ops-data",
            "signals": tuple(signals),
        })
        output.append(row)
    return output
