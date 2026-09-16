from datetime import datetime, timezone

from src.cloudwatch_ec2 import get_ec2_utilization
from src.ec2_utilization_intelligence import correlate_cost_and_utilization


class FakeCloudWatch:
    def get_metric_data(self, **kwargs):
        assert len(kwargs["MetricDataQueries"]) == 4
        return {"MetricDataResults": [
            {"Id": "cpuavg", "Values": [5.0, 15.0]},
            {"Id": "cpumax", "Values": [35.0, 40.0]},
            {"Id": "networkin", "Values": [100.0, 200.0]},
            {"Id": "networkout", "Values": [300.0, 400.0]},
        ]}


def test_get_ec2_utilization_reads_cloudwatch_metrics():
    result = get_ec2_utilization(["i-test"], datetime(2026, 9, 1, tzinfo=timezone.utc), datetime(2026, 9, 2, tzinfo=timezone.utc), region="us-east-1", client=FakeCloudWatch())
    assert result[0]["cpu_average_pct"] == 10.0
    assert result[0]["cpu_max_pct"] == 40.0
    assert result[0]["network_in_bytes"] == 300.0
    assert result[0]["network_out_bytes"] == 700.0


def test_low_cpu_signal_is_evidence_based():
    result = correlate_cost_and_utilization([{ "resource_id": "i-test", "cost": 50.0 }], [{"instance_id": "i-test", "cpu_average_pct": 5.0, "cpu_max_pct": 20.0, "cpu_datapoints": 10}])
    assert "low-average-cpu-review" in result[0]["signals"]
    assert result[0]["mode"] == "analysis-only"


def test_missing_utilization_is_not_treated_as_zero():
    result = correlate_cost_and_utilization([{ "resource_id": "i-test", "cost": 50.0 }], [])
    assert result[0]["utilization_status"] == "not-available"
    assert result[0]["signals"] == ()
