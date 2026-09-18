# ☁️ AWS FinOps & Cost Optimization Intelligence Platform

> Evidence-driven AWS FinOps platform for cloud cost visibility, infrastructure intelligence, forecasting, governance, and data-quality analysis.

**AWS Cost Explorer · CloudWatch · EC2 · RDS · EBS · Python · Streamlit · Docker · GitHub Actions**

## 🎯 Project Overview

Cloud infrastructure costs can grow without a clear understanding of which services, resources, usage patterns, and architectural decisions are driving spend.

This project brings AWS billing, infrastructure, and utilization evidence into a single **read-only FinOps control center** for analysis and decision support.

### What it covers

- AWS cost and service-level spend analysis
- EC2, RDS, EBS, and load-balancer intelligence
- CloudWatch utilization correlation
- Resource-level attribution when explicit resource IDs exist
- Cost allocation quality
- Multi-account cost analysis
- Savings Plan and Reserved Instance coverage/utilization
- Unit economics and unit-cost trends
- Forecasting and forecast validation
- Cost anomaly analysis
- FinOps governance
- Evidence freshness, lineage, and reconciliation
- Production health, readiness, observability, Docker hardening, CI, and security validation

## 💰 Documented Cost Optimization Outcome

Historical billing evidence documented a reduction from:

```text
December 2025     $813.43
        ↓
June 2026         $327.07

Reduction         $486.36
Reduction rate    ~59.8%
```

Additional documented changes include EC2, RDS, ELB/VPC, and Data Transfer cost reductions.

> **Evidence boundary:** The historical billing reduction is documented AWS cost-optimization evidence. The portfolio platform demonstrates the analytical and engineering workflow; it should not be interpreted as the sole cause of the historical savings.

## 🏗️ Architecture

```text
                         AWS Environment
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Cost Explorer         CloudWatch         AWS Inventory
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       Evidence Layer
                              │
                              ▼
                    Normalization Layer
                              │
                              ▼
                     FinOps Intelligence
          ┌───────────────────┼───────────────────┐
          │                   │                   │
       Cost Analysis     Utilization         Governance
          │              Correlation              │
          ├─ Allocation       │              ├─ Commitments
          ├─ Unit Economics   │              ├─ Forecasting
          ├─ Anomalies        │              └─ Data Quality
          └─ Multi-account    │
                              │
                              ▼
                    FinOps Control Center
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Dashboard     Reports      Evidence
```

## 🔎 Core Capabilities

### Cost Intelligence
- Monthly and service-level cost analysis
- Month-over-month movement
- Cost-driver analysis
- Anomaly detection
- Forecasting and forecast validation

### Infrastructure Intelligence
- EC2 inventory and architecture analysis
- RDS cost and utilization intelligence
- EBS capacity/activity intelligence
- CloudWatch CPU and network evidence
- Explicit resource-level cost attribution

### FinOps Intelligence
- Cost allocation quality
- Multi-account analysis
- Commitment coverage
- Commitment utilization
- Unit economics
- Unit-cost trends
- Governance signals
- Evidence freshness and reconciliation

## 🖥️ FinOps Control Center

The Streamlit application provides a unified interface for:

- Executive cost overview
- Service analysis
- Cost alerts and anomalies
- Forecast and savings simulations
- AWS infrastructure observation
- Evidence and control visibility

### Data modes

**Demo / CSV**
- Uses repository/sample or uploaded normalized billing data
- Performs local analysis
- Makes no AWS API calls

**AWS Cost Explorer**
- Reads live AWS Cost Explorer service-level evidence
- Uses the standard Boto3 credential chain
- Requires an explicitly authorized read-only AWS identity

## 🛠️ Technology Stack

### AWS
AWS Cost Explorer · EC2 · RDS · EBS · ELB · VPC · CloudWatch · IAM

### Application
Python · Pandas · Boto3 · Streamlit · Pytest

### DevOps
Docker · GitHub Actions

### Security & Reliability
Read-only IAM · secret-pattern scanning · dependency auditing · non-root containers · read-only filesystem support · dropped capabilities · no-new-privileges · health/readiness endpoints · Prometheus-compatible metrics

## 🔐 Security Model

The AWS-connected implementation is intentionally **analysis-only**.

- No resource creation, deletion, resizing, restart, or deployment actions
- No AWS credentials stored in source control
- Standard Boto3 credential chain
- Read-only AWS permissions
- Hardened non-root production container
- Security and dependency checks in CI
- Sensitive production evidence must be sanitized before publication

The platform does **not** claim regulatory certification.

## 🧪 Engineering Workflow

```text
Implement
   ↓
Test
   ↓
CI
   ↓
Security Validation
   ↓
Pull Request
   ↓
Manual Review
```

CI validates supported Python versions, compilation, tests, and container/security paths.

## 📊 Evidence Model

The project explicitly separates:

**Verified AWS evidence**
- Documented billing and infrastructure evidence
- Sanitized before portfolio publication

**Synthetic demonstration evidence**
- Used to demonstrate analytical capabilities where live AWS data is not required

**Analytical projections**
- Forecasts and savings simulations
- Not guarantees

**Resource-level attribution**
- Used only when the underlying billing evidence explicitly identifies resources
- Service-level cost is never artificially divided across resources

## 📁 Repository Structure

```text
aws-cost-optimization/
├── README.md
├── PROJECT.md
├── IMPLEMENTATION.md
├── src/
├── dashboard/
├── deployment/
├── security/
├── tests/
├── data/
└── .github/workflows/
```

The repository intentionally keeps three canonical Markdown documents:

- **README.md** — public project overview
- **PROJECT.md** — complete case study, architecture, evidence, decisions, and outcomes
- **IMPLEMENTATION.md** — implementation, commands, testing, and troubleshooting

## 🚀 Quick Start

```bash
git clone https://github.com/jenidevops30/aws-cost-optimization.git
cd aws-cost-optimization

python -m venv .venv
source .venv/bin/activate
pip install -r dashboard/requirements.txt

streamlit run dashboard/app.py
```

### Production container

```bash
docker build -f deployment/Dockerfile -t aws-finops-control-center .
docker run --rm -p 8501:8501 -p 8080:8080 aws-finops-control-center
```

Operational endpoints:

```text
/health
/readiness
/metrics
```

## 📌 Portfolio Positioning

This project demonstrates how a DevOps/Cloud engineer can combine **AWS infrastructure knowledge, FinOps analysis, Python automation, observability, security, Docker, and CI/CD** into a single operational decision-support platform.

It is designed to answer:

> **Where is AWS money being spent, what evidence explains the spend, what infrastructure signals can be correlated with it, and how can the findings be presented safely for human decision-making?**

## 👨‍💻 Author

**Jeni Patel**  
DevOps Engineer | AWS | Cloud Infrastructure | FinOps

- GitHub: https://github.com/jenidevops30
- Portfolio: https://jenidevops.in/

## ⚠️ Disclaimer

Production billing information must be sanitized before publication. Never commit AWS account IDs, credentials, private keys, private IPs, customer information, internal hostnames, or proprietary infrastructure code.


### Budget Governance
Budget thresholds are treated as governance evidence for cost review and alerting; this project does not automatically change AWS resources.
