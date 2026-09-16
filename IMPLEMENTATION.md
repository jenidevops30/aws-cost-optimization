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
CloudWatch Utilization Evidence
        ↓
Review Signals
        ↓
Human Review
        ↓
Report / Validation
```

## 3. AWS Read-Only Sources

### Cost Explorer

- Service-level monthly cost through `GetCostAndUsage`.
- EC2 resource-level cost through `GetCostAndUsageWithResources` when AWS returns resource IDs.
- RDS is intentionally kept at service-level cost in the current milestone; the implementation does not manufacture per-database allocation.

### EC2

`DescribeInstances` supplies inventory. CloudWatch `GetMetricData` supplies CPU and network evidence.

### RDS

`DescribeDBInstances` supplies:

- DB identifier
- instance class
- engine
- status
- Multi-AZ state
- allocated storage

CloudWatch `GetMetricData` supplies:

- `CPUUtilization`
- `DatabaseConnections`
- `FreeStorageSpace`
- `ReadIOPS`
- `WriteIOPS`

## 4. RDS Review Rules

Default review thresholds are explicit and configurable:

- Average CPU below 10% → `low-average-cpu-review`.
- Average CPU at/above 80% → `high-average-cpu`.
- Peak CPU at/above 80% → `high-peak-cpu`.
- Average free storage below 20 GiB → `low-free-storage-review`.
- Average free storage below 20% of allocated storage → `low-free-storage-percent-review`.

These thresholds create review signals only. They do not estimate savings, recommend a specific DB class, or modify RDS.

## 5. Missing Data Semantics

A missing CloudWatch metric is represented as unavailable. It is never converted to zero because zero and missing are materially different operational states.

## 6. Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The dashboard provides separate EC2 and RDS intelligence pages. The RDS page shows aggregate Cost Explorer spend alongside DB inventory and utilization evidence, without pretending that service-level spend is per-instance spend.

## 7. Testing

Run:

```bash
python -m pytest -q
```

Tests cover metric query construction, aggregation, review signals, missing-data handling, and dashboard source wiring.

## 8. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. The repository's AWS policy is observation-only and contains no EC2/RDS mutation actions.

## 9. Recommendation Lifecycle

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
```

## 10. Current Milestones

1. CSV ingestion and normalization — complete.
2. Cost-analysis API/CLI — complete.
3. Dashboard — complete.
4. Anomaly detection — complete.
5. EC2 resource-level investigation — complete.
6. EC2 CloudWatch utilization intelligence — complete.
7. RDS CloudWatch cost/utilization intelligence — current milestone.
8. EBS capacity and I/O intelligence.
9. ALB and data-transfer investigation.
10. FinOps reports, exports, and validation workflows.
