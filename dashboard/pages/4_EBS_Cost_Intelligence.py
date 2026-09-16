from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import streamlit as st

from src.aws_cost_explorer import get_service_costs
from src.cloudwatch_ebs import get_ebs_metrics
from src.ebs_intelligence import build_ebs_intelligence, get_ebs_inventory

st.set_page_config(page_title="EBS Cost Intelligence", page_icon="💾", layout="wide")
st.title("💾 EBS Cost Intelligence")
st.caption("EBS inventory + CloudWatch I/O evidence + aggregate EBS spend")

with st.sidebar:
    region = st.text_input("AWS region", value="us-east-1")
    end = date.today()
    start = st.date_input("Cost start date", value=end - timedelta(days=30))
    metric_start = st.date_input("CloudWatch start date", value=end - timedelta(days=7))
    period = st.selectbox("CloudWatch period", [300, 900, 3600], index=0, format_func=lambda x: f"{x // 60} minutes")
    st.info("Read-only analysis. No EBS resources are modified.")

if end <= start or end <= metric_start:
    st.error("Start dates must be before today.")
    st.stop()

if not st.button("Load EBS cost + capacity intelligence", type="primary"):
    st.info("Choose the region/date ranges and load EBS inventory, aggregate cost and CloudWatch metrics.")
    st.stop()

try:
    with st.spinner("Reading EBS inventory, Cost Explorer and CloudWatch metrics…"):
        inventory = get_ebs_inventory(region)
        service_costs = get_service_costs(start, end)
        ebs_costs = [r for r in service_costs if "Elastic Block Store" in r.service]
        aggregate_cost = sum(r.cost for r in ebs_costs)
        volume_ids = [item["volume_id"] for item in inventory if item.get("volume_id")]
        metric_rows = get_ebs_metrics(
            volume_ids,
            datetime.combine(metric_start, time.min, tzinfo=timezone.utc),
            datetime.combine(end, time.min, tzinfo=timezone.utc),
            region=region,
            period=period,
        )
        intelligence = build_ebs_intelligence(inventory, metric_rows)
except Exception as exc:
    st.error("Unable to load EBS cost intelligence.")
    st.code(str(exc))
    st.caption("Verify EC2 DescribeVolumes, Cost Explorer and CloudWatch GetMetricData permissions and the selected region.")
    st.stop()

frame = pd.DataFrame(intelligence)

c1, c2, c3, c4 = st.columns(4)
c1.metric("EBS volumes", len(frame))
c2.metric("Aggregate EBS cost", f"${aggregate_cost:,.2f}")
c3.metric("I/O data", int((frame["utilization_status"] == "available").sum()) if not frame.empty else 0)
c4.metric("Review signals", int((frame["signals"].apply(bool)).sum()) if not frame.empty else 0)

st.subheader("EBS inventory + I/O evidence")
if frame.empty:
    st.warning("No EBS volumes were returned in the selected region.")
else:
    display_columns = [
        "volume_id", "volume_type", "size_gb", "state", "az", "encrypted", "iops", "throughput_mibps",
        "attachments", "read_ops_average", "write_ops_average", "read_bytes_average", "write_bytes_average",
        "queue_length_average", "idle_time_average", "utilization_status", "signals",
    ]
    for column in display_columns:
        if column not in frame:
            frame[column] = None
    frame["signals"] = frame["signals"].apply(lambda values: ", ".join(values) if values else "none")
    frame["attachments"] = frame["attachments"].apply(lambda values: ", ".join(values) if values else "unattached")
    st.dataframe(frame[display_columns], use_container_width=True, hide_index=True)

st.subheader("Cost evidence")
st.info(
    "Cost Explorer data is service-level in this view. The aggregate EBS amount is intentionally not divided across volumes unless resource-level billing evidence is available."
)
if ebs_costs:
    cost_frame = pd.DataFrame([{"billing_period": r.billing_period, "service": r.service, "cost": r.cost} for r in ebs_costs])
    st.dataframe(cost_frame.style.format({"cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
else:
    st.warning("No EBS service-level Cost Explorer records were returned for the selected period.")

st.subheader("Review signals")
for signal in ["unattached-volume-review", "gp2-migration-review", "low-activity-review", "high-queue-review"]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum()) if not frame.empty else 0
    st.write(f"**{signal}** — {count} volume(s)")

st.warning("Signals are review candidates, not automatic modification decisions. Raw CloudWatch I/O evidence is shown without converting it into fabricated utilization percentages, prices, or savings estimates.")
st.caption("Mode: analysis-only • Cost: EBS service-level Cost Explorer • Inventory: EC2 DescribeVolumes • I/O: CloudWatch GetMetricData")
