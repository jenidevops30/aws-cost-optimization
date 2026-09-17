from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


@dataclass(frozen=True)
class ComplianceCheck:
    name: str
    status: str
    detail: str


_SECRET_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[^\s'\"]+"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE\s+KEY-----"),
    re.compile(r"(?i)(?:password|passwd|api[_-]?key|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
)
_EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}
_EXCLUDED_FILES = {"tests/test_security_compliance.py"}
_TEXT_SUFFIXES = {".py", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".env", ".md", ".txt"}

_READ_ONLY_ACTIONS = re.compile(r"^(?:ce:Get|ce:Describe|ec2:Describe|rds:Describe|elasticloadbalancing:Describe|autoscaling:Describe|cloudwatch:(?:Get|List))")
_MUTATING_TOKENS = ("Create", "Delete", "Terminate", "Modify", "Stop", "Reboot", "Start", "Update", "Put", "Attach", "Detach", "Authorize", "Revoke", "Associate", "Disassociate")


def scan_text_for_secrets(text: str) -> list[str]:
    """Return pattern identifiers only; never return matched secret values."""
    return [str(index) for index, pattern in enumerate(_SECRET_PATTERNS, start=1) if pattern.search(text)]


def _iter_text_files(base: Path):
    for path in base.rglob("*"):
        if not path.is_file() or any(part in _EXCLUDED for part in path.parts):
            continue
        if path.relative_to(base).as_posix() in _EXCLUDED_FILES:
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES and path.name != "Dockerfile":
            continue
        yield path


def validate_readonly_policy(path: str | Path) -> ComplianceCheck:
    policy_path = Path(path)
    if not policy_path.exists():
        return ComplianceCheck("readonly-policy", "failed", "read-only IAM policy file missing")
    try:
        document = json.loads(policy_path.read_text(encoding="utf-8"))
        statements = document.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        actions: list[str] = []
        for statement in statements:
            if statement.get("Effect") != "Allow":
                continue
            value = statement.get("Action", [])
            actions.extend([value] if isinstance(value, str) else value)
        invalid = [action for action in actions if not _READ_ONLY_ACTIONS.match(action) or any(token in action for token in _MUTATING_TOKENS)]
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return ComplianceCheck("readonly-policy", "failed", "policy is not valid JSON with a readable Statement/Action structure")
    return ComplianceCheck("readonly-policy", "ready" if not invalid else "failed", "all allowed actions are read-only" if not invalid else f"non-read-only actions detected={len(invalid)}")


def scan_repository(root: str | Path) -> list[ComplianceCheck]:
    base = Path(root)
    findings = 0
    scanned = 0
    for path in _iter_text_files(base):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        findings += bool(scan_text_for_secrets(text))

    checks = [
        ComplianceCheck(
            "secret-pattern-scan",
            "ready" if findings == 0 else "failed",
            f"scanned={scanned}; findings={findings}; matched values are never reported",
        )
    ]

    dockerignore = base / "deployment" / ".dockerignore"
    required = {".env", ".env.*", "*.pem", "*.key", ".git", "secrets/"}
    if dockerignore.exists():
        try:
            lines = {line.strip() for line in dockerignore.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}
            missing = sorted(required - lines)
            checks.append(ComplianceCheck("docker-build-context", "ready" if not missing else "failed", "sensitive build-context exclusions present" if not missing else f"missing={','.join(missing)}"))
        except OSError:
            checks.append(ComplianceCheck("docker-build-context", "failed", "unable to read deployment/.dockerignore"))
    else:
        checks.append(ComplianceCheck("docker-build-context", "failed", "deployment/.dockerignore is missing"))

    checks.append(validate_readonly_policy(base / "security" / "readonly-policy.json"))
    return checks


def compliance_ready(checks: list[ComplianceCheck]) -> bool:
    return bool(checks) and all(check.status == "ready" for check in checks)
