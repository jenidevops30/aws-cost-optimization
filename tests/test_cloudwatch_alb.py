from datetime import datetime, timezone

import pytest

from src.cloudwatch_alb import get_alb_metrics


class FakeCloudWatch:
    def get_metric_data(self, **kwargs):
        return {
            "MetricDataResults": [
                {"Id": query["Id"], "Values": [2.0, 4.0]}
                for query in kwargs["MetricDataQueries"]
            ]
        }


def test_get_alb_metrics_reads_expected_evidence():
    rows = get_alb_metrics(
        [{"load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/demo/abc"}],
        datetime(2026, 9, 1, tzinfo=timezone.utc),
        datetime(2026, 9, 2, tzinfo=timezone.utc),
        region="us-east-1",
        client=FakeCloudWatch(),
    )
    assert rows[0]["request_count_average"] == 3.0
    assert rows[0]["processed_bytes_average"] == 3.0
    assert rows[0]["target_response_time_average"] == 3.0
    assert rows[0]["mode"] == "analysis-only"


def test_get_alb_metrics_rejects_invalid_window():
    with pytest.raises(ValueError, match="end must be after start"):
        get_alb_metrics([], datetime(2026, 9, 2, tzinfo=timezone.utc), datetime(2026, 9, 1, tzinfo=timezone.utc), region="us-east-1", client=FakeCloudWatch())
