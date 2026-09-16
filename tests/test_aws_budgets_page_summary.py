from pathlib import Path


def test_budget_dashboard_summary_labels():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "Budgets" in source
    assert "Over budget" in source
    assert "Near limit" in source
    assert "Forecast" in source
