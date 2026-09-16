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

`dashboard/pages/9_FinOps_Executive_Governance.py` provides an executive snapshot with latest cost, MoM change, budget alerts, anomaly count, evidence status, and a full governance table. The page is analysis-only and explicitly warns that attribution and savings claims require supporting evidence.

The dashboard is intentionally conservative: unavailable inputs remain unavailable instead of being converted into fabricated values.

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

## 8. Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The Streamlit application includes EC2, RDS, EBS, ALB, reporting, anomaly, budget governance, and executive governance views.

## 9. Testing

Run:

```bash
python -m pytest -q
```

Executive governance tests cover combined signals, MoM calculation, budget status counts, anomaly impact aggregation, forecast evidence, validation status, and insufficient-evidence handling.

## 10. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Dashboard errors must not expose raw AWS responses or sensitive service details.

## 11. Recommendation Lifecycle

```text
IDENTIFIED → ANALYZED → RECOMMENDED → HUMAN REVIEW → IMPLEMENTED → VALIDATING → VALIDATED / NOT VALIDATED → REPORTED
```

## 12. Current Milestones

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
15. FinOps Executive Governance — in progress.
