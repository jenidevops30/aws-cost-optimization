import logging

import pytest

from src.runtime_config import ConfigurationError, load_config
from src.runtime_health import readiness_report
from src.structured_logging import RedactedJsonFormatter


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("FINOPS_MODE", raising=False)
    cfg = load_config()
    assert cfg.mode == "demo"
    assert cfg.region


def test_invalid_mode(monkeypatch):
    monkeypatch.setenv("FINOPS_MODE", "mutate")
    with pytest.raises(ConfigurationError):
        load_config()


def test_invalid_timeout(monkeypatch):
    monkeypatch.setenv("FINOPS_AWS_READ_TIMEOUT", "0")
    with pytest.raises(ConfigurationError):
        load_config()


def test_readiness_is_explicitly_analysis_only(monkeypatch):
    monkeypatch.setenv("FINOPS_MODE", "live")
    report = readiness_report()
    assert report["status"] == "ready"
    assert report["aws_mutations"] is False


def test_logging_redacts_secrets():
    formatter = RedactedJsonFormatter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "token=abc123 secret=xyz", (), None)
    output = formatter.format(record)
    assert "abc123" not in output
    assert "xyz" not in output
    assert "REDACTED" in output
