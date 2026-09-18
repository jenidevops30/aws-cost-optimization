from __future__ import annotations
import pandas as pd
import streamlit as st
from src.finops_unit_economics_governance import UnitEconomicsGovernanceEvidence, governance_rows, governance_summary
st.set_page_config(page_title="FinOps Unit Economics Governance",layout="wide")
st.title("FinOps Unit Economics Governance")
st.caption("Governance view combining forecast validation and anomaly review signals.")
records=[
 UnitEconomicsGovernanceEvidence("2026-06","production-api",0.000120,0.000118),
 UnitEconomicsGovernanceEvidence("2026-07","production-api",0.000105,0.000118,True),
 UnitEconomicsGovernanceEvidence("2026-08","production-api",None,0.000110),
]
summary=governance_summary(records)
c1,c2,c3=st.columns(3)
c1.metric("Records",summary["records"]); c2.metric("Unavailable",summary["unavailable"]); c3.metric("Anomaly reviews",summary["anomaly_reviews"])
st.info("Synthetic evidence only. Governance status is a review aid; it does not recommend remediation or claim causality.")
st.dataframe(pd.DataFrame(governance_rows(records)),use_container_width=True)
