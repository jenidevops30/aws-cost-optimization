from src.deployment_readiness import deployment_ready, run_deployment_checks
from src.runtime_config import load_config


def test_demo_deployment_is_ready(tmp_path, monkeypatch):
    monkeypatch.setenv("FINOPS_MODE", "demo")
    monkeypatch.setenv("FINOPS_DATA_DIR", str(tmp_path))
    config = load_config()
    checks = run_deployment_checks(config)
    assert deployment_ready(config)
    assert {check.name for check in checks} >= {"configuration", "data-directory", "live-mode-safety"}


def test_missing_data_directory_blocks_readiness(tmp_path, monkeypatch):
    monkeypatch.setenv("FINOPS_MODE", "demo")
    monkeypatch.setenv("FINOPS_DATA_DIR", str(tmp_path / "missing"))
    config = load_config()
    assert not deployment_ready(config)


def test_live_mode_remains_analysis_only(tmp_path, monkeypatch):
    monkeypatch.setenv("FINOPS_MODE", "live")
    monkeypatch.setenv("FINOPS_DATA_DIR", str(tmp_path))
    config = load_config()
    checks = run_deployment_checks(config)
    safety = next(check for check in checks if check.name == "live-mode-safety")
    assert safety.status == "ready"
    assert "analysis-only" in safety.detail
