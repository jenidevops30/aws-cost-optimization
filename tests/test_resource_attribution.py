from dataclasses import dataclass

from src.resource_attribution import attribute_resource_costs


@dataclass
class Record:
    cost: float
    resource_id: str | None = None


def test_resource_cost_is_attributed_only_with_resource_id():
    records = [Record(12.5, "i-123"), Record(7.5, None)]
    inventory = [{"instance_id": "i-123"}]

    result = attribute_resource_costs(records, inventory)

    assert result[0]["resource_id"] == "i-123"
    assert result[0]["cost"] == 12.5
    assert result[0]["inventory_match"] is True
    assert result[0]["confidence"] == "high"
    assert result[1]["resource_id"] is None
    assert result[1]["cost"] == 7.5
    assert result[1]["confidence"] == "not-attributed"


def test_unknown_resource_id_is_not_claimed_as_inventory_match():
    result = attribute_resource_costs([Record(5.0, "i-unknown")], [{"instance_id": "i-known"}])

    assert result[0]["inventory_match"] is False
    assert result[0]["confidence"] == "medium"
