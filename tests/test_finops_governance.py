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
    assert snapshot.month_over_month_pct == -20.0
    assert snapshot.over_budget_count == 1
    assert snapshot.near_limit_count == 1
    assert snapshot.anomaly_count == 2
    assert snapshot.anomaly_impact_usd == 15.0
    assert snapshot.finding_count == 1
    assert snapshot.forecast_usd == 85.0
    assert snapshot.evidence_status == "multi-signal"
    assert snapshot.mode == "analysis-only"


def test_snapshot_handles_missing_evidence():
    snapshot = build_governance_snapshot([])
    data = snapshot_to_dict(snapshot)
    assert data["latest_cost_usd"] is None
    assert data["month_over_month_pct"] is None
    assert data["forecast_usd"] is None
    assert data["evidence_status"] == "insufficient-evidence"
