import pytest
from src.finops_unit_economics_quality import UnitEconomicsQualityEvidence, quality_flags, quality_rows

def test_quality_rows_preserve_source_and_cost_per_unit():
    row = quality_rows([UnitEconomicsQualityEvidence("2026-08","api","requests",120.0,1000,"telemetry")])[0]
    assert row["cost_per_unit"] == pytest.approx(0.12)
    assert row["source"] == "telemetry"
    assert row["evidence_status"] == "available"

def test_zero_volume_is_unavailable():
    record = UnitEconomicsQualityEvidence("2026-08","api","requests",120.0,0)
    assert quality_rows([record])[0]["evidence_status"] == "unavailable"
    assert "zero-volume-evidence" in quality_flags([record])

def test_available_volume_requires_source():
    with pytest.raises(ValueError):
        UnitEconomicsQualityEvidence("2026-08","api","requests",120.0,1000)

def test_empty_evidence_flag():
    assert quality_flags([]) == ["no-evidence"]

def test_negative_values_rejected():
    with pytest.raises(ValueError):
        UnitEconomicsQualityEvidence("2026-08","api","requests",-1.0,1,"telemetry")
