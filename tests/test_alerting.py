from dataclasses import dataclass

from src.alerting import alerts_from_anomalies, classify_severity


@dataclass
class Anomaly:
    period: str
    service: str
    cost: float
    baseline: float
    change_pct: float
    severity: str = "medium"


def test_classify_severity():
    assert classify_severity(10) == "info"
    assert classify_severity(25) == "warning"
    assert classify_severity(60) == "critical"
    assert classify_severity(-60) == "critical"


def test_alerts_preserve_evidence_and_analysis_only_mode():
    alerts = alerts_from_anomalies([Anomaly("2026-06", "EC2", 150, 100, 50)])
    assert len(alerts) == 1
    assert alerts[0].service == "EC2"
    assert alerts[0].current_cost == 150
    assert alerts[0].baseline_cost == 100
    assert alerts[0].change_pct == 50
    assert alerts[0].severity == "critical"
    assert alerts[0].mode == "analysis-only"
