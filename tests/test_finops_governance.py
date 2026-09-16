from src.finops_governance import build_governance_snapshot, snapshot_to_dict


def test_snapshot_combines_governance_signals():
    snapshot = build_governance_snapshot(
        [{"period": "2026-05", "cost": 100}, {"period": "2026-06", "cost": 80}],
        [{"name": "prod", "status": "over-budget"}, {"name": "dev", "status": "near-limit"}],
        [{"estimated_impact_usd": 12.5}, {"estimated_impact_usd": 2.5}],
        [{"signal": "review"}],
        {"projected_cost": 85, "confidence": "medium"},
        {"validation_status": "observed-reduction"},
    )
    assert snapshot.latest_period == "2026-06"
    assert snapshot.latest_cost_usd == 80.0
    assert snapshot.previous_cost_usd == 100.0
    assert snapshot.month_over_month_pct == -20.0
    assert snapshot.over_budget_count == 1
    assert snapshot.near_limit_count == 1
    assert snapshot.anomaly_count == 2
    assert snapshot.anomaly_impact_usd == 15.0
    assert snapshot.finding_count == 1
    assert snapshot.forecast_usd == 85.0
    assert snapshot.forecast_confidence == "medium"
    assert snapshot.validation_status == "observed-reduction"
    assert snapshot.evidence_status == "multi-signal"
    assert snapshot.mode == "analysis-only"


def test_snapshot_handles_missing_evidence():
    snapshot = build_governance_snapshot([])
    data = snapshot_to_dict(snapshot)
    assert data["latest_cost_usd"] is None
    assert data["previous_cost_usd"] is None
    assert data["month_over_month_pct"] is None
    assert data["forecast_usd"] is None
    assert data["forecast_confidence"] is None
    assert data["budget_count"] == 0
    assert data["anomaly_count"] == 0
    assert data["finding_count"] == 0
    assert data["validation_status"] == "not-provided"
    assert data["evidence_status"] == "insufficient-evidence"


def test_cost_only_evidence_is_distinguished_from_multi_signal():
    snapshot = build_governance_snapshot([{"period": "2026-06", "cost": 327.07}])
    assert snapshot.evidence_status == "cost-only"


def test_zero_previous_cost_does_not_create_invalid_mom():
    snapshot = build_governance_snapshot(
        [{"period": "2026-05", "cost": 0}, {"period": "2026-06", "cost": 100}]
    )
    assert snapshot.month_over_month_pct is None


def test_invalid_anomaly_impact_does_not_become_fake_cost():
    snapshot = build_governance_snapshot(
        [{"period": "2026-06", "cost": 100}],
        anomalies=[{"estimated_impact_usd": "unavailable"}],
    )
    assert snapshot.anomaly_count == 1
    assert snapshot.anomaly_impact_usd == 0.0
    assert snapshot.evidence_status == "multi-signal"
