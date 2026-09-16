from pathlib import Path


def test_budget_dashboard_is_analysis_only():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "AWS Budget Governance" in source
    assert "Analysis-only" in source
    assert "does not create, update, delete" in source
    assert "get_budgets" in source
