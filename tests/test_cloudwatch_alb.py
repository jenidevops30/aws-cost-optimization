from datetime import datetime, timezone

import pytest

from src.cloudwatch_alb import get_alb_metrics


class FakeCloudWatch:
    def __init__(self, paginated=False):
        self.calls = 0
        self.paginated = paginated

    def get_metric_data(self, **kwargs):
        self.calls += 1
        if self.paginated and self.calls == 1:
            return {
                "MetricDataResults": [
                    {"Id": query["Id"], "Values": [2.0, 4.0]}
                    for query in kwargs["MetricDataQueries"]
                ],
                "NextToken": "page-2",
            }
        values = [6.0] if self.paginated else [2.0, 4.0]
        return {
            "MetricDataResults": [
                {"Id": query["Id"], "Values": values}
                for query in kwargs["MetricDataQueries"]
            ]
        }


def test_get_alb_metrics_aggregates_sum_metrics_and_averages_average_metrics():
    rows = get_alb_metrics(
        [{"load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/demo/abc"}],
        datetime(2026, 9, 1, tzinfo=timezone.utc),
        datetime(2026, 9, 2, tzinfo=timezone.utc),
        region="us-east-1",
        client=FakeCloudWatch(),
    )
    assert rows[0]["request_count_total"] == 6.0
    assert rows[0]["processed_bytes_total"] == 6.0
    assert rows[0]["new_connections_total"] == 6.0
    assert rows[0]["active_connections_average"] == 3.0
    assert rows[0]["target_response_time_average"] == 3.0
    assert rows[0]["mode"] == "analysis-only"


def test_get_alb_metrics_collects_all_pages():
    client = FakeCloudWatch(paginated=True)
    rows = get_alb_metrics(
        [{"load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/demo/abc"}],
        datetime(2026, 9, 1, tzinfo=timezone.utc),
        datetime(2026, 9, 2, tzinfo=timezone.utc),
        region="us-east-1",
        client=client,
    )
    assert client.calls == 2
    assert rows[0]["request_count_total"] == 12.0
    assert rows[0]["active_connections_average"] == 4.0


def test_get_alb_metrics_rejects_invalid_window():
    with pytest.raises(ValueError, match="end must be after start"):
        get_alb_metrics([], datetime(2026, 9, 2, tzinfo=timezone.utc), datetime(2026, 9, 1, tzinfo=timezone.utc), region="us-east-1", client=FakeCloudWatch())
