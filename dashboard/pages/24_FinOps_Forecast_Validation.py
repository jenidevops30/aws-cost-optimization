from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_unit_economics_forecast_validation import UnitEconomicsForecastValidation, validate_forecast_rows, mean_absolute_error
st.set_page_config(page_title="FinOps Forecast Validation",layout="wide")
st.title("FinOps Unit Economics Forecast Validation")
st.caption("Descriptive validation of observed unit cost against prior forecast evidence.")
records=[
 UnitEconomicsForecastValidation("2026-07","production-api",0.000126,0.000120),
 UnitEconomicsForecastValidation("2026-08","production-api",0.000132,0.000127),
]
st.info("Synthetic evidence only. Validation measures forecast error; it does not establish causality or guarantee future accuracy.")
st.metric("Mean absolute error", f"{mean_absolute_error(records):.8f}")
st.dataframe(pd.DataFrame(validate_forecast_rows(records)),use_container_width=True)
