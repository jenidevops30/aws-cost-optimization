#!/usr/bin/env python3
"""
AWS Cost Optimization & FinOps Analysis Script

Analyzes monthly AWS billing CSV data to identify cost drivers,
calculate optimization opportunities, and generate evidence-based
reports.

Follows the INFORM → OPTIMIZE → OPERATE FinOps model.

WARNING: Never modifies raw input data. All processed datasets
are created in data/processed/.
"""

import os
import sys
import json
import glob
import pandas as pd
import numpy as np
from datetime import datetime


# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "analysis")

# Verified authoritative baseline totals (from AWS invoices)
AUTHORITATIVE_BASELINE = {
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

# Verified cost category data (December 2025 vs June 2026)
CATEGORY_DATA = {
    "EC2 Instances": {"December 2025": 244.96, "June 2026": 115.56},
    "RDS": {"December 2025": 205.05, "June 2026": 79.72},
    "ELB": {"December 2025": 116.88, "June 2026": 46.15},
    "VPC": {"December 2025": 46.42, "June 2026": 24.98},
    "EC2 Other": {"December 2025": 29.89, "June 2026": 9.30},
}


def discover_csv_files(raw_dir: str) -> list:
    """Discover monthly CSV files in the raw data directory.
    
    Expected filenames:
    - dec-costs.csv
    - Jan-costs.csv
    - Feb-costs.csv
    - Mar-costs.csv
    - Apr-costs.csv
    - May-costs.csv
    - Jun-costs.csv
    - July-costs.csv
    
    Returns list of found CSV file paths.
    """
    if not os.path.exists(raw_dir):
        print(f"Raw data directory not found: {raw_dir}")
        return []
    
    csv_patterns = [
        "dec-costs.csv",
        "Jan-costs.csv",
        "Feb-costs.csv",
        "Mar-costs.csv",
        "Apr-costs.csv",
        "May-costs.csv",
        "Jun-costs.csv",
        "Jul-costs.csv",
        "Aug-costs.csv",
    ]
    
    found_files = []
    for pattern in csv_patterns:
        filepath = os.path.join(raw_dir, pattern)
        if os.path.exists(filepath):
            found_files.append(filepath)
            print(f"Found: {pattern}")
        else:
            print(f"Not found: {pattern}")
    
    return sorted(found_files)


def normalize_column_name(col: str) -> str:
    """Normalize column names from AWS billing CSV format.
    
    Maps common AWS CSV column names to standardized names.
    Handles prefixed names like "LineItem/UnblendedCost" and "Billing/Month".
    """
    col_lower = col.strip().lower()
    
    # Common AWS billing column name mappings
    # Handles both plain names and prefixed names (LineItem/, Billing/)
    mapping = {
        "lineitem/unblendedcost": "cost",
        "lineitem/unblended_cost": "cost",
        "unblendedcost": "cost",
        "unblended_cost": "cost",
        "cost": "cost",
        "lineitem/usagetype": "usage_type",
        "lineitem/usage_type": "usage_type",
        "usagetype": "usage_type",
        "usage_type": "usage_type",
        "lineitem/instancetype": "instance_type",
        "lineitem/instance_type": "instance_type",
        "instancetype": "instance_type",
        "instance_type": "instance_type",
        "lineitem/availabilityzone": "availability_zone",
        "lineitem/availability_zone": "availability_zone",
        "availabilityzone": "availability_zone",
        "availability_zone": "availability_zone",
        "lineitem/operation": "operation",
        "lineitem/operation": "operation",
        "operation": "operation",
        "billingmonth": "billing_month",
        "billing_month": "billing_month",
        "billingmonth/": "billing_month",
        "billing/": "billing_month",
        "billingmonth/": "billing_month",
        "servicename": "service_name",
        "service_name": "service_name",
    }
    
    # Try exact match first, then try stripping prefixes
    if col_lower in mapping:
        return mapping[col_lower]
    
    # Try stripping "lineitem/" prefix
    if col_lower.startswith("lineitem/"):
        stripped = col_lower[len("lineitem/"):]
        if stripped in mapping:
            return mapping[stripped]
    
    # Try stripping "billing/" prefix
    if col_lower.startswith("billing/"):
        stripped = col_lower[len("billing/"):]
        if stripped in mapping:
            return mapping[stripped]
    
    return col_lower


def read_and_normalize_csv(filepath: str) -> pd.DataFrame:
    """Read a CSV file and normalize its column names."""
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return pd.DataFrame()
    
    # Normalize column names
    df.columns = [normalize_column_name(col) for col in df.columns]
    
    # Ensure cost column exists and is numeric
    if "cost" in df.columns:
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    else:
        print(f"Warning: No 'cost' column found in {filepath}")
        # Try to find a numeric column that could be cost
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            df["cost"] = df[numeric_cols[0]]
            print(f"  Using '{numeric_cols[0]}' as cost column")
    
    # Ensure billing_month column exists
    if "billing_month" not in df.columns:
        # Try to infer from filename
        basename = os.path.basename(filepath)
        month_map = {
            "dec": "December",
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "may": "May",
            "jun": "June",
            "jul": "July",
            "aug": "August",
        }
        for short, long in month_map.items():
            if short in basename.lower():
                df["billing_month"] = long
                break
        else:
            df["billing_month"] = "Unknown"
    
    return df


def aggregate_monthly_costs(csv_files: list) -> pd.DataFrame:
    """Aggregate costs by month from all CSV files."""
    all_data = []
    
    for filepath in csv_files:
        df = read_and_normalize_csv(filepath)
        if df.empty:
            continue
        
        # Group by billing_month and sum costs
        if "billing_month" in df.columns and "cost" in df.columns:
            monthly_summary = (
                df.groupby("billing_month")["cost"]
                .sum()
                .reset_index()
                .rename(columns={"cost": "total_cost"})
            )
            all_data.append(monthly_summary)
    
    if not all_data:
        return pd.DataFrame()
    
    # Combine all monthly summaries using concat (not merge)
    result = pd.concat(all_data, ignore_index=True)
    
    # Group by billing_month again in case there are duplicates
    result = result.groupby("billing_month")["total_cost"].sum().reset_index()
    
    # Fill NaN costs with 0
    result["total_cost"] = result["total_cost"].fillna(0)
    
    # Sort by month order
    month_order = [
        "December", "January", "February", "March",
        "April", "May", "June", "July", "August"
    ]
    result["sort_key"] = result["billing_month"].map(
        {month: i for i, month in enumerate(month_order)}
    )
    result = result.sort_values("sort_key").drop(columns=["sort_key"])
    
    return result


def aggregate_by_category(csv_files: list, categories: dict) -> pd.DataFrame:
    """Aggregate costs by category from CSV files.
    
    Categories dict format:
    {
        "EC2 Instances": ["pattern1", "pattern2"],
        "RDS": ["pattern3"],
        ...
    }
    """
    all_data = []
    
    for filepath in csv_files:
        df = read_and_normalize_csv(filepath)
        if df.empty:
            continue
        
        if "cost" not in df.columns or "usage_type" not in df.columns:
            continue
        
        # Filter by category patterns
        category_results = {}
        for category, patterns in categories.items():
            # Check if any usage_type matches the category patterns
            for _, row in df.iterrows():
                usage_type = str(row.get("usage_type", ""))
                cost = row.get("cost", 0)
                
                matched = False
                for pattern in patterns:
                    if pattern.lower() in usage_type.lower():
                        matched = True
                        break
                
                if matched:
                    if category not in category_results:
                        category_results[category] = 0
                    category_results[category] += cost
        
        if category_results:
            # Add billing month
            basename = os.path.basename(filepath)
            month_name = "Unknown"
            month_map = {
                "dec": "December", "jan": "January", "feb": "February",
                "mar": "March", "apr": "April", "may": "May",
                "jun": "June", "jul": "July", "aug": "August"
            }
            for short, long in month_map.items():
                if short in basename.lower():
                    month_name = long
                    break
            
            row = {"billing_month": month_name}
            row.update(category_results)
            all_data.append(row)
    
    if not all_data:
        return pd.DataFrame()
    
    result = pd.DataFrame(all_data)
    return result


def calculate_changes(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Calculate absolute and percentage changes between first and last month."""
    if df.empty or col_name not in df.columns:
        return df
    
    # Sort by month to ensure correct order
    month_order = [
        "December", "January", "February", "March",
        "April", "May", "June", "July", "August"
    ]
    df = df.copy()
    df["sort_key"] = df["billing_month"].map(
        {month: i for i, month in enumerate(month_order)}
    )
    df = df.sort_values("sort_key").drop(columns=["sort_key"])
    
    if len(df) < 2:
        df["absolute_change"] = 0
        df["percentage_change"] = 0
        return df
    
    # Get first and last month values
    first_month_row = df.iloc[0]
    last_month_row = df.iloc[-1]
    
    first_value = first_month_row[col_name]
    last_value = last_month_row[col_name]
    
    df["absolute_change"] = last_value - first_value
    
    if first_value != 0:
        df["percentage_change"] = ((last_value - first_value) / first_value) * 100
    else:
        df["percentage_change"] = 0 if last_value == 0 else float("inf")
    
    return df


def verify_against_baseline(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Verify derived monthly totals against authoritative baseline."""
    if monthly_df.empty or "billing_month" not in monthly_df.columns:
        return monthly_df
    
    verification_results = []
    for _, row in monthly_df.iterrows():
        month = row["billing_month"]
        derived_cost = row.get("total_cost", 0)
        
        if month in AUTHORITATIVE_BASELINE:
            authoritative = AUTHORITATIVE_BASELINE[month]
            difference = derived_cost - authoritative
            variance_percent = (difference / authoritative) * 100 if authoritative != 0 else 0
            
            verification_results.append({
                "month": month,
                "derived_cost": derived_cost,
                "authoritative_cost": authoritative,
                "difference": difference,
                "variance_percent": variance_percent,
                "baseline_match": abs(difference) < 0.01,  # Within 1 cent
            })
        else:
            verification_results.append({
                "month": month,
                "derived_cost": derived_cost,
                "authoritative_cost": "N/A",
                "difference": "N/A",
                "variance_percent": "N/A",
                "baseline_match": False,
            })
    
    verification_df = pd.DataFrame(verification_results)
    return pd.concat([monthly_df, verification_df], axis=1)


def generate_processed_csvs(monthly_df: pd.DataFrame, category_df: pd.DataFrame) -> None:
    """Generate processed CSV files in data/processed/."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    # Monthly cost summary
    if not monthly_df.empty:
        monthly_path = os.path.join(PROCESSED_DATA_DIR, "monthly-cost-summary.csv")
        monthly_df.to_csv(monthly_path, index=False)
        print(f"Generated: {monthly_path}")
    
    # Category comparison
    if not category_df.empty:
        category_path = os.path.join(PROCESSED_DATA_DIR, "category-comparison.csv")
        category_df.to_csv(category_path, index=False)
        print(f"Generated: {category_path}")
    
    # Optimization candidates
    opt_path = os.path.join(PROCESSED_DATA_DIR, "optimization-candidates.csv")
    # Generate optimization candidates based on category data
    opt_data = []
    for category, data in CATEGORY_DATA.items():
        dec_val = data["December 2025"]
        jun_val = data["June 2026"]
        abs_change = jun_val - dec_val
        pct_change = (abs_change / dec_val) * 100 if dec_val != 0 else 0
        opt_data.append({
            "category": category,
            "dec_2025": dec_val,
            "jun_2026": jun_val,
            "absolute_change": abs_change,
            "percentage_change": pct_change,
        })
    
    opt_df = pd.DataFrame(opt_data)
    opt_df.to_csv(opt_path, index=False)
    print(f"Generated: {opt_path}")


def generate_json_output(monthly_df: pd.DataFrame, category_df: pd.DataFrame) -> dict:
    """Generate machine-readable JSON output."""
    output = {
        "project": "AWS Cost Optimization & FinOps",
        "generated": datetime.now().isoformat(),
        "monthly_summary": {},
        "category_analysis": {},
    }
    
    # Monthly summary
    if not monthly_df.empty:
        for _, row in monthly_df.iterrows():
            month = row["billing_month"]
            output["monthly_summary"][month] = {
                "cost": row.get("total_cost", 0),
                "absolute_change": row.get("absolute_change", 0),
                "percentage_change": row.get("percentage_change", 0),
            }
    
    # Category analysis
    if not category_df.empty:
        for category in CATEGORY_DATA.keys():
            if category in category_df.columns:
                cat_data = category_df[category]
                # Get December and June values
                dec_val = cat_data[cat_data["billing_month"] == "December 2025"]
                jun_val = cat_data[cat_data["billing_month"] == "June 2026"]
                
                if not dec_val.empty and not jun_val.empty:
                    dec_cost = dec_val.iloc[0].get(category, 0)
                    jun_cost = jun_val.iloc[0].get(category, 0)
                    abs_change = jun_cost - dec_cost
                    pct_change = (abs_change / dec_cost) * 100 if dec_cost != 0 else 0
                    
                    output["category_analysis"][category] = {
                        "december_2025": dec_cost,
                        "june_2026": jun_cost,
                        "absolute_change": abs_change,
                        "percentage_change": pct_change,
                    }
    
    return output


def main():
    """Main analysis entry point."""
    print("=" * 60)
    print("AWS Cost Optimization & FinOps Analysis")
    print("=" * 60)
    
    # Step 1: Discover CSV files
    print("\n[1/7] Discovering CSV files...")
    csv_files = discover_csv_files(RAW_DATA_DIR)
    
    if not csv_files:
        print("No CSV files found. Creating sample data structure...")
        # Create empty data structure for demonstration
        csv_files = []
    
    # Step 2: Aggregate monthly costs
    print("\n[2/7] Aggregating monthly costs...")
    monthly_df = aggregate_monthly_costs(csv_files)
    
    # Step 3: Verify against baseline
    print("\n[3/7] Verifying against authoritative baseline...")
    monthly_df = verify_against_baseline(monthly_df)
    
    # Step 4: Aggregate by category
    print("\n[4/7] Aggregating costs by category...")
    category_df = aggregate_by_category(csv_files, CATEGORY_DATA)
    
    # Step 5: Calculate changes
    print("\n[5/7] Calculating cost changes...")
    category_df = calculate_changes(category_df, "cost") if not category_df.empty else category_df
    
    # Step 6: Generate processed CSV files
    print("\n[6/7] Generating processed CSV files...")
    generate_processed_csvs(monthly_df, category_df)
    
    # Step 7: Generate JSON output
    print("\n[7/7] Generating JSON output...")
    json_output = generate_json_output(monthly_df, category_df)
    json_path = os.path.join(PROJECT_ROOT, "analysis", "analysis-output.json")
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2)
    print(f"Generated: {json_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    if not monthly_df.empty:
        print("\nMonthly Costs:")
        for _, row in monthly_df.iterrows():
            month = row["billing_month"]
            cost = row.get("total_cost", 0)
            auth_cost = AUTHORITATIVE_BASELINE.get(month)
            if auth_cost is not None:
                match = "✓" if abs(cost - auth_cost) < 0.01 else " "
                print(f"  {month}: ${cost:.2f} (baseline: ${auth_cost:.2f}) {match}")
            else:
                print(f"  {month}: ${cost:.2f} (baseline: N/A)")
    
    if not category_df.empty:
        print("\nCategory Changes (Dec 2025 → Jun 2026):")
        for category in CATEGORY_DATA.keys():
            cat_data = category_df[category_df["billing_month"].isin(["December 2025", "June 2026"])]
            if len(cat_data) >= 2:
                dec_row = cat_data[cat_data["billing_month"] == "December 2025"]
                jun_row = cat_data[cat_data["billing_month"] == "June 2026"]
                if not dec_row.empty and not jun_row.empty:
                    dec_cost = dec_row.iloc[0].get(category, 0)
                    jun_cost = jun_row.iloc[0].get(category, 0)
                    abs_change = jun_cost - dec_cost
                    pct_change = (abs_change / dec_cost) * 100 if dec_cost != 0 else 0
                    print(f"  {category}: ${dec_cost:.2f} → ${jun_cost:.2f} "
                          f"({abs_change:+.2f}, {pct_change:+.1f}%)")
    
    print("\nOutput files generated in data/processed/ and analysis/")


if __name__ == "__main__":
    main()