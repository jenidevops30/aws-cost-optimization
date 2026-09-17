from __future__ import annotations

import streamlit as st

from src.alert_monitoring import AlertMonitor


st.set_page_config(page_title="FinOps Alerting & Monitoring", page_icon="🔔", layout="wide")
st.title("🔔 FinOps Alerting & Monitoring")
st.caption("Analysis-only alert lifecycle and deduplication. No AWS resources are modified.")

st.info("Create review alerts locally; production notification transports must be explicitly configured outside the intelligence engine.")
monitor = AlertMonitor()

with st.form("alert-form"):
    service = st.selectbox("Service", ["EC2", "RDS", "EBS", "ALB"])
    period = st.text_input("Period", "2026-09")
    severity = st.selectbox("Severity", ["info", "warning", "critical"])
    detail = st.text_area("Alert detail", f"{service} requires review based on current evidence.")
    submitted = st.form_submit_button("Create analysis alert")

if submitted:
    events = monitor.ingest_findings([{"name": f"{service}-REVIEW", "period": period, "severity": severity, "detail": detail}])
    if events:
        st.success("Alert created. Repeated identical alerts are deduplicated.")
    else:
        st.warning("Duplicate alert suppressed.")

summary = monitor.summary()
cols = st.columns(4)
for col, (name, value) in zip(cols, summary.items()):
    col.metric(name.title(), value)

st.subheader("Alert lifecycle")
st.markdown("`OPEN` → `ACKNOWLEDGED` → `RESOLVED`")
st.warning("No EC2, RDS, EBS, ALB, IAM, or other AWS resource is modified by this alerting layer.")
