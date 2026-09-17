from src.alert_monitoring import AlertMonitor
from src.alert_notifications import ConsoleNotifier, format_alert, webhook_payload
from src.alerting import CostAlert


def make_alert(reason="EC2 cost increased by 25.00% versus the previous period."):
    return CostAlert("2026-09", "EC2", "warning", 125.0, 100.0, 25.0, reason, "Review usage.")


def test_ingest_deduplicates_same_alert():
    monitor = AlertMonitor()
    assert len(monitor.ingest_cost_alerts([make_alert()])) == 1
    assert monitor.ingest_cost_alerts([make_alert()]) == []
    assert monitor.summary() == {"total": 1, "open": 1, "acknowledged": 0, "resolved": 0}


def test_alert_lifecycle():
    monitor = AlertMonitor()
    event = monitor.ingest_cost_alerts([make_alert()])[0]
    assert monitor.acknowledge(event.key).status == "acknowledged"
    assert monitor.resolve(event.key).status == "resolved"
    assert monitor.summary()["resolved"] == 1


def test_missing_event_key_is_safe():
    monitor = AlertMonitor()
    assert monitor.acknowledge("missing") is None
    assert monitor.resolve("missing") is None


def test_finding_ingestion_has_explicit_default_detail():
    event = AlertMonitor().ingest_findings([{"name": "EBS-001", "period": "2026-09"}])[0]
    assert event.detail == "Review finding evidence."


def test_notification_payload_is_serializable():
    event = AlertMonitor().ingest_cost_alerts([make_alert()])[0]
    assert "EC2 cost increased" in format_alert(event)
    assert "EC2" in webhook_payload(event)


def test_console_notifier_returns_messages(capsys):
    event = AlertMonitor().ingest_cost_alerts([make_alert()])[0]
    assert ConsoleNotifier().send([event]) == [format_alert(event)]
    assert "WARNING" in capsys.readouterr().out
