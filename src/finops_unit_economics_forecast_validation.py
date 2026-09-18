from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class UnitEconomicsForecastValidation:
    period: str
    workload: str
    observed_unit_cost: float | None
    forecast_unit_cost: float | None

    def __post_init__(self) -> None:
        if not self.period.strip() or not self.workload.strip():
            raise ValueError("period and workload are required")
        if self.observed_unit_cost is not None and self.observed_unit_cost < 0:
            raise ValueError("observed_unit_cost must be non-negative")
        if self.forecast_unit_cost is not None and self.forecast_unit_cost < 0:
            raise ValueError("forecast_unit_cost must be non-negative")

def validate_forecast_rows(records: Iterable[UnitEconomicsForecastValidation]) -> list[dict[str, object]]:
    rows=[]
    for r in sorted(records,key=lambda x:(x.period,x.workload)):
        if r.observed_unit_cost is None or r.forecast_unit_cost is None:
            status="unavailable"
            error=None
        else:
            error=r.observed_unit_cost-r.forecast_unit_cost
            status="available"
        rows.append({"period":r.period,"workload":r.workload,"observed_unit_cost":r.observed_unit_cost,"forecast_unit_cost":r.forecast_unit_cost,"forecast_error":error,"validation_status":status})
    return rows

def mean_absolute_error(records: Iterable[UnitEconomicsForecastValidation]) -> float | None:
    errors=[abs(r.observed_unit_cost-r.forecast_unit_cost) for r in records if r.observed_unit_cost is not None and r.forecast_unit_cost is not None]
    return None if not errors else sum(errors)/len(errors)
