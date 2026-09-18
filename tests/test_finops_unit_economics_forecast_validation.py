import pytest
from src.finops_unit_economics_forecast_validation import UnitEconomicsForecastValidation, validate_forecast_rows, mean_absolute_error

def test_validation_error():
    rows=validate_forecast_rows([UnitEconomicsForecastValidation("2026-08","api",0.15,0.10)])
    assert rows[0]["forecast_error"] == pytest.approx(0.05)

def test_mae():
    records=[UnitEconomicsForecastValidation("2026-07","api",0.12,0.10),UnitEconomicsForecastValidation("2026-08","api",0.14,0.10)]
    assert mean_absolute_error(records)==pytest.approx(0.03)

def test_unavailable():
    row=validate_forecast_rows([UnitEconomicsForecastValidation("2026-08","api",None,0.1)])[0]
    assert row["validation_status"]=="unavailable"
    assert row["forecast_error"] is None

def test_negative_rejected():
    with pytest.raises(ValueError):
        UnitEconomicsForecastValidation("2026-08","api",-1,1)

def test_empty_error_metric():
    assert mean_absolute_error([]) is None
