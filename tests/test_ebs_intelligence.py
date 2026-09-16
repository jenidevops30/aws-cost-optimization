from src.ebs_intelligence import build_ebs_intelligence


def test_ebs_intelligence_flags_unattached_gp2_and_low_activity():
    inventory = [{
        "volume_id": "vol-123",
        "volume_type": "gp2",
        "size_gb": 100,
        "state": "available",
        "az": "us-east-1a",
        "encrypted": True,
        "iops": 300,
        "throughput_mibps": None,
        "attachments": [],
    }]
    metrics = [{
        "volume_id": "vol-123",
        "read_ops_average": 0.1,
        "write_ops_average": 0.2,
        "read_bytes_average": 1000.0,
        "write_bytes_average": 1000.0,
        "queue_length_average": 0.0,
        "idle_time_average": 1.0,
        "read_ops_datapoints": 10,
        "write_ops_datapoints": 10,
    }]

    row = build_ebs_intelligence(inventory, metrics)[0]
    assert row["utilization_status"] == "available"
    assert "unattached-volume-review" in row["signals"]
    assert "gp2-migration-review" in row["signals"]
    assert "low-activity-review" in row["signals"]


def test_missing_metrics_are_not_zero():
    row = build_ebs_intelligence(
        [{"volume_id": "vol-456", "volume_type": "gp3", "state": "in-use", "attachments": ["i-123"]}],
        [],
    )[0]
    assert row["utilization_status"] == "not-available"
    assert row["signals"] == ()
