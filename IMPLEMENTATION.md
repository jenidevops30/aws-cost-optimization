# Implementation — AWS Billing & Cost Optimization Platform

## 1. Local Prototype

The implementation works from normalized CSV billing data and can optionally connect to AWS through read-only APIs. Historical analysis remains deterministic and testable without AWS credentials.

## 2. Data Flow

```text
CSV / Cost Explorer
        ↓
Normalized Cost Records
        ↓
Cost Analytics
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
- RDS, EBS, and ELB are intentionally kept at service-level cost in the current implementation; it does not manufacture per-resource allocation.

### EC2

`DescribeInstances` supplies inventory. CloudWatch `GetMetricData` supplies CPU and network evidence.

### RDS

`DescribeDBInstances` supplies DB identifier, instance class, engine, status, Multi-AZ state, and allocated storage. CloudWatch `GetMetricData` supplies CPU, connections, free storage, ReadIOPS and WriteIOPS.

### EBS

`DescribeVolumes` supplies volume inventory. CloudWatch `GetMetricData` supplies read/write operations, bytes, queue length, and idle time. Missing metrics remain unavailable.

### ALB

ELBv2 `DescribeLoadBalancers` supplies load balancer ARN/name, type, scheme, state, DNS name, VPC, and Availability Zones.

CloudWatch `GetMetricData` supplies:

- `RequestCount`
- `ProcessedBytes`
- `ActiveConnectionCount`
- `NewConnectionCount`
- `TargetResponseTime`

For correctness, the collector treats the metric statistic as part of the data contract:

- `RequestCount`, `ProcessedBytes`, and `NewConnectionCount` use `Sum` and are aggregated into totals across returned datapoints.
- `ActiveConnectionCount` and `TargetResponseTime` use `Average` and are represented as arithmetic means of returned datapoints.
- `GetMetricData` `NextToken` pagination is consumed until no token remains.
- Missing metric results remain `None`/unavailable rather than becoming zero.

The implementation presents these as operational evidence. It does not convert traffic volume into fabricated pricing or savings estimates.

## 4. ALB Review Rules

Default review signals are explicit and configurable:

- Average request activity below 1 per metric period → `low-request-activity-review`.
- Average processed bytes at/above 1 GB per metric period → `high-processed-bytes-review`.
- Average target response time at/above 1 second → `high-target-response-time-review`.
- Load balancer state other than active → `non-active-load-balancer-review`.

These are investigation signals only. A human must verify traffic patterns, application behavior, target health, architecture requirements, and current AWS pricing before making a change.

## 5. FinOps Reporting & Validation

`src/finops_exports.py` provides deterministic, analysis-only export helpers:

- `build_validation_summary()` compares two observed billing periods and reports the observed delta when both values are supplied.
- `build_export_bundle()` attaches validation evidence to a report without changing the original findings.
- `report_to_json()` creates a machine-readable JSON artifact.
- `report_to_csv()` exports the monthly billing rows for spreadsheet analysis.
- `report_to_markdown()` creates a human-readable engineering report.

The validation status is deliberately limited to evidence that is actually available:

- `insufficient-evidence` when one or both comparison values are missing.
- `observed-reduction` when the comparison cost is lower than the baseline.
- `no-observed-reduction` when the comparison cost is equal to or higher than the baseline.

An observed reduction is **not** treated as proof of causality. The platform does not automatically attribute a billing change to a particular infrastructure optimization.

The Streamlit page `dashboard/pages/6_FinOps_Reports_Validation.py` provides:

1. Billing CSV selection and validation.
2. Service filtering.
3. Executive summary.
4. Baseline/post-optimization period selection.
5. Validation status and observed cost delta.
6. JSON, CSV, and Markdown downloads.
7. Read-only safety controls and attribution limitations.

## 6. Missing Data and AWS Failure Semantics

Missing CloudWatch metrics are represented as unavailable. They are never converted to zero because zero and missing are materially different operational states.

Live AWS failures are handled separately by `src/aws_resilience.py`:

- Boto3 clients use `standard` retry mode with a maximum of five attempts.
- Connect timeout is 10 seconds and read timeout is 30 seconds.
- `ClientError` and `BotoCoreError` failures are classified into stable categories.
- Throttling is reported as `throttled`.
- Permission failures are reported as `access-denied`.
- Missing resources are reported as `not-found`.
- Invalid request parameters are reported as `validation`.
- AWS service failures and transport failures have separate states.
- Raw AWS exception text is not used as the dashboard-facing error message.

The SDK performs bounded retries for transient conditions. The application does not implement an unbounded retry loop and does not add retries around known validation or permission failures.

## 7. Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The dashboard provides separate EC2, RDS, EBS, ALB, and FinOps reporting pages. The reporting page uses the same normalized billing model and does not require AWS credentials when operating from the repository sample dataset.

The ALB page explicitly labels Sum-derived fields as totals and Average-derived fields as averages, preventing the previous ambiguity where traffic totals were displayed as averages.

Live AWS-facing views can use the classified failure states from `aws_resilience.py` so an API failure is not presented as empty/zero evidence. Raw AWS responses are intentionally not displayed to users.

## 8. Testing

Run:

```bash
python -m pytest -q
```

The production-hardening milestone adds regression coverage for:

- ALB Sum versus Average aggregation semantics.
- Multi-page `GetMetricData` responses.
- Existing invalid-window validation.
- Analysis-only output mode.

The AWS API reliability milestone adds tests for:

- Standard bounded retry configuration.
- Throttling classification.
- Access-denied classification.
- Not-found and validation classification.
- Transport-error classification.
- Safe conversion of AWS failures into application errors.
- Dashboard-safe messages without raw service details.

The reporting milestone also covers JSON/CSV/Markdown export, validation evidence requirements, observed cost deltas, and export-bundle integrity. Existing tests continue to cover metric query construction, review signals, missing-data handling, and dashboard source wiring.

## 9. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. The repository's AWS policy is observation-only and contains no EC2/RDS/EBS/ELB mutation actions. Error messages shown to dashboard users must not expose raw AWS responses, request identifiers, credentials, or other sensitive service details.

## 10. Recommendation Lifecycle

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

## 11. Current Milestones

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
12. AWS API reliability and error handling — in progress.
