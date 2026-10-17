#!/usr/bin/env python3
"""Analyze local AWS billing CSV exports without making AWS API calls.

Raw files under data/raw are read-only inputs. Derived reports are written
under data/processed and analysis. Authoritative invoice totals are used only
for comparison; they never replace measured CSV totals.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"

# Rounded invoice totals recorded in project evidence. September is omitted:
# the repository's Cost Explorer export marks it Estimated=true, and its raw CSV
# currently does not reconcile to that estimate.
AUTHORITATIVE_BASELINE: dict[str, float] = {
    "December 2025": 813.43,
    "January 2026": 762.62,
    "February 2026": 500.50,
    "March 2026": 481.71,
    "April 2026": 467.80,
    "May 2026": 372.32,
    "June 2026": 327.07,
    "July 2026": 327.73,
    "August 2026": 357.36,
}

MONTHS = {
    "jan": "January", "feb": "February", "mar": "March",
    "apr": "April", "may": "May", "jun": "June",
    "jul": "July", "aug": "August", "sep": "September",
    "oct": "October", "nov": "November", "dec": "December",
}
CATEGORY_ALIASES = {
    "ec2-compute": "EC2 Instances",
    "ec2 instances": "EC2 Instances",
    "ec2": "EC2 Instances",
    "rds": "RDS",
    "elb": "ELB",
    "elastic load balancing": "ELB",
    "vpc": "VPC",
    "ec2-other": "EC2 Other",
    "ec2 other": "EC2 Other",
}


def month_from_filename(path: Path) -> str:
    """Return a canonical month label from a monthly filename."""
    match = re.search(r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", path.stem)
    if not match:
        raise ValueError(f"Cannot determine billing month from filename: {path.name}")
    month = MONTHS[match.group(1).lower()]
    year_match = re.search(r"(?:19|20)\d{2}", path.stem)
    year = int(year_match.group(0)) if year_match else (2025 if month == "December" else 2026)
    return f"{month} {year}"


def discover_csv_files(raw_dir: Path = RAW_DATA_DIR) -> list[Path]:
    """Discover supported monthly CSV files; ignore non-monthly CSVs."""
    if not raw_dir.is_dir():
        return []
    found: list[Path] = []
    for path in raw_dir.glob("*.csv"):
        try:
            month_from_filename(path)
        except ValueError:
            continue
        found.append(path)
    return sorted(found, key=lambda p: datetime.strptime(month_from_filename(p), "%B %Y"))


def _normalized_header(header: object) -> str:
    name = str(header).strip().lower()
    # pandas suffixes duplicate CSV headers with .1, .2, etc.
    name = re.sub(r"\.\d+$", "", name)
    compact = name.replace(" ", "")
    mappings = {
        "lineitem/unblendedcost": "cost",
        "lineitem/unblended_cost": "cost",
        "unblendedcost": "cost",
        "unblended_cost": "cost",
        "cost": "cost",
        "lineitem/usagetype": "usage_type",
        "usagetype": "usage_type",
        "usage_type": "usage_type",
        "billing/month": "billing_month",
        "billingmonth": "billing_month",
        "billing_month": "billing_month",
        "usagetype/description": "usage_description",
        "usage/availabilityzone": "availability_zone",
        "usage/instancetype": "instance_type",
        "lineitem/instancetype": "instance_type",
        "usage/operation": "operation",
        "lineitem/operation": "operation",
        "servicename": "service_name",
        "service_name": "service_name",
    }
    return mappings.get(compact, name.replace("/", "_"))


def read_and_normalize_csv(filepath: Path) -> pd.DataFrame:
    """Read a monthly CSV and normalize columns without guessing cost fields.

    The checked-in CSVs contain a duplicate LineItem/UsageType header. In those
    files the first column contains service/category labels and the second
    occurrence contains usage-type detail; preserve that distinction.
    """
    filepath = Path(filepath)
    df = pd.read_csv(filepath)
    canonical = [_normalized_header(col) for col in df.columns]

    if canonical.count("usage_type") > 1:
        first = canonical.index("usage_type")
        canonical[first] = "service_name"

    counts: dict[str, int] = {}
    unique_columns: list[str] = []
    for name in canonical:
        count = counts.get(name, 0)
        counts[name] = count + 1
        unique_columns.append(name if count == 0 else f"{name}_{count + 1}")
    df.columns = unique_columns

    if "cost" not in df.columns:
        raise ValueError(f"Missing cost column in {filepath}")
    original_cost = df["cost"].copy()
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    invalid = original_cost.notna() & df["cost"].isna()
    if invalid.any():
        rows = (invalid[invalid].index + 2).tolist()
        raise ValueError(f"Non-numeric cost values in {filepath} at CSV rows {rows}")
    if df["cost"].isna().any():
        raise ValueError(f"Blank cost values in {filepath}; refusing to silently omit costs")

    # The filename is the reliable month source for the checked-in data: some
    # raw rows have a shifted/missing Billing/Month value due to malformed rows.
    df["billing_month"] = month_from_filename(filepath)
    return df


def aggregate_monthly_costs(csv_files: Iterable[Path]) -> pd.DataFrame:
    """Sum raw line-item costs by month, retaining measured totals."""
    rows: list[dict[str, object]] = []
    for filepath in csv_files:
        df = read_and_normalize_csv(Path(filepath))
        rows.append({
            "billing_month": month_from_filename(Path(filepath)),
            "total_cost": round(float(df["cost"].sum()), 2),
        })
    if not rows:
        return pd.DataFrame(columns=["billing_month", "total_cost"])
    return pd.DataFrame(rows).sort_values(
        "billing_month", key=lambda s: s.map(lambda v: datetime.strptime(v, "%B %Y"))
    ).reset_index(drop=True)


def verify_against_baseline(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Add reconciliation fields without overwriting measured CSV totals."""
    result = monthly_df.copy()
    authoritative: list[float | None] = []
    differences: list[float | None] = []
    variances: list[float | None] = []
    matches: list[bool | None] = []
    for _, row in result.iterrows():
        month = str(row["billing_month"])
        expected = AUTHORITATIVE_BASELINE.get(month)
        if expected is None:
            authoritative.append(None)
            differences.append(None)
            variances.append(None)
            matches.append(None)
            continue
        measured = float(row["total_cost"])
        difference = round(measured - expected, 2)
        authoritative.append(expected)
        differences.append(difference)
        variances.append(round((difference / expected) * 100, 2) if expected else None)
        matches.append(abs(difference) <= 0.01)
    result["authoritative_cost"] = authoritative
    result["difference"] = differences
    result["variance_percent"] = variances
    result["baseline_match"] = matches
    return result


