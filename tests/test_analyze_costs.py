from pathlib import Path

import pandas as pd
import pytest

from scripts import analyze_costs as ac


def write_billing_csv(path: Path, rows: str) -> None:
    path.write_text(rows, encoding="utf-8")


def test_duplicate_usage_type_headers_are_disambiguated(tmp_path):
    path = tmp_path / "dec-costs.csv"
    write_billing_csv(
        path,
        "LineItem/UsageType,LineItem/UnblendedCost,LineItem/UsageType,Billing/Month\n"
        "EC2-Compute,12.345,BoxUsage:c6g.xlarge,\n"
        "RDS,3.005,DBInstance:db.t4g.small,\n",
    )
    df = ac.read_and_normalize_csv(path)
    assert "service_name" in df.columns
    assert "usage_type" in df.columns
    assert df["billing_month"].tolist() == ["December 2025", "December 2025"]
    assert df["cost"].tolist() == [12.345, 3.005]


def test_monthly_totals_retain_measured_values_and_reconcile(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    write_billing_csv(
        raw / "dec-costs.csv",
        "LineItem/UsageType,LineItem/UnblendedCost,LineItem/UsageType,Billing/Month\n"
        "EC2-Compute,500.00,BoxUsage:c6g.xlarge,\n"
        "RDS,313.43,DBInstance:db.t4g.small,\n",
    )
    files = ac.discover_csv_files(raw)
    measured = ac.aggregate_monthly_costs(files)
    checked = ac.verify_against_baseline(measured)
    assert checked.loc[0, "billing_month"] == "December 2025"
    assert checked.loc[0, "total_cost"] == 813.43
    assert checked.loc[0, "difference"] == 0.0
    assert bool(checked.loc[0, "baseline_match"]) is True


def test_category_aggregation_uses_observed_service_labels(tmp_path):
    path = tmp_path / "dec-costs.csv"
    write_billing_csv(
        path,
        "LineItem/UsageType,LineItem/UnblendedCost,LineItem/UsageType,Billing/Month\n"
        "EC2-Compute,100.00,BoxUsage:c6g.xlarge,\n"
        "EC2-Compute,20.00,BoxUsage:c6g.large,\n"
        "RDS,50.00,DBInstance:db.t4g.small,\n"
        "Tax,5.00,Tax,\n",
    )
    categories = ac.aggregate_by_category([path])
    observed = dict(zip(categories["category"], categories["cost"]))
    assert observed["EC2 Instances"] == 120.0
    assert observed["RDS"] == 50.0
    assert "Tax" not in observed


def test_discover_includes_september_and_sorts_months(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for name in ["Sep-costs.csv", "dec-costs.csv", "Jan-costs.csv"]:
        (raw / name).write_text(
            "LineItem/UsageType,LineItem/UnblendedCost\nEC2-Compute,1\n",
            encoding="utf-8",
        )
    assert [p.name for p in ac.discover_csv_files(raw)] == [
        "dec-costs.csv", "Jan-costs.csv", "Sep-costs.csv"
    ]


def test_missing_cost_column_fails_closed(tmp_path):
    path = tmp_path / "dec-costs.csv"
    write_billing_csv(path, "LineItem/UsageType\nEC2-Compute\n")
    with pytest.raises(ValueError, match="Missing cost column"):
        ac.read_and_normalize_csv(path)


def test_baseline_missing_for_september_is_not_marked_failed():
    frame = pd.DataFrame([{"billing_month": "September 2026", "total_cost": 12.34}])
    result = ac.verify_against_baseline(frame)
    assert pd.isna(result.loc[0, "baseline_match"])
    assert pd.isna(result.loc[0, "authoritative_cost"])
