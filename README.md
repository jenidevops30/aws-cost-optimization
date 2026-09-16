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
- Cost/utilization correlation with explicit missing-data handling.
- Anomaly detection and evidence-aware review signals.
- FinOps executive reporting and baseline-vs-post-optimization validation.
- JSON, CSV, and Markdown report exports.
- Read-only AWS guardrails and automated tests.
- Streamlit dashboard for interactive investigation and reporting.

## Architecture

```text
AWS Cost Explorer ───────┐
Historical CSV ──────────┤
EC2 / RDS / EBS / ALB ───┤
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
   Validate → Export Report
```

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

The ALB module combines ELBv2 `DescribeLoadBalancers` inventory with CloudWatch `GetMetricData` evidence for:

- `RequestCount`
- `ProcessedBytes`
- `ActiveConnectionCount`
- `NewConnectionCount`
- `TargetResponseTime`

Sum metrics are aggregated across the selected CloudWatch window, while Average metrics use the arithmetic mean of returned datapoints. CloudWatch pagination is consumed until all result pages are collected. The dashboard exposes the resulting totals/averages with explicit metric semantics.

The dashboard keeps Elastic Load Balancing Cost Explorer spend at service level. It does **not** divide aggregate ELB cost across individual load balancers without resource-level billing evidence.

Review signals include low request activity, high processed bytes, high target response time, and non-active load balancers. These are evidence-based investigation candidates, not automatic modification decisions. The platform does not fabricate data-transfer prices or savings.

## Production Hardening

The production-hardening milestone strengthens the ALB evidence path by:

- Distinguishing CloudWatch `Sum` metrics from `Average` metrics.
- Aggregating `RequestCount`, `ProcessedBytes`, and `NewConnectionCount` as totals rather than misleading averages.
- Preserving `ActiveConnectionCount` and `TargetResponseTime` as averages.
- Handling `GetMetricData` `NextToken` pagination.
- Adding regression tests for aggregation and pagination.
- Keeping missing metrics unavailable rather than treating them as zero.
- Keeping all AWS integration analysis-only with no resource mutation APIs.

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
│   ├── cloudwatch_ebs.py
│   ├── cloudwatch_alb.py
│   ├── ec2_intelligence.py
│   ├── ec2_utilization_intelligence.py
│   ├── rds_intelligence.py
│   ├── ebs_intelligence.py
│   ├── alb_intelligence.py
│   └── finops_exports.py
├── dashboard/
│   └── pages/
│       ├── 2_EC2_Cost_Intelligence.py
│       ├── 3_RDS_Cost_Intelligence.py
│       ├── 4_EBS_Cost_Intelligence.py
│       ├── 5_ALB_Data_Transfer_Intelligence.py
│       └── 6_FinOps_Reports_Validation.py
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

For the reporting workflow, open the Streamlit multipage dashboard and select **FinOps Reports & Validation**.

## Three Documentation Files

- `README.md` — public project overview.
- `PROJECT.md` — complete FinOps case study, architecture, evidence, decisions, and outcomes.
- `IMPLEMENTATION.md` — hands-on implementation, data model, commands, testing, and troubleshooting.

## Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, secrets, private IPs, customer information, internal hostnames, or proprietary infrastructure code.
