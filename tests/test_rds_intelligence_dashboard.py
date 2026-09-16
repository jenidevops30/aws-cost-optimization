from pathlib import Path


DASHBOARD = Path(__file__).parents[1] / "dashboard/pages/3_RDS_Cost_Intelligence.py"


def test_rds_dashboard_compiles():
    compile(DASHBOARD.read_text(encoding="utf-8"), str(DASHBOARD), "exec")


def test_rds_dashboard_uses_read_only_evidence_sources():
    source = DASHBOARD.read_text(encoding="utf-8")
    assert "get_rds_inventory" in source
    assert "get_service_costs" in source
    assert "get_rds_utilization" in source
    assert "GetMetricData" in source
    assert "No RDS resources are modified" in source
    assert "not be divided across DB instances" in source
