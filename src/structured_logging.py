from __future__ import annotations

import json
import logging
import re

_SECRET = re.compile(r"(?i)(aws_access_key_id|aws_secret_access_key|aws_session_token|authorization|token|password|secret|private_key)\s*[:=]\s*[^,\s]+")


class RedactedJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = _SECRET.sub(r"\1=[REDACTED]", record.getMessage())
        payload = {"level": record.levelname, "logger": record.name, "message": message}
        return json.dumps(payload, separators=(",", ":"))


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(RedactedJsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
