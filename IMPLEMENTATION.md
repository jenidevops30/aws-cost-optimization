# Implementation and Operations Guide

## Scope

This repository analyzes exported AWS billing CSV files and documents cost-optimization findings. The local analysis path does not need AWS credentials and does not call AWS APIs.

The optional script scripts/export_aws_evidence.py calls read-only AWS APIs using the AWS CLI profile named wc. It is not needed for local analysis or tests. Do not run it as part of the local-only validation workflow.

## Requirements

- Python 3.11 or 3.12
- pip
- Local billing CSV inputs under data/raw/

No pyproject.toml or uv lockfile is currently maintained, so use the pip requirements files rather than uv sync.

## Set up a local environment

~~~bash
git clone https://github.com/jenidevops30/aws-cost-optimization.git
cd aws-cost-optimization

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
~~~

## Run local validation

~~~bash
python -m pytest -q
python -m compileall -q scripts tests
~~~

## Run the analysis

~~~bash
python scripts/analyze_costs.py
~~~

The analysis reads recognized monthly CSV files from data/raw/ and writes generated outputs to:

- data/processed/monthly-cost-summary.csv
- data/processed/category-comparison.csv
- data/processed/optimization-candidates.csv
- analysis/analysis-output.json

The script keeps the measured CSV total separate from the reference invoice total. It reports the difference and match status; it must not overwrite a measured value to make it agree with the reference.

## Raw data rules

- Treat data/raw/ as immutable source input.
- Do not edit or reformat raw billing files to make totals reconcile.
- Investigate mismatches in the source export, included billing dimensions, rounding, and billing period before changing the analysis.
- The checked-in CSVs contain duplicate LineItem/UsageType headers and rows with incomplete trailing fields. The analysis currently handles these known shapes by distinguishing the duplicated service/category field and deriving the month from the filename. Corrected source exports should be preferred when available.
- September 2026 is marked estimated in the checked-in Cost Explorer export and is not treated as an authoritative invoice baseline.

## Evidence and privacy

Before publishing new evidence files:

1. Review the contents locally.
2. Remove credentials, access tokens, account identifiers, resource IDs, internal names, public IP addresses, and customer/company details that are not required for the case study.
3. Keep the original evidence private when it contains sensitive operational metadata.
4. Record the source, timestamp, billing period, and whether the value is estimated.
5. Update the evidence register only after the cited artifact is present and has been checked.

The evidence exporter currently writes resource identifiers and metadata to JSON files; do not assume its output is sanitized merely because the script description says so.

## AWS safety boundary

No AWS resource modification is part of this implementation workflow. Never add automatic stop, terminate, resize, delete, networking, database, or billing-configuration actions to the analysis script. Any future infrastructure change must be a separately reviewed, explicitly approved operation with a rollback plan.

## Current limitations

- The chart-generation script contains embedded values and is not yet driven by the generated analysis output.
- The monthly and category reports must be reconciled against the source evidence before the savings figures are presented as verified.
- The evidence register and case-study narrative need a claim-by-claim review against source artifacts.
