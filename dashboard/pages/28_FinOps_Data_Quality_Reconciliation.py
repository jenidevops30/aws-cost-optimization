from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_data_quality_reconciliation import ReconciliationEvidence,reconciliation_row,reconciliation_summary
st.set_page_config(page_title="FinOps Data Reconciliation",layout="wide")
st.title("FinOps Data Quality & Reconciliation")
st.caption("Compare two explicitly identified evidence sources without assuming which source is correct.")
items=[
 ReconciliationEvidence("2026-08 billing",357.36,357.36,0.01),
 ReconciliationEvidence("2026-08 unit economics",132.0,131.5,0.25),
]
rows=[reconciliation_row(x) for x in items]
s=reconciliation_summary(rows)
c1,c2,c3=st.columns(3)
c1.metric("Dimensions",s["dimensions"]);c2.metric("Matched",s["matched"]);c3.metric("Mismatch",s["mismatch"])
st.info("Synthetic evidence only. A mismatch is a data-quality review signal; it does not establish which source is authoritative.")
st.dataframe(pd.DataFrame(rows),use_container_width=True)
