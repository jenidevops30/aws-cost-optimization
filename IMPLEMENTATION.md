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
Commitment Coverage Analysis
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

`src/cost_allocation.py` is an evidence-preserving layer for organizational cost allocation review. Explicit allocation keys classify spend as allocated; missing allocation evidence remains unallocated.

## 11. Commitment Coverage Intelligence

`src/finops_commitment.py` defines `CommitmentEvidence` for `reserved-instance` and `savings-plan` evidence.

```python
from src.finops_commitment import CommitmentEvidence, coverage_percent

evidence = CommitmentEvidence(
    period="2026-08",
    commitment_type="savings-plan",
    service="Amazon EC2",
    eligible_spend=100.0,
    covered_spend=75.0,
)

coverage = coverage_percent(evidence)
```

Coverage is calculated as covered spend divided by eligible spend. If eligible spend is zero, coverage is `None`, not zero. Invalid commitment types, negative spend, and covered spend greater than eligible spend raise `ValueError`.

`aggregate_commitment_coverage()` groups evidence by billing period and commitment type and returns eligible, covered, uncovered, and coverage percentage values. `commitment_review_flags()` provides deterministic review signals such as `no-eligible-spend`, `no-covered-eligible-spend`, and `low-coverage-review`.

`dashboard/pages/15_Commitment_Coverage.py` uses synthetic evidence and clearly labels it. It is not a purchase optimizer and does not execute AWS commitment changes.

### Evidence rules

- Eligible and covered spend must be supplied by an approved evidence source.
- The platform does not invent commitment utilization or savings.
- Coverage is not a savings estimate.
- Zero eligible spend is unavailable coverage, not evidence of zero utilization.
- Synthetic dashboard values must never be presented as production AWS billing data.

## 12. Production Preflight

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
11. Review allocation and commitment coverage evidence before organizational decisions.

## 13. Testing

Run:

```bash
python -m pytest -q
```

CI covers Python 3.11 and 3.12, compilation, the full pytest suite, security checks, dependency audit, and the hardened container smoke path. Commitment tests cover deterministic calculations, zero eligible spend, aggregation, invalid types, invalid spend relationships, and dashboard safety.

If CI reports a failure, fix the underlying implementation or test issue and rerun CI. Do not suppress failures or weaken assertions solely to obtain a green build.

## 14. Safety

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Structured logging redacts common secret-like fields. Dashboard errors must not expose raw AWS responses or sensitive service details.

Commitment coverage is analysis-only: it does not purchase, cancel, modify, or resize Savings Plans or Reserved Instances.

## 15. Three Documentation Files

The project maintains exactly three canonical Markdown documents: `README.md`, `PROJECT.md`, and `IMPLEMENTATION.md`.

## 16. Current Milestones

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
23. Commitment Coverage Intelligence — in progress.


## 12. Commitment Trend & Coverage/Utilization Correlation

`src/finops_commitment_trend.py` defines `CommitmentTrendEvidence` and deterministic helpers:

- `commitment_trend()` returns period/type trend rows.
- `coverage_utilization_gap()` returns coverage minus utilization in percentage points when both measures are available.
- `trend_review_flags()` identifies unavailable evidence, low coverage, low utilization, and coverage/utilization mismatch.

Coverage uses `covered_spend / eligible_spend`. Utilization uses `utilized_value / committed_value`. Zero denominators return `None` rather than zero.

Example:

```python
from src.finops_commitment_trend import CommitmentTrendEvidence, coverage_utilization_gap

record = CommitmentTrendEvidence(
    period="2026-08",
    commitment_type="savings-plan",
    eligible_spend=130.0,
    covered_spend=104.0,
    committed_value=100.0,
    utilized_value=82.0,
)

gap = coverage_utilization_gap(record)
```

The dashboard `17_Commitment_Trend_Correlation.py` is synthetic and analysis-only. It does not purchase, cancel, modify, or resize commitments.

### Evidence rules

- Coverage and utilization are separate evidence dimensions.
- A percentage-point gap is unavailable when either denominator is zero.
- Low utilization is an investigation signal, not proof that a commitment should be changed.
- No savings amount is derived from a utilization percentage.
- Synthetic dashboard values are not production AWS billing evidence.


## 13. FinOps Unit Economics

`src/finops_unit_economics.py` defines `UnitEconomicsEvidence` and deterministic cost-per-unit aggregation.

`cost_per_unit()` returns `None` when units are zero. `aggregate_unit_economics()` preserves period, workload, and unit dimensions. `unit_economics_review_flags()` identifies unavailable unit volume and zero-cost review cases.

Example:

```python
from src.finops_unit_economics import UnitEconomicsEvidence, cost_per_unit

record = UnitEconomicsEvidence(
    period="2026-08",
    workload="production-api",
    cost=132.0,
    units=1_500_000,
    unit_name="requests",
)

unit_cost = cost_per_unit(record)
```

The dashboard uses synthetic evidence only. Unit economics must not be treated as a savings guarantee; workload volume must come from an approved evidence source.


## 15. FinOps Unit Economics Correlation

`src/finops_unit_economics_correlation.py` defines `UnitCostCorrelationEvidence` and `correlation_rows()`.

The model preserves an optional supporting signal and its explicit name. Missing signals remain `None` with `evidence_status=unavailable`. Cost per unit also remains unavailable when workload volume is zero.

Example:

```python
from src.finops_unit_economics_correlation import UnitCostCorrelationEvidence, correlation_rows

record = UnitCostCorrelationEvidence(
    period="2026-08",
    workload="production-api",
    unit_name="requests",
    cost=132.0,
    units=1_500_000,
    supporting_signal=71.0,
    signal_name="avg_cpu_pct",
)

row = correlation_rows([record])[0]
```

The supporting signal is evidence to investigate alongside unit economics, not proof of causality or a savings estimate.


## 16. FinOps Unit Economics Trends

`src/finops_unit_economics_trend.py` provides `unit_cost_trend()` and `unit_cost_change()`.

`unit_cost_change()` calculates percentage change in observed cost per unit between two records. It returns `None` when either unit volume is zero or the previous unit cost is zero.

Example:

```python
from src.finops_unit_economics_trend import unit_cost_change

change = unit_cost_change(
    {"cost": 100.0, "units": 1000},
    {"cost": 120.0, "units": 1500},
)
```

The dashboard uses synthetic evidence only. Trend changes must be correlated with approved workload, infrastructure, and operational evidence before causal conclusions are made.


## 17. FinOps Unit Economics Quality

`src/finops_unit_economics_quality.py` defines `UnitEconomicsQualityEvidence`, `quality_rows()`, and `quality_flags()`.

Available unit volume requires an explicit source. Zero volume remains unavailable. Flags include `no-evidence`, `zero-volume-evidence`, `missing-volume-source`, and `zero-cost-evidence`.

The dashboard is synthetic and analysis-only. Production volume must come from an approved workload metric source.


## 20. FinOps Unit Economics Forecast Validation

`src/finops_unit_economics_forecast_validation.py` compares observed and forecast unit costs. `mean_absolute_error()` returns `None` when no complete observations exist. Missing values remain unavailable rather than zero.


## 21. FinOps Unit Economics Governance

`src/finops_unit_economics_governance.py` combines forecast error, anomaly review, and evidence availability. `governance_summary()` returns deterministic counts for operational review.
