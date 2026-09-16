from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finops_governance import build_governance_snapshot, snapshot_to_dict

st.set_page_config(page_title="FinOps Executive Governance", layout="wide")
st.title("FinOps Executive Governance")
st.caption("Evidence-driven governance view. Analysis-only; no AWS resources are modified.")

st.info("Supply normalized evidence from your existing FinOps report pipeline. Missing evidence is shown explicitly rather than inferred.")

monthly = [
    {"period": "2026-05", "cost": 372.32},
    {"period": "2026-06", "cost": 327.07},
]
budgets: list[dict] = []
anomalies: list[dict] = []
findings: list[dict] = []

snapshot = build_governance_snapshot(monthly, budgets, anomalies, findings)
data = snapshot_to_dict(snapshot)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Cost", "N/A" if data["latest_cost_usd"] is None else f"${data['latest_cost_usd']:,.2f}")
c2.metric("MoM Change", "N/A" if data["month_over_month_pct"] is None else f"{data['month_over_month_pct']:.2f}%")
c3.metric("Budget Alerts", data["over_budget_count"] + data["near_limit_count"])
c4.metric("Anomalies", data["anomaly_count"])

st.subheader("Governance Snapshot")
st.dataframe(pd.DataFrame([data]), use_container_width=True, hide_index=True)

st.subheader("Evidence Status")
st.write(f"**{data['evidence_status']}** — the dashboard does not invent budget, anomaly, forecast, or finding evidence that was not supplied.")

st.warning("All outputs are analysis-only. Cost attribution, savings realization, and causal claims require supporting evidence.")
