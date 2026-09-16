from src.deployment_readiness import deployment_ready, run_deployment_checks
from src.runtime_config import RuntimeConfig


def test_demo_deployment_is_ready(tmp_path):
    config = RuntimeConfig(mode="demo", data_dir=str(tmp_path))
    checks = run_deployment_checks(config)
    assert deployment_ready(config)
    assert {check.name for check in checks} >= {"configuration", "data-directory", "live-mode-safety"}


def test_missing_data_directory_blocks_readiness(tmp_path):
    config = RuntimeConfig(mode="demo", data_dir=str(tmp_path / "missing"))
    assert not deployment_ready(config)


def test_live_mode_remains_analysis_only(tmp_path):
    config = RuntimeConfig(mode="live", data_dir=str(tmp_path))
    checks = run_deployment_checks(config)
    safety = next(check for check in checks if check.name == "live-mode-safety")
    assert safety.status == "ready"
    assert "analysis-only" in safety.detail
