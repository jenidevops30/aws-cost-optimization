from pathlib import Path


PAGE = Path("dashboard/pages/2_EC2_Cost_Intelligence.py")


def test_ec2_cost_intelligence_page_compiles():
    source = PAGE.read_text(encoding="utf-8")
    compile(source, str(PAGE), "exec")


def test_ec2_dashboard_is_read_only():
    source = PAGE.read_text(encoding="utf-8")
    assert "get_ec2_resource_costs" in source
    assert "get_ec2_inventory" in source
    assert "No EC2 resources are modified" in source
    assert "Signals are review candidates, not automatic rightsizing decisions." in source
    assert "CPU utilization is evidence for investigation, not a complete capacity model" in source
