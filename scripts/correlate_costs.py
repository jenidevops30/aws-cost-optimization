from __future__ import annotations

import argparse
import json

from src.aws_readonly import get_readonly_summary
from src.correlation import correlate_costs_to_inventory
from src.cost_engine import load_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Correlate billing totals with AWS inventory")
    parser.add_argument("csv_file")
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    records = load_csv(args.csv_file)
    inventory = get_readonly_summary(args.region)
    result = correlate_costs_to_inventory(records, inventory["ec2"], inventory["rds"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
