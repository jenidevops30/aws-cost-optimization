from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class ComplianceCheck:
    name: str
    status: str
    detail: str


_SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*[^\s]+"),
    re.compile(r"(?i)(password|token|secret)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
_EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}


def scan_text_for_secrets(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)
    return findings


def scan_repository(root: str | Path) -> list[ComplianceCheck]:
    base = Path(root)
    checks: list[ComplianceCheck] = []
    secret_files = 0
    scanned = 0
    for path in base.rglob("*"):
        if not path.is_file() or any(part in _EXCLUDED for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".env", ".md", ".txt", ".dockerfile"} and path.name != "Dockerfile":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        if scan_text_for_secrets(text):
            secret_files += 1
    checks.append(ComplianceCheck("secret-pattern-scan", "ready" if secret_files == 0 else "failed", f"scanned={scanned}; findings={secret_files}"))

    dockerignore = base / "deployment" / ".dockerignore"
    required = {".env", "*.pem", ".git", "__pycache__"}
    if dockerignore.exists():
        lines = {line.strip() for line in dockerignore.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}
        missing = sorted(required - lines)
        checks.append(ComplianceCheck("docker-build-context", "ready" if not missing else "failed", "required exclusions present" if not missing else f"missing={','.join(missing)}"))
    else:
        checks.append(ComplianceCheck("docker-build-context", "failed", "deployment/.dockerignore is missing"))

    policy = base / "security" / "readonly-policy.json"
    checks.append(ComplianceCheck("readonly-policy", "ready" if policy.exists() else "failed", "read-only IAM policy file present" if policy.exists() else "read-only IAM policy file missing"))
    return checks


def compliance_ready(checks: list[ComplianceCheck]) -> bool:
    return all(check.status == "ready" for check in checks)
