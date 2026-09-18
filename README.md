# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, correlating spend with infrastructure and utilization evidence, producing evidence-based optimization reviews, governance signals, and auditable reports.

> **Scope:** Decision-support only. It does not automatically modify AWS resources. Production evidence must be sanitized before publication.

## Current Capabilities

- Historical AWS billing CSV analysis.
- AWS Cost Explorer service-level cost collection.
- EC2 resource-level cost attribution when Cost Explorer returns `RESOURCE_ID` data.
- EC2, RDS, EBS, and ALB inventory/utilization intelligence.
- AWS Cost Anomaly Detection and AWS Budgets read-only governance intelligence.
- Cost/utilization correlation with explicit missing-data handling.
- FinOps executive reporting, validation, and JSON/CSV/Markdown exports.
- Bounded AWS SDK retries and classified API failures.
- **FinOps Executive Governance snapshot combining spend, budgets, anomalies, forecast, findings, validation, and evidence status.**
- **Production deployment readiness checks, structured redacted logging, and container health checks.**
- **Hardened production container profile using a non-root user, dropped capabilities, `no-new-privileges`, and read-only root filesystem support.**
- **Production observability endpoints for liveness, readiness, and Prometheus-compatible in-process metrics.**
- **Security/compliance checks for secret patterns, Docker build context, read-only IAM actions, and dependency vulnerabilities.**
- **FinOps alert lifecycle with deterministic deduplication and acknowledgement/resolution states.**
- **Multi-account cost aggregation that preserves account boundaries.**
- **Cost-allocation quality analysis that separates explicitly allocated spend from unallocated spend without inventing ownership or redistributing costs.**
- **Commitment coverage analysis for Savings Plans and Reserved Instances using supplied eligible/covered-spend evidence.**

## Architecture

```text
AWS Billing / Cost Explorer / CSV
        │
        ├── Anomaly Detection / Budgets
        ├── EC2 / RDS / EBS / ALB
        └── CloudWatch Evidence
                 │
          Cost + Evidence Analytics
                 │
        Account / Allocation Analysis
                 │
       Commitment Coverage Analysis
                 │
        Review / Governance Signals
                 │
            Human Decision
                 │
        Validate → Report → Export
```

## Cost Allocation Quality

`src/cost_allocation.py` provides deterministic analysis of whether normalized cost records contain explicit allocation evidence. Records are classified as `allocated` only when an allocation key is present; otherwise they remain `unallocated`.

The model reports allocated/unallocated spend, record counts, allocation coverage, and unallocated spend grouped by account, service, region, or billing period. Missing allocation evidence is never converted into zero or silently redistributed.

The dashboard page `dashboard/pages/14_Cost_Allocation_Quality.py` uses synthetic evidence for review. Production allocation requires approved billing, account, tagging, or other ownership evidence.

## Commitment Coverage Intelligence

`src/finops_commitment.py` provides deterministic coverage calculations for `reserved-instance` and `savings-plan` evidence. It separates eligible, covered, and uncovered spend and returns unavailable coverage when eligible spend is zero.

The dashboard page `dashboard/pages/15_Commitment_Coverage.py` uses synthetic values only. The platform does not purchase, cancel, modify, or recommend a commitment without appropriate evidence.

## Production Deployment Readiness

The platform includes deterministic runtime configuration and readiness checks. The production container exposes Streamlit on `8501` and operational health on `8080` through `/health`, `/readiness`, and `/metrics`.

The production container runs as an unprivileged `app` user. The hardened Compose profile can enable a read-only root filesystem, drop all Linux capabilities, enforce `no-new-privileges`, and isolate temporary state through tmpfs.

Live AWS credentials continue to use the standard boto3 credential chain. No AWS mutation capability is introduced.

## Production Observability

The observability layer provides process-local operational signals, correlation IDs, AWS/dependency failure classification, and secret-like error sanitization. Metrics are ephemeral and are not billing evidence.

## Security & Compliance Hardening

The repository security layer checks secret-like patterns, Docker build-context exclusions, observation-only IAM actions, and dependency vulnerabilities through `pip-audit`. These are preventive checks, not regulatory certification.

