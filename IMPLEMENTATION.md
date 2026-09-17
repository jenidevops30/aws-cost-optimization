# Implementation — AWS Billing & Cost Optimization Platform

## 1. Local Prototype

The implementation works from normalized CSV billing data and can optionally connect to AWS through read-only APIs. Historical analysis remains deterministic and testable without AWS credentials.

## 2. Data Flow

```text
CSV / Cost Explorer
        ↓
Normalized Cost Records
        ↓
Cost + Anomaly + Budget Evidence
        ↓
Inventory / CloudWatch Correlation
        ↓
Review / Governance Signals
        ↓
Human Review
        ↓
Validation
        ↓
JSON / CSV / Markdown Report
```

## 3. Executive Governance Layer

`src/finops_governance.py` is a deterministic aggregation layer over existing evidence. It accepts normalized monthly costs, budget rows, anomaly rows, review findings, forecast data, and validation data.

`build_governance_snapshot()` calculates:

1. Latest and previous analyzed cost.
2. Month-over-month percentage change when the previous cost is valid and non-zero.
3. Forecast amount and confidence when supplied.
4. Budget count, over-budget count, and near-limit count.
5. Anomaly count and summed AWS-reported estimated impact.
6. Finding count.
7. Validation status.
8. Evidence status: `insufficient-evidence`, `cost-only`, or `multi-signal`.

No AWS API is called by this aggregation layer and no resource is modified.

## 4. Executive Governance Dashboard

`dashboard/pages/9_FinOps_Executive_Governance.py` provides an executive snapshot with latest cost, MoM change, budget alerts, anomaly count, cost trend, evidence status, review queue, and a full governance table.

The page accepts the project's normalized billing CSV schema and optional JSON evidence with `budgets`, `anomalies`, `findings`, `forecast`, and `validation` keys. Invalid or incomplete evidence is surfaced explicitly rather than converted into defaults that imply evidence exists.

## 5. AWS Read-Only Sources

### Cost Explorer

- Service-level monthly cost through `GetCostAndUsage`.
- EC2 resource-level cost through `GetCostAndUsageWithResources` when AWS returns resource IDs.
- RDS, EBS, and ELB remain service-level unless resource-level billing evidence exists.

### Cost Anomaly Detection

`src/cost_anomaly.py` calls `GetAnomalies` in read-only mode, validates the date interval, consumes `NextPageToken`, and preserves AWS-reported impact and root-cause evidence.

### AWS Budgets

`src/aws_budgets.py` calls `DescribeBudgets` in read-only mode, consumes `NextToken`, preserves limit/actual/forecast/period evidence, and produces deterministic threshold statuses. No budget mutation APIs are used.

### EC2 / RDS / EBS / ALB

Inventory and CloudWatch collectors remain read-only and use the shared resilience layer. Missing CloudWatch metrics remain unavailable rather than zero.

## 6. Missing Data and AWS Failure Semantics

Missing CloudWatch metrics are represented as unavailable. Live AWS failures are classified by `src/aws_resilience.py`, which uses bounded standard SDK retries, connection/read timeouts, and safe dashboard-facing errors.

Cost Anomaly Detection and AWS Budgets collectors consume API pagination explicitly.

## 7. FinOps Reporting & Validation

`src/finops_exports.py` provides deterministic JSON, CSV, and Markdown exports plus baseline/post-optimization validation. An observed reduction is not treated as proof of causality.

## 8. Production Deployment Readiness

`src/deployment_readiness.py` provides a local pre-deployment gate:

```python
from src.deployment_readiness import deployment_ready, run_deployment_checks
from src.runtime_config import RuntimeConfig

config = RuntimeConfig.from_env()
checks = run_deployment_checks(config)
assert deployment_ready(config)
```

Checks are non-mutating and cover runtime configuration, the configured data directory, and the explicit analysis-only safety model.

Runtime configuration supports:

- `FINOPS_MODE=demo|live`
- `AWS_REGION` or `AWS_DEFAULT_REGION`
- `FINOPS_LOG_LEVEL`
- `FINOPS_AWS_CONNECT_TIMEOUT`
- `FINOPS_AWS_READ_TIMEOUT`
- `FINOPS_AWS_MAX_ATTEMPTS`
- `FINOPS_DATA_DIR`

## 9. Container Deployment

