from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_data_freshness_lineage import FinOpsEvidenceLineage, lineage_rows, lineage_summary
st.set_page_config(page_title="FinOps Evidence Lineage",layout="wide")
st.title("FinOps Evidence Freshness & Lineage")
st.caption("Track where FinOps evidence came from and whether the observed dataset is usable.")
records=[
 FinOpsEvidenceLineage("billing","2026-08","sanitized-csv","2026-09-01T10:00:00Z",1200),
 FinOpsEvidenceLineage("unit-economics","2026-08","approved-telemetry","2026-09-01T10:05:00Z",0,False),
]
s=lineage_summary(records)
c1,c2,c3=st.columns(3)
c1.metric("Datasets",s["datasets"]); c2.metric("Available",s["available"]); c3.metric("Review",s["review"])
st.info("Evidence lineage is descriptive. It does not infer ownership, causality, savings, or remediation.")
st.dataframe(pd.DataFrame(lineage_rows(records)),use_container_width=True)
