import pytest
from src.finops_unit_economics_anomaly import UnitEconomicsAnomalyEvidence, anomaly_rows

def test_baseline_excludes_current_period():
    rows=anomaly_rows([
      UnitEconomicsAnomalyEvidence("2026-06","api",100,1000),
      UnitEconomicsAnomalyEvidence("2026-07","api",110,1000),
      UnitEconomicsAnomalyEvidence("2026-08","api",150,1000),
    ], .25)
    assert rows[0]["baseline_unit_cost"] is None
    assert rows[1]["baseline_unit_cost"] == pytest.approx(.1)
    assert rows[2]["anomaly_review"] is True

def test_zero_volume_is_unavailable():
    row=anomaly_rows([UnitEconomicsAnomalyEvidence("2026-08","api",100,0)])[0]
    assert row["unit_cost"] is None
    assert row["evidence_status"] == "unavailable"

def test_threshold_validation():
    with pytest.raises(ValueError):
        anomaly_rows([], -0.1)

def test_negative_values_rejected():
    with pytest.raises(ValueError):
        UnitEconomicsAnomalyEvidence("2026-08","api",-1,100)

def test_workloads_have_separate_history():
    rows=anomaly_rows([
      UnitEconomicsAnomalyEvidence("2026-06","a",100,1000),
      UnitEconomicsAnomalyEvidence("2026-07","b",200,1000),
    ])
    assert all(r["baseline_unit_cost"] is None for r in rows)
