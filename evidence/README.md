# Evidence Register

This directory holds supporting artifacts and notes for the AWS cost optimization case study. Evidence must support a specific claim and be safe to publish.

## Evidence status definitions

- **Reported:** recorded in project notes, but not fully reconciled to source evidence.
- **Collected:** source artifact exists, but has not completed review.
- **Reconciled:** billing period, scope, totals, and source data have been checked.
- **Verified:** a reviewer has confirmed the claim is supported by the available evidence.
- **Estimated:** a projection or estimate, not a final billed amount.

## Register

Update this table only after checking that the linked artifact exists and has been reviewed.

| Claim or metric | Period | Source artifact | Status | Reviewer / review date |
|---|---|---|---|---|
| Baseline spend $813.43 | Dec 2025 | See [baseline evidence](baseline/README.md) and source exports | Reported; reconciliation pending | Pending |
| Comparison spend $327.07 | Jun 2026 | See [baseline evidence](baseline/README.md) and source exports | Reported; reconciliation pending | Pending |
| Monthly difference $486.36 | Dec 2025 vs Jun 2026 | Derived from the two reference values above | Calculated from reported values; not independently verified | Pending |
| ~59.8% reduction | Dec 2025 vs Jun 2026 | Derived from the two reference values above | Calculated from reported values; not independently verified | Pending |
| Specific optimization attribution | Varies | Decision record plus before/after billing and workload evidence | Pending claim-by-claim review | Pending |

## Publication and privacy checklist

Before committing evidence:

- [ ] Confirm the artifact is needed to substantiate a public claim.
- [ ] Remove credentials, access tokens, secret values, account IDs, and unnecessary resource identifiers.
- [ ] Review IP addresses, hostnames, internal names, customer details, and metadata for disclosure risk.
- [ ] Record source, collection timestamp, billing period, scope, and whether the data is estimated.
- [ ] Keep sensitive originals private; publish only a sanitized copy when appropriate.
- [ ] Do not edit raw billing inputs to force a reconciliation match.
- [ ] Link each material optimization claim to a decision record and validation result.

Never treat a resource snapshot by itself as proof of a historical migration, causal attribution, or performance improvement.
