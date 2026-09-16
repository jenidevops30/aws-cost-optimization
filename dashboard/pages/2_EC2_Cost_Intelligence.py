from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.aws_cost_explorer import get_ec2_resource_costs
from src.aws_readonly import get_ec2_inventory
from src.ec2_intelligence import build_ec2_cost_insights


st.set_page_config(page_title="EC2 Cost Intelligence", page_icon="🔎", layout="wide")
st.title("🔎 EC2 Cost Intelligence")
st.caption("Resource-level cost correlation with read-only EC2 inventory")

with st.sidebar:
    region = st.text_input("AWS region", value="us-east-1")
    end = date.today()
    start = st.date_input("Start date", value=end - timedelta(days=30))
    st.info("Read-only analysis. No EC2 resources are modified.")

if end <= start:
    st.error("Start date must be before today.")
    st.stop()

if not st.button("Load EC2 cost intelligence", type="primary"):
    st.info("Choose a region/date range and load resource-level Cost Explorer data.")
    st.stop()

try:
    with st.spinner("Reading EC2 resource costs and inventory…"):
        costs = get_ec2_resource_costs(start, end)
        inventory = get_ec2_inventory(region)
        rows = [
            {"resource_id": r.resource_id, "cost": r.cost, "billing_period": r.billing_period}
            for r in costs
            if r.resource_id
        ]
        insights = build_ec2_cost_insights(rows, inventory)
except Exception as exc:
    st.error("Unable to load EC2 cost intelligence.")
    st.code(str(exc))
    st.caption("Verify Cost Explorer resource-level access, region, and read-only IAM permissions.")
    st.stop()

if not rows:
    st.warning("Cost Explorer returned no EC2 resource-level records for this period. Service-level cost cannot be safely distributed across instances.")
    st.stop()

if not insights:
    st.warning("Resource-level costs were returned, but no matching EC2 inventory records were found in the selected region.")
    st.stop()

frame = pd.DataFrame([
    {
        "instance_id": item.instance_id,
        "instance_type": item.instance_type,
        "architecture": item.architecture,
        "state": item.state,
        "cost": item.cost,
        "cost_share_pct": item.monthly_share_pct,
        "signals": ", ".join(item.signals) if item.signals else "none",
        "confidence": item.confidence,
    }
    for item in insights
])

c1, c2, c3 = st.columns(3)
c1.metric("Attributed EC2 resources", len(frame))
c2.metric("Attributed cost", f"${frame['cost'].sum():,.2f}")
c3.metric("Review signals", int((frame["signals"] != "none").sum()))

st.subheader("Resource-level intelligence")
st.dataframe(
    frame.style.format({"cost": "${:,.2f}", "cost_share_pct": "{:.1f}%"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Review signals")
for signal in ["arm64-review", "stopped-resource-review", "high-cost-concentration"]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum())
    st.write(f"**{signal}** — {count} resource(s)")

st.warning(
    "Signals are review candidates, not automatic rightsizing decisions. "
    "No CPU/memory utilization or savings estimate is inferred from cost alone."
)
st.caption("Mode: analysis-only • Cost scope: EC2 resource-level Cost Explorer records • Inventory: EC2 DescribeInstances")
