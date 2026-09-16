from pathlib import Path


def test_budget_dashboard_has_region_input():
    source = Path("dashboard/pages/8_Budget_Governance.py").read_text(encoding="utf-8")
    assert 'text_input("AWS region"' in source
