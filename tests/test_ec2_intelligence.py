from dataclasses import dataclass

from src.ec2_intelligence import build_ec2_cost_insights


@dataclass
class Cost:
    resource_id: str
    cost: float


def test_ec2_cost_insights_correlate_cost_and_inventory():
    costs = [Cost("i-expensive", 80.0), Cost("i-small", 20.0)]
    inventory = [
        {"instance_id": "i-expensive", "instance_type": "c5.xlarge", "architecture": "x86_64", "state": "running"},
        {"instance_id": "i-small", "instance_type": "t4g.small", "architecture": "arm64", "state": "running"},
    ]

    result = build_ec2_cost_insights([c.__dict__ for c in costs], inventory)

    assert result[0].instance_id == "i-expensive"
    assert result[0].cost == 80.0
    assert result[0].monthly_share_pct == 80.0
    assert "arm64-review" in result[0].signals
    assert "high-cost-concentration" in result[0].signals
    assert result[1].signals == ()


def test_stopped_instance_gets_review_signal_without_savings_claim():
    result = build_ec2_cost_insights(
        [{"resource_id": "i-stopped", "cost": 10.0}],
        [{"instance_id": "i-stopped", "instance_type": "m5.large", "architecture": "x86_64", "state": "stopped"}],
    )

    assert "stopped-resource-review" in result[0].signals
    assert result[0].mode == "analysis-only"
