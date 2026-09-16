from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.cost_engine import CostRecord, monthly_totals
from src.finops_governance import build_governance_snapshot, snapshot_to_dict

st.set_page_config(page_title="FinOps Executive Governance", layout="wide")
st.title("FinOps Executive Governance")
st.caption("Evidence-driven governance view. Analysis-only; no AWS resources are modified.")

st.info(
    "Load normalized billing CSV data and optionally supply JSON evidence from the existing FinOps pipeline. "
    "Missing evidence stays unavailable rather than being inferred."
)

uploaded = st.file_uploader("Normalized billing CSV", type=["csv"])
records: list[CostRecord] = []

if uploaded is not None:
    try:
        frame = pd.read_csv(uploaded)
        required = {"billing_period", "service", "usage_type", "region", "cost"}
        missing = required - set(frame.columns)
        if missing:
            st.error(f"Missing required CSV columns: {', '.join(sorted(missing))}")
        else:
            records = [
                CostRecord(
                    billing_period=str(row["billing_period"]),
                    service=str(row["service"]),
                    usage_type=str(row["usage_type"]),
                    region=str(row["region"]),
                    cost=float(row["cost"]),
                    currency=str(row.get("currency") or "USD"),
                    source=str(row.get("source") or "csv"),
                )
                for _, row in frame.iterrows()
            ]
    except (ValueError, TypeError) as exc:
        st.error(f"Unable to parse billing CSV: {exc}")

monthly = [{"period": period, "cost": cost} for period, cost in monthly_totals(records).items()]

with st.expander("Optional evidence JSON", expanded=False):
    st.caption(
        "Expected object keys: budgets, anomalies, findings, forecast, validation. "
        "Use the normalized structures already produced by the project; do not paste secrets."
    )
    evidence_text = st.text_area("Evidence payload", height=180, placeholder='{"budgets": [], "anomalies": []}')

budgets: list[dict] = []
anomalies: list[dict] = []
findings: list[dict] = []
forecast: dict | None = None
validation: dict | None = None

if evidence_text.strip():
    try:
        payload = json.loads(evidence_text)
        if not isinstance(payload, dict):
            raise ValueError("Evidence payload must be a JSON object")

        budgets_value = payload.get("budgets", [])
        anomalies_value = payload.get("anomalies", [])
        findings_value = payload.get("findings", [])
        forecast_value = payload.get("forecast")
        validation_value = payload.get("validation")

        if not isinstance(budgets_value, list):
            raise ValueError("budgets must be a JSON array")
        if not isinstance(anomalies_value, list):
            raise ValueError("anomalies must be a JSON array")
        if not isinstance(findings_value, list):
            raise ValueError("findings must be a JSON array")
        if forecast_value is not None and not isinstance(forecast_value, dict):
            raise ValueError("forecast must be a JSON object")
        if validation_value is not None and not isinstance(validation_value, dict):
            raise ValueError("validation must be a JSON object")

        budgets = budgets_value
        anomalies = anomalies_value
        findings = findings_value
        forecast = forecast_value
        validation = validation_value
    except (json.JSONDecodeError, ValueError) as exc:
        st.error(f"Invalid evidence JSON: {exc}")

snapshot = build_governance_snapshot(
    monthly,
    budgets=budgets,
    anomalies=anomalies,
    findings=findings,
    forecast=forecast,
    validation=validation,
)
data = snapshot_to_dict(snapshot)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Cost", "N/A" if data["latest_cost_usd"] is None else f"${data['latest_cost_usd']:,.2f}")
c2.metric("MoM Change", "N/A" if data["month_over_month_pct"] is None else f"{data['month_over_month_pct']:.2f}%")
c3.metric("Budget Alerts", data["over_budget_count"] + data["near_limit_count"])
c4.metric("Anomalies", data["anomaly_count"])

if monthly:
    st.subheader("Cost Trend")
    trend = pd.DataFrame(monthly)
    st.line_chart(trend.set_index("period")["cost"])
else:
    st.warning("No billing evidence loaded. Upload a normalized CSV to populate cost metrics.")

st.subheader("Governance Snapshot")
st.dataframe(pd.DataFrame([data]), use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("Evidence Status")
    st.write(f"**{data['evidence_status']}**")
    st.write("Cost-only evidence is not treated as resource-level attribution or proof of savings causality.")
with right:
    st.subheader("Review Queue")
    st.write(f"Findings requiring review: **{data['finding_count']}**")
    st.write(f"Anomaly impact reported by AWS: **${data['anomaly_impact_usd']:,.2f}**")

st.warning(
    "Analysis-only: this view does not change AWS resources, budgets, or alerts. "
    "Cost attribution, savings realization, and causal claims require supporting evidence."
)
