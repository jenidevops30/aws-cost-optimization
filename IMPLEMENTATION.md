# Implementation — AWS Billing & Cost Optimization Platform

## 1. Local Prototype

The implementation works from normalized CSV billing data and can optionally connect to AWS through read-only APIs. Historical analysis remains deterministic and testable without AWS credentials.

## 2. Data Flow

```text
CSV / Cost Explorer
        ↓
Normalized Cost Records
        ↓
Cost Analytics + Cost Anomaly Detection
        ↓
Inventory Correlation
        ↓
CloudWatch Utilization / I/O / Traffic Evidence
        ↓
Review Signals
        ↓
Human Review
        ↓
Validation
        ↓
JSON / CSV / Markdown Report
```

## 3. AWS Read-Only Sources

### Cost Explorer

- Service-level monthly cost through `GetCostAndUsage`.
- EC2 resource-level cost through `GetCostAndUsageWithResources` when AWS returns resource IDs.
- RDS, EBS, and ELB remain service-level unless resource-level billing evidence exists.

### Cost Anomaly Detection

`src/cost_anomaly.py` calls the Cost Explorer `GetAnomalies` API in read-only mode. It accepts an explicit date interval and optional monitor ARN, consumes `NextPageToken`, and normalizes returned findings into a stable application model.

Captured evidence includes:

- anomaly identifier
- monitor ARN
- anomaly start/end dates
- AWS-reported `TotalImpact`
- AWS-reported `TotalActualSpend`
- available root causes: service, region, usage type, linked account

The implementation does not calculate a replacement anomaly impact, invent pricing, or turn a finding into an automatic remediation. `TotalImpact` is presented as AWS-reported anomaly evidence.

### EC2 / RDS / EBS / ALB

Inventory and CloudWatch collectors remain read-only and use the shared resilience layer. Missing CloudWatch metrics remain unavailable rather than zero.

## 4. Cost Anomaly Dashboard

`dashboard/pages/7_Cost_Anomaly_Detection.py` provides:

1. Region and date-window selection.
2. Optional Cost Anomaly Detection monitor ARN.
3. Read-only anomaly retrieval.
4. Count of returned findings.
5. Sum of AWS-reported estimated impact values.
6. Affected-service summary.
7. Per-anomaly evidence table.
8. Root-cause service/region display.
9. Explicit analysis-only and causality warnings.

If AWS retrieval fails, the dashboard shows a generic safe error rather than raw service exception content.

## 5. Missing Data and AWS Failure Semantics

Missing CloudWatch metrics are represented as unavailable. They are never converted to zero.

Live AWS failures are handled by `src/aws_resilience.py`:

- Boto3 clients use `standard` retry mode with a maximum of five attempts.
- Connect timeout is 10 seconds and read timeout is 30 seconds.
- AWS failures are classified into stable categories.
- Raw AWS exception text is not used as dashboard-facing output.

The anomaly collector consumes pagination explicitly, so a multi-page response is not silently truncated.

## 6. ALB Review Rules

The ALB collector treats `RequestCount`, `ProcessedBytes`, and `NewConnectionCount` as Sum metrics and `ActiveConnectionCount` and `TargetResponseTime` as Average metrics. `NextToken` pagination is consumed until complete.

## 7. FinOps Reporting & Validation

`src/finops_exports.py` provides deterministic, analysis-only JSON, CSV, and Markdown exports plus baseline/post-optimization validation. An observed reduction is not treated as proof of causality.

## 8. Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The Streamlit application includes dedicated EC2, RDS, EBS, ALB, FinOps reporting, and Cost Anomaly Detection pages.

## 9. Testing

Run:

```bash
python -m pytest -q
```

Cost Anomaly Detection tests cover:

- date-window validation
- maximum page-size validation
- `NextPageToken` pagination
- AWS impact field preservation
- deterministic summary statistics

Existing tests continue to cover CloudWatch aggregation, missing-data semantics, AWS failure classification, read-only behavior, reporting exports, review signals, and dashboard wiring.

## 10. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. AWS integration is observation-only and contains no resource mutation actions. Dashboard errors must not expose raw AWS responses or sensitive service details.

## 11. Recommendation Lifecycle

```text
IDENTIFIED
    ↓
ANALYZED
    ↓
RECOMMENDED
    ↓
HUMAN REVIEW
    ↓
IMPLEMENTED
    ↓
VALIDATING
    ↓
VALIDATED / NOT VALIDATED
    ↓
REPORTED
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
13. AWS Cost Anomaly Detection intelligence — in progress.
