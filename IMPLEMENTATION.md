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
Account / Allocation Analysis
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

`src/finops_governance.py` is a deterministic aggregation layer over existing evidence. It combines normalized monthly costs, budget rows, anomaly rows, review findings, forecast data, and validation data without calling AWS or modifying resources.

## 4. AWS Read-Only Sources

### Cost Explorer

- Service-level monthly cost through `GetCostAndUsage`.
- EC2 resource-level cost through `GetCostAndUsageWithResources` when AWS returns resource IDs.
- RDS, EBS, and ELB remain service-level unless resource-level billing evidence exists.

### Cost Anomaly Detection and Budgets

The anomaly and budget collectors use read-only APIs, validate intervals, consume pagination, and preserve source evidence. No budget mutation APIs are used.

### EC2 / RDS / EBS / ALB

Inventory and CloudWatch collectors remain read-only and use the shared resilience layer. Missing CloudWatch metrics remain unavailable rather than zero.

## 5. Missing Data and AWS Failure Semantics

Missing evidence is represented explicitly. Live AWS failures are classified by `src/aws_resilience.py`, which uses bounded standard SDK retries, connection/read timeouts, and safe dashboard-facing errors.

## 6. FinOps Reporting & Validation

`src/finops_exports.py` provides deterministic JSON, CSV, and Markdown exports plus baseline/post-optimization validation. An observed reduction is not treated as proof of causality.

## 7. Production Deployment and Observability

`src/deployment_readiness.py` provides a local pre-deployment gate. The production image runs as a non-root `app` user and the hardened Compose profile can enforce read-only filesystem, dropped capabilities, `no-new-privileges`, and bounded tmpfs.

The operational server exposes `/health`, `/readiness`, and `/metrics`. Metrics are process-local and reset after restart. They are operational telemetry, not durable billing evidence.

## 8. Security & Compliance

The security layer checks secret-like repository patterns, Docker build-context exclusions, observation-only IAM actions, and dependency vulnerabilities through `pip-audit`. These controls do not constitute regulatory certification.

## 9. FinOps Alerting & Multi-Account Analysis

The alerting layer provides deterministic event identity and `OPEN → ACKNOWLEDGED → RESOLVED` lifecycle states without AWS remediation. `src/multi_account_finops.py` preserves account boundaries for totals, account/service totals, and per-account period comparisons.

## 10. Cost Allocation Quality

`src/cost_allocation.py` is an evidence-preserving layer for organizational cost allocation review.

### Data model

```python
from src.cost_allocation import AllocationRecord

record = AllocationRecord(
    billing_period="2026-08",
    account_id="111111111111",
    service="EC2",
    cost=120.0,
    region="ap-south-1",
    allocation_key="prod",
)
```

An explicit, non-empty `allocation_key` is required for the record to be classified as `allocated`. A missing key produces `unallocated`; no ownership is inferred.

### Core analysis

```python
from src.cost_allocation import allocation_quality, unallocated_by_dimension

quality = allocation_quality(records)
unallocated = unallocated_by_dimension(records, "service")
```

`allocation_quality()` returns record counts, allocated/unallocated cost, total cost, and allocation coverage percentage. Coverage is unavailable when total cost is zero rather than being represented as a misleading percentage.

`unallocated_by_dimension()` supports only `service`, `account_id`, `region`, and `billing_period`. Unsupported dimensions raise `ValueError` so a caller cannot silently obtain an invalid grouping.

### Evidence rules

- Allocated spend is based only on an explicit allocation key.
- Unallocated spend remains unallocated.
- No service-level spend is divided among teams or resources without evidence.
- Account, service, region, and billing period are descriptive grouping dimensions, not ownership proof.
- Synthetic dashboard records must remain clearly separated from production billing evidence.

### Dashboard

`dashboard/pages/14_Cost_Allocation_Quality.py` provides total allocation coverage and unallocated-spend breakdowns using synthetic evidence. Production data should come from approved billing allocation keys, tagging evidence, account ownership metadata, or another documented source.

## 11. Production Preflight

Before a production release:

1. Build the image from a clean checkout.
2. Run the full test suite and compile check.
3. Run deployment readiness with the intended runtime configuration.
4. Confirm the IAM identity uses an organization-approved read-only policy.
5. Confirm AWS region and data directory settings.
6. Start the container and verify `/health` and `/readiness`.
7. Verify `/metrics` responds with Prometheus text.
8. Open the dashboard and validate Demo/CSV mode first.
9. Enable live mode only after AWS credentials and read-only permissions are confirmed.
10. Confirm no credentials, `.env` files, private keys, or confidential evidence are present in the build context.
11. Review allocation quality before using cost data for organizational chargeback/showback decisions.

## 12. Testing

Run:

```bash
python -m pytest -q
```

CI covers Python 3.11 and 3.12, compilation, the full pytest suite, security checks, dependency audit, and the hardened container smoke path. The allocation-quality tests cover allocated/unallocated totals, coverage calculations, supported dimension grouping, and invalid-dimension failure behavior.

If CI reports a failure, fix the underlying test or implementation issue and rerun CI before treating the PR as review-ready. Do not suppress failures or weaken assertions solely to obtain a green build.

## 13. Safety

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Structured logging redacts common secret-like fields. Dashboard errors must not expose raw AWS responses or sensitive service details.

Cost allocation is also analysis-only: it does not create tags, modify accounts, change billing configuration, or perform chargeback actions.

## 14. Three Documentation Files

The project maintains exactly three canonical Markdown documents: `README.md`, `PROJECT.md`, and `IMPLEMENTATION.md`.

## 15. Current Milestones

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
22. Cost Allocation Quality — in progress.
