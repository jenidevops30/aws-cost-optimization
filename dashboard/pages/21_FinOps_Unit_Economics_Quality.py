from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_unit_economics_quality import UnitEconomicsQualityEvidence, quality_flags, quality_rows

st.set_page_config(page_title="FinOps Unit Economics Quality", layout="wide")
st.title("FinOps Unit Economics Quality")
st.caption("Validate the evidence quality behind workload cost-per-unit analysis.")
records = [
    UnitEconomicsQualityEvidence("2026-06", "production-api", "requests", 120.0, 1_000_000, "approved-telemetry"),
    UnitEconomicsQualityEvidence("2026-07", "production-api", "requests", 126.0, 1_200_000, "approved-telemetry"),
    UnitEconomicsQualityEvidence("2026-08", "production-api", "requests", 132.0, 1_500_000, "approved-telemetry"),
]
st.info("Synthetic evidence only. Quality flags identify missing evidence; they do not estimate savings or recommend changes.")
st.write("Review flags:", quality_flags(records))
st.dataframe(pd.DataFrame(quality_rows(records)), use_container_width=True)