Build and run the dashboard container:

```bash
docker build -f deployment/Dockerfile -t aws-finops-control-center .
docker run --rm -p 8501:8501 -p 8080:8080 aws-finops-control-center
```

The image exposes Streamlit on `8501` and the operational health server on `8080`. `deployment/entrypoint.py` starts both workloads. The Docker `HEALTHCHECK` calls `/health`; readiness is available separately through `/readiness`.

For the hardened production profile:

```bash
docker compose -f deployment/compose.production.yml up -d --build
```

The Compose profile configures a read-only root filesystem, drops all Linux capabilities, enables `no-new-privileges`, and mounts `/tmp` as a bounded tmpfs. These controls are container-level hardening; they do not provide an AWS deployment or modify cloud resources.

For live AWS access, provide credentials through the deployment environment or an attached IAM role rather than embedding them in the image. The application itself does not create or modify AWS resources.

## 10. Production Observability

The operational health server is intentionally implemented with Python's standard library so the container does not need another runtime dependency.

Endpoints:

```text
GET /health      → 200 when the health process is responding
GET /readiness   → 200 when runtime readiness passes, otherwise 503
GET /metrics     → Prometheus text-format process-local metrics
```

`src/observability.py` contains a thread-safe `MetricsRegistry`, correlation-ID generation, AWS/dependency failure classification, secret-like error sanitization, and a timing context manager for AWS operations.

Example operational checks:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/readiness
curl http://127.0.0.1:8080/metrics
```

The metrics registry is process-local and resets after a restart. It must not be used as a substitute for durable Prometheus storage, CloudWatch billing evidence, or incident history.

### Failure classification

The observability layer distinguishes common classes such as:

- `configuration-error`
- `dependency-error`
- `aws-authentication-error`
- `aws-permission-error`
- `aws-throttling`
- `application-error`

Classification is diagnostic metadata, not proof of the underlying AWS root cause. Detailed AWS responses should remain outside user-facing errors.

## 11. Production Preflight

Before a production release:

1. Build the image from a clean checkout.
2. Run the full test suite and compile check.
3. Run `deployment_ready()` with the intended runtime configuration.
4. Confirm the IAM identity uses the repository's read-only policy or an organization-approved equivalent.
5. Confirm AWS region and data directory settings.
6. Start the container and verify `/health` and `/readiness` locally.
7. Verify `/metrics` responds with Prometheus text.
8. Open the dashboard and validate Demo/CSV mode first.
9. Enable live mode only when AWS credentials and read-only permissions are confirmed.
10. Confirm no credentials, `.env` files, private keys, or confidential evidence are present in the image/build context.
11. Review structured logs and error messages for secret-like values.

## 12. Testing

Run:

```bash
python -m pytest -q
```

The CI matrix covers Python 3.11 and 3.12, Python compilation, and the full pytest suite. Deployment-readiness and observability tests cover configuration, analysis-only behavior, correlation IDs, error classification, sanitization, metrics, and readiness. The production CI path also builds the Docker image and starts it to smoke-test `/health`, `/readiness`, and `/metrics`.

The security workflow additionally runs repository security tests and `pip-audit -r dashboard/requirements.txt` against declared dashboard dependencies. A dependency advisory is a review/release signal; the workflow does not auto-upgrade packages.

## 13. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Structured logging redacts common secret-like fields. Dashboard errors must not expose raw AWS responses or sensitive service details.

The container runs without root privileges. The hardened Compose profile additionally applies a read-only root filesystem, `no-new-privileges`, and `cap_drop: ALL`. Container hardening reduces process privileges but is not a substitute for network controls, IAM controls, image scanning, or host security.

## 14. Security & Compliance Hardening

The repository security gate is implemented in `security/compliance.py`.

### Secret-pattern scan

The scanner checks text-like source/configuration files for a small set of high-signal credential patterns. It returns pattern identifiers and counts only; it never places matched values in dashboard output, logs, or test assertions.

### Docker build context

`deployment/.dockerignore` must exclude common sensitive inputs such as `.env`, environment variants, private-key extensions, Git metadata, and the `secrets/` directory. The check fails if required exclusions are missing.

### Read-only IAM policy validation

`security/readonly-policy.json` is parsed as JSON and its allowed actions are checked against the platform's observation-only AWS action families. Actions associated with resource creation, deletion, termination, modification, start/stop, attachment, authorization, or revocation are rejected by the static validator.

### Dependency audit

CI runs `pip-audit` against `dashboard/requirements.txt`. This identifies known published Python dependency vulnerabilities; it does not guarantee that the complete runtime or host is vulnerability-free.

### Dashboard review

`dashboard/pages/11_Security_Compliance.py` displays the static control results and their limitations. It is a review aid, not a compliance certification system.

## 15. FinOps Alerting & Monitoring

The alerting layer is intentionally separated into event lifecycle and notification transport.

### Alert lifecycle

```text
Cost / finding signal
       ↓
   AlertMonitor
       ↓
