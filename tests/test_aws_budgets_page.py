from pathlib import Path


def test_budget_dashboard_fields():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "Limit (USD)" in source
    assert "Actual (USD)" in source
    assert "Forecast (USD)" in source
    assert "Status" in source
