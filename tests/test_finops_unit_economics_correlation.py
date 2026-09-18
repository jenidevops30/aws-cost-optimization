import pytest

from src.finops_unit_economics_correlation import UnitCostCorrelationEvidence, correlation_rows, cost_per_unit


def test_cost_per_unit_and_signal_are_preserved():
    record = UnitCostCorrelationEvidence("2026-08", "api", "requests", 120.0, 1000, 70.0, "avg_cpu_pct")
    assert cost_per_unit(record) == pytest.approx(0.12)
    row = correlation_rows([record])[0]
    assert row["supporting_signal"] == 70.0
    assert row["signal_name"] == "avg_cpu_pct"
    assert row["evidence_status"] == "available"


def test_missing_signal_is_not_zero():
    record = UnitCostCorrelationEvidence("2026-08", "api", "requests", 120.0, 1000)
    assert correlation_rows([record])[0]["supporting_signal"] is None
    assert correlation_rows([record])[0]["evidence_status"] == "unavailable"


def test_zero_units_remains_unavailable():
    record = UnitCostCorrelationEvidence("2026-08", "api", "requests", 120.0, 0)
    assert cost_per_unit(record) is None


def test_signal_requires_name():
    try:
        UnitCostCorrelationEvidence("2026-08", "api", "requests", 1.0, 1, 50.0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_negative_values_rejected():
    with pytest.raises(ValueError):
        UnitCostCorrelationEvidence("2026-08", "api", "requests", -1.0, 1)
