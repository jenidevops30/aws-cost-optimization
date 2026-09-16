# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, correlating spend with infrastructure and utilization evidence, and producing evidence-based optimization reviews and exportable reports.

> **Scope:** The platform is decision-support only. It does not automatically modify AWS resources. Production evidence must be sanitized before publication.

## Current Capabilities

- Historical AWS billing CSV analysis.
- AWS Cost Explorer service-level cost collection.
- EC2 resource-level cost attribution when Cost Explorer returns `RESOURCE_ID` data.
- EC2 inventory and CloudWatch CPU/network utilization intelligence.
- RDS inventory and CloudWatch CPU, connections, storage, and IOPS intelligence.
- EBS inventory and CloudWatch I/O evidence for volume-level investigation.
- ALB inventory and CloudWatch traffic/data-transfer evidence.
- AWS Cost Anomaly Detection findings with root-cause evidence.
- Cost/utilization correlation with explicit missing-data handling.
- Anomaly detection and evidence-aware review signals.
- FinOps executive reporting and baseline-vs-post-optimization validation.
- JSON, CSV, and Markdown report exports.
- Read-only AWS guardrails and automated tests.
- Bounded standard AWS SDK retries and classified API failure states.
- Streamlit dashboard for interactive investigation and reporting.

## Architecture

```text
AWS Cost Explorer ───────┐
Historical CSV ──────────┤
EC2 / RDS / EBS / ALB ───┤
CloudWatch Metrics ──────┤
Cost Anomaly Detection ──┘
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
   Validate → Export Report
```

## Cost Anomaly Detection

The platform can read AWS Cost Anomaly Detection findings through the Cost Explorer API. Findings include AWS-reported anomaly identifiers, time windows, estimated impact, actual spend, and available root-cause dimensions such as service, region, and usage type.

The collector consumes API pagination and uses the shared AWS reliability layer. Anomaly impact is presented as AWS-reported evidence, not as a fabricated savings estimate. A finding is an investigation signal; it does not by itself establish causality or authorize an infrastructure change.

## FinOps Reporting & Validation

The reporting milestone turns the analysis model into an auditable output workflow:

- Executive summary of analyzed spend and findings.
- Monthly spend and service totals.
- Evidence-aware anomaly findings.
- Baseline versus post-optimization period comparison.
- Observed cost delta and percentage change when both periods are available.
- JSON export for machine-readable workflows.
- CSV export for monthly cost analysis.
- Markdown export for engineering or portfolio documentation.

A lower post-optimization cost is reported as an **observed reduction**, not as proof that a particular engineering change caused it. Attribution requires supporting operational evidence.

## ALB & Data Transfer Intelligence

The ALB module combines ELBv2 `DescribeLoadBalancers` inventory with CloudWatch `GetMetricData` evidence for `RequestCount`, `ProcessedBytes`, `ActiveConnectionCount`, `NewConnectionCount`, and `TargetResponseTime`. Sum metrics are aggregated as totals, Average metrics as arithmetic means, and CloudWatch pagination is consumed until complete.

## Production Hardening & Reliability

The production-hardening work separates metric semantics and consumes CloudWatch pagination. The AWS API reliability layer configures bounded standard SDK retries, connection/read timeouts, stable failure classification, and dashboard-safe error messages. Missing evidence remains distinct from failed AWS calls.

## Safety Model

The AWS-connected implementation is read-only. It must not stop, terminate, reboot, resize, delete, create, or modify AWS resources. No application-level unbounded retry loop or automatic optimization action is introduced.

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
│   ├── cost_anomaly.py
│   ├── cloudwatch_ec2.py
│   ├── cloudwatch_rds.py
│   ├── cloudwatch_ebs.py
│   ├── cloudwatch_alb.py
│   └── finops_exports.py
├── dashboard/
│   └── pages/
│       ├── 2_EC2_Cost_Intelligence.py
│       ├── 3_RDS_Cost_Intelligence.py
│       ├── 4_EBS_Cost_Intelligence.py
│       ├── 5_ALB_Data_Transfer_Intelligence.py
│       ├── 6_FinOps_Reports_Validation.py
│       └── 7_Cost_Anomaly_Detection.py
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
