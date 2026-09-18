# Project Case Study — AWS Billing & Cost Optimization Platform

## 1. Objective

Create an evidence-driven FinOps platform that turns AWS billing data into cost trends, cost-driver analysis, anomaly findings, infrastructure/utilization evidence, optimization review signals, savings validation, governance signals, and auditable reports.

## 2. Problem

AWS bills can show that spending changed without immediately explaining which services or resources require investigation. Governance also needs to distinguish allocated organizational spend from spend for which ownership evidence is missing.

## 3. Core Workflow

```text
Collect → Normalize → Analyze → Detect → Investigate → Correlate → Allocate → Govern → Recommend → Validate → Report → Export
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

The executive governance layer aggregates existing normalized evidence instead of introducing duplicate AWS collection paths. `src/finops_governance.py` produces a deterministic `GovernanceSnapshot` containing latest/previous cost, MoM change, optional forecast, budget status, anomaly impact, findings, validation, and evidence state.

## 8. Production Deployment Readiness — Milestone #16

The deployment-readiness layer adds a deterministic pre-deployment gate around runtime configuration, data-directory availability, and the explicit read-only operating model. The production container uses Python 3.12, Streamlit on `8501`, and an operational health server on `8080`.

## 9. Production Observability — Milestone #18

The observability layer provides `/health`, `/readiness`, and `/metrics`, plus process-local counters/timers, correlation IDs, common AWS/dependency failure classification, and secret-like error sanitization. Metrics reset on restart and are not billing evidence.

## 10. Production Security & Compliance Hardening — Milestone #19

The security layer provides deterministic checks for secret-like repository patterns, Docker build-context exclusions, and observation-only IAM actions. CI also runs `pip-audit` against dashboard requirements. These controls are release-gate evidence, not regulatory certification.

## 11. FinOps Alerting & Monitoring — Milestone #20

The alerting layer consumes existing cost alerts and review findings, assigns deterministic event identities, suppresses duplicates within process lifetime, and supports `OPEN → ACKNOWLEDGED → RESOLVED`. Notification transport is separated from alert generation and no AWS remediation is performed.

## 12. Multi-Account FinOps Intelligence — Milestone #21

`src/multi_account_finops.py` defines `AccountCostRecord` and deterministic account totals, account × service totals, and per-account period/MoM calculations. The account boundary is preserved throughout aggregation.

## 13. Cost Allocation Quality — Milestone #22

`src/cost_allocation.py` defines `AllocationRecord` and classifies spend as allocated only when explicit allocation evidence is present. Missing evidence remains unallocated. The layer calculates allocation coverage and supported unallocated-spend groupings without inferring ownership.

## 14. Commitment Coverage Intelligence — Milestone #23

`src/finops_commitment.py` provides an evidence-preserving model for `reserved-instance` and `savings-plan` coverage. It separates eligible, covered, and uncovered spend and calculates coverage percentage only when eligible spend is non-zero.

The model validates commitment type and spend boundaries, including rejecting negative values and covered spend greater than eligible spend. A zero eligible-spend record is represented as unavailable coverage rather than zero percent, preventing a misleading interpretation.

`dashboard/pages/15_Commitment_Coverage.py` demonstrates the analysis with synthetic values. It is a review aid only and does not purchase, cancel, modify, or automatically recommend AWS commitments.

### Testing and failure safety

Commitment tests cover deterministic coverage, zero eligible spend, aggregation by period and commitment type, invalid commitment types, invalid spend relationships, and dashboard safety. The objective is to fail explicitly on invalid evidence rather than weakening assertions to make CI green.

## 15. AWS Integration Principle

The live AWS collector uses read-only observation APIs with bounded SDK retry behavior. The platform is decision-support, not autonomous infrastructure modification.

## 16. Confidentiality

Professional production evidence must be sanitized. Proprietary application code, Terraform, account identifiers, private addresses, credentials, customer information, and internal hostnames are not part of this public repository.

## 17. Success Criteria

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
14. Can a deployment candidate be checked for valid runtime configuration and analysis-only safety?
15. Can the dashboard run as a non-root container with health checks and a reduced build context?
16. Can CI validate the production image and operational endpoints?
17. Can liveness, readiness, and ephemeral operational metrics be distinguished?
18. Can common AWS/dependency failures be classified safely?
19. Can secret-like patterns, Docker build context, IAM policy, and dependency vulnerabilities be checked before release?
20. Can organizational cost be analyzed while preserving AWS account boundaries?
21. Can account/service and per-account period comparisons be calculated deterministically?
22. Can the system distinguish explicitly allocated spend from unallocated spend without inventing ownership?
23. Can unallocated spend be grouped by a supported dimension without silently changing its source evidence?
24. Can eligible and covered commitment spend be separated without fabricating savings or coverage?
25. Can zero eligible spend be represented as unavailable rather than misleading zero coverage?

## 18. Non-Goals

- Automatic resource termination, reboot, resizing, or modification.
- Automatic infrastructure deployment.
- Publishing confidential production configuration.
- Claiming savings attribution without evidence.
- Treating missing utilization, allocation, or commitment evidence as zero.
- Retrying validation or permission failures through custom application loops.
- Turning anomaly findings into automatic infrastructure changes.
- Creating or modifying AWS Budgets or budget subscribers.
- Treating governance output as an autonomous remediation engine.
- Treating the container image as proof of a production deployment.
- Treating process-local metrics as durable monitoring or billing history.
- Treating static security checks as proof of regulatory compliance.
- Automatically upgrading dependencies or remediating security findings.
- Assuming cross-account access or credentials that have not been explicitly configured and approved.
- Treating synthetic multi-account, allocation, or commitment data as production billing evidence.
- Purchasing, canceling, or modifying Savings Plans or Reserved Instances automatically.


## 15. Commitment Trend & Coverage/Utilization Correlation — Milestone #24

`src/finops_commitment_trend.py` adds a period-aware evidence model containing eligible spend, covered spend, committed value, and utilized value for Savings Plans and Reserved Instances.

The layer calculates coverage and utilization independently, reports uncovered spend and unused commitment value, and calculates a percentage-point gap only when both denominators are non-zero. This prevents a zero or missing denominator from being interpreted as a real utilization or coverage result.

Review flags include low coverage, low utilization, unavailable evidence, and a coverage/utilization mismatch where coverage is at least 50% but utilization is below 50%. These are investigation signals, not purchase recommendations or savings estimates.

The dashboard uses synthetic values only.


## 16. FinOps Unit Economics — Milestone #25

The unit economics layer relates observed cost to an explicitly supplied workload volume, such as requests or jobs. It reports cost per unit only when the unit denominator is available and preserves zero-volume evidence as unavailable.

This is descriptive operational evidence. It does not infer workload ownership, fabricate workload metrics, forecast savings, or recommend an optimization action. Production use requires an approved workload metric source.


## 18. FinOps Unit Economics Correlation — Milestone #27

The correlation layer preserves cost, workload volume, and an optional supporting operational signal such as an approved utilization metric. It reports whether that supporting evidence is available without inferring a relationship when the signal is missing.

The layer is intentionally descriptive. Correlation evidence does not prove causality, ownership, or savings opportunity. Production signals must come from an approved telemetry source.


## 19. FinOps Unit Economics Trends — Milestone #26

The trend layer extends unit economics with period-over-period cost-per-unit change. It requires valid unit volume in both periods and returns unavailable when a denominator is zero or the prior unit cost is zero.

The result is descriptive evidence for investigation. A change in cost per unit does not establish why the change occurred and is not a savings forecast.


## 20. FinOps Unit Economics Quality — Milestone #28

The quality layer checks whether unit-economics records have valid dimensions, non-negative cost and volume, and an explicit source whenever volume is available. Zero-volume evidence remains unavailable.

Quality flags are evidence-review signals only. They do not establish workload ownership, causality, savings, or an optimization action.


## 23. FinOps Unit Economics Forecast Validation

This milestone validates forecast observations using explicit forecast error and mean absolute error. It evaluates historical evidence only and does not guarantee future accuracy or imply causality.


## 27. FinOps Data Quality & Reconciliation

This milestone compares explicitly identified evidence sources using deterministic absolute differences and configurable tolerances. It preserves uncertainty about source authority and does not infer business impact from mismatches.
