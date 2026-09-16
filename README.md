# AWS Billing & Cost Optimization Platform

A read-only FinOps/DevOps platform for collecting AWS billing data, analyzing cost trends and drivers, detecting anomalies, correlating spend with infrastructure and utilization evidence, producing evidence-based optimization reviews, governance signals, and auditable reports.

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
- **Executive dashboard accepts normalized billing CSV evidence and optional normalized governance JSON.**
- Streamlit dashboard for interactive investigation and reporting.
- **Production deployment readiness checks with environment validation, deterministic readiness reporting, structured redacted logging, and a container health check.**
- **Hardened production container profile using a non-root user, dropped Linux capabilities, `no-new-privileges`, read-only root filesystem support, and Docker health checks.**
- **Production observability endpoints for liveness, readiness, and Prometheus-compatible in-process metrics.**
- **Operational observability dashboard with runtime state, readiness checks, and metric visibility.**
- **Security and compliance checks for secret patterns, Docker build context, read-only IAM actions, and dependency vulnerabilities.**

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
       Runtime / Health / Metrics
                 │
        Security / Compliance Gates
                 │
            Human Decision
                 │
        Validate → Report → Export
```

## Production Deployment Readiness

The platform includes a deployment-readiness layer that validates runtime configuration, checks the configured data directory, and explicitly records the analysis-only safety model. The production container exposes a lightweight operational health server with `GET /health`, `GET /readiness`, and `GET /metrics`. Streamlit remains available on port `8501`; operational health is served on port `8080`.

The production container runs as an unprivileged `app` user. The production Compose profile can additionally enable a read-only root filesystem, drop all Linux capabilities, and enforce `no-new-privileges`. Temporary runtime state is isolated through a tmpfs mount.

Live AWS credentials continue to use the standard boto3 credential chain. No AWS mutation capability is introduced by the deployment or observability layers.

## Production Observability

The observability layer provides process-local operational signals without introducing a monitoring SaaS dependency. It records health/readiness requests, AWS operation status and duration when integrated through the shared helper, generates correlation IDs for future request instrumentation, classifies common AWS/dependency failures, and sanitizes secret-like error fields.

`/health` is a liveness-style process check, `/readiness` evaluates the existing runtime readiness model, and `/metrics` exposes counters and duration summaries in Prometheus text format. These metrics are intentionally ephemeral and are not used as billing evidence.

## Security & Compliance Hardening

The security layer adds repository-level controls before release:

- Secret-pattern scanning that reports pattern identifiers and never prints matched secret values.
- Docker build-context validation for environment files, private keys, Git metadata, and secret directories.
- Static validation that the repository IAM policy contains observation-only AWS actions.
- CI dependency auditing with `pip-audit` against the dashboard runtime requirements.
- A Streamlit security/compliance review page that reports control status and explicitly avoids claiming regulatory certification.

These controls are preventive checks, not a substitute for organization-specific compliance programs, host security, network controls, or runtime cloud security review.

## FinOps Executive Governance

Milestone #15 provides a deterministic governance layer above the existing collectors. It combines already-available evidence into a single executive snapshot containing latest spend, month-over-month change, forecast evidence, budget statuses, anomaly count/impact, finding count, validation status, and an explicit evidence state.

The dashboard can load normalized billing CSV data and optional JSON evidence for budgets, anomalies, findings, forecast, and validation. It does not invent missing data, divide service-level spend across resources without billing evidence, claim causality, or perform remediation.

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
│   ├── Dockerfile
│   ├── compose.production.yml
│   ├── entrypoint.py
│   ├── health_server.py
│   └── .dockerignore
├── security/
│   ├── readonly-policy.json
│   └── compliance.py
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
│   ├── finops_governance.py
│   ├── deployment_readiness.py
│   └── observability.py
├── dashboard/
│   └── pages/
│       ├── 2_EC2_Cost_Intelligence.py
│       ├── 3_RDS_Cost_Intelligence.py
│       ├── 4_EBS_Cost_Intelligence.py
│       ├── 5_ALB_Data_Transfer_Intelligence.py
│       ├── 6_FinOps_Reports_Validation.py
│       ├── 7_Cost_Anomaly_Detection.py
│       ├── 8_Budget_Governance.py
│       ├── 9_FinOps_Executive_Governance.py
│       ├── 10_Production_Observability.py
│       └── 11_Security_Compliance.py
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

Review the production preflight in `IMPLEMENTATION.md` before enabling live AWS access.

## Three Documentation Files

- `README.md` — public project overview.
- `PROJECT.md` — complete FinOps case study, architecture, evidence, decisions, and outcomes.
- `IMPLEMENTATION.md` — hands-on implementation, data model, commands, testing, and troubleshooting.

## Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, private IPs, customer information, internal hostnames, or proprietary infrastructure code.
