from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .intelligence import Anomaly


@dataclass(frozen=True)
class CostAlert:
    period: str
    service: str
    severity: str
    current_cost: float
    baseline_cost: float
    change_pct: float
    reason: str
    action: str
    mode: str = "analysis-only"


def classify_severity(change_pct: float, warning_pct: float = 20.0, critical_pct: float = 50.0) -> str:
    magnitude = abs(change_pct)
    if magnitude >= critical_pct:
        return "critical"
    if magnitude >= warning_pct:
        return "warning"
    return "info"


def alerts_from_anomalies(
    anomalies: Iterable[Anomaly],
    *,
    warning_pct: float = 20.0,
    critical_pct: float = 50.0,
) -> list[CostAlert]:
    alerts: list[CostAlert] = []
    for anomaly in anomalies:
        severity = classify_severity(anomaly.change_pct, warning_pct, critical_pct)
        direction = "increased" if anomaly.change_pct > 0 else "decreased"
        alerts.append(
            CostAlert(
                period=anomaly.period,
                service=anomaly.service,
                severity=severity,
                current_cost=round(anomaly.cost, 2),
                baseline_cost=round(anomaly.baseline, 2),
                change_pct=round(anomaly.change_pct, 2),
                reason=f"{anomaly.service} cost {direction} by {abs(anomaly.change_pct):.2f}% versus the previous period.",
                action="Review usage, resource sizing, and recent infrastructure changes before taking action.",
            )
        )
    return alerts
