from src.finops_exports import (
    build_export_bundle,
    build_validation_summary,
    report_to_csv,
    report_to_json,
    report_to_markdown,
)


def sample_report():
    return {
        "generated_at": "2026-09-16T00:00:00+00:00",
        "summary": {
            "total_analyzed_cost": 100.0,
            "billing_periods": 2,
            "services": 2,
            "anomalies": 1,
            "recommendation_candidates": 1,
        },
        "monthly_costs": [
            {"billing_period": "2026-01", "cost": 60.0},
            {"billing_period": "2026-02", "cost": 40.0},
        ],
        "service_totals": {"EC2": 70.0, "RDS": 30.0},
        "anomalies": [{"reason": "cost increase"}],
        "recommendations": [{"signal": "review"}],
        "limitations": ["No mutation"],
    }


def test_json_export_is_machine_readable():
    payload = report_to_json(sample_report())
    assert '"service_totals"' in payload
    assert '"EC2"' in payload


def test_csv_export_contains_monthly_rows():
    payload = report_to_csv(sample_report())
    assert "billing_period,cost" in payload
    assert "2026-02,40.0" in payload


def test_markdown_export_contains_summary_and_findings():
    payload = report_to_markdown(sample_report())
    assert "# FinOps Cost Report" in payload
    assert "## Executive Summary" in payload
    assert "cost increase" in payload


def test_validation_requires_both_comparison_periods():
    result = build_validation_summary(sample_report()["monthly_costs"], baseline=100)
    assert result["validation_status"] == "insufficient-evidence"
    assert result["post_optimization_cost"] is None


def test_validation_reports_observed_delta_without_attribution_claim():
    result = build_validation_summary(sample_report()["monthly_costs"], baseline=100, post_optimization=70)
    assert result["validation_status"] == "observed-reduction"
    assert result["observed_delta"] == 30.0
    assert "attribution" in result["notes"][0]


def test_export_bundle_preserves_report_and_validation():
    report = sample_report()
    bundle = build_export_bundle(report, {"validation_status": "observed-reduction"})
    assert bundle["summary"] == report["summary"]
    assert bundle["validation"]["validation_status"] == "observed-reduction"
    assert "exported_at" in bundle
