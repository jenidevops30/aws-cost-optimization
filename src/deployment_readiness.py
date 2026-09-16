from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.runtime_config import RuntimeConfig
from src.runtime_health import HealthCheck


@dataclass(frozen=True)
class DeploymentCheck:
    name: str
    status: str
    detail: str


def run_deployment_checks(config: RuntimeConfig) -> list[DeploymentCheck]:
    """Run local, non-mutating checks before deploying the dashboard."""
    checks: list[DeploymentCheck] = []
    health = HealthCheck(config)

    for item in health.readiness_report():
        checks.append(DeploymentCheck(item.name, item.status, item.detail))

    data_dir = Path(config.data_dir)
    if data_dir.exists() and data_dir.is_dir():
        checks.append(DeploymentCheck("data-directory", "ready", str(data_dir)))
    else:
        checks.append(DeploymentCheck("data-directory", "not-ready", f"Directory does not exist: {data_dir}"))

    if config.mode == "live":
        checks.append(
            DeploymentCheck(
                "live-mode-safety",
                "ready",
                "Live AWS integration remains analysis-only; no mutation APIs are enabled.",
            )
        )
    else:
        checks.append(DeploymentCheck("live-mode-safety", "ready", "Demo mode performs no AWS API calls."))

    return checks


def deployment_ready(config: RuntimeConfig) -> bool:
    """Return true only when every deployment check is ready."""
    return all(check.status == "ready" for check in run_deployment_checks(config))
