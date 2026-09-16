from __future__ import annotations

from dataclasses import asdict, dataclass

from .runtime_config import ConfigurationError, RuntimeConfig, load_config


@dataclass(frozen=True)
class HealthCheck:
    name: str
    status: str
    detail: str


def check_configuration(config: RuntimeConfig | None = None) -> HealthCheck:
    try:
        cfg = config or load_config()
        return HealthCheck("configuration", "ok", f"mode={cfg.mode}; region={cfg.region}")
    except ConfigurationError as exc:
        return HealthCheck("configuration", "failed", str(exc))


def readiness_report(config: RuntimeConfig | None = None) -> dict[str, object]:
    check = check_configuration(config)
    return {
        "status": "ready" if check.status == "ok" else "not-ready",
        "checks": [asdict(check)],
        "aws_mutations": False,
    }
