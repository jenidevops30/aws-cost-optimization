# Project Case Study — AWS Billing & Cost Optimization Platform

## 1. Objective

Create an evidence-driven FinOps platform that turns AWS billing data into cost trends, cost-driver analysis, anomaly findings, optimization recommendations, and savings validation.

## 2. Problem

AWS bills can show that spending changed without immediately explaining which services or resources require investigation. The platform provides a repeatable workflow for moving from spend data to evidence-backed engineering decisions.

## 3. Core Workflow

```text
Collect → Normalize → Analyze → Detect → Investigate → Recommend → Validate → Report
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

### Investigation

- Cost-driver identification
- Resource metadata correlation
- Utilization evidence
- Anomaly detection

### Optimization

- EC2 right-sizing review
- Graviton opportunity review
- RDS capacity review
- Network/data-transfer investigation
- Idle-resource investigation

### Validation

- Baseline capture
- Post-change measurement
- Observed cost difference
- Attribution confidence
- Optimization lifecycle tracking

## 7. AWS Integration Principle

The future live AWS collector will use read-only permissions. The platform is a decision-support system, not an autonomous infrastructure modification system.

## 8. Confidentiality

Professional production evidence must be sanitized. Proprietary application code, Terraform, account identifiers, private addresses, credentials, customer information, and internal hostnames are not part of this public repository.

## 9. Success Criteria

A successful implementation can answer:

1. How much did AWS spend?
2. How did spend change over time?
3. Which services drove the change?
4. Which findings require investigation?
5. What optimization opportunities are supported by evidence?
6. Did an implemented optimization produce an observed cost change?

## 10. Non-Goals

- Automatic resource termination or resizing.
- Automatic infrastructure deployment.
- Publishing confidential production configuration.
- Claiming savings attribution without evidence.
