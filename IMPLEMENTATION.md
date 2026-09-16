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
Report / Validation
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

The implementation presents these as raw/aggregated operational evidence. It does not convert traffic volume into fabricated pricing or savings estimates.

## 4. ALB Review Rules

Default review signals are explicit and configurable:

- Average request count below 1 per metric period → `low-request-activity-review`.
- Average processed bytes at/above 1 GB per metric period → `high-processed-bytes-review`.
- Average target response time at/above 1 second → `high-target-response-time-review`.
- Load balancer state other than active → `non-active-load-balancer-review`.

These are investigation signals only. A human must verify traffic patterns, application behavior, target health, architecture requirements, and current AWS pricing before making a change.

## 5. Missing Data Semantics

Missing CloudWatch metrics are represented as unavailable. They are never converted to zero because zero and missing are materially different operational states.

## 6. Dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The dashboard provides separate EC2, RDS, EBS, and ALB intelligence pages. The ALB page shows aggregate ELB Cost Explorer spend alongside load balancer inventory and CloudWatch traffic evidence, without pretending that service-level spend is per-load-balancer spend.

## 7. Testing

Run:

```bash
python -m pytest -q
```

Tests cover metric query construction, aggregation, review signals, missing-data handling, and dashboard source wiring.

## 8. Security

Never store AWS access keys in source code. Use the standard boto3 credential chain or IAM roles. The repository's AWS policy is observation-only and contains no EC2/RDS/EBS/ELB mutation actions.

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
7. RDS CloudWatch cost/utilization intelligence — complete.
8. EBS capacity and I/O intelligence — complete.
9. ALB and data-transfer investigation — current milestone.
10. FinOps reports, exports, and validation workflows.
