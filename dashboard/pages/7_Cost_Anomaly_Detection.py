from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cost Anomaly Detection", page_icon="🚨", layout="wide")
st.title("🚨 AWS Cost Anomaly Detection")
st.caption("Read-only AWS Cost Anomaly Detection evidence. Findings are investigation signals, not automatic actions.")

with st.sidebar:
    st.header("Query")
    region = st.text_input("AWS region", value="us-east-1")
    end = st.date_input("End date (exclusive)", value=date.today())
    start = st.date_input("Start date", value=end - timedelta(days=30))
    monitor_arn = st.text_input("Monitor ARN (optional)", value="")
    run = st.button("↻ Load anomalies", type="primary", use_container_width=True)

if not run:
    st.info("Select a date range and load AWS Cost Anomaly Detection findings.")
    st.stop()
if end <= start:
    st.error("End date must be after start date.")
    st.stop()

try:
    from src.cost_anomaly import get_cost_anomalies, summarize_anomalies
    with st.spinner("Reading Cost Anomaly Detection findings…"):
        anomalies = get_cost_anomalies(start, end, region=region, monitor_arn=monitor_arn or None)
except Exception:
    st.error("Unable to query AWS Cost Anomaly Detection.")
    st.caption("Check the selected region, AWS credentials, and read-only Cost Explorer permissions.")
    st.stop()

summary = summarize_anomalies(anomalies)
c1, c2, c3 = st.columns(3)
c1.metric("Anomalies", summary["anomaly_count"])
c2.metric("Estimated impact", f"${summary['total_estimated_impact_usd']:,.2f}")
c3.metric("Affected services", len(summary["affected_services"]))

if not anomalies:
    st.success("No anomaly findings were returned for the selected window.")
    st.stop()

rows = []
for item in anomalies:
    services = sorted({str(c.get("service")) for c in item.get("root_causes", []) if c.get("service")})
    regions = sorted({str(c.get("region")) for c in item.get("root_causes", []) if c.get("region")})
    rows.append({
        "anomaly_id": item.get("anomaly_id"),
        "start": item.get("anomaly_start"),
        "end": item.get("anomaly_end"),
        "estimated_impact_usd": item.get("estimated_impact_usd"),
        "actual_spend_usd": item.get("actual_spend_usd"),
        "services": ", ".join(services),
        "regions": ", ".join(regions),
    })

df = pd.DataFrame(rows)
st.subheader("Detected anomalies")
st.dataframe(df.style.format({"estimated_impact_usd": "${:,.2f}", "actual_spend_usd": "${:,.2f}"}), use_container_width=True, hide_index=True)

st.subheader("Evidence scope")
st.write("**Source:** AWS Cost Anomaly Detection via Cost Explorer API")
st.write("**Mode:** analysis-only")
st.write("**Impact:** AWS-reported anomaly impact fields; not a fabricated savings estimate")
st.write("**Decision:** investigate root causes and validate billing/infrastructure evidence before taking action")
st.warning("An anomaly finding does not by itself establish causality or identify a specific infrastructure change that should be made.")
