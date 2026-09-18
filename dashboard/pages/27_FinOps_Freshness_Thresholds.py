from __future__ import annotations
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from src.finops_freshness_thresholds import FreshnessEvidence, freshness_rows, freshness_summary
st.set_page_config(page_title="FinOps Freshness Thresholds", layout="wide")
st.title("FinOps Evidence Freshness Thresholds")
st.caption("Detect stale evidence using explicit dataset-specific maximum age thresholds.")
now=datetime(2026,9,1,12,0,tzinfo=timezone.utc)
records=[
 FreshnessEvidence("billing","2026-09-01T10:00:00Z",24,1200),
 FreshnessEvidence("unit-economics","2026-08-30T10:00:00Z",24,800),
]
rows=freshness_rows(records,now)
s=freshness_summary(rows)
c1,c2,c3=st.columns(3)
c1.metric("Datasets",s["datasets"]); c2.metric("Fresh",s["fresh"]); c3.metric("Stale",s["stale"])
st.info("Synthetic evidence only. Stale status is a data-quality signal, not a cost or savings conclusion.")
st.dataframe(pd.DataFrame(rows),use_container_width=True)
