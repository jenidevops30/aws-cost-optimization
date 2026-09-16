# Project Case Study — AWS Billing & Cost Optimization Platform

## 1. Objective

Create an evidence-driven FinOps platform that turns AWS billing data into cost trends, cost-driver analysis, anomaly findings, infrastructure/utilization evidence, optimization review signals, savings validation, and auditable reports.

## 2. Problem

AWS bills can show that spending changed without immediately explaining which services or resources require investigation. The platform provides a repeatable workflow from spend data to evidence-backed engineering decisions.

## 3. Core Workflow

```text
Collect → Normalize → Analyze → Detect → Investigate → Correlate → Recommend → Validate → Report → Export
```

## 4. Evidence Model

Every finding should identify its evidence source and confidence:

- `VERIFIED` — directly supported by available billing or AWS evidence.
- `PARTIALLY VERIFIED` — supported by some evidence but missing a required confirmation.
- `INFERENCE — NOT DIRECTLY VERIFIED` — a plausible explanation that must not be presented as a confirmed fact.

## 5. Historical Case Study

The repository contains historical monthly billing data from December 2025 through August 2026. These figures are treated as observed billing inputs. The platform must not infer causality from a cost change without supporting infrastructure or operational evidence.

## 6. Platform Capabilities

### Billing analytics

- Monthly spend
- Month-over-month change
- Service-level spend
- Cost contribution
- Trend analysis

### AWS Cost Anomaly Detection

The platform reads AWS Cost Anomaly Detection findings through the Cost Explorer API. Each finding can include an anomaly identifier, time window, AWS-reported estimated impact, actual spend, monitor ARN, and available root-cause dimensions.

The collector handles `NextPageToken` pagination and passes AWS failures through the shared resilience layer. Root causes are preserved as evidence rather than converted into automatic recommendations. Anomaly impact is reported as AWS-returned evidence, not as a self-calculated savings estimate.

### Infrastructure investigation

- EC2 resource-level cost attribution when resource IDs are available.
- EC2 inventory correlation.
- RDS inventory correlation.
- EBS volume inventory correlation.
- ALB inventory correlation.
- CloudWatch utilization, I/O, traffic, and performance evidence.
- Explicit handling of unavailable metrics and failed API observations.

### EC2 intelligence

- CPU average/max evidence.
- Network in/out evidence.
- ARM64 review signal.
- Stopped-resource review signal.
- High-cost concentration signal.

### RDS intelligence

RDS inventory is correlated with CloudWatch evidence for CPU, connections, free storage, ReadIOPS and WriteIOPS. Review signals are investigation candidates, not automatic resizing decisions.

### EBS intelligence

EBS inventory is correlated with CloudWatch read/write operations, bytes, queue length, and idle time. Review signals include unattached volumes, low activity, high queue length, and `gp2` migration review.

### ALB & data transfer intelligence

ALB inventory is correlated with CloudWatch `RequestCount`, `ProcessedBytes`, `ActiveConnectionCount`, `NewConnectionCount`, and `TargetResponseTime`. Sum metrics are aggregated as totals; Average metrics remain arithmetic means. Review signals are investigation candidates only.

### FinOps reporting and validation

The reporting layer packages analysis into executive summaries, monthly/service totals, anomaly findings, JSON/CSV/Markdown exports, and baseline/post-optimization comparisons. A lower post-optimization period is an observed reduction, not proof of causality.

### Production hardening and AWS API reliability

The platform uses correct ALB metric aggregation and consumes CloudWatch pagination. Live AWS observations use bounded standard SDK retries, connection/read timeouts, stable failure categories, and safe dashboard messages. Missing evidence remains distinct from API failure.

### Optimization

- EC2 right-sizing review
- Graviton opportunity review
- RDS capacity review
- EBS capacity/type review
- ALB and data-transfer investigation
- Idle-resource investigation

### Validation

- Baseline capture
- Post-change measurement
- Observed cost difference
- Attribution confidence
- Optimization lifecycle tracking
- Exportable evidence for review

## 7. AWS Integration Principle

The live AWS collector uses read-only observation APIs with bounded SDK retry behavior. The platform is a decision-support system, not an autonomous infrastructure modification system.

## 8. Confidentiality

Professional production evidence must be sanitized. Proprietary application code, Terraform, account identifiers, private addresses, credentials, customer information, and internal hostnames are not part of this public repository.

## 9. Success Criteria

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
11. Can AWS Cost Anomaly Detection findings be retrieved and paginated without introducing mutation capability?

## 10. Non-Goals

- Automatic resource termination, reboot, resizing, or modification.
- Automatic infrastructure deployment.
- Publishing confidential production configuration.
- Claiming savings attribution without evidence.
- Treating missing utilization data as zero.
- Retrying validation or permission failures through custom application loops.
- Turning anomaly findings into automatic infrastructure changes.
