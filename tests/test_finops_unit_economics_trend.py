import pytest

from src.finops_unit_economics_trend import unit_cost_change, unit_cost_trend


def test_trend_adds_cost_per_unit_and_sorts():
    rows = unit_cost_trend([
        {"period": "2026-08", "workload": "api", "unit_name": "requests", "cost": 120.0, "units": 1000},
        {"period": "2026-07", "workload": "api", "unit_name": "requests", "cost": 100.0, "units": 1000},
    ])
    assert rows[0]["period"] == "2026-07"
    assert rows[0]["cost_per_unit"] == 0.1


def test_unit_cost_change_is_percent_change():
    previous = {"cost": 100.0, "units": 1000}
    current = {"cost": 120.0, "units": 1500}
    assert unit_cost_change(previous, current) == pytest.approx(-20.0)


def test_zero_volume_is_unavailable():
    previous = {"cost": 100.0, "units": 0}
    current = {"cost": 120.0, "units": 1000}
    assert unit_cost_change(previous, current) is None


def test_zero_previous_unit_cost_is_unavailable():
    previous = {"cost": 0.0, "units": 1000}
    current = {"cost": 10.0, "units": 1000}
    assert unit_cost_change(previous, current) is None
