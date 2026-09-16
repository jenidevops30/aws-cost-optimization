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
docker run --rm -p 8501:8501 aws-finops-control-center
```

The image exposes port `8501`, uses Streamlit's health endpoint for its Docker `HEALTHCHECK`, and runs the application as the unprivileged `app` user. The build context excludes Git metadata, environment files, private keys, virtual environments, and common secret directories.

For the hardened production profile:

```bash
docker compose -f deployment/compose.production.yml up -d --build
```

The Compose profile configures a read-only root filesystem, drops all Linux capabilities, enables `no-new-privileges`, and mounts `/tmp` as a bounded tmpfs. These controls are container-level hardening; they do not provide an AWS deployment or modify cloud resources.

For live AWS access, provide credentials through the deployment environment or an attached IAM role rather than embedding them in the image. The application itself does not create or modify AWS resources.

## 10. Production Preflight

Before a production release:

1. Build the image from a clean checkout.
2. Run the full test suite and compile check.
3. Run `deployment_ready()` with the intended runtime configuration.
4. Confirm the IAM identity uses the repository's read-only policy or an organization-approved equivalent.
5. Confirm AWS region and data directory settings.
6. Start the container and verify `/_stcore/health` locally.
7. Open the dashboard and validate Demo/CSV mode first.
8. Enable live mode only when AWS credentials and read-only permissions are confirmed.
9. Confirm no credentials, `.env` files, private keys, or confidential evidence are present in the image/build context.
10. Review logs for structured output and absence of secret-like values.

## 11. Testing

Run:

```bash
python -m pytest -q
```

The CI matrix covers Python 3.11 and 3.12, Python compilation, and the full pytest suite. Deployment-readiness tests cover valid demo configuration, missing data directories, and the analysis-only live-mode contract. The production CI path also builds the Docker image from `deployment/Dockerfile`.

## 12. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Structured logging redacts common secret-like fields. Dashboard errors must not expose raw AWS responses or sensitive service details.

The container runs without root privileges. The hardened Compose profile additionally applies a read-only root filesystem, `no-new-privileges`, and `cap_drop: ALL`. Container hardening reduces process privileges but is not a substitute for network controls, IAM controls, image scanning, or host security.

## 13. Recommendation Lifecycle

```text
IDENTIFIED → ANALYZED → RECOMMENDED → HUMAN REVIEW → IMPLEMENTED → VALIDATING → VALIDATED / NOT VALIDATED → REPORTED
```

## 14. Current Milestones

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
17. Production Container Hardening — in progress.
