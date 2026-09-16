# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, correlating spend with infrastructure and utilization evidence, and producing evidence-based optimization reviews.

> **Scope:** The platform is decision-support only. It does not automatically modify AWS resources. Production evidence must be sanitized before publication.

## Current Capabilities

- Historical AWS billing CSV analysis.
- AWS Cost Explorer service-level cost collection.
- EC2 resource-level cost attribution when Cost Explorer returns `RESOURCE_ID` data.
- EC2 inventory and CloudWatch CPU/network utilization intelligence.
- RDS inventory and CloudWatch CPU, connections, storage, and IOPS intelligence.
- Cost/utilization correlation with explicit missing-data handling.
- Anomaly detection and evidence-aware review signals.
- Read-only AWS guardrails and automated tests.
- Streamlit dashboard for interactive investigation.

## Architecture

```text
AWS Cost Explorer ───────┐
Historical CSV ──────────┤
EC2 / RDS Inventory ─────┤
CloudWatch Metrics ──────┘
            │
       Data Collection
            │
      Cost Analytics
       /    |     \
   Trends  Drivers  Anomalies
       \    |     /
       Evidence Correlation
            │
    Review Recommendations
            │
       Human Decision
            │
          Report
```

## RDS Intelligence

The RDS module combines `DescribeDBInstances` inventory with CloudWatch `GetMetricData` evidence for:

- `CPUUtilization`
- `DatabaseConnections`
- `FreeStorageSpace`
- `ReadIOPS`
- `WriteIOPS`

The dashboard keeps RDS Cost Explorer spend at service level. It does **not** divide aggregate RDS cost across DB instances without resource-level billing evidence.

## Safety Model

The AWS-connected implementation is read-only. It must not stop, terminate, reboot, resize, delete, create, or modify AWS resources. Missing CloudWatch data is represented as unavailable rather than zero.

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
│   ├── cloudwatch_ec2.py
│   ├── cloudwatch_rds.py
│   ├── ec2_intelligence.py
│   ├── ec2_utilization_intelligence.py
│   └── rds_intelligence.py
├── dashboard/
│   └── pages/
│       ├── 2_EC2_Cost_Intelligence.py
│       └── 3_RDS_Cost_Intelligence.py
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

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, secrets, private IPs, customer information, internal hostnames, or proprietary infrastructure code.
