from __future__ import annotations

import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


_SECRET_RE = re.compile(
    r"(?i)(aws_access_key_id|aws_secret_access_key|aws_session_token|authorization|token|password|secret|private_key)\s*[=:]\s*([^,\s;]+)"
)


@dataclass
class MetricCounter:
    value: int = 0


@dataclass
class MetricsRegistry:
    _counters: dict[str, MetricCounter] = field(default_factory=dict)
    _durations_ms: dict[str, list[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters.setdefault(name, MetricCounter()).value += amount

    def observe(self, name: str, duration_ms: float) -> None:
        with self._lock:
            self._durations_ms.setdefault(name, []).append(max(0.0, duration_ms))

    def record_aws_call(self, operation: str, status: str, duration_ms: float) -> None:
        self.increment(f"aws_api_calls_total|operation={operation}|status={status}")
        self.observe(f"aws_api_call_duration_ms|operation={operation}", duration_ms)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            durations = {
                key: {
                    "count": len(values),
                    "avg_ms": round(sum(values) / len(values), 2) if values else 0.0,
                    "max_ms": round(max(values), 2) if values else 0.0,
                }
                for key, values in self._durations_ms.items()
            }
            return {
                "counters": {key: counter.value for key, counter in self._counters.items()},
                "durations": durations,
            }

    def prometheus_text(self) -> str:
        snapshot = self.snapshot()
        lines = ["# HELP finops_events_total Operational events.", "# TYPE finops_events_total counter"]
        for key, value in snapshot["counters"].items():
            metric, *labels = key.split("|")
            label_text = ""
            if labels:
                label_pairs = [item.split("=", 1) for item in labels if "=" in item]
                label_text = "{" + ",".join(f'{k}="{v}"' for k, v in label_pairs) + "}"
            lines.append(f"{metric}{label_text} {value}")
        for key, values in snapshot["durations"].items():
            metric, *labels = key.split("|")
            label_text = ""
            if labels:
                label_pairs = [item.split("=", 1) for item in labels if "=" in item]
                label_text = "{" + ",".join(f'{k}="{v}"' for k, v in label_pairs) + "}"
            lines.append(f"{metric}_count{label_text} {values['count']}")
            lines.append(f"{metric}_avg_ms{label_text} {values['avg_ms']}")
            lines.append(f"{metric}_max_ms{label_text} {values['max_ms']}")
        return "\n".join(lines) + "\n"


METRICS = MetricsRegistry()


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def classify_exception(exc: BaseException) -> str:
    name = type(exc).__name__.lower()
    text = str(exc).lower()
    if "credential" in name or "credential" in text or "auth" in name:
        return "aws-authentication-error"
    if "accessdenied" in name or "unauthorized" in text or "forbidden" in text:
        return "aws-permission-error"
    if "throttl" in name or "throttl" in text:
        return "aws-throttling"
    if name in {"connectionerror", "timeout", "timeouterror", "endpointconnectionerror"}:
        return "dependency-error"
    if "config" in name:
        return "configuration-error"
    return "application-error"


def sanitize_error(value: str) -> str:
    return _SECRET_RE.sub(r"\1=[REDACTED]", value)


def timed_aws_call(operation: str):
    class _Timer:
        def __enter__(self):
            self.started = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc, tb):
            duration_ms = (time.perf_counter() - self.started) * 1000
            status = "success" if exc is None else classify_exception(exc)
            METRICS.record_aws_call(operation, status, duration_ms)
            return False

    return _Timer()
