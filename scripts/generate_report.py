from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.cost_engine import load_csv, month_over_month, service_totals
from src.reporting import build_finops_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a FinOps JSON report")
    parser.add_argument("csv_file")
    parser.add_argument("--output", default="finops-report.json")
    args = parser.parse_args()

    records = load_csv(args.csv_file)
    report = build_finops_report(
        monthly=month_over_month(records),
        service_totals=service_totals(records),
    )
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
