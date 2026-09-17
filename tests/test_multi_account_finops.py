from src.multi_account_finops import AccountCostRecord, account_mom, account_service_totals, account_totals, validate_account_id


def records():
    return [
        AccountCostRecord("2026-05", "111111111111", "Production", "EC2", "us-east-1", 100.0),
        AccountCostRecord("2026-05", "111111111111", "Production", "RDS", "us-east-1", 50.0),
        AccountCostRecord("2026-06", "111111111111", "Production", "EC2", "us-east-1", 120.0),
        AccountCostRecord("2026-06", "222222222222", "Staging", "EC2", "us-east-1", 25.0),
    ]


def test_account_totals_are_grouped_and_sorted():
    assert account_totals(records()) == {"111111111111": 270.0, "222222222222": 25.0}


def test_account_service_totals_preserve_account_boundary():
    totals = account_service_totals(records())
    assert totals[("111111111111", "EC2")] == 220.0
    assert totals[("111111111111", "RDS")] == 50.0
    assert totals[("222222222222", "EC2")] == 25.0


def test_account_mom_calculates_change():
    rows = account_mom(records())
    june = next(row for row in rows if row["account_id"] == "111111111111" and row["period"] == "2026-06")
    assert june["cost"] == 120.0
    assert june["change"] == -30.0
    assert june["change_pct"] == -20.0


def test_account_id_validation():
    assert validate_account_id("123456789012")
    assert not validate_account_id("1234")
    assert not validate_account_id("abcdefghijkl")
