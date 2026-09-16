from pathlib import Path


def test_budget_dashboard_uses_read_only_collector():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert "get_budgets" in source
    assert "st.session_state" in source
