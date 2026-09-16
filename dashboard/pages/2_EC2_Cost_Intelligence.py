from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import streamlit as st

from src.aws_cost_explorer import get_ec2_resource_costs
from src.aws_readonly import get_ec2_inventory
from src.cloudwatch_ec2 import get_ec2_utilization
from src.ec2_intelligence import build_ec2_cost_insights
from src.ec2_utilization_intelligence import correlate_cost_and_utilization


st.set_page_config(page_title="EC2 Cost Intelligence", page_icon="🔎", layout="wide")
st.title("🔎 EC2 Cost Intelligence")
st.caption("Resource cost + EC2 inventory + CloudWatch utilization evidence")

with st.sidebar:
    region = st.text_input("AWS region", value="us-east-1")
    end = date.today()
    start = st.date_input("Cost start date", value=end - timedelta(days=30))
    metric_start = st.date_input("CloudWatch start date", value=end - timedelta(days=7))
    period = st.selectbox("CloudWatch period", [300, 900, 3600], index=0, format_func=lambda x: f"{x // 60} minutes")
    st.info("Read-only analysis. No EC2 resources are modified.")

if end <= start or end <= metric_start:
    st.error("Start dates must be before today.")
    st.stop()

if not st.button("Load EC2 cost + utilization intelligence", type="primary"):
    st.info("Choose the region/date ranges and load resource-level cost and CloudWatch metrics.")
    st.stop()

try:
    with st.spinner("Reading EC2 cost, inventory and CloudWatch metrics…"):
        costs = get_ec2_resource_costs(start, end)
        inventory = get_ec2_inventory(region)
        rows = [
            {"resource_id": r.resource_id, "cost": r.cost, "billing_period": r.billing_period}
            for r in costs
            if r.resource_id
        ]
        insights = build_ec2_cost_insights(rows, inventory)
        instance_ids = [item["instance_id"] for item in inventory if item.get("instance_id")]
        metric_rows = get_ec2_utilization(
            instance_ids,
            datetime.combine(metric_start, time.min, tzinfo=timezone.utc),
            datetime.combine(end, time.min, tzinfo=timezone.utc),
            region=region,
            period=period,
        )
        utilization = correlate_cost_and_utilization(rows, metric_rows)
        utilization_by_id = {row["resource_id"]: row for row in utilization}
except Exception as exc:
    st.error("Unable to load EC2 cost intelligence.")
    st.code(str(exc))
    st.caption("Verify Cost Explorer resource-level access, CloudWatch GetMetricData permission, region, and read-only IAM permissions.")
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
        "cpu_avg_pct": utilization_by_id.get(item.instance_id, {}).get("cpu_average_pct"),
        "cpu_max_pct": utilization_by_id.get(item.instance_id, {}).get("cpu_max_pct"),
        "network_out_bytes": utilization_by_id.get(item.instance_id, {}).get("network_out_bytes"),
        "utilization_status": utilization_by_id.get(item.instance_id, {}).get("utilization_status", "not-available"),
        "signals": ", ".join(utilization_by_id.get(item.instance_id, {}).get("signals", item.signals)) if utilization_by_id.get(item.instance_id) else ", ".join(item.signals) if item.signals else "none",
        "confidence": item.confidence,
    }
    for item in insights
])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Attributed EC2 resources", len(frame))
c2.metric("Attributed cost", f"${frame['cost'].sum():,.2f}")
c3.metric("Utilization data", int((frame["utilization_status"] == "available").sum()))
c4.metric("Review signals", int((frame["signals"] != "none").sum()))

st.subheader("Resource + utilization intelligence")
st.dataframe(
    frame.style.format({"cost": "${:,.2f}", "cost_share_pct": "{:.1f}%", "cpu_avg_pct": "{:.1f}%", "cpu_max_pct": "{:.1f}%"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Utilization evidence")
st.caption("CPUUtilization is read from AWS/EC2 through CloudWatch GetMetricData. Network values are bytes over the selected metric window. Missing metrics are not treated as zero.")
for signal in ["low-average-cpu-review", "high-average-cpu", "high-peak-cpu"]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum())
    st.write(f"**{signal}** — {count} resource(s)")

st.subheader("Existing cost review signals")
for signal in ["arm64-review", "stopped-resource-review", "high-cost-concentration"]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum())
    st.write(f"**{signal}** — {count} resource(s)")

st.warning(
    "Signals are review candidates, not automatic rightsizing decisions. "
    "CPU utilization is evidence for investigation, not a complete capacity model; memory utilization requires a separately installed CloudWatch agent/custom metric and is not inferred here."
)
st.caption("Mode: analysis-only • Cost: EC2 resource-level Cost Explorer • Inventory: EC2 DescribeInstances • Utilization: CloudWatch GetMetricData")
