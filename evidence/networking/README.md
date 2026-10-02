# Evidence: Network, ELB & VPC Optimization

## Verification Overview

* **Categories Analyzed**: Elastic Load Balancing (ELB), Virtual Private Cloud (VPC), EC2-Other (EBS/EIP)
* **Status**: Verified
* **Combined Savings**: **-$112.76/month**
  * ELB: $116.88 → $46.15 (-$70.72 / -60.5%)
  * VPC: $46.42 → $24.98 (-$21.44 / -46.2%)
  * EC2 Other: $29.89 → $9.30 (-$20.60 / -68.9%)

---

## 1. Load Balancing Consolidation
* **Observation**: Multiple Application Load Balancers were provisioned for disparate microservices, each incurring base hourly charges (~$16–$22/month baseline per ALB regardless of traffic).
* **Intervention**: Consolidated microservice routes onto a unified Application Load Balancer utilizing path-based and host-based listener rules (`/api/*`, `/auth/*`, etc.).
* **Result**: Reduced ongoing hourly ALB base rates while retaining TLS termination and health-check isolation.

---

## 2. VPC & Cross-AZ Egress Reduction
* **Observation**: Unintentional cross-availability-zone communication between compute nodes and database layers caused recurring data transfer charges.
* **Intervention**:
  * Aligned compute workloads and database endpoints within primary target AZs.
  * Implemented AWS VPC Gateway Endpoints for Amazon S3, routing storage traffic privately and eliminating NAT Gateway data processing fees ($0.045/GB).

---

## 3. EC2-Other (Storage & Elastic IPs) Cleanup
* **Observation**: Orphaned EBS volumes detached after instance terminations; unattached Elastic IPs accumulating hourly non-association fees.
* **Intervention**:
  * Audited and deleted unattached `available` status EBS volumes and obsolete manual snapshots.
  * Released unattached Elastic IP addresses.

---

## 4. Verified Live AWS Evidence Artifacts

* Load Balancer export: [`aws_elbv2_loadbalancers.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/networking/aws_elbv2_loadbalancers.json)
  - Confirms single active consolidated ALB: `wishlist-alb`
* Storage & volume audit: [`aws_ec2_volumes.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/networking/aws_ec2_volumes.json)
  - Confirms 0 unattached/orphan volumes; all 4 volumes are `gp3` and `in-use`.
