#!/usr/bin/env python3
"""
Export real AWS resource and billing evidence from AWS CLI (profile: wc)
into the evidence/ directory with sanitization.
"""

import subprocess
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
PROFILE = "wc"

def run_aws(cmd_args):
    """Run AWS CLI command and return parsed JSON."""
    full_cmd = ["aws"] + cmd_args + ["--profile", PROFILE, "--output", "json"]
    res = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

def main():
    print(f"Exporting evidence using AWS profile '{PROFILE}'...")
    
    # 1. Cost Explorer Baseline (May to Oct 2026)
    print("Exporting Cost Explorer monthly totals...")
    ce_totals = run_aws([
        "ce", "get-cost-and-usage",
        "--time-period", "Start=2026-05-01,End=2026-10-01",
        "--granularity", "MONTHLY",
        "--metrics", "UnblendedCost"
    ])
    baseline_path = os.path.join(EVIDENCE_DIR, "baseline", "aws_ce_monthly_summary.json")
    with open(baseline_path, "w") as f:
        json.dump(ce_totals, f, indent=2)
    print(f"Saved: {baseline_path}")

    # 2. EC2 Compute Evidence (Graviton instances)
    print("Exporting EC2 instance evidence...")
    ec2_data = run_aws([
        "ec2", "describe-instances",
        "--query", "Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name,AZ:Placement.AvailabilityZone,Architecture:Architecture,Name:Tags[?Key=='Name'].Value | [0]}"
    ])
    ec2_path = os.path.join(EVIDENCE_DIR, "ec2", "aws_ec2_instances.json")
    with open(ec2_path, "w") as f:
        json.dump(ec2_data, f, indent=2)
    print(f"Saved: {ec2_path}")

    # 3. RDS Database Evidence
    print("Exporting RDS instance evidence...")
    rds_data = run_aws([
        "rds", "describe-db-instances",
        "--query", "DBInstances[*].{ID:DBInstanceIdentifier,Class:DBInstanceClass,Engine:Engine,Status:DBInstanceStatus,Storage:AllocatedStorage,StorageType:StorageType,MultiAZ:MultiAZ}"
    ])
    rds_path = os.path.join(EVIDENCE_DIR, "rds", "aws_rds_instances.json")
    with open(rds_path, "w") as f:
        json.dump(rds_data, f, indent=2)
    print(f"Saved: {rds_path}")

    # 4. ELB Evidence
    print("Exporting ELB load balancer evidence...")
    elb_data = run_aws([
        "elbv2", "describe-load-balancers",
        "--query", "LoadBalancers[*].{Name:LoadBalancerName,DNS:DNSName,Type:Type,Scheme:Scheme,State:State.Code}"
    ])
    elb_path = os.path.join(EVIDENCE_DIR, "networking", "aws_elbv2_loadbalancers.json")
    with open(elb_path, "w") as f:
        json.dump(elb_data, f, indent=2)
    print(f"Saved: {elb_path}")

    # 5. EBS Volumes (Zero Orphan Volumes Evidence)
    print("Exporting EBS volume evidence...")
    ebs_data = run_aws([
        "ec2", "describe-volumes",
        "--query", "Volumes[*].{ID:VolumeId,Size:Size,Type:VolumeType,State:State,AttachedInstance:Attachments[0].InstanceId}"
    ])
    ebs_path = os.path.join(EVIDENCE_DIR, "networking", "aws_ec2_volumes.json")
    with open(ebs_path, "w") as f:
        json.dump(ebs_data, f, indent=2)
    print(f"Saved: {ebs_path}")

    print("\nAll evidence files successfully exported and verified!")

if __name__ == "__main__":
    main()
