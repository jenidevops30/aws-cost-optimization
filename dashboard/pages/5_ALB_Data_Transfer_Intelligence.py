from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import streamlit as st

from src.alb_intelligence import build_alb_intelligence, get_alb_inventory
from src.aws_cost_explorer import get_service_costs
from src.cloudwatch_alb import get_alb_metrics

st.set_page_config(page_title="ALB & Data Transfer Intelligence", page_icon="⚖️", layout="wide")
st.title("⚖️ ALB & Data Transfer Cost Intelligence")
st.caption("ALB inventory + CloudWatch traffic evidence + aggregate load-balancing spend")

with st.sidebar:
    region = st.text_input("AWS region", value="us-east-1")
    end = date.today()
    start = st.date_input("Cost start date", value=end - timedelta(days=30))
    metric_start = st.date_input("CloudWatch start date", value=end - timedelta(days=7))
    period = st.selectbox("CloudWatch period", [300, 900, 3600], index=0, format_func=lambda x: f"{x // 60} minutes")
    st.info("Read-only analysis. No load balancer is modified.")

if end <= start or end <= metric_start:
    st.error("Start dates must be before today.")
    st.stop()

if not st.button("Load ALB + data transfer intelligence", type="primary"):
    st.info("Choose the region/date ranges and load ALB inventory, aggregate cost and CloudWatch traffic metrics.")
    st.stop()

try:
    with st.spinner("Reading ALB inventory, Cost Explorer and CloudWatch metrics…"):
        inventory = get_alb_inventory(region)
        service_costs = get_service_costs(start, end)
        alb_costs = [r for r in service_costs if "Elastic Load Balancing" in r.service]
        aggregate_cost = sum(r.cost for r in alb_costs)
        metric_rows = get_alb_metrics(
            inventory,
            datetime.combine(metric_start, time.min, tzinfo=timezone.utc),
            datetime.combine(end, time.min, tzinfo=timezone.utc),
            region=region,
            period=period,
        )
        intelligence = build_alb_intelligence(inventory, metric_rows)
except Exception as exc:
    st.error("Unable to load ALB cost intelligence.")
    st.code(str(exc))
    st.caption("Verify ELBv2 DescribeLoadBalancers, Cost Explorer and CloudWatch GetMetricData permissions and the selected region.")
    st.stop()

frame = pd.DataFrame(intelligence)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Load balancers", len(frame))
c2.metric("Aggregate ELB cost", f"${aggregate_cost:,.2f}")
c3.metric("Traffic data", int((frame["metrics_status"] == "available").sum()) if not frame.empty else 0)
c4.metric("Review signals", int((frame["signals"].apply(bool)).sum()) if not frame.empty else 0)

st.subheader("ALB inventory + traffic evidence")
if frame.empty:
    st.warning("No load balancers were returned in the selected region.")
else:
    columns = ["name", "type", "scheme", "state", "vpc_id", "availability_zones", "request_count_average", "processed_bytes_average", "active_connections_average", "new_connections_average", "target_response_time_average", "metrics_status", "signals"]
    for column in columns:
        if column not in frame:
            frame[column] = None
    frame["availability_zones"] = frame["availability_zones"].apply(lambda values: ", ".join(values) if isinstance(values, list) else "unknown")
    frame["signals"] = frame["signals"].apply(lambda values: ", ".join(values) if values else "none")
    st.dataframe(frame[columns], use_container_width=True, hide_index=True)

st.subheader("Cost evidence")
st.info("Cost Explorer data is service-level in this view. Aggregate ELB spend is not divided across individual load balancers without resource-level billing evidence.")
if alb_costs:
    cost_frame = pd.DataFrame([{"billing_period": r.billing_period, "service": r.service, "cost": r.cost} for r in alb_costs])
    st.dataframe(cost_frame.style.format({"cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
else:
    st.warning("No ELB service-level Cost Explorer records were returned for the selected period.")

st.subheader("Review signals")
for signal in ["low-request-activity-review", "high-processed-bytes-review", "high-target-response-time-review", "non-active-load-balancer-review"]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum()) if not frame.empty else 0
    st.write(f"**{signal}** — {count} load balancer(s)")

st.warning("Signals are investigation candidates, not automatic modification decisions. CloudWatch traffic evidence is shown without converting it into fabricated prices or savings estimates.")
st.caption("Mode: analysis-only • Cost: ELB service-level Cost Explorer • Inventory: ELBv2 DescribeLoadBalancers • Traffic: CloudWatch GetMetricData")
