from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finops_commitment_trend import (
    CommitmentTrendEvidence,
    commitment_trend,
    coverage_utilization_gap,
    trend_review_flags,
)

st.set_page_config(page_title="Commitment Trend & Correlation", layout="wide")
st.title("FinOps Commitment Trend & Correlation")
st.caption("Evidence-preserving trend analysis for commitment coverage and utilization.")

records = [
    CommitmentTrendEvidence("2026-06", "savings-plan", 120, 78, 100, 62),
    CommitmentTrendEvidence("2026-07", "savings-plan", 125, 92, 100, 70),
    CommitmentTrendEvidence("2026-08", "savings-plan", 130, 104, 100, 82),
    CommitmentTrendEvidence("2026-06", "reserved-instance", 80, 48, 70, 31),
    CommitmentTrendEvidence("2026-07", "reserved-instance", 82, 55, 70, 38),
    CommitmentTrendEvidence("2026-08", "reserved-instance", 84, 63, 70, 49),
]

st.info(
    "Demo evidence only. Coverage and utilization are separate measures. "
    "The platform does not estimate savings or recommend purchasing commitments."
)

rows = commitment_trend(records)
st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.subheader("Coverage vs utilization")
for record in records:
    gap = coverage_utilization_gap(record)
    flags = trend_review_flags(record)
    st.write(
        f"{record.period} · {record.commitment_type}: "
        f"gap={gap:.1f} percentage points" if gap is not None
        else f"{record.period} · {record.commitment_type}: gap unavailable"
    )
    if flags:
        st.warning(", ".join(flags))
