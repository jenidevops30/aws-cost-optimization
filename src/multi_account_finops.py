from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class AccountCostRecord:
    billing_period: str
    account_id: str
    account_name: str
    service: str
    region: str
    cost: float
    currency: str = "USD"


def account_totals(records: list[AccountCostRecord]) -> dict[str, float]:
    totals: defaultdict[str, float] = defaultdict(float)
    for record in records:
        totals[record.account_id] += record.cost
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def account_period_totals(records: list[AccountCostRecord]) -> dict[tuple[str, str], float]:
    totals: defaultdict[tuple[str, str], float] = defaultdict(float)
    for record in records:
        totals[(record.account_id, record.billing_period)] += record.cost
    return dict(totals)


def account_service_totals(records: list[AccountCostRecord]) -> dict[tuple[str, str], float]:
    totals: defaultdict[tuple[str, str], float] = defaultdict(float)
    for record in records:
        totals[(record.account_id, record.service)] += record.cost
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def account_mom(records: list[AccountCostRecord]) -> list[dict[str, float | str | None]]:
    periods = account_period_totals(records)
    accounts = {record.account_id: record.account_name for record in records}
    result: list[dict[str, float | str | None]] = []
    for account_id in sorted(accounts):
        account_periods = sorted(period for aid, period in periods if aid == account_id)
        previous = None
        for period in account_periods:
            current = periods[(account_id, period)]
            change = None if previous is None else current - previous
            percent = None if previous in (None, 0) else (change / previous) * 100
            result.append({"account_id": account_id, "account_name": accounts[account_id], "period": period, "cost": current, "change": change, "change_pct": percent})
            previous = current
    return result


def validate_account_id(account_id: str) -> bool:
    return account_id.isdigit() and len(account_id) == 12
