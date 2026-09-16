from datetime import datetime, timezone

import pytest

from src.cloudwatch_ebs import get_ebs_metrics


class FakeCloudWatch:
    def get_metric_data(self, **kwargs):
        results = []
        for query in kwargs["MetricDataQueries"]:
            values = [2.0, 4.0] if query["Id"] in {"read_ops", "write_ops"} else [10.0]
            results.append({"Id": query["Id"], "Values": values})
        return {"MetricDataResults": results}


def test_get_ebs_metrics_reads_expected_evidence():
    rows = get_ebs_metrics(
        ["vol-123"],
        datetime(2026, 9, 1, tzinfo=timezone.utc),
        datetime(2026, 9, 2, tzinfo=timezone.utc),
        region="us-east-1",
        client=FakeCloudWatch(),
    )
    assert rows[0]["volume_id"] == "vol-123"
    assert rows[0]["read_ops_average"] == 3.0
    assert rows[0]["write_ops_average"] == 3.0
    assert rows[0]["queue_length_average"] == 10.0
    assert rows[0]["mode"] == "analysis-only"


def test_get_ebs_metrics_rejects_invalid_window():
    with pytest.raises(ValueError, match="end must be after start"):
        get_ebs_metrics(
            ["vol-123"],
            datetime(2026, 9, 2, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            region="us-east-1",
            client=FakeCloudWatch(),
        )