## FinOps Alerting & Monitoring

The alerting layer consumes existing cost and review signals and provides deterministic event identity, duplicate suppression, and `open → acknowledged → resolved` lifecycle states. Notification transport is separated from alert generation and AWS remediation is never executed.

## Multi-Account FinOps Intelligence

`src/multi_account_finops.py` keeps costs grouped by AWS account before calculating account totals, account/service totals, and per-account period comparisons. The dashboard uses clearly labeled synthetic evidence and does not assume cross-account credentials or role assumption.

## FinOps Executive Governance

The governance layer combines already-available evidence into a deterministic executive snapshot containing latest spend, month-over-month change, forecast evidence, budget statuses, anomaly count/impact, finding count, validation status, and explicit evidence state. It does not invent missing evidence or perform remediation.

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
├── deployment/
├── security/
├── src/
│   ├── finops_commitment.py
│   ├── cost_allocation.py
│   ├── multi_account_finops.py
│   └── ...
├── dashboard/
│   └── pages/
│       ├── 14_Cost_Allocation_Quality.py
│       ├── 15_Commitment_Coverage.py
│       └── ...
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

For the production container:

```bash
docker build -f deployment/Dockerfile -t aws-finops-control-center .
docker run --rm -p 8501:8501 -p 8080:8080 aws-finops-control-center
```

For the hardened Compose profile:

```bash
docker compose -f deployment/compose.production.yml up -d --build
```

Operational checks:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/readiness
curl http://127.0.0.1:8080/metrics
```

## Three Documentation Files

- `README.md` — public project overview.
- `PROJECT.md` — complete FinOps case study, architecture, evidence, decisions, and outcomes.
- `IMPLEMENTATION.md` — hands-on implementation, data model, commands, testing, and troubleshooting.

## Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, private IPs, customer information, internal hostnames, or proprietary infrastructure code.


## Commitment Trend & Correlation Intelligence

`src/finops_commitment_trend.py` compares commitment coverage and utilization across periods while preserving unavailable denominators. A coverage/utilization gap is reported only when both measures have valid evidence.

The dashboard page `dashboard/pages/17_Commitment_Trend_Correlation.py` uses synthetic evidence and provides review flags such as low coverage, low utilization, and a coverage/utilization mismatch. It does not estimate savings or perform commitment changes.


## FinOps Unit Economics

`src/finops_unit_economics.py` provides evidence-preserving cost-per-unit analysis by workload and period. It keeps zero unit volume explicitly unavailable and does not turn unit economics into an unsupported savings forecast.

The dashboard `dashboard/pages/18_FinOps_Unit_Economics.py` uses synthetic evidence for demonstration.


## FinOps Unit Economics Correlation

The platform can preserve an explicitly supplied operational signal alongside workload cost-per-unit evidence. Missing supporting signals remain unavailable rather than being represented as zero. This correlation view is descriptive and does not establish causality.

The dashboard `dashboard/pages/20_FinOps_Unit_Economics_Correlation.py` uses synthetic evidence.


## FinOps Unit Economics Trends

The unit-economics trend layer compares observed cost-per-unit values across periods while preserving unavailable volume denominators. It reports descriptive percentage changes only; it does not claim causality or forecast savings.

The dashboard `dashboard/pages/19_FinOps_Unit_Economics_Trends.py` uses synthetic evidence.


## FinOps Unit Economics Quality

The unit-economics quality layer validates whether workload volume has an explicit evidence source and preserves zero-volume or missing-source states as unavailable. It provides deterministic review flags rather than savings estimates or optimization recommendations.

The dashboard `dashboard/pages/21_FinOps_Unit_Economics_Quality.py` uses synthetic evidence.


## FinOps Unit Economics Forecast Validation

Adds descriptive validation of observed unit cost against forecast evidence, including forecast error and mean absolute error. Missing observations remain unavailable.


## FinOps Data Quality & Reconciliation

Adds explicit source-to-source reconciliation with configurable tolerances. Mismatches are surfaced as data-quality review signals without assuming which source is authoritative.
