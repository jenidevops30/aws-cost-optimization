import pytest
from src.finops_unit_economics_forecast import UnitEconomicsForecastEvidence, forecast_rows

def test_forecast_uses_historical_unit_cost_mean():
    row=forecast_rows([
      UnitEconomicsForecastEvidence("2026-06","api",100,1000),
      UnitEconomicsForecastEvidence("2026-07","api",120,1000),
    ])[0]
    assert row["next_period_unit_cost_forecast"] == pytest.approx(0.11)
    assert row["confidence"] == "low"

def test_three_observations_medium_confidence():
    row=forecast_rows([
      UnitEconomicsForecastEvidence("2026-06","api",100,1000),
      UnitEconomicsForecastEvidence("2026-07","api",120,1000),
      UnitEconomicsForecastEvidence("2026-08","api",140,1000),
    ])[0]
    assert row["confidence"] == "medium"

def test_zero_volume_unavailable():
    row=forecast_rows([UnitEconomicsForecastEvidence("2026-08","api",100,0)])[0]
    assert row["next_period_unit_cost_forecast"] is None
    assert row["evidence_status"] == "unavailable"

def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        UnitEconomicsForecastEvidence("2026-08","api",-1,100)