def aggregate_by_category(csv_files: Iterable[Path]) -> pd.DataFrame:
    """Aggregate supported service categories from actual CSV line items."""
    rows: list[dict[str, object]] = []
    for filepath in csv_files:
        df = read_and_normalize_csv(Path(filepath))
        source_column = "service_name" if "service_name" in df.columns else "usage_type"
        if source_column not in df.columns:
            continue
        for label, group in df.groupby(source_column, dropna=False):
            category = CATEGORY_ALIASES.get(str(label).strip().lower())
            if category:
                rows.append({
                    "billing_month": month_from_filename(Path(filepath)),
                    "category": category,
                    "cost": round(float(group["cost"].sum()), 2),
                })
    if not rows:
        return pd.DataFrame(columns=["billing_month", "category", "cost"])
    result = pd.DataFrame(rows).groupby(
        ["billing_month", "category"], as_index=False
    )["cost"].sum()
    return result.sort_values(["billing_month", "category"]).reset_index(drop=True)


def build_category_comparison(category_df: pd.DataFrame) -> pd.DataFrame:
    """Compare observed December 2025 and June 2026 category totals."""
    columns = ["category", "dec_2025", "jun_2026", "absolute_change", "percentage_change"]
    if category_df.empty:
        return pd.DataFrame(columns=columns)
    pivot = category_df.pivot_table(index="category", columns="billing_month", values="cost", aggfunc="sum")
    rows: list[dict[str, object]] = []
    for category in pivot.index:
        dec = pivot.loc[category].get("December 2025")
        jun = pivot.loc[category].get("June 2026")
        if pd.isna(dec) or pd.isna(jun):
            continue
        change = round(float(jun) - float(dec), 2)
        rows.append({
            "category": category,
            "dec_2025": round(float(dec), 2),
            "jun_2026": round(float(jun), 2),
            "absolute_change": change,
            "percentage_change": round(change / float(dec) * 100, 2) if float(dec) else None,
        })
    return pd.DataFrame(rows, columns=columns)


def generate_reports(monthly_df: pd.DataFrame, category_df: pd.DataFrame) -> dict:
    """Write local CSV/JSON reports and return the JSON payload."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    monthly_df.to_csv(PROCESSED_DATA_DIR / "monthly-cost-summary.csv", index=False)
    category_df.to_csv(PROCESSED_DATA_DIR / "category-comparison.csv", index=False)
    comparison = build_category_comparison(category_df)
    comparison.to_csv(PROCESSED_DATA_DIR / "optimization-candidates.csv", index=False)

    payload = {
        "project": "AWS Cost Optimization & FinOps",
        "generated": datetime.now(timezone.utc).isoformat(),
        "monthly_summary": {
            str(row.billing_month): {
                "cost": float(row.total_cost),
                "authoritative_cost": None if pd.isna(row.authoritative_cost) else float(row.authoritative_cost),
                "difference": None if pd.isna(row.difference) else float(row.difference),
                "variance_percent": None if pd.isna(row.variance_percent) else float(row.variance_percent),
                "baseline_match": None if pd.isna(row.baseline_match) else bool(row.baseline_match),
            }
            for row in monthly_df.itertuples(index=False)
        },
        "category_analysis": comparison.to_dict(orient="records"),
    }
    (ANALYSIS_DIR / "analysis-output.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    csv_files = discover_csv_files()
    if not csv_files:
        raise SystemExit(f"No monthly billing CSV files found in {RAW_DATA_DIR}")
    monthly = verify_against_baseline(aggregate_monthly_costs(csv_files))
    categories = aggregate_by_category(csv_files)
    generate_reports(monthly, categories)
    mismatches = monthly[monthly["baseline_match"] == False]  # noqa: E712
    print(f"Processed {len(csv_files)} monthly CSV files locally; no AWS API calls made.")
    print(monthly.to_string(index=False))
    if not mismatches.empty:
        print(f"WARNING: {len(mismatches)} month(s) do not reconcile to the recorded baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
