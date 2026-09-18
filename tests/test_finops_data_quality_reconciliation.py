import pytest
from src.finops_data_quality_reconciliation import ReconciliationEvidence,reconciliation_row,reconciliation_summary

def test_match_within_tolerance():
    row=reconciliation_row(ReconciliationEvidence("billing",100,100.005,.01))
    assert row["reconciliation_status"]=="matched"

def test_mismatch():
    row=reconciliation_row(ReconciliationEvidence("billing",100,98,0.5))
    assert row["difference"]==pytest.approx(2)
    assert row["reconciliation_status"]=="mismatch"

def test_zero_baseline_relative_difference_unavailable():
    row=reconciliation_row(ReconciliationEvidence("billing",0,0,0))
    assert row["relative_difference"] is None

def test_summary():
    rows=[
      reconciliation_row(ReconciliationEvidence("a",10,10)),
      reconciliation_row(ReconciliationEvidence("b",10,8)),
    ]
    assert reconciliation_summary(rows)=={"dimensions":2,"matched":1,"mismatch":1}

def test_negative_rejected():
    with pytest.raises(ValueError):
        ReconciliationEvidence("a",-1,1)
