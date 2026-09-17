from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Iterable, Mapping

from .alerting import CostAlert


@dataclass(frozen=True)
class AlertEvent:
    key: str
    severity: str
    title: str
    detail: str
    status: str = "open"
    created_at: str = ""


class AlertMonitor:
    """In-memory, analysis-only alert lifecycle with deterministic deduplication."""

    def __init__(self) -> None:
        self._events: dict[str, AlertEvent] = {}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def key_for(service: str, period: str, reason: str) -> str:
        return f"{service.strip().lower()}|{period.strip()}|{reason.strip()}"

    def ingest_cost_alerts(self, alerts: Iterable[CostAlert]) -> list[AlertEvent]:
        created: list[AlertEvent] = []
        for alert in alerts:
            key = self.key_for(alert.service, alert.period, alert.reason)
            if key in self._events:
                continue
            event = AlertEvent(key, alert.severity, f"{alert.service} cost alert", alert.reason, created_at=self._now())
            self._events[key] = event
            created.append(event)
        return created

    def ingest_findings(self, findings: Iterable[Mapping[str, object]]) -> list[AlertEvent]:
        created: list[AlertEvent] = []
        for finding in findings:
            name = str(finding.get("name", finding.get("id", "finding")))
            period = str(finding.get("period", "current"))
            detail = str(finding.get("detail", finding.get("reason", "Review finding evidence.")))
            severity = str(finding.get("severity", "info"))
            key = self.key_for(name, period, detail)
            if key in self._events:
                continue
            event = AlertEvent(key, severity, name, detail, created_at=self._now())
            self._events[key] = event
            created.append(event)
        return created

    def _transition(self, key: str, status: str) -> AlertEvent | None:
        event = self._events.get(key)
        if event is None:
            return None
        updated = replace(event, status=status)
        self._events[key] = updated
        return updated

    def acknowledge(self, key: str) -> AlertEvent | None:
        return self._transition(key, "acknowledged")

    def resolve(self, key: str) -> AlertEvent | None:
        return self._transition(key, "resolved")

    def list_events(self, status: str | None = None) -> list[AlertEvent]:
        events = list(self._events.values())
        if status is not None:
            events = [event for event in events if event.status == status]
        return sorted(events, key=lambda event: event.created_at, reverse=True)

    def summary(self) -> dict[str, int]:
        events = self.list_events()
        return {
            "total": len(events),
            "open": sum(event.status == "open" for event in events),
            "acknowledged": sum(event.status == "acknowledged" for event in events),
            "resolved": sum(event.status == "resolved" for event in events),
        }
