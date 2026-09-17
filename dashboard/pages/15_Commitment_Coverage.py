import streamlit as st

from src.finops_commitment import CommitmentEvidence, aggregate_commitment_coverage

st.set_page_config(page_title="Commitment Coverage", layout="wide")
st.title("Commitment Coverage Intelligence")
st.caption("Evidence-driven review of reserved-instance and savings-plan coverage. Analysis-only.")

records = [
    CommitmentEvidence("2026-07", "reserved-instance", "Amazon EC2", 1000.0, 600.0),
    CommitmentEvidence("2026-07", "savings-plan", "Amazon EC2", 800.0, 500.0),
    CommitmentEvidence("2026-08", "reserved-instance", "Amazon RDS", 700.0, 250.0),
]

st.info("Demo values are synthetic. Do not interpret them as production AWS commitment recommendations or savings estimates.")
rows = aggregate_commitment_coverage(records)
st.dataframe(rows, use_container_width=True)

st.warning("Coverage is calculated only from supplied eligible and covered-spend evidence. The platform does not purchase, modify, or cancel commitments.")
