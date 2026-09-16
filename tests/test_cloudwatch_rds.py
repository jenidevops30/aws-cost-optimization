from datetime import datetime, timezone

from src.cloudwatch_rds import get_rds_utilization
from src.rds_intelligence import build_rds_intelligence


class FakeCloudWatch:
    def get_metric_data(self, **kwargs):
        assert len(kwargs["MetricDataQueries"]) == 6
        return {
            "MetricDataResults": [
                {"Id": "cpuavg", "Values": [8, 12]},
                {"Id": "cpumax", "Values": [45]},
                {"Id": "connections", "Values": [10, 20]},
                {"Id": "freestorage", "Values": [10 * 1024 ** 3, 12 * 1024 ** 3]},
                {"Id": "readiops", "Values": [100, 120]},
                {"Id": "writeiops", "Values": [50, 70]},
            ]
        }


def test_rds_utilization_reads_expected_metrics():
    rows = get_rds_utilization(
        ["db-prod"],
        datetime(2026, 9, 1, tzinfo=timezone.utc),
        datetime(2026, 9, 2, tzinfo=timezone.utc),
        region="us-east-1",
        client=FakeCloudWatch(),
    )
    assert rows[0]["db_identifier"] == "db-prod"
    assert rows[0]["cpu_average_pct"] == 10
    assert rows[0]["connections_average"] == 15
    assert rows[0]["free_storage_bytes_average"] == 11 * 1024 ** 3
    assert rows[0]["read_iops_average"] == 110
    assert rows[0]["write_iops_average"] == 60


def test_rds_intelligence_surfaces_storage_signal():
    inventory = [{
        "identifier": "db-prod",
        "class": "db.t3.medium",
        "engine": "mariadb",
        "status": "available",
        "multi_az": True,
        "storage_gb": 100,
    }]
    metrics = [{
        "db_identifier": "db-prod",
        "cpu_average_pct": 5,
        "cpu_max_pct": 45,
        "connections_average": 15,
        "free_storage_bytes_average": 10 * 1024 ** 3,
        "read_iops_average": 100,
        "write_iops_average": 50,
        "cpu_datapoints": 2,
    }]
    rows = build_rds_intelligence(inventory, metrics)
    assert "low-average-cpu-review" in rows[0]["signals"]
    assert "low-free-storage-review" in rows[0]["signals"]
    assert "low-free-storage-percent-review" in rows[0]["signals"]


def test_missing_rds_metrics_are_not_zero():
    inventory = [{"identifier": "db-prod", "class": "db.t3.medium", "engine": "mariadb", "status": "available", "storage_gb": 100}]
    rows = build_rds_intelligence(inventory, [])
    assert rows[0]["utilization_status"] == "not-available"
    assert rows[0]["signals"] == ()
