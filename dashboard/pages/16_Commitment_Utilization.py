import streamlit as st

from src.finops_commitment_utilization import CommitmentUtilizationEvidence, aggregate_utilization

st.set_page_config(page_title="Commitment Utilization", layout="wide")
st.title("Commitment Utilization Intelligence")
st.caption("Evidence-driven utilization review for Savings Plans and Reserved Instances. Analysis-only.")

records = [
    CommitmentUtilizationEvidence("2026-07", "savings-plan", 1000.0, 820.0),
    CommitmentUtilizationEvidence("2026-07", "reserved-instance", 900.0, 430.0),
    CommitmentUtilizationEvidence("2026-08", "savings-plan", 1000.0, 610.0),
]

st.info("Demo values are synthetic. They are not AWS commitment utilization measurements.")
st.dataframe(aggregate_utilization(records), use_container_width=True)
st.warning("Unused commitment value is calculated only from supplied evidence. The platform does not purchase, modify, cancel, or resize commitments.")
