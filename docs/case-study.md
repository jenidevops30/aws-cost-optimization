# AWS Cost Optimization Case Study

## Executive summary

This case study records a reported reduction in monthly AWS spend from **$813.43 (December 2025)** to **$327.07 (June 2026)**.

| Metric | Recorded value |
|---|---:|
| Baseline period | December 2025 |
| Baseline monthly spend | $813.43 |
| Comparison period | June 2026 |
| Comparison monthly spend | $327.07 |
| Difference per month | $486.36 |
| Reduction relative to baseline | 59.8% |
| Annualized run-rate difference | $5,836.32 |

**Evidence status: reported, not yet independently verified.** These values are the case study's reference figures. They must not be presented as fully verified savings until source exports/invoices and the generated reconciliation outputs agree and the individual optimization claims are supported by traceable evidence.

The annualized figure is a simple run-rate illustration ($486.36 × 12), not a claim that this amount was realized over a full year.

## Problem statement

AWS spend required a structured review to understand the main cost drivers, identify optimization opportunities, and establish a repeatable method for validating financial impact without making unreviewed production changes.

## Method

The repository follows an evidence-first workflow:

1. **Measure:** preserve original billing exports and calculate totals from observed rows.
2. **Reconcile:** compare calculated totals with the reference ledger and invoice/Cost Explorer evidence for the same billing period.
3. **Attribute:** group observed spend into supported service categories; document coverage gaps.
4. **Investigate:** connect each proposed optimization to source evidence and workload context.
5. **Decide:** record options, expected impact, risks, approval, and rollback in a decision record.
6. **Validate:** compare before/after billing periods and review service performance, availability, and operational risk.
7. **Operate:** keep recurring cost review, alerts, tagging, and ownership controls documented.

## Recorded monthly trend

The current reference ledger contains these figures:

| Billing month | Reference spend (USD) |
|---|---:|
| December 2025 | $813.43 |
| January 2026 | $762.62 |
| February 2026 | $500.50 |
| March 2026 | $481.71 |
| April 2026 | $467.80 |
| May 2026 | $372.32 |
| June 2026 | $327.07 |
| July 2026 | $327.73 |
| August 2026 | $357.36 |

These are reference values, not a replacement for the totals computed from raw billing CSVs. The trend alone does not establish which change caused each movement. Billing-period coverage, taxes, credits, discounts, usage, and other changes must be considered.

## Optimization areas to investigate

The project narrative references the following areas. Treat each as a hypothesis until its evidence and impact are reconciled.

- **Compute:** instance family/size, utilization, scheduling, and applicable purchase options.
- **Database:** instance sizing, storage, I/O, connections, query performance, and availability requirements.
- **Load balancing:** number of load balancers, utilization, processed bytes, and fixed hourly charges.
- **Networking:** public IPv4, NAT/data processing, transfer, and other network line items.
- **Storage and idle resources:** unattached volumes, snapshots, and resources with no confirmed owner or workload.
- **Governance:** tags, budgets, anomaly detection, ownership, and recurring review.

Do not infer that a specific action delivered a specific dollar saving without before/after evidence and a documented calculation.

## Validation checklist

- [ ] Raw billing CSVs are preserved unchanged.
- [ ] Source billing periods and account/region scope are documented.
- [ ] Calculated totals are generated from the checked-in input data.
- [ ] Baseline differences and data-quality warnings are reviewed.
- [ ] Estimated Cost Explorer periods are clearly labelled and excluded from authoritative comparisons.
- [ ] Each material optimization has a decision record and supporting evidence.
- [ ] Workload performance and reliability were checked after changes.
- [ ] Taxes, credits, discounts, refunds, and one-time charges are accounted for consistently.
- [ ] Evidence is sanitized before publication.
- [ ] A reviewer has approved the final claim wording.

## Risks and limitations

- Current billing CSVs have known duplicate headers and incomplete trailing fields; corrected source exports should be preferred.
- The September 2026 Cost Explorer value is marked estimated and is not an authoritative invoice baseline.
- Resource snapshots describe a point in time and do not, by themselves, prove historical migrations or causation.
- The current chart script contains embedded values; charts should be generated from reconciled analysis outputs before publication.
- Monthly differences may reflect usage changes, billing adjustments, credits, taxes, or unrelated infrastructure changes—not only optimization work.

## Safe operating boundary

The local analysis and validation workflow must not create, modify, stop, resize, or delete AWS resources. The optional evidence exporter is separate and read-only. Keep production changes under a separately reviewed change process with explicit approval, testing, monitoring, and rollback instructions.

## Related documentation

- [Baseline evidence and reconciliation](../evidence/baseline/README.md)
- [Evidence register](../evidence/README.md)
- [Decision record template](decisions/README.md)
- [Implementation and operations guide](../IMPLEMENTATION.md)
