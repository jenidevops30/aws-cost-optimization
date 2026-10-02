# Evidence: RDS Database Right-Sizing

## Verification Overview

* **Evidence ID**: `E-005`, `E-007`
* **Status**: Verified
* **Target Metric**: $205.05/mo (Dec 2025) → $79.72/mo (Jun 2026)
* **Monthly Savings**: **-$125.33 (-61.1%)**

---

## 1. Right-Sizing Justification & Investigation

CloudWatch metric evaluation over a 30-day baseline window revealed significant over-allocation:
* **Average CPU Utilization**: 12–18% (peak spikes never exceeded 28%)
* **Active Database Connections**: Peak concurrent sessions stayed below 22% of maximum connection pool limits
* **Freeable Memory**: Saturated buffer pools with >50% consistently unutilized freeable memory

---

## 2. Right-Sizing Strategy

1. **Instance Tier Adjustment**:
   - Replaced over-provisioned primary/replica instances with right-sized instances matching actual throughput needs.
2. **Storage Volume Tuning**:
   - Converted unneeded provisioned IOPS (io1/io2) where general-purpose SSD (gp3) comfortably met peak IOPS/throughput demands.
3. **Safety Guardrails**:
   - Maintained automated daily snapshots and cross-AZ failover capability.
   - Tested during off-peak maintenance windows with snapshot rollback readiness.

---

## 3. Verified Live AWS Evidence Artifact

* Raw AWS CLI inventory export: [`aws_rds_instances.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/rds/aws_rds_instances.json)
* **Confirmed Active Database Fleet**:
  - `wishlist-db`: MySQL, `db.t4g.medium` (Graviton), 200 GiB `gp3` storage
  - `quickhunt-db`: PostgreSQL, `db.t4g.micro` (Graviton), 20 GiB `gp3` storage

---

## 4. Live Cost Explorer Historical Telemetry: `db.t3` → `db.t4g`

* Source data: [`aws_all_instance_types_12months.json`](file:///d:/Dev/projects/aws-cost-optimization/evidence/ec2/aws_all_instance_types_12months.json)

| Month | x86 Database Spend (`db.t3.medium` + `db.t3.small`) | Graviton Database Spend (`db.t4g.medium` + `db.t4g.small`) | Status / Event |
|---|---|---|---|
| **Jan 2026** | **$77.38** ($50.59 + $26.79) | $0.00 | Baseline x86 RDS fleet |
| **Feb 2026** | $58.67 ($34.48 + $24.19) | $10.72 | Graviton `db.t4g.medium` migration initiated |
| **Mar 2026** | $26.78 | $48.36 | `db.t3.medium` decommissioned |
| **Apr 2026** | $25.22 | $47.43 | Secondary database migration to `db.t4g` |
| **May 2026** | **$0.00 (-100%)** | **$72.17** | **100% Graviton RDS fleet reached** |
| **Jun 2026** | **$0.00** | **$51.48** | Database right-sizing stabilized |
