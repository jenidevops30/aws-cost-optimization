from __future__ import annotations

import streamlit as st

from src.cost_allocation import AllocationRecord, allocation_quality, unallocated_by_dimension


st.set_page_config(page_title="Cost Allocation Quality", layout="wide")
st.title("Cost Allocation Quality")
st.caption("Read-only FinOps review of allocated versus unallocated spend")

records = [
    AllocationRecord("2026-08", "111111111111", "EC2", 120.0, "ap-south-1", "prod"),
    AllocationRecord("2026-08", "111111111111", "RDS", 80.0, "ap-south-1", "prod"),
    AllocationRecord("2026-08", "222222222222", "EC2", 45.0, "ap-south-1", ""),
    AllocationRecord("2026-08", "222222222222", "ELB", 15.0, "ap-south-1", ""),
]

st.info("Demo evidence is synthetic. Production allocation requires approved billing/tag/account evidence.")
quality = allocation_quality(records)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total cost", f"${quality['total_cost']:,.2f}")
c2.metric("Allocated cost", f"${quality['allocated_cost']:,.2f}")
c3.metric("Unallocated cost", f"${quality['unallocated_cost']:,.2f}")
c4.metric("Allocated coverage", "Unavailable" if quality["allocated_pct"] is None else f"{quality['allocated_pct']:.1f}%")

st.subheader("Unallocated spend by dimension")
dimension = st.selectbox("Dimension", ["service", "account_id", "region", "billing_period"])
breakdown = unallocated_by_dimension(records, dimension)
if breakdown:
    st.dataframe(
        [{"dimension_value": key, "unallocated_cost": value} for key, value in breakdown.items()],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("No unallocated records are present in this evidence set.")

st.subheader("Evidence quality")
st.write(
    "Allocation coverage is calculated only from an explicit allocation key. "
    "Missing allocation evidence is not treated as zero cost and is not redistributed across resources."
)
st.warning("This page does not estimate savings, infer ownership, or modify AWS resources.")
