# AWS Cost Optimization & FinOps — Project Specification

## Purpose

Provide a reproducible, local-first workflow for analyzing AWS billing CSV exports, comparing monthly spend, identifying supported service-level cost drivers, and documenting optimization decisions using the FinOps INFORM → OPTIMIZE → OPERATE lifecycle.

The analysis workflow is read-only with respect to AWS: it reads local files and writes local reports. The separate evidence-export script calls read-only AWS APIs, but it is optional and is not part of local validation.

## Reported case-study result

The current narrative records monthly spend decreasing from $813.43 in December 2025 to $327.07 in June 2026, a reported reduction of $486.36/month (about 59.8%). These are reference figures, not independently verified results. The generated reconciliation output must be checked against raw source exports and invoices before these values are described as confirmed savings.

## Goals

- Parse local monthly billing CSV files without modifying the raw inputs.
- Normalize known AWS billing column shapes, including duplicate usage-type headers in the current sample files.
- Calculate monthly totals from observed cost rows.
- Compare measured totals with recorded invoice reference values without overwriting the measurements.
- Aggregate selected categories from observed service labels.
- Produce CSV and JSON reports that can be regenerated locally.
- Make tests and basic Python compilation part of automated quality checks.
- Keep AWS resource changes outside this project workflow.

## Non-goals

- Automatically stopping, terminating, resizing, or deleting AWS resources.
- Modifying RDS, load balancers, networking, IAM, budgets, or billing configuration.
- Treating estimated Cost Explorer values as final invoice totals.
- Claiming performance, availability, or savings outcomes without traceable supporting evidence.

## Current implementation status

| Area | Status | Notes |
|---|---|---|
| Local CSV analysis | Implemented; under validation | Reconciliation discrepancies must be investigated |
| Monthly baseline comparison | Implemented | Measured values remain separate from reference totals |
| Category aggregation | Implemented for selected service labels | Coverage depends on source CSV labels |
| Unit tests | Added | Must pass locally and in CI |
| Continuous integration | Added | Runs tests and Python compilation; no AWS credentials |
| Dynamic charts | Not complete | Chart script still embeds values instead of consuming analysis outputs |
| Evidence sanitization | Not complete | Review public resource identifiers and metadata |
| Claim-by-claim verification | Not complete | Resource snapshots alone do not prove historical migrations or performance changes |
| Automated remediation | Out of scope | No resource-changing actions are implemented |

## Data sources and integrity

Raw files live under data/raw/. They should be treated as immutable inputs. Derived reports are written under data/processed/ and analysis/.

The current CSVs contain duplicate LineItem/UsageType headers and incomplete trailing fields. The parser accommodates the known header shape and derives the billing month from the filename. Corrected source exports should be preferred when available; the parser workaround is not a substitute for data-quality remediation.

The stored Cost Explorer response covers May through September 2026 and marks September as estimated. The September raw CSV does not reconcile to that estimate, so September is not included in the authoritative baseline mapping.

## Reported cost reference values

| Month | Reference spend (USD) |
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

These values are comparison inputs. The local analysis must report its own calculated totals and any differences.

## Reported optimization hypotheses

The case-study narrative describes EC2 Graviton migration, RDS rightsizing, load-balancer consolidation, network-cost changes, and cleanup of idle resources. Before publishing these as verified outcomes, attach and review the relevant before/after billing exports, resource configuration evidence, performance metrics, and change/rollback records.

Current resource snapshots show selected resource metadata at one point in time. They do not by themselves prove what resources existed before an optimization or demonstrate that a migration caused a specific savings or latency improvement.

## Local acceptance criteria

- A fresh environment can install requirements-dev.txt.
- Unit tests pass without AWS credentials.
- Python sources compile.
- Analysis runs using local CSV files only.
- Raw input files remain unchanged.
- Monthly totals are derived from the CSV data.
- Reconciliation differences are explicit and are not silently replaced.
- Months without an authoritative baseline are marked not comparable.
- Generated JSON is valid and generated reports are reproducible.
- Public evidence is reviewed for unnecessary resource identifiers and internal metadata.
- Case-study claims are labelled reported until the source evidence supports verification.

## Safety and release policy

No AWS resource modifications are permitted as part of this project. The optional evidence exporter must remain read-only and must not be run in the local-only test workflow. Any future resource-changing automation would require a separate design, explicit approval, least-privilege permissions, a dry-run path, and a documented rollback plan.
