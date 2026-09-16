from datetime import date

import pytest

from src.cost_anomaly import get_cost_anomalies, summarize_anomalies


class FakeCE:
    def __init__(self):
        self.calls = []

    def get_anomalies(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return {"Anomalies": [{"AnomalyId": "a-1", "MonitorArn": "arn:monitor", "AnomalyStartDate": "2026-09-01", "AnomalyEndDate": "2026-09-02", "Impact": {"TotalImpact": "42.50", "TotalActualSpend": "142.50"}, "RootCauses": [{"Service": "Amazon EC2", "Region": "ap-south-1", "UsageType": "BoxUsage", "LinkedAccount": "123"}]}], "NextPageToken": "page-2"}
        return {"Anomalies": [{"AnomalyId": "a-2", "Impact": {"TotalImpact": "7.50", "TotalActualSpend": "57.50"}, "RootCauses": [{"Service": "Amazon RDS"}]}]}


def test_get_cost_anomalies_handles_pagination_and_preserves_impact_fields():
    client = FakeCE()
    rows = get_cost_anomalies(date(2026, 9, 1), date(2026, 9, 10), monitor_arn="arn:monitor", client=client)
    assert len(rows) == 2
    assert rows[0]["estimated_impact_usd"] == 42.5
    assert rows[0]["actual_spend_usd"] == 142.5
    assert client.calls[1]["NextPageToken"] == "page-2"


def test_summary_is_deterministic():
    summary = summarize_anomalies([
        {"estimated_impact_usd": 10, "root_causes": [{"service": "Amazon EC2"}]},
        {"estimated_impact_usd": 2.5, "root_causes": [{"service": "Amazon RDS"}]},
    ])
    assert summary["anomaly_count"] == 2
    assert summary["total_estimated_impact_usd"] == 12.5
    assert summary["max_estimated_impact_usd"] == 10
    assert summary["affected_services"] == ["Amazon EC2", "Amazon RDS"]


def test_invalid_window_and_page_size_are_rejected():
    with pytest.raises(ValueError):
        get_cost_anomalies(date(2026, 9, 10), date(2026, 9, 1), client=FakeCE())
    with pytest.raises(ValueError):
        get_cost_anomalies(date(2026, 9, 1), date(2026, 9, 2), max_results=101, client=FakeCE())
