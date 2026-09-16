# Project Case Study — AWS Billing & Cost Optimization Platform

## 1. Objective

Create an evidence-driven FinOps platform that turns AWS billing data into cost trends, cost-driver analysis, anomaly findings, infrastructure/utilization evidence, optimization review signals, savings validation, governance signals, and auditable reports.

## 2. Problem

AWS bills can show that spending changed without immediately explaining which services or resources require investigation. Governance needs to combine spend, budgets, anomalies, forecast evidence, operational findings, and validation without turning incomplete evidence into unsupported conclusions.

## 3. Core Workflow

```text
Collect → Normalize → Analyze → Detect → Investigate → Correlate → Govern → Recommend → Validate → Report → Export
```

## 4. Evidence Model

- `VERIFIED` — directly supported by available billing or AWS evidence.
- `PARTIALLY VERIFIED` — supported by some evidence but missing a required confirmation.
- `INFERENCE — NOT DIRECTLY VERIFIED` — plausible explanation that must not be presented as confirmed fact.

## 5. Historical Case Study

The repository contains historical monthly billing data from December 2025 through August 2026. These figures are observed billing inputs. The platform must not infer causality from a cost change without supporting infrastructure or operational evidence.

## 6. Platform Capabilities

### Billing, anomaly, and budget intelligence

- Monthly spend and month-over-month change.
- Service-level spend and cost contribution.
- AWS Cost Anomaly Detection findings with AWS-reported impact and root causes.
- AWS Budgets limits, actual spend, forecast spend, periods, and threshold statuses.

### Infrastructure investigation

- EC2 resource-level cost attribution when resource IDs are available.
- EC2, RDS, EBS, and ALB inventory correlation.
- CloudWatch utilization, I/O, traffic, and performance evidence.
- Explicit handling of unavailable metrics and failed API observations.

### Optimization and validation

- EC2, RDS, EBS, ALB, data-transfer, and idle-resource review signals.
- Baseline/post-change measurement and observed cost difference.
- Exportable evidence for review.

## 7. FinOps Executive Governance — Milestone #15

The executive governance layer aggregates existing normalized evidence instead of introducing duplicate AWS collection paths. `src/finops_governance.py` produces a deterministic `GovernanceSnapshot` containing:

- Latest and previous analyzed cost.
- Month-over-month percentage change when a valid previous period exists.
- Forecast amount and confidence when supplied.
- Budget count, over-budget count, and near-limit count.
- Anomaly count and AWS-reported estimated impact when supplied.
- Review-finding count.
- Validation status.
- Evidence state: `insufficient-evidence`, `cost-only`, or `multi-signal`.

The Streamlit page `dashboard/pages/9_FinOps_Executive_Governance.py` surfaces this snapshot as an executive review view. It accepts the project's normalized billing CSV schema and optional JSON evidence for budgets, anomalies, findings, forecast, and validation. It explicitly distinguishes missing evidence from zero and warns that the output is analysis-only.

The governance snapshot does **not** rank cloud providers, authorize changes, claim that an anomaly caused a cost increase, fabricate savings, or treat a forecast as a guarantee.

## 8. Production Deployment Readiness — Milestone #16

The deployment-readiness layer adds a deterministic pre-deployment gate around the existing runtime configuration and health model. `src/deployment_readiness.py` checks configuration status, configured data-directory availability, and the explicit read-only operating model.

The dashboard is containerized with `deployment/Dockerfile`. The image uses Python 3.12, installs only the dashboard runtime requirements, exposes Streamlit on port `8501`, and includes a container health check against the operational health endpoint. `deployment/.dockerignore` excludes Git metadata, virtual environments, environment files, private keys, and common secret directories from the build context.

The hardened image runs as an unprivileged `app` user rather than root. The production Compose profile additionally enables a read-only root filesystem, drops all Linux capabilities, enforces `no-new-privileges`, and provides a bounded tmpfs for temporary runtime state. These controls reduce the container's available privileges without changing the application's read-only AWS behavior.

This milestone does not introduce an AWS deployment target or automated infrastructure provisioning. The container is a deployment artifact; runtime AWS access still follows the standard boto3 credential chain. Live mode remains analysis-only.

## 9. Production Observability — Milestone #18

The production observability layer adds a lightweight operational control plane beside Streamlit. `deployment/health_server.py` exposes:

- `GET /health` — liveness-style process response.
- `GET /readiness` — the existing deterministic runtime readiness report.
- `GET /metrics` — Prometheus-compatible process-local counters and duration summaries.

`deployment/entrypoint.py` starts the health server and Streamlit as one container workload and forwards termination signals to the dashboard process. The Docker health check now uses `/health`, while the hardened Compose profile keeps the health service internal unless an operator chooses to publish port `8080`.

`src/observability.py` provides thread-safe counters/timers, correlation-ID generation, common AWS/dependency error classification, and sanitization of secret-like fields. The metrics registry is intentionally process-local: restarting a container resets it, so these signals are operational telemetry rather than durable billing evidence.

The new `dashboard/pages/10_Production_Observability.py` gives operators runtime mode/region, readiness state, current process-local counters, and endpoint guidance. No mutation capability is introduced.

## 10. AWS Integration Principle

The live AWS collector uses read-only observation APIs with bounded SDK retry behavior. The platform is decision-support, not autonomous infrastructure modification.

## 11. Confidentiality

Professional production evidence must be sanitized. Proprietary application code, Terraform, account identifiers, private addresses, credentials, customer information, and internal hostnames are not part of this public repository.

## 12. Success Criteria

A successful implementation can answer:

1. How much did AWS spend?
2. How did spend change over time?
3. Which services drove the change?
4. Which resources have verified cost attribution?
5. What utilization, I/O, traffic, and performance evidence is available?
6. Which findings require investigation?
7. What optimization opportunities are supported by evidence?
8. Did an implemented optimization produce an observed cost change?
9. Can the evidence be exported into a repeatable report?
10. Can the system distinguish missing evidence from classified AWS API failure?
11. Can anomaly findings be retrieved and paginated without mutation capability?
12. Can budget limits, actual spend, and forecast spend be inspected with explicit evidence states?
13. Can executive governance combine these signals without inventing missing evidence?
14. Can an operator load normalized billing evidence and review governance signals without granting mutation permissions?
15. Can a deployment candidate be checked for valid runtime configuration, required local paths, and explicit analysis-only safety before release?
16. Can the dashboard run as a non-root container with a health check and a reduced build context?
17. Can the production Compose profile enforce a read-only filesystem, dropped capabilities, and `no-new-privileges`?
18. Can CI validate that the production image builds successfully?
19. Can an operator distinguish liveness from readiness without granting mutation permissions?
20. Can operational counters and AWS call timing be exposed without treating ephemeral telemetry as billing evidence?
21. Can common authentication, permission, throttling, dependency, configuration, and application failures be classified safely?

## 13. Non-Goals

- Automatic resource termination, reboot, resizing, or modification.
- Automatic infrastructure deployment.
- Publishing confidential production configuration.
- Claiming savings attribution without evidence.
- Treating missing utilization data as zero.
- Retrying validation or permission failures through custom application loops.
- Turning anomaly findings into automatic infrastructure changes.
- Creating or modifying AWS Budgets or budget subscribers.
- Treating executive governance output as an autonomous remediation engine.
- Treating the container image as proof of a production deployment.
- Treating process-local metrics as durable monitoring or billing history.
