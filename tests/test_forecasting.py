import pytest

from src.cost_engine import CostRecord
from src.forecasting import forecast_next_month, simulate_savings


def records():
    return [
        CostRecord("2026-01", "EC2", "instances", "us-east-1", 100),
        CostRecord("2026-02", "EC2", "instances", "us-east-1", 120),
        CostRecord("2026-03", "EC2", "instances", "us-east-1", 140),
    ]


def test_forecast_uses_recent_historical_mean():
    result = forecast_next_month(records())
    assert result.forecast_period == "2026-04"
    assert result.projected_cost == 120
    assert result.confidence == "medium"
    assert result.mode == "analysis-only"


def test_forecast_rolls_year_boundary():
    data = [CostRecord("2026-12", "EC2", "instances", "us-east-1", 200)]
    assert forecast_next_month(data).forecast_period == "2027-01"


def test_savings_simulation():
    scenarios = simulate_savings(records(), (10.0, 30.0))
    assert scenarios[0].projected_cost == 126
    assert scenarios[0].projected_saving == 14
    assert scenarios[1].projected_cost == 98
    assert scenarios[1].projected_saving == 42


def test_invalid_savings_percentage():
    with pytest.raises(ValueError):
        simulate_savings(records(), (110.0,))
