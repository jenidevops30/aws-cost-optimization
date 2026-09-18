from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finops_unit_economics_trend import unit_cost_trend

st.set_page_config(page_title="FinOps Unit Economics Trends", layout="wide")
st.title("FinOps Unit Economics Trends")
st.caption("Descriptive period-over-period workload cost analysis.")

records = [
    {"period": "2026-06", "workload": "production-api", "unit_name": "requests", "cost": 120.0, "units": 1_000_000},
    {"period": "2026-07", "workload": "production-api", "unit_name": "requests", "cost": 126.0, "units": 1_200_000},
    {"period": "2026-08", "workload": "production-api", "unit_name": "requests", "cost": 132.0, "units": 1_500_000},
]
st.info("Synthetic evidence only. A unit-cost change is descriptive and is not proof of causality or a savings forecast.")
st.dataframe(pd.DataFrame(unit_cost_trend(records)), use_container_width=True)
