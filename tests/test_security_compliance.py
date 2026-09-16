from __future__ import annotations

import json

from security.compliance import compliance_ready, scan_repository, scan_text_for_secrets, validate_readonly_policy


def test_secret_scan_returns_pattern_ids_not_values():
    findings = scan_text_for_secrets('aws_secret_access_key = "super-secret-value-123"')
    assert findings
    assert "super-secret-value-123" not in " ".join(findings)


def test_repository_security_checks_pass():
    checks = scan_repository(".")
    assert {check.name for check in checks} == {"secret-pattern-scan", "docker-build-context", "readonly-policy"}
    assert compliance_ready(checks)


def test_readonly_policy_rejects_mutating_action(tmp_path):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"Statement": [{"Effect": "Allow", "Action": ["ec2:StopInstances"], "Resource": "*"}]}), encoding="utf-8")
    check = validate_readonly_policy(policy)
    assert check.status == "failed"


def test_readonly_policy_accepts_describe_action(tmp_path):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"Statement": [{"Effect": "Allow", "Action": ["ec2:DescribeInstances"], "Resource": "*"}]}), encoding="utf-8")
    check = validate_readonly_policy(policy)
    assert check.status == "ready"
