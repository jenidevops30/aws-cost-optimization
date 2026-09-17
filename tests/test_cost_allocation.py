from src.cost_allocation import (
    AllocationRecord,
    allocation_quality,
    allocation_totals,
    unallocated_by_dimension,
)


def records():
    return [
        AllocationRecord("2026-08", "111111111111", "EC2", 100, "ap-south-1", "prod"),
        AllocationRecord("2026-08", "111111111111", "RDS", 50, "ap-south-1", "prod"),
        AllocationRecord("2026-08", "222222222222", "EC2", 25, "ap-south-1", ""),
    ]


def test_allocation_totals_preserve_unallocated_spend():
    assert allocation_totals(records()) == {"allocated": 150.0, "unallocated": 25.0}


def test_allocation_quality_distinguishes_missing_allocation_from_zero():
    quality = allocation_quality(records())
    assert quality["record_count"] == 3
    assert quality["allocated_records"] == 2
    assert quality["unallocated_records"] == 1
    assert quality["unallocated_cost"] == 25.0
    assert quality["allocated_pct"] == 150 / 175 * 100


def test_unallocated_spend_can_be_grouped_by_dimension():
    assert unallocated_by_dimension(records(), "account_id") == {"222222222222": 25.0}


def test_unknown_dimension_is_rejected():
    try:
        unallocated_by_dimension(records(), "owner")
    except ValueError as exc:
        assert "unsupported allocation dimension" in str(exc)
    else:
        raise AssertionError("unsupported dimension must fail")
