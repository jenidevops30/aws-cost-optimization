# Evidence: EC2 Instance Optimization & Graviton Migration

## Verification Overview

* **Evidence ID**: `E-004`, `E-006`
* **Status**: Verified
* **Target Metric**: $244.96/mo (Dec 2025) → $115.56/mo (Jun 2026)
* **Monthly Savings**: **-$129.40 (-52.8%)**

---

## 1. Migration Profile: x86 to AWS Graviton2

| Dimension | Previous State (x86) | Optimized State (ARM64) |
|---|---|---|
| **Instance Type** | `c5.xlarge` | `c6g.xlarge` |
| **vCPU / Memory** | 4 vCPU / 8 GiB | 4 vCPU / 8 GiB |
| **Processor Architecture** | Intel Xeon Platinum 8000 | AWS Graviton2 (64-bit ARM) |
| **On-Demand Hourly Rate** | ~$0.170 / hr | ~$0.136 / hr (~20% lower base rate) |
| **Throughput / Efficiency** | Baseline x86 | +20-40% better price-performance |

---

## 2. Compatibility & Risk Mitigation Steps

1. **Dependency Audit**:
   - Audited application dependencies (Python runtimes, compiled C extensions, native libraries).
   - Rebuilt container images using Docker multi-platform builders (`docker buildx --platform linux/arm64`).
2. **Performance & Stress Testing**:
   - Ran automated regression suites against staging Graviton instances.
   - Evaluated p95 / p99 API latencies; observed a 14% improvement in average request latency under identical mock traffic.
3. **Cutover & Validation**:
   - Zero downtime blue/green target group switchover via Application Load Balancer.

---

## 3. Verified Live AWS Evidence Artifact

* Raw AWS CLI inventory export: [`aws_ec2_instances.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/ec2/aws_ec2_instances.json)
* **Confirmed Active Graviton Instances**:
  - `i-023d2c10e465eaa4a`: `c6g.xlarge` (`arm64`, Wishlist)
  - `i-0f60e2e9de7d869b1`: `c6g.xlarge` (`arm64`, Wishlist)
  - `i-0b3fce488ca59e42c`: `t4g.small` (`arm64`, Quickhunt-Prod)
  - `i-0b1b9f76e2772395c`: `t4g.micro` (`arm64`, Quickhunt-Dev)

---

## 4. Live Cost Explorer Historical Telemetry: `c5.xlarge` → `c6g.xlarge`

* Complete Month-by-Month Migration Export: [`aws_all_instance_types_12months.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/ec2/aws_all_instance_types_12months.json)

| Month | `c5.xlarge` (x86) Spend | `c6g.xlarge` (Graviton2) Spend | Status / Event |
|---|---|---|---|
| **Jan 2026** | **$171.87** | $72.02 | Baseline x86 in production; Graviton pilot testing |
| **Feb 2026** | **$0.00 (-100%)** | **$149.08** | **Full cutover: c5.xlarge terminated; 100% Graviton** |
| **Mar 2026** | $0.00 | $157.80 | Graviton production run |
| **Apr 2026** | $0.00 | $122.94 | Workload fine-tuning & scaling optimizations |
| **May 2026** | $0.00 | $104.48 | Secondary workload rightsizing |
| **Jun 2026** | **$0.00** | **$105.72** | **Target steady-state spend reached** |
