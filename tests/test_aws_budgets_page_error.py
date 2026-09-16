from pathlib import Path


def test_budget_dashboard_uses_generic_error_message():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "Budget data could not be loaded" in source
    assert "Exception" in source
