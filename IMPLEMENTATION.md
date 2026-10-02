# AWS Cost Optimization & FinOps — Implementation

## Prerequisites

- The user wants me to build a portfolio project based on AWS cost optimization. I need to create the project structure and files according to the master implementation prompt. I've already created the directory structure and the three required Markdown files: README.md, PROJECT.md, and IMPLEMENTATION.md. I need to make sure all the requirements are met. Let me review what I've done so far and what's still needed:

- Python 3.8+
- AWS CLI configured with appropriate permissions
- Python packages: pandas, numpy, matplotlib, seaborn

## Repository Setup

```bash
git clone <repository-url>
cd aws-cost-optimization
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib seaborn
```

## Billing Data Collection

Monthly AWS billing CSV files should be placed in `data/raw/`. Expected filenames:

- dec-costs.csv
- Jan-costs.csv
- Feb-costs.csv
- Mar-costs.csv
- Apr-costs.csv
- May-costs.csv
- Jun-costs.csv
- July-costs.csv

August 2026 monthly billing total also available as verified invoice value.

## Raw Data Handling

Raw billing data is immutable source evidence. Do not modify raw input files. Create normalized/processed datasets separately in `data/processed/`.

Example raw CSV column structure:

- LineItem/UsageType
- LineItem/UnblendedCost
- LineItem/UsageType
- UsageType/Description
- Usage/AvailabilityZone
- Usage/InstanceType
- Usage/Operation
- Billing/Month

## Data Normalization

Normalize column names for consistent processing. Handle missing columns gracefully. Map AWS billing column names to standardized names.

Example normalization mapping:

- UnblendedCost → cost
- UsageType → usage_type
- InstanceType → instance_type
- Month → billing_month

## Python Analysis

Create and run `scripts/analyze_costs.py`:

```bash
python scripts/analyze_costs.py
```

The script will:

1. Discover monthly CSV files
2. Read the billing data
3. Normalize column names
4. Handle missing columns gracefully
5. Aggregate costs by month
6. Aggregate costs by category/service
7. Calculate absolute change and percentage change
8. Generate processed CSV files
9. Generate machine-readable JSON if useful
10. Never modify raw input data

## Monthly Cost Calculation

Calculate monthly totals from CSV data. Verify against authoritative baseline:

- December 2025: $813.43
- January 2026: $762.62
- February 2026: $500.50
- March 2026: $481.71
- April 2026: $467.80
- May 2026: $372.32
- June 2026: $327.07
- July 2026: $327.73
- August 2026: $357.36

If derived subtotals differ from authoritative baseline, the verified invoice totals remain the authoritative baseline.

## Category Comparison

Aggregate costs by category/service and compare month-over-month and before/after optimization.

Expected output files:

- `analysis/monthly-cost-summary.csv`
- `analysis/category-comparison.csv`
- `analysis/optimization-candidates.csv`

## Cost Driver Identification

Identify major cost drivers by comparing category costs across months. Key categories to analyze:

- EC2 Instances
- RDS
- ELB
- VPC
- EC2 Other
- Data Transfer

Only discuss categories supported by evidence.

## EC2 Investigation

Investigate EC2 cost drivers:

1. Read EC2 category data from CSV
2. Analyze instance types and usage
3. Identify rightsizing opportunities
4. Evaluate ARM64/Graviton migration opportunities
5. Validate performance after changes

Key finding: EC2 Instances reduced from $244.96 (Dec 2025) to $115.56 (Jun 2026), -$129.40 change.

## RDS Investigation

Investigate RDS cost drivers:

1. Read RDS category data from CSV
2. Analyze current instance sizing
3. Evaluate right-sizing opportunities
4. Validate capacity requirements

Key finding: RDS costs reduced from $205.05 (Dec 2025) to $79.72 (Jun 2026), -$125.33 change.

Do not fabricate the previous/current RDS instance class. If metrics are unavailable: "Utilization data not available in the current evidence."

## Network Investigation

Analyze:

- Data transfer costs
- ELB costs
- VPC costs
- EC2 Other network costs

Investigate possible causes without automatic assumptions. Cross-AZ traffic was evaluated as a potential contributor, but only confirmed if AWS evidence proves it.

## AWS Resource Correlation

Where AWS credentials are available, inspect current resources read-only using AWS CLI/API to correlate:

- Billing → resource → instance type → utilization → optimization opportunity

Investigate: EC2, RDS, ELB, VPC, CloudWatch

DO NOT modify AWS resources automatically. The analysis tool must be READ-ONLY unless the user explicitly requests a change in a separate step.

Never:

- terminate instances
- stop instances
- resize instances
- modify RDS
- modify networking
- delete resources
- modify billing configuration

## Evidence Collection

Collect and verify all evidence:

- AWS invoice totals
- Billing CSV data
- Cost category analysis
- Optimization decision evidence
- Validation results

Store evidence in `evidence/` directory:

- `evidence/baseline/` - baseline cost data
- `evidence/ec2/` - EC2 optimization evidence
- `evidence/rds/` - RDS optimization evidence
- `evidence/networking/` - network cost analysis
- `evidence/results/` - optimization results

Sanitize public evidence: remove credentials, secrets, unnecessary IP addresses, account IDs where unnecessary, internal company information, customer information.

## Cost Monitoring

Set up cost monitoring using:

- AWS Budgets
- Cost Explorer
- CloudWatch metrics
- Monthly cost reviews

## FinOps Controls

Document implemented FinOps controls and recommendations:

- Budgets: [Implemented/Recommendation]
- Cost monitoring: [Implemented/Recommendation]
- Cost anomaly detection: [Implemented/Recommendation]
- Resource tagging: [Implemented/Recommendation]
- Rightsizing reviews: [Implemented/Recommendation]
- Idle-resource reviews: [Implemented/Recommendation]
- Monthly cost reviews: [Implemented/Recommendation]

Only mark controls as implemented if actually implemented. Otherwise classify as recommendations.

## Security

Never store:

- AWS access keys
- AWS secret keys
- passwords
- API tokens
- private keys
- database credentials

in Git.

Add to .gitignore:

```
.env
.env.*
*.pem
*.key
*.tfstate
*.tfstate.*
.terraform/
node_modules/
```

Use IAM roles where possible. If AWS access is required for analysis, prefer temporary credentials or IAM roles.

## Cleanup

Remove any temporary resources, temporary analysis files, or temporary configurations that are not part of the permanent project structure.

## Troubleshooting

Common issues:

- CSV column name mismatches: Normalize column names before analysis
- Missing monthly data: Verify CSV files cover expected date range
- Category mapping discrepancies: Verify category mapping between AWS Bills UI and cost category exports
- Discrepancies with authoritative totals: Verified invoice totals remain authoritative

## Python Analysis Script: scripts/analyze_costs.py

The main analysis script that:

1. Discovers monthly CSV files from data/raw/
2. Reads and normalizes billing data
3. Aggregates costs by month and category
4. Calculates absolute and percentage changes
5. Generates processed output files
6. Never modifies raw input data

The script uses pandas for data manipulation and is documented with comments.
