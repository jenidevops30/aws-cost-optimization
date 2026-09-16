# Implementation — AWS Billing & Cost Optimization Platform

## 1. Local Prototype

The first implementation is provider-independent and works from normalized CSV billing data. This makes the analysis deterministic and testable before connecting an AWS account.

## 2. Data Flow

```text
CSV
 ↓
Parser
 ↓
Normalized Cost Records
 ↓
Monthly Analysis
 ↓
Service Analysis
 ↓
Findings
```

## 3. Normalized Record

Each record uses:

- `billing_period`
- `service`
- `usage_type`
- `region`
- `cost`
- `currency`
- `source`

## 4. Run the Prototype

```bash
python cli.py data/sample-billing.csv
```

## 5. Run Tests

```bash
python -m unittest discover -s tests -v
```

## 6. Analysis Rules

The initial engine calculates:

- total spend
- monthly spend
- month-over-month absolute change
- month-over-month percentage change
- service totals
- service-level changes
- top cost contributors

It does not claim a root cause from billing data alone.

## 7. Future AWS Read-Only Collector

The AWS adapter should collect billing and resource metadata using a dedicated least-privilege read-only role. AWS access must remain optional so historical analysis works without credentials.

Suggested read-only domains:

- Billing / Cost Explorer
- EC2
- RDS
- Elastic Load Balancing
- VPC
- CloudWatch

No write permissions should be required.

## 8. Recommendation Lifecycle

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

## 9. Security

Never store AWS access keys in source code. Use environment-independent AWS credential mechanisms such as IAM roles in deployed environments. Sanitize all exported evidence before publication.

## 10. Next Implementation Milestones

1. CSV ingestion and normalization.
2. Cost-analysis API/CLI.
3. Dashboard.
4. Anomaly detection.
5. Resource-level investigation.
6. Evidence-aware recommendations.
7. Savings validation.
8. AWS read-only integration.
9. FinOps reports and exports.
