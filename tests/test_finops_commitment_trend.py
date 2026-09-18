from src.finops_commitment_trend import (
    CommitmentTrendEvidence,
    commitment_trend,
    coverage_utilization_gap,
    trend_review_flags,
)


def test_trend_is_deterministic_and_sorted():
    records = [
        CommitmentTrendEvidence("2026-08", "savings-plan", 100, 80, 100, 60),
        CommitmentTrendEvidence("2026-07", "savings-plan", 100, 50, 100, 40),
    ]
    rows = commitment_trend(records)
    assert [row["period"] for row in rows] == ["2026-07", "2026-08"]
    assert rows[0]["coverage_pct"] == 50.0
    assert rows[1]["utilization_pct"] == 60.0


def test_gap_is_coverage_minus_utilization():
    record = CommitmentTrendEvidence("2026-08", "savings-plan", 100, 80, 100, 60)
    assert coverage_utilization_gap(record) == 20.0


def test_zero_denominators_are_unavailable():
    record = CommitmentTrendEvidence("2026-08", "savings-plan", 0, 0, 0, 0)
    assert coverage_utilization_gap(record) is None
    assert trend_review_flags(record) == ["coverage-unavailable"]


def test_low_utilization_with_coverage_is_flagged_as_mismatch():
    record = CommitmentTrendEvidence("2026-08", "savings-plan", 100, 80, 100, 20)
    assert trend_review_flags(record) == [
        "low-utilization-review",
        "coverage-utilization-mismatch",
    ]


def test_invalid_relationships_are_rejected():
    try:
        CommitmentTrendEvidence("2026-08", "savings-plan", 10, 11, 100, 20)
    except ValueError as exc:
        assert "covered_spend" in str(exc)
    else:
        raise AssertionError("expected ValueError")
