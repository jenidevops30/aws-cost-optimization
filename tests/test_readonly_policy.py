import json
from pathlib import Path


POLICY = Path(__file__).parents[1] / "security" / "readonly-policy.json"


def test_readonly_policy_has_no_mutating_actions():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    actions = [action.lower() for statement in policy["Statement"] for action in statement["Action"]]

    forbidden_prefixes = ("create", "delete", "terminate", "modify", "update", "put", "start", "stop", "reboot", "attach", "detach", "authorize", "revoke")
    assert not any(action.split(":", 1)[1].startswith(forbidden_prefixes) for action in actions)


def test_readonly_policy_contains_required_observation_permissions():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    actions = {action.lower() for statement in policy["Statement"] for action in statement["Action"]}

    assert "ce:getcostandusage" in actions
    assert "ec2:describeinstances" in actions
    assert "rds:describedbinstances" in actions
    assert "cloudwatch:getmetricdata" in actions
