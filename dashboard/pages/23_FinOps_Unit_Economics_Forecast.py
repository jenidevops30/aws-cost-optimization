from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_unit_economics_forecast import UnitEconomicsForecastEvidence, forecast_rows
st.set_page_config(page_title="FinOps Unit Economics Forecast", layout="wide")
st.title("FinOps Unit Economics Forecast")
st.caption("Simple descriptive forecast of next-period unit cost from observed history.")
records=[
 UnitEconomicsForecastEvidence("2026-06","production-api",120,1_000_000),
 UnitEconomicsForecastEvidence("2026-07","production-api",126,1_200_000),
 UnitEconomicsForecastEvidence("2026-08","production-api",132,1_500_000),
]
st.info("Synthetic evidence only. Forecasts are descriptive, not guarantees, savings estimates, or remediation recommendations.")
st.dataframe(pd.DataFrame(forecast_rows(records)), use_container_width=True)
