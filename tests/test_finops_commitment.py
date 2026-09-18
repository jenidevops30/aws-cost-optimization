import pytest

from src.finops_commitment import (
    CommitmentEvidence,
    aggregate_commitment_coverage,
    commitment_review_flags,
    coverage_percent,
)


def test_coverage_is_deterministic():
    record = CommitmentEvidence("2026-08", "savings-plan", "Amazon EC2", 100, 75)
    assert coverage_percent(record) == pytest.approx(75.0)
    assert commitment_review_flags(record) == []


def test_zero_eligible_spend_is_not_zero_coverage():
    record = CommitmentEvidence("2026-08", "reserved-instance", "Amazon RDS", 0, 0)
    assert coverage_percent(record) is None
    assert commitment_review_flags(record) == ["no-eligible-spend"]


def test_aggregate_preserves_commitment_type_and_period():
    records = [
        CommitmentEvidence("2026-08", "savings-plan", "Amazon EC2", 100, 40),
        CommitmentEvidence("2026-08", "savings-plan", "Amazon EC2", 50, 30),
        CommitmentEvidence("2026-08", "reserved-instance", "Amazon RDS", 80, 20),
    ]
    rows = aggregate_commitment_coverage(records)
    assert rows == [
        {
            "period": "2026-08",
            "commitment_type": "reserved-instance",
            "eligible_spend": 80.0,
            "covered_spend": 20.0,
            "uncovered_spend": 60.0,
            "coverage_pct": 25.0,
        },
        {
            "period": "2026-08",
            "commitment_type": "savings-plan",
            "eligible_spend": 150.0,
            "covered_spend": 70.0,
            "uncovered_spend": 80.0,
            "coverage_pct": pytest.approx(46.666666666666664),
        },
    ]


def test_invalid_commitment_type_and_spend_are_rejected():
    with pytest.raises(ValueError):
        CommitmentEvidence("2026-08", "spot", "Amazon EC2", 100, 50)
    with pytest.raises(ValueError):
        CommitmentEvidence("2026-08", "savings-plan", "Amazon EC2", 50, 60)
