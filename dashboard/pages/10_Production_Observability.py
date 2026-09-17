from __future__ import annotations

import os

import streamlit as st

from src.observability import METRICS
from src.runtime_config import load_config
from src.runtime_health import readiness_report


st.set_page_config(page_title="Production Observability", page_icon="🩺", layout="wide")
st.title("🩺 Production Observability")
st.caption("Operational visibility for the FinOps Control Center. AWS access remains read-only.")

config = load_config()
report = readiness_report(config)

left, right = st.columns(2)
with left:
    st.metric("Service health", "OK")
with right:
    st.metric("Readiness", str(report["status"]).upper())

st.subheader("Runtime")
st.json({
    "mode": config.mode,
    "region": config.region,
    "log_level": config.log_level,
    "aws_mutations": False,
})

st.subheader("Readiness checks")
for check in report["checks"]:
    if check["status"] == "ok":
        st.success(f"{check['name']}: {check['detail']}")
    else:
        st.error(f"{check['name']}: {check['detail']}")

st.subheader("In-process metrics")
snapshot = METRICS.snapshot()
if snapshot["counters"]:
    st.dataframe(
        [{"metric": key, "value": value} for key, value in snapshot["counters"].items()],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No operational events have been recorded in this process yet.")

st.subheader("Health endpoints")
st.code(
    "GET /health\nGET /readiness\nGET /metrics",
    language="text",
)
st.info(
    f"Health server: {os.getenv('FINOPS_HEALTH_HOST', '0.0.0.0')}:{os.getenv('FINOPS_HEALTH_PORT', '8080')}"
)
st.warning("Metrics are process-local and reset when the container restarts; they are intended for operational smoke checks, not durable billing evidence.")
