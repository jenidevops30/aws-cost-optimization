# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, generating evidence-based optimization recommendations, and validating savings.

> **Scope:** This branch evolves the repository into an AWS billing and cost-optimization platform. It does not include the Wishlist application. S3 and CloudFront are intentionally excluded from this platform scope unless later verified as required.

## Goals

- Import historical AWS billing CSV data.
- Normalize billing records into a consistent cost model.
- Calculate monthly and service-level cost trends.
- Detect unusual cost movements.
- Correlate billing findings with AWS resource metadata when available.
- Produce evidence-aware optimization recommendations.
- Track optimization actions and savings validation.
- Keep AWS integration strictly read-only.

## Current Evidence

The repository retains the historical billing case study used as project input. The platform must distinguish observed billing data from inferred causes and recommendations.

## Architecture

```text
AWS Billing / Cost Explorer     Historical CSV
            |                         |
            +-----------+-------------+
                        |
                  Data Ingestion
                        |
                    Normalize
                        |
                  Cost Analytics
                   /    |    \
                Trends Drivers Anomalies
                   \    |    /
                    Recommendations
                           |
                    Human Review
                           |
                    Savings Validation
                           |
                        Reports
```

## Safety Model

The AWS-connected implementation is read-only. It must not stop, terminate, resize, delete, create, or modify AWS resources.

## Repository Structure

```text
aws-cost-optimization/
├── README.md
├── PROJECT.md
├── IMPLEMENTATION.md
├── src/
│   └── cost_engine.py
├── cli.py
├── tests/
│   └── test_cost_engine.py
└── data/
    └── sample-billing.csv
```

## Quick Start

```bash
python cli.py data/sample-billing.csv
python -m unittest discover -s tests -v
```

## Three Documentation Files

- `README.md` — public project overview.
- `PROJECT.md` — complete FinOps case study, architecture, evidence, decisions, and outcomes.
- `IMPLEMENTATION.md` — hands-on implementation, data model, commands, testing, and future AWS read-only integration.

## Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, secrets, private IPs, customer information, internal hostnames, or proprietary infrastructure code.
