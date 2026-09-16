from pathlib import Path


SOURCE = Path("dashboard/pages/9_FinOps_Executive_Governance.py").read_text(encoding="utf-8")


def test_executive_dashboard_uses_governance_snapshot():
    assert "build_governance_snapshot" in SOURCE
    assert "snapshot_to_dict" in SOURCE
    assert "Analysis-only" in SOURCE


def test_executive_dashboard_supports_normalized_billing_upload():
    assert "file_uploader" in SOURCE
    assert "billing_period" in SOURCE
    assert "monthly_totals" in SOURCE


def test_executive_dashboard_does_not_contain_mutation_apis():
    forbidden = ("create_", "delete_", "modify_", "put_", "update_")
    assert not any(token in SOURCE for token in forbidden)
