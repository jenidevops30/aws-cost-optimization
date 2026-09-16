from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from src.aws_cost_explorer import get_service_costs


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AWS Cost Explorer service costs")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD")
    parser.add_argument("--output", default="aws-cost-explorer.csv")
    args = parser.parse_args()

    records = get_service_costs(date.fromisoformat(args.start), date.fromisoformat(args.end))
    output = Path(args.output)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["billing_period", "service", "usage_type", "region", "cost", "currency", "source"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "billing_period": record.billing_period,
                    "service": record.service,
                    "usage_type": "SERVICE",
                    "region": record.region,
                    "cost": f"{record.cost:.8f}",
                    "currency": record.currency,
                    "source": record.source,
                }
            )
    print(f"Exported {len(records)} Cost Explorer records to {output}")


if __name__ == "__main__":
    main()
