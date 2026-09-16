from datetime import date

from src.aws_cost_explorer import _parse_resource_results, get_ec2_resource_costs


class FakeCE:
    def get_cost_and_usage_with_resources(self, **kwargs):
        self.kwargs = kwargs
        return {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2026-09-01", "End": "2026-09-02"},
                    "Groups": [
                        {"Keys": ["i-123"], "Metrics": {"UnblendedCost": {"Amount": "2.50", "Unit": "USD"}}}
                    ],
                }
            ]
        }


def test_resource_parser_preserves_resource_id():
    result = _parse_resource_results([
        {
            "TimePeriod": {"Start": "2026-09-01", "End": "2026-09-02"},
            "Groups": [{"Keys": ["i-123"], "Metrics": {"UnblendedCost": {"Amount": "2.50", "Unit": "USD"}}}],
        }
    ])
    assert result[0].resource_id == "i-123"
    assert result[0].cost == 2.5
    assert result[0].source == "aws-cost-explorer-resource"


def test_resource_query_uses_daily_ec2_resource_grouping():
    client = FakeCE()
    result = get_ec2_resource_costs(date(2026, 9, 1), date(2026, 9, 2), client=client)
    assert result[0].resource_id == "i-123"
    assert client.kwargs["Granularity"] == "DAILY"
    assert client.kwargs["GroupBy"][0]["Key"] == "RESOURCE_ID"
    assert client.kwargs["Filter"]["Dimensions"]["Key"] == "SERVICE"
