# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, correlating spend with infrastructure and utilization evidence, producing evidence-based optimization reviews, governance signals, and exportable reports.

> **Scope:** Decision-support only. It does not automatically modify AWS resources. Production evidence must be sanitized before publication.

## Current Capabilities

- Historical AWS billing CSV analysis.
- AWS Cost Explorer service-level cost collection.
- EC2 resource-level cost attribution when Cost Explorer returns `RESOURCE_ID` data.
- EC2 inventory and CloudWatch CPU/network utilization intelligence.
- RDS inventory and CloudWatch CPU, connections, storage, and IOPS intelligence.
- EBS inventory and CloudWatch I/O evidence.
- ALB inventory and CloudWatch traffic/data-transfer evidence.
- AWS Cost Anomaly Detection findings and root-cause evidence.
- AWS Budgets read-only governance intelligence.
- Cost/utilization correlation with explicit missing-data handling.
- FinOps executive reporting and baseline-vs-post-optimization validation.
- JSON, CSV, and Markdown report exports.
- Bounded AWS SDK retries and classified API failures.
- **FinOps Executive Governance snapshot combining spend, budgets, anomalies, forecast, findings, validation, and evidence status.**
- Streamlit dashboard for interactive investigation and reporting.

## Architecture

```text
AWS Billing / Cost Explorer / CSV
        │
        ├── Anomaly Detection
        ├── AWS Budgets
        ├── EC2 / RDS / EBS / ALB
        └── CloudWatch Evidence
                 │
          Cost + Evidence Analytics
                 │
        Review / Governance Signals
                 │
        Executive Governance Snapshot
                 │
            Human Decision
                 │
        Validate → Report → Export
```

## FinOps Executive Governance

Milestone #15 adds a deterministic governance layer above the existing collectors. It combines already-available evidence into a single executive snapshot containing latest spend, month-over-month change, forecast evidence, budget statuses, anomaly count/impact, finding count, validation status, and an explicit evidence state.

The governance layer does not invent missing data, divide service-level spend across resources without billing evidence, claim causality, or perform remediation. It is analysis-only.

## Reporting & Validation

The reporting workflow provides executive summaries, monthly/service totals, anomaly findings, baseline/post-optimization comparison, and JSON/CSV/Markdown exports. A lower post-optimization period is reported as an observed reduction, not proof of causality.

## Safety Model

The AWS-connected implementation is read-only. It must not stop, terminate, reboot, resize, delete, create, or modify AWS resources. No automatic optimization action is introduced.

## Repository Structure

```text
aws-cost-optimization/
├── README.md
├── PROJECT.md
├── IMPLEMENTATION.md
├── src/
│   ├── cost_engine.py
│   ├── aws_cost_explorer.py
│   ├── aws_readonly.py
│   ├── aws_resilience.py
│   ├── aws_budgets.py
│   ├── cost_anomaly.py
│   ├── cloudwatch_ec2.py
│   ├── cloudwatch_rds.py
│   ├── cloudwatch_ebs.py
│   ├── cloudwatch_alb.py
│   ├── finops_exports.py
│   └── finops_governance.py
├── dashboard/
│   └── pages/
│       ├── 2_EC2_Cost_Intelligence.py
│       ├── 3_RDS_Cost_Intelligence.py
│       ├── 4_EBS_Cost_Intelligence.py
│       ├── 5_ALB_Data_Transfer_Intelligence.py
│       ├── 6_FinOps_Reports_Validation.py
│       ├── 7_Cost_Anomaly_Detection.py
│       ├── 8_Budget_Governance.py
│       └── 9_FinOps_Executive_Governance.py
├── tests/
└── data/
    └── sample-billing.csv
```

## Quick Start

```bash
python cli.py data/sample-billing.csv
python -m pytest -q
streamlit run dashboard/app.py
```

## Three Documentation Files

- `README.md` — public project overview.
- `PROJECT.md` — complete FinOps case study, architecture, evidence, decisions, and outcomes.
- `IMPLEMENTATION.md` — hands-on implementation, data model, commands, testing, and troubleshooting.

## Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, private IPs, customer information, internal hostnames, or proprietary infrastructure code.
