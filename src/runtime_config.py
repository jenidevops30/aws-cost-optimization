from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Raised when runtime configuration is invalid."""


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True)
class RuntimeConfig:
    mode: str
    region: str
    log_level: str
    aws_connect_timeout: int
    aws_read_timeout: int
    aws_max_attempts: int
    data_dir: str


def load_config() -> RuntimeConfig:
    mode = os.getenv("FINOPS_MODE", "demo").strip().lower()
    if mode not in {"demo", "live"}:
        raise ConfigurationError("FINOPS_MODE must be demo or live")
    region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1")).strip()
    if not region:
        raise ConfigurationError("AWS region must not be empty")
    log_level = os.getenv("FINOPS_LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigurationError("FINOPS_LOG_LEVEL is invalid")
    return RuntimeConfig(
        mode=mode,
        region=region,
        log_level=log_level,
        aws_connect_timeout=_positive_int("FINOPS_AWS_CONNECT_TIMEOUT", 10),
        aws_read_timeout=_positive_int("FINOPS_AWS_READ_TIMEOUT", 30),
        aws_max_attempts=_positive_int("FINOPS_AWS_MAX_ATTEMPTS", 5),
        data_dir=os.getenv("FINOPS_DATA_DIR", "data"),
    )
