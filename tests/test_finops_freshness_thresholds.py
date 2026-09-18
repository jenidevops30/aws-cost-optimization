import pytest
from datetime import datetime, timezone
from src.finops_freshness_thresholds import FreshnessEvidence, freshness_rows, freshness_summary

NOW=datetime(2026,9,1,12,0,tzinfo=timezone.utc)

def test_fresh_within_threshold():
    row=freshness_rows([FreshnessEvidence("billing","2026-09-01T10:00:00Z",24,10)],NOW)[0]
    assert row["freshness_status"]=="fresh"
    assert row["age_hours"]==pytest.approx(2)

def test_stale_after_threshold():
    row=freshness_rows([FreshnessEvidence("billing","2026-08-30T10:00:00Z",24,10)],NOW)[0]
    assert row["freshness_status"]=="stale"

def test_empty_dataset_is_stale():
    row=freshness_rows([FreshnessEvidence("billing","2026-09-01T10:00:00Z",24,0)],NOW)[0]
    assert row["freshness_status"]=="stale"

def test_summary():
    rows=freshness_rows([
      FreshnessEvidence("a","2026-09-01T10:00:00Z",24,1),
      FreshnessEvidence("b","2026-08-30T10:00:00Z",24,1),
    ],NOW)
    assert freshness_summary(rows)=={"datasets":2,"fresh":1,"stale":1}

def test_invalid_threshold_rejected():
    with pytest.raises(ValueError):
        FreshnessEvidence("a","2026-09-01T10:00:00Z",-1,1)
