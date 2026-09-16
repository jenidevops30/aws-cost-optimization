from pathlib import Path


def test_budget_dashboard_is_read_only():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "Analysis-only" in source
    assert "does not create, update, delete" in source
