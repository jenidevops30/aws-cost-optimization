from pathlib import Path


def test_budget_dashboard_metadata():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "page_title=\"Budget Governance\"" in source
