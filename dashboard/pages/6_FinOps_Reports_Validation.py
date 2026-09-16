from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "sample-billing.csv"

st.set_page_config(page_title="FinOps Reports & Validation", page_icon="📊", layout="wide")
st.title("📊 FinOps Reports & Validation")
st.caption("Export analyzed evidence and compare validated billing periods without changing AWS resources.")


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"billing_period", "service", "usage_type", "region", "cost"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    result = frame.copy()
    result["cost"] = pd.to_numeric(result["cost"], errors="coerce")
    result = result.dropna(subset=["cost"])
    result["billing_period"] = result["billing_period"].astype(str)
    return result


with st.sidebar:
    st.header("Report source")
    uploaded = st.file_uploader("Upload normalized billing CSV", type=["csv"])
    st.caption("Required: billing_period, service, usage_type, region, cost")
    st.divider()
    st.caption("Safety: report generation is analysis-only and performs no AWS mutations.")

try:
    df = validate_frame(pd.read_csv(uploaded) if uploaded is not None else pd.read_csv(DEFAULT_DATA))
except Exception as exc:
    st.error(f"Unable to load billing data: {exc}")
    st.stop()

services = sorted(df["service"].unique())
selected = st.multiselect("Services", services, default=services)
filtered = df[df["service"].isin(selected)].copy()
if filtered.empty:
    st.warning("No data matches the selected services.")
    st.stop()

monthly = filtered.groupby("billing_period", as_index=False)["cost"].sum().sort_values("billing_period")
service_totals = filtered.groupby("service")["cost"].sum().sort_values(ascending=False).to_dict()

from src.alerting import alerts_from_anomalies
from src.cost_engine import CostRecord
from src.finops_exports import build_export_bundle, build_validation_summary, report_to_csv, report_to_json, report_to_markdown
from src.intelligence import detect_anomalies

records = [CostRecord(str(r.billing_period), str(r.service), str(r.usage_type), str(r.region), float(r.cost)) for r in filtered.itertuples(index=False)]
anomalies = detect_anomalies(records, threshold_pct=20.0)
alerts = alerts_from_anomalies(anomalies)
anomaly_rows = [{"period": a.period, "service": a.service, "current_cost": a.current_cost, "baseline": a.baseline_cost, "change_pct": a.change_pct, "severity": a.severity, "reason": a.reason} for a in alerts]

report = {
    "report_version": "1.0",
    "scope": {
        "cost_scope": "billing records supplied to the analysis",
        "resource_scope": "not inferred from service-level billing",
        "mode": "analysis-only",
    },
    "summary": {
        "total_analyzed_cost": round(float(filtered["cost"].sum()), 2),
        "billing_periods": len(monthly),
        "services": len(service_totals),
        "anomalies": len(anomaly_rows),
        "recommendation_candidates": 0,
    },
    "monthly_costs": monthly.to_dict("records"),
    "service_totals": {str(k): round(float(v), 2) for k, v in service_totals.items()},
    "correlation": [],
    "anomalies": anomaly_rows,
    "recommendations": [],
    "limitations": [
        "Service-level billing is not treated as per-resource cost.",
        "This report page does not invent resource-level attribution.",
        "Observed reductions are not automatically attributed to a particular optimization action.",
        "No AWS resource mutation is performed by report generation.",
    ],
}

st.subheader("Executive report")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Analyzed spend", f"${filtered['cost'].sum():,.2f}")
c2.metric("Billing periods", len(monthly))
c3.metric("Services", len(service_totals))
c4.metric("Findings", len(anomaly_rows))

st.dataframe(
    pd.DataFrame([{"service": k, "cost": v, "share_pct": v / sum(service_totals.values()) * 100} for k, v in service_totals.items()]).style.format({"cost": "${:,.2f}", "share_pct": "{:.1f}%"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Baseline vs post-optimization validation")
periods = monthly["billing_period"].tolist()
if len(periods) >= 2:
    baseline_period = st.selectbox("Baseline period", periods, index=0)
    post_period = st.selectbox("Post-optimization period", periods, index=len(periods) - 1)
    baseline_cost = float(monthly.loc[monthly["billing_period"] == baseline_period, "cost"].iloc[0])
    post_cost = float(monthly.loc[monthly["billing_period"] == post_period, "cost"].iloc[0])
    validation = build_validation_summary(monthly.to_dict("records"), baseline=baseline_cost, post_optimization=post_cost)
    report = build_export_bundle(report, validation)
    v1, v2, v3 = st.columns(3)
    v1.metric("Baseline", f"${baseline_cost:,.2f}")
    v2.metric("Comparison", f"${post_cost:,.2f}")
    v3.metric("Observed change", f"${validation['observed_delta']:,.2f}" if validation.get("observed_delta") is not None else "N/A")
    st.info("Validation is descriptive. A lower comparison period does not by itself prove which optimization action caused the change.")
else:
    report = build_export_bundle(report)
    st.info("At least two billing periods are required for a baseline comparison.")

st.subheader("Findings")
if anomaly_rows:
    st.dataframe(pd.DataFrame(anomaly_rows), use_container_width=True, hide_index=True)
else:
    st.success("No cost anomalies exceeded the 20% analytical threshold.")

st.subheader("Exports")
st.caption("Exports contain the analyzed evidence only. They do not execute AWS changes.")
col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("Download JSON", report_to_json(report), file_name="finops-report.json", mime="application/json", use_container_width=True)
with col2:
    st.download_button("Download CSV", report_to_csv(report), file_name="finops-monthly-costs.csv", mime="text/csv", use_container_width=True)
with col3:
    st.download_button("Download Markdown", report_to_markdown(report), file_name="finops-report.md", mime="text/markdown", use_container_width=True)

with st.expander("Read-only controls"):
    st.write("**AWS mutation policy:** no create, delete, resize, start, stop, reboot, or deployment operations.")
    st.write("**Cost attribution policy:** service-level totals are not divided across resources without billing evidence.")
    st.write("**Evidence policy:** missing evidence remains unavailable rather than being treated as zero.")
