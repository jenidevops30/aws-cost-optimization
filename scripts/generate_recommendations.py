from __future__ import annotations

import argparse
import json

from src.aws_readonly import get_readonly_summary
from src.recommendations import build_recommendations


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate analysis-only FinOps candidates")
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    inventory = get_readonly_summary(args.region)
    recommendations = build_recommendations(inventory["ec2"], inventory["rds"])
    print(json.dumps(recommendations, indent=2))


if __name__ == "__main__":
    main()
