from __future__ import annotations

import argparse
import json

from src.aws_readonly import get_readonly_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect a read-only AWS inventory")
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    summary = get_readonly_summary(args.region)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
