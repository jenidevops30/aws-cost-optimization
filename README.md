# AWS Cost Optimization & FinOps

A local-first Python toolkit and case study for reviewing AWS billing exports, comparing service-level spend, and documenting FinOps opportunities. The analysis workflow reads CSV files and writes reports locally; it does not create, change, stop, resize, or delete AWS resources.

> **Evidence status:** This repository documents a reported reduction from $813.43/month (December 2025) to $327.07/month (June 2026). Treat that as a reported case-study result until the raw exports, generated summaries, and evidence register reconcile. The analysis script reports discrepancies rather than replacing measured CSV totals with reference values.

## What it does

- Discovers monthly billing CSV files under data/raw/.
- Normalizes the billing columns used by this repository, including duplicate LineItem/UsageType headers.
- Calculates monthly totals and compares them with the recorded invoice baseline where one exists.
- Aggregates the supported categories EC2 Instances, RDS, ELB, VPC, and EC2 Other from observed line items.
- Writes deterministic CSV and JSON outputs under data/processed/ and analysis/.
- CI regenerates reports and fails if committed outputs are stale.
- Keeps AWS evidence collection separate from local CSV analysis.

## Repository layout

- scripts/analyze_costs.py — local CSV analysis; no AWS API calls.
- scripts/generate_charts.py — chart-generation script. Its current chart values are embedded in the script; reconcile them with the generated analysis outputs before publishing updated charts.
- scripts/export_aws_evidence.py — optional AWS CLI evidence exporter. It calls read-only AWS APIs using the configured wc profile and writes evidence files. Do not run it for the local-only workflow; review and sanitize exported identifiers before committing any output.
- data/raw/ — input billing CSVs. Treat these as immutable inputs.
- data/processed/ — generated monthly and category summaries.
- analysis/ — generated machine-readable analysis and committed chart images.
- evidence/ — supporting billing/resource evidence and case-study notes.
- PROJECT.md — project goals and current case-study narrative.
- IMPLEMENTATION.md — local setup, data handling, and safety notes.

## Requirements

- Python 3.11 or 3.12
- pip
- No AWS credentials are required for the local analysis or unit tests

## Local setup and usage

~~~bash
git clone https://github.com/jenidevops30/aws-cost-optimization.git
cd aws-cost-optimization

python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
~~~

Run the tests:

~~~bash
python -m pytest -q
python -m compileall -q scripts tests
~~~

Run the local billing analysis:

~~~bash
python scripts/analyze_costs.py
~~~

The script reads supported monthly CSV files and writes:

- data/processed/monthly-cost-summary.csv
- data/processed/category-comparison.csv
- data/processed/optimization-candidates.csv
- analysis/analysis-output.json

The JSON report intentionally omits wall-clock generation metadata so identical inputs produce identical output. CI regenerates reports and checks that committed artifacts match the source data. It prints a warning when derived totals do not reconcile to the recorded baseline. A month without a non-estimated authoritative baseline is reported as not comparable, not as a failed match.

## Current baseline reported by the case study

| Month | Reported total (USD) |
|---|---:|
| December 2025 | $813.43 |
| January 2026 | $762.62 |
| February 2026 | $500.50 |
| March 2026 | $481.71 |
| April 2026 | $467.80 |
| May 2026 | $372.32 |
| June 2026 | $327.07 |
| July 2026 | $327.73 |
| August 2026 | $357.36 |

These figures are reference values for reconciliation, not substitutes for calculated CSV totals. The Cost Explorer evidence marks September 2026 as estimated; it is intentionally excluded from the authoritative baseline until final billing data is available.

## Case study and engineering records

- [AWS Cost Optimization Case Study](docs/case-study.md) — reported baseline-to-comparison result, methodology, validation checklist, and limitations.
- [Cost Optimization Decision Records](docs/decisions/README.md) — decision record guidance and template.
- [Evidence Register](evidence/README.md) — claim status, source traceability, and publication safety checklist.

## Architecture and evidence

- [Architecture case study](architecture/README.md)
- [Baseline evidence and reconciliation notes](evidence/baseline/README.md)
- [EC2 evidence](evidence/ec2/README.md)
- [RDS evidence](evidence/rds/README.md)
- [Networking evidence](evidence/networking/README.md)
- [Results and sign-off notes](evidence/results/README.md)

The architecture and results documents contain claims about resource migrations, performance, and operating controls. Validate each claim against its cited source before using it as a verified production outcome.

## Safety and data handling

- The local analysis script does not call AWS APIs.
- The evidence exporter is separate and read-only, but may write resource identifiers and metadata to local files.
- Never commit credentials, access tokens, private keys, customer data, or unnecessary account/resource identifiers.
- Do not change raw billing inputs to force a match. Investigate and document discrepancies.
- No automated remediation is implemented by this analysis workflow.
