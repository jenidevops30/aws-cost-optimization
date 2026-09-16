from src.aws_cost_explorer import _parse_resource_results, _parse_results


def test_parse_results_groups_service_costs():
    results = [
        {
            "TimePeriod": {"Start": "2026-06-01", "End": "2026-07-01"},
            "Groups": [
                {
                    "Keys": ["Amazon Elastic Compute Cloud - Compute"],
                    "Metrics": {"UnblendedCost": {"Amount": "118.72", "Unit": "USD"}},
                },
                {
                    "Keys": ["Amazon Relational Database Service"],
                    "Metrics": {"UnblendedCost": {"Amount": "79.71", "Unit": "USD"}},
                },
            ],
        }
    ]

    records = _parse_results(results)

    assert len(records) == 2
    assert records[0].billing_period == "2026-06"
    assert records[0].cost == 118.72
    assert records[0].source == "aws-cost-explorer"


def test_parse_results_handles_empty_group_key():
    results = [
        {
            "TimePeriod": {"Start": "2026-07-01", "End": "2026-08-01"},
            "Groups": [
                {
                    "Keys": [],
                    "Metrics": {"UnblendedCost": {"Amount": "1.25", "Unit": "USD"}},
                }
            ],
        }
    ]

    records = _parse_results(results)

    assert records[0].service == "Uncategorized"
    assert records[0].cost == 1.25


def test_parse_resource_results_preserves_resource_id():
    results = [
        {
            "TimePeriod": {"Start": "2026-06-15", "End": "2026-06-16"},
            "Groups": [
                {
                    "Keys": ["i-0123456789abcdef0"],
                    "Metrics": {"UnblendedCost": {"Amount": "4.25", "Unit": "USD"}},
                }
            ],
        }
    ]

    records = _parse_resource_results(results)

    assert len(records) == 1
    assert records[0].billing_period == "2026-06"
    assert records[0].service == "EC2"
    assert records[0].resource_id == "i-0123456789abcdef0"
    assert records[0].cost == 4.25
    assert records[0].source == "aws-cost-explorer-resource"
