from src.finops_unit_economics import UnitEconomicsEvidence, aggregate_unit_economics, cost_per_unit, unit_economics_review_flags


def test_cost_per_unit():
    assert cost_per_unit(UnitEconomicsEvidence("2026-08", "api", 100.0, 1000, "requests")) == 0.1


def test_zero_units_are_unavailable():
    r = UnitEconomicsEvidence("2026-08", "api", 100.0, 0, "requests")
    assert cost_per_unit(r) is None
    assert unit_economics_review_flags(r) == ["unit-volume-unavailable"]


def test_aggregation():
    rows = aggregate_unit_economics([
        UnitEconomicsEvidence("2026-08", "api", 60.0, 600, "requests"),
        UnitEconomicsEvidence("2026-08", "api", 40.0, 400, "requests"),
    ])
    assert rows[0]["cost"] == 100.0
    assert rows[0]["units"] == 1000
    assert rows[0]["cost_per_unit"] == 0.1


def test_negative_values_rejected():
    try:
        UnitEconomicsEvidence("2026-08", "api", -1.0, 100, "requests")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_required_dimensions():
    for workload, unit in [("", "requests"), ("api", "")]:
        try:
            UnitEconomicsEvidence("2026-08", workload, 1.0, 1, unit)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
