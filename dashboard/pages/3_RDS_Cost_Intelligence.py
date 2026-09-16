from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import streamlit as st

from src.aws_cost_explorer import get_service_costs
from src.aws_readonly import get_rds_inventory
from src.cloudwatch_rds import get_rds_utilization
from src.rds_intelligence import build_rds_intelligence

st.set_page_config(page_title="RDS Cost Intelligence", page_icon="🗄️", layout="wide")
st.title("🗄️ RDS Cost Intelligence")
st.caption("RDS inventory + CloudWatch utilization evidence + aggregate Cost Explorer spend")

with st.sidebar:
    region = st.text_input("AWS region", value="us-east-1")
    end = date.today()
    start = st.date_input("Cost start date", value=end - timedelta(days=30))
    metric_start = st.date_input("CloudWatch start date", value=end - timedelta(days=7))
    period = st.selectbox("CloudWatch period", [300, 900, 3600], index=0, format_func=lambda x: f"{x // 60} minutes")
    st.info("Read-only analysis. No RDS resources are modified.")

if end <= start or end <= metric_start:
    st.error("Start dates must be before today.")
    st.stop()

if not st.button("Load RDS cost + utilization intelligence", type="primary"):
    st.info("Choose the region/date ranges and load RDS inventory, aggregate cost and CloudWatch metrics.")
    st.stop()

try:
    with st.spinner("Reading RDS inventory, Cost Explorer and CloudWatch metrics…"):
        inventory = get_rds_inventory(region)
        service_costs = get_service_costs(start, end)
        rds_costs = [r for r in service_costs if "Relational Database Service" in r.service]
        aggregate_cost = sum(r.cost for r in rds_costs)
        identifiers = [item["identifier"] for item in inventory if item.get("identifier")]
        metric_rows = get_rds_utilization(
            identifiers,
            datetime.combine(metric_start, time.min, tzinfo=timezone.utc),
            datetime.combine(end, time.min, tzinfo=timezone.utc),
            region=region,
            period=period,
        )
        intelligence = build_rds_intelligence(inventory, metric_rows)
except Exception as exc:
    st.error("Unable to load RDS cost intelligence.")
    st.code(str(exc))
    st.caption("Verify RDS DescribeDBInstances, Cost Explorer, CloudWatch GetMetricData permissions and the selected region.")
    st.stop()

frame = pd.DataFrame(intelligence)

c1, c2, c3, c4 = st.columns(4)
c1.metric("RDS instances", len(frame))
c2.metric("Aggregate RDS cost", f"${aggregate_cost:,.2f}")
c3.metric("Utilization data", int((frame["utilization_status"] == "available").sum()) if not frame.empty else 0)
c4.metric("Review signals", int((frame["signals"].apply(bool)).sum()) if not frame.empty else 0)

st.subheader("RDS inventory + utilization")
if frame.empty:
    st.warning("No RDS DB instances were returned in the selected region.")
else:
    display_columns = [
        "db_identifier", "db_class", "engine", "status", "multi_az", "allocated_storage_gb",
        "cpu_average_pct", "cpu_max_pct", "connections_average", "free_storage_gib_average",
        "free_storage_pct_of_allocated", "read_iops_average", "write_iops_average",
        "utilization_status", "signals",
    ]
    for column in display_columns:
        if column not in frame:
            frame[column] = None
    frame["signals"] = frame["signals"].apply(lambda values: ", ".join(values) if values else "none")
    st.dataframe(frame[display_columns], use_container_width=True, hide_index=True)

st.subheader("Cost evidence")
st.info(
    "Cost Explorer data is service-level in this view. The aggregate RDS amount is intentionally not divided across DB instances because service-level billing does not provide evidence for a per-instance allocation."
)
if rds_costs:
    cost_frame = pd.DataFrame([{"billing_period": r.billing_period, "service": r.service, "cost": r.cost} for r in rds_costs])
    st.dataframe(cost_frame.style.format({"cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
else:
    st.warning("No RDS service-level Cost Explorer records were returned for the selected period.")

st.subheader("Utilization review signals")
for signal in [
    "low-average-cpu-review",
    "high-average-cpu",
    "high-peak-cpu",
    "low-free-storage-review",
    "low-free-storage-percent-review",
]:
    count = int(frame["signals"].str.contains(signal, regex=False).sum()) if not frame.empty else 0
    st.write(f"**{signal}** — {count} resource(s)")

st.warning("Signals are review candidates, not automatic resizing decisions. Connection and IOPS metrics are operational evidence; they are not converted into pricing or savings estimates.")
st.caption("Mode: analysis-only • Cost: RDS service-level Cost Explorer • Inventory: RDS DescribeDBInstances • Utilization: CloudWatch GetMetricData")
