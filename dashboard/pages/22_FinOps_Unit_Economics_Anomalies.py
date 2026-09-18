from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_unit_economics_anomaly import UnitEconomicsAnomalyEvidence, anomaly_rows

st.set_page_config(page_title="FinOps Unit Economics Anomalies", layout="wide")
st.title("FinOps Unit Economics Anomaly Intelligence")
st.caption("Descriptive review of unit-cost deviations from prior observed history.")
threshold=st.slider("Review threshold (%)", 0, 100, 25) / 100
records=[
 UnitEconomicsAnomalyEvidence("2026-06","production-api",120,1000000),
 UnitEconomicsAnomalyEvidence("2026-07","production-api",126,1200000),
 UnitEconomicsAnomalyEvidence("2026-08","production-api",165,1000000),
]
st.info("Synthetic evidence only. Anomaly signals are descriptive and do not establish root cause, savings, or remediation.")
st.dataframe(pd.DataFrame(anomaly_rows(records, threshold)), use_container_width=True)
