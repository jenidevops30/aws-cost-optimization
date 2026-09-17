from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.observability import METRICS
from src.runtime_config import load_config
from src.runtime_health import readiness_report


class HealthHandler(BaseHTTPRequestHandler):
    server_version = "FinOpsHealth/1.0"

    def _send(self, status: int, payload: object, content_type: str = "application/json") -> None:
        body = json.dumps(payload, separators=(",", ":")).encode() if content_type == "application/json" else str(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            METRICS.increment("health_requests_total")
            self._send(200, {"status": "ok", "service": "finops-dashboard", "aws_mutations": False})
            return
        if self.path == "/readiness":
            METRICS.increment("readiness_requests_total")
            report = readiness_report(load_config())
            self._send(200 if report["status"] == "ready" else 503, report)
            return
        if self.path == "/metrics":
            self._send(200, METRICS.prometheus_text(), "text/plain; version=0.0.4")
            return
        self._send(404, {"status": "not-found"})

    def log_message(self, format: str, *args: object) -> None:
        return


def serve() -> None:
    host = os.getenv("FINOPS_HEALTH_HOST", "0.0.0.0")
    port = int(os.getenv("FINOPS_HEALTH_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    serve()
