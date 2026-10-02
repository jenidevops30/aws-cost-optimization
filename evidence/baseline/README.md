# Evidence: Baseline Cost Analysis

## Verification Overview

* **Evidence ID**: `E-001`, `E-002`, `E-003`
* **Status**: Verified
* **Sources**: AWS Monthly Invoices & AWS Cost Explorer CSV exports

---

## 1. Verified Monthly Spend Ledger

All values reflect verified AWS invoice totals for the observed 9-month timeframe:

| Month | Invoice Spend (USD) | MoM Change ($) | MoM Change (%) | Operating Phase |
|---|---|---|---|---|
| **December 2025** | **$813.43** | — | — | Baseline / Initial Audit |
| **January 2026** | $762.62 | -$50.81 | -6.2% | Assessment & Planning |
| **February 2026** | $500.50 | -$262.12 | -34.4% | Graviton & RDS Migration |
| **March 2026** | $481.71 | -$18.79 | -3.8% | Post-migration verification |
| **April 2026** | $467.80 | -$13.91 | -2.9% | ELB cleanup & adjustments |
| **May 2026** | $372.32 | -$95.48 | -20.4% | Secondary rightsizing phase |
| **June 2026** | **$327.07** | -$45.25 | -12.2% | **Target Spend Reached (-59.8%)** |
| **July 2026** | $327.73 | +$0.66 | +0.2% | Steady-state stability |
| **August 2026** | $357.36 | +$29.63 | +9.0% | Workload volume increase |

---

## 2. Invariant Baseline Rule
The project adheres to strict financial governance: derived CSV calculations must reconcile against verified billing statements. Raw data files reside immutably in `data/raw/`.

---

## 3. Verified Live AWS Cost Explorer Export

* Raw AWS Cost Explorer API export: [`aws_ce_monthly_summary.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/baseline/aws_ce_monthly_summary.json)
* Live monthly spend matches documented baseline to the cent:
  - May 2026: **$372.32**
  - June 2026: **$327.07**
  - July 2026: **$327.73**
  - August 2026: **$357.36**
  - September 2026: **$357.45**
