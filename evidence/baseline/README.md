# Baseline Cost Evidence and Reconciliation

## Status

The figures below are the case-study's recorded monthly reference totals. They are not considered fully reconciled until the local analysis output matches the corresponding source export or invoice within the documented rounding tolerance.

The analysis script does not replace calculated CSV totals with these reference values. See the generated [monthly reconciliation report](../../data/processed/monthly-cost-summary.csv) after running the local workflow.

## Recorded monthly reference totals

| Month | Reference spend (USD) | Notes |
|---|---:|---|
| December 2025 | $813.43 | Baseline reference |
| January 2026 | $762.62 | Reference |
| February 2026 | $500.50 | Reference |
| March 2026 | $481.71 | Reference |
| April 2026 | $467.80 | Reference |
| May 2026 | $372.32 | Reference |
| June 2026 | $327.07 | Optimized-period reference |
| July 2026 | $327.73 | Reference |
| August 2026 | $357.36 | Reference |
| September 2026 | $357.45 | Estimated Cost Explorer amount; not an authoritative invoice baseline |

## Source artifacts

- [Stored Cost Explorer response](aws_ce_monthly_summary.json)
- Raw monthly CSVs: [December](../../data/raw/dec-costs.csv), [June](../../data/raw/Jun-costs.csv), [August](../../data/raw/Aug-costs.csv), [September](../../data/raw/Sep-costs.csv)
- Generated reconciliation output: [monthly-cost-summary.csv](../../data/processed/monthly-cost-summary.csv)

The stored Cost Explorer response covers May through September 2026. September is marked Estimated=true in that response. A Cost Explorer result is not a substitute for an invoice when a final invoice is available.

## Reconciliation procedure

1. Run the local analysis from the repository root.
2. Compare the calculated monthly totals with this reference ledger and the source invoice/export.
3. Investigate differences in source coverage, tax/credit treatment, billing dimensions, incomplete rows, and rounding.
4. Record the outcome and source artifact. Do not edit raw inputs or force calculated totals to match the reference ledger.

The current checked-in CSVs contain duplicate headers and incomplete trailing fields, and the September raw CSV does not reconcile to the estimated Cost Explorer total. These are known data-quality limitations that must be resolved before presenting the full savings claim as independently verified.
