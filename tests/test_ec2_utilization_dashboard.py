from pathlib import Path


PAGE = Path("dashboard/pages/2_EC2_Cost_Intelligence.py")


def test_dashboard_page_compiles():
    source = PAGE.read_text(encoding="utf-8")
    compile(source, str(PAGE), "exec")


def test_dashboard_uses_read_only_cloudwatch_metrics():
    source = PAGE.read_text(encoding="utf-8")
    assert "get_ec2_utilization" in source
    assert "GetMetricData" in source
    assert "No EC2 resources are modified" in source
    assert "memory utilization requires" in source
