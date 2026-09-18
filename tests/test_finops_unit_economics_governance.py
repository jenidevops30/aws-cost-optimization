import pytest
from src.finops_unit_economics_governance import UnitEconomicsGovernanceEvidence, governance_rows, governance_summary

def test_governance_combines_signals():
    row=governance_rows([UnitEconomicsGovernanceEvidence("2026-08","api",.12,.10,True)])[0]
    assert row["forecast_error"] == pytest.approx(.02)
    assert row["governance_status"]=="review"

def test_incomplete_evidence_is_unavailable():
    row=governance_rows([UnitEconomicsGovernanceEvidence("2026-08","api",None,.10)])[0]
    assert row["evidence_status"]=="unavailable"
    assert row["forecast_error"] is None

def test_summary_counts():
    rows=[
      UnitEconomicsGovernanceEvidence("2026-06","api",.1,.1),
      UnitEconomicsGovernanceEvidence("2026-07","api",None,.1),
      UnitEconomicsGovernanceEvidence("2026-08","api",.2,.1,True),
    ]
    assert governance_summary(rows)=={"records":3,"available":2,"unavailable":1,"anomaly_reviews":1}

def test_negative_forecast_rejected():
    with pytest.raises(ValueError):
        UnitEconomicsGovernanceEvidence("2026-08","api",.1,-.1)
