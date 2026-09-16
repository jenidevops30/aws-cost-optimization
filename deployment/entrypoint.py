from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading

from deployment.health_server import serve


def main() -> int:
    health_thread = threading.Thread(target=serve, name="health-server", daemon=True)
    health_thread.start()

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard/app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501",
    ]
    process = subprocess.Popen(command, env=os.environ.copy())

    def stop(_signum: int, _frame: object) -> None:
        if process.poll() is None:
            process.terminate()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
