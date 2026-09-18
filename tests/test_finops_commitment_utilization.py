import pytest

from src.finops_commitment_utilization import (
    CommitmentUtilizationEvidence,
    aggregate_utilization,
    utilization_percent,
    utilization_review_flags,
)


def test_utilization_is_deterministic():
    record = CommitmentUtilizationEvidence("2026-08", "savings-plan", 100, 75)
    assert utilization_percent(record) == pytest.approx(75.0)
    assert utilization_review_flags(record) == []


def test_zero_committed_value_is_unavailable():
    record = CommitmentUtilizationEvidence("2026-08", "reserved-instance", 0, 0)
    assert utilization_percent(record) is None
    assert utilization_review_flags(record) == ["no-committed-value"]


def test_low_utilization_is_flagged():
    record = CommitmentUtilizationEvidence("2026-08", "reserved-instance", 100, 25)
    assert utilization_review_flags(record) == ["low-utilization-review"]


def test_aggregate_preserves_period_and_type():
    records = [
        CommitmentUtilizationEvidence("2026-08", "savings-plan", 100, 40),
        CommitmentUtilizationEvidence("2026-08", "savings-plan", 50, 30),
    ]
    assert aggregate_utilization(records) == [{
        "period": "2026-08", "commitment_type": "savings-plan",
        "committed_value": 150.0, "utilized_value": 70.0,
        "unused_value": 80.0, "utilization_pct": pytest.approx(46.666666666666664),
    }]


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        CommitmentUtilizationEvidence("2026-08", "spot", 100, 50)
    with pytest.raises(ValueError):
        CommitmentUtilizationEvidence("2026-08", "savings-plan", 50, 60)
