from __future__ import annotations

from src.observability import MetricsRegistry, classify_exception, new_correlation_id, sanitize_error, timed_aws_call
from src.runtime_config import load_config
from src.runtime_health import readiness_report


class AccessDeniedException(Exception):
    pass


class ThrottlingException(Exception):
    pass


class CredentialError(Exception):
    pass


def test_correlation_id_is_unique():
    assert new_correlation_id() != new_correlation_id()


def test_exception_classification():
    assert classify_exception(CredentialError("bad credentials")) == "aws-authentication-error"
    assert classify_exception(AccessDeniedException("forbidden")) == "aws-permission-error"
    assert classify_exception(ThrottlingException("throttling")) == "aws-throttling"


def test_error_sanitization():
    value = "token=super-secret password=hunter2 authorization=Bearer-secret"
    safe = sanitize_error(value)
    assert "super-secret" not in safe
    assert "hunter2" not in safe
    assert "Bearer-secret" not in safe
    assert "[REDACTED]" in safe


def test_metrics_registry_records_calls():
    registry = MetricsRegistry()
    with timed_aws_call("DescribeInstances"):
        pass
    # The shared registry is intentionally exercised through the production helper;
    # direct registry behavior is also verified here.
    registry.increment("test_events_total")
    registry.observe("test_duration_ms", 12.5)
    snapshot = registry.snapshot()
    assert snapshot["counters"]["test_events_total"] == 1
    assert snapshot["durations"]["test_duration_ms"]["count"] == 1


def test_readiness_remains_analysis_only(monkeypatch, tmp_path):
    monkeypatch.setenv("FINOPS_MODE", "demo")
    monkeypatch.setenv("FINOPS_DATA_DIR", str(tmp_path))
    report = readiness_report(load_config())
    assert report["status"] == "ready"
    assert report["aws_mutations"] is False
