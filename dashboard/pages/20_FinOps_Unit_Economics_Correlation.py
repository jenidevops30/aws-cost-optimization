from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finops_unit_economics_correlation import UnitCostCorrelationEvidence, correlation_rows

st.set_page_config(page_title="FinOps Unit Economics Correlation", layout="wide")
st.title("FinOps Unit Economics Correlation")
st.caption("Correlate unit cost with an explicitly supplied supporting signal.")

records = [
    UnitCostCorrelationEvidence("2026-06", "production-api", "requests", 120.0, 1_000_000, 62.0, "avg_cpu_pct"),
    UnitCostCorrelationEvidence("2026-07", "production-api", "requests", 126.0, 1_200_000, 68.0, "avg_cpu_pct"),
    UnitCostCorrelationEvidence("2026-08", "production-api", "requests", 132.0, 1_500_000, 71.0, "avg_cpu_pct"),
]

st.info("Demo evidence only. A supporting signal is correlation evidence, not proof of causality or an optimization recommendation.")
st.dataframe(pd.DataFrame(correlation_rows(records)), use_container_width=True)
