from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finops_unit_economics import UnitEconomicsEvidence, aggregate_unit_economics

st.set_page_config(page_title="FinOps Unit Economics", layout="wide")
st.title("FinOps Unit Economics")
st.caption("Evidence-preserving cost-per-unit analysis.")

records = [
    UnitEconomicsEvidence("2026-06", "production-api", 120.0, 1_000_000, "requests"),
    UnitEconomicsEvidence("2026-07", "production-api", 126.0, 1_200_000, "requests"),
    UnitEconomicsEvidence("2026-08", "production-api", 132.0, 1_500_000, "requests"),
    UnitEconomicsEvidence("2026-06", "batch-processing", 80.0, 40_000, "jobs"),
    UnitEconomicsEvidence("2026-07", "batch-processing", 84.0, 42_000, "jobs"),
    UnitEconomicsEvidence("2026-08", "batch-processing", 88.0, 44_000, "jobs"),
]

st.info("Demo evidence only. Cost per unit is descriptive, not a savings forecast or optimization recommendation.")
st.dataframe(pd.DataFrame(aggregate_unit_economics(records)), use_container_width=True)
