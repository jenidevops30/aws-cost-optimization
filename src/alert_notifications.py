from __future__ import annotations

import json
from dataclasses import asdict
from typing import Callable, Iterable

from .alert_monitoring import AlertEvent


def format_alert(event: AlertEvent) -> str:
    return f"[{event.severity.upper()}] {event.title}: {event.detail}"


class ConsoleNotifier:
    """Dependency-free notifier for local and CI diagnostics."""

    def send(self, events: Iterable[AlertEvent]) -> list[str]:
        messages = [format_alert(event) for event in events]
        for message in messages:
            print(message)
        return messages


class WebhookNotifier:
    """Transport-neutral adapter; callers inject their approved HTTP sender."""

    def __init__(self, sender: Callable[[dict[str, object]], None]) -> None:
        self._sender = sender

    def send(self, events: Iterable[AlertEvent]) -> int:
        count = 0
        for event in events:
            self._sender({"event": asdict(event)})
            count += 1
        return count


def webhook_payload(event: AlertEvent) -> str:
    return json.dumps({"event": asdict(event)}, sort_keys=True)
