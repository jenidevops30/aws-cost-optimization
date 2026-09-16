from src.cost_engine import CostRecord
from src.intelligence import detect_anomalies, savings_opportunities


def records():
    return [
        CostRecord("2026-01", "EC2", "instance", "us-east-1", 100),
        CostRecord("2026-02", "EC2", "instance", "us-east-1", 150),
        CostRecord("2026-03", "EC2", "instance", "us-east-1", 100),
        CostRecord("2026-01", "RDS", "db", "us-east-1", 50),
        CostRecord("2026-02", "RDS", "db", "us-east-1", 55),
        CostRecord("2026-03", "RDS", "db", "us-east-1", 80),
    ]


def test_detect_anomalies_flags_large_monthly_change():
    result = detect_anomalies(records(), threshold_pct=30)
    assert any(item.service == "EC2" and item.period == "2026-02" for item in result)


def test_savings_opportunities_only_flags_latest_period_above_baseline():
    result = savings_opportunities(records())
    assert result[0].service == "RDS"
    assert result[0].potential_monthly_saving > 0
    assert result[0].confidence == "analysis-only"