Deduplicate by deterministic key
       ↓
OPEN → ACKNOWLEDGED → RESOLVED
```

`AlertMonitor.ingest_cost_alerts()` consumes existing `CostAlert` objects. `ingest_findings()` accepts normalized finding mappings so future collectors can integrate without adding AWS mutation paths.

Deduplication is process-local. An identical service/period/reason or finding/period/detail identity is not emitted twice during the same process lifetime.

### Notification adapters

`src/alert_notifications.py` contains:

- `ConsoleNotifier` for dependency-free local/CI diagnostics.
- `WebhookNotifier` with an injected sender, keeping HTTP implementation and credentials outside the alerting core.
- `webhook_payload()` for deterministic JSON serialization.

Example:

```python
from src.alert_monitoring import AlertMonitor
from src.alert_notifications import ConsoleNotifier

monitor = AlertMonitor()
new_events = monitor.ingest_cost_alerts(alerts)
ConsoleNotifier().send(new_events)
```

No AWS credentials or webhook secrets belong in the source tree. Production notification delivery should use an approved secret-management mechanism.

### Dashboard

`dashboard/pages/12_FinOps_Alerting_Monitoring.py` provides a lightweight review interface and demonstrates alert creation, deduplication messaging, lifecycle states, and the analysis-only safety model.

The demo monitor is process-local and resets on application restart. It is not a durable incident-management system.

## 16. Multi-Account FinOps Intelligence

`src/multi_account_finops.py` adds an account-aware normalized model without introducing a second AWS collection path. `AccountCostRecord` keeps billing period, account ID/name, service, region, cost, and currency together.

Core functions:

```python
from src.multi_account_finops import account_totals, account_service_totals, account_mom

account_totals(records)
account_service_totals(records)
account_mom(records)
```

The aggregation layer preserves account boundaries and calculates:

- total cost by account;
- cost by account and service;
- per-account period and month-over-month changes.

`validate_account_id()` performs a basic 12-digit AWS account-ID shape check. It does not prove that an account exists or that the caller has access to it.

The dashboard page `dashboard/pages/13_Multi_Account_FinOps.py` demonstrates the model with synthetic records. Production billing data should come from approved billing evidence. The page intentionally does not assume cross-account credentials or role assumption.

### Testing

`tests/test_multi_account_finops.py` verifies account aggregation, account/service boundaries, period-change calculations, and account-ID validation.

### Safety

This milestone introduces no AWS Organizations calls, STS role assumption, account changes, IAM changes, or resource mutations. Account identifiers and production billing data must be sanitized before publication.

## 17. Current Milestones

1. CSV ingestion and normalization — complete.
2. Cost-analysis API/CLI — complete.
3. Dashboard — complete.
4. Anomaly detection — complete.
5. EC2 resource-level investigation — complete.
6. EC2 CloudWatch utilization intelligence — complete.
7. RDS CloudWatch cost/utilization intelligence — complete.
8. EBS capacity and I/O intelligence — complete.
9. ALB and data-transfer investigation — complete.
10. FinOps reports, exports, and validation workflows — complete.
11. Production hardening — complete.
12. AWS API reliability and error handling — complete.
13. AWS Cost Anomaly Detection intelligence — complete.
14. AWS Budget Governance intelligence — complete.
15. FinOps Executive Governance — complete.
16. Production Deployment Readiness — complete.
17. Production Container Hardening — complete.
18. Production Observability — in progress.
19. Production Security & Compliance Hardening — in progress.
20. FinOps Alerting & Monitoring — in progress.
21. Multi-Account FinOps Intelligence — in progress.
