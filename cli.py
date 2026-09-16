from __future__ import annotations

import argparse

from src.cost_engine import load_csv, month_over_month, service_totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze normalized AWS billing CSV data")
    parser.add_argument("csv_file")
    args = parser.parse_args()

    records = load_csv(args.csv_file)
    print(f"Records: {len(records)}")
    print("\nMonthly totals:")
    for item in month_over_month(records):
        change = "—" if item["change"] is None else f"{item['change']:+.2f}"
        pct = "—" if item["change_pct"] is None else f"{item['change_pct']:+.1f}%"
        print(f"  {item['period']}: ${item['cost']:.2f} ({change}, {pct})")

    print("\nTop services:")
    for service, cost in list(service_totals(records).items())[:10]:
        print(f"  {service}: ${cost:.2f}")


if __name__ == "__main__":
    main()
