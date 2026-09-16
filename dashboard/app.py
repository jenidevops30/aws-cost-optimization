from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sample-billing.csv"

st.set_page_config(page_title="AWS FinOps Dashboard", page_icon="☁️", layout="wide")

st.title("AWS FinOps Cost Intelligence")
st.caption("Evidence-driven AWS billing analysis — demo mode uses the repository sample dataset.")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload normalized billing CSV", type=["csv"])
    st.info("Expected columns: billing_period, service, usage_type, region, cost, currency, source")

try:
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        source_label = f"Uploaded: {uploaded.name}"
    else:
        df = pd.read_csv(DEFAULT_DATA)
        source_label = "Repository sample dataset"
except Exception as exc:
    st.error(f"Unable to load billing data: {exc}")
    st.stop()

required = {"billing_period", "service", "usage_type", "region", "cost"}
missing = required - set(df.columns)
if missing:
    st.error(f"Missing required columns: {', '.join(sorted(missing))}")
    st.stop()

df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
df = df.dropna(subset=["cost"]).copy()
df["billing_period"] = df["billing_period"].astype(str)

periods = sorted(df["billing_period"].unique())
services = sorted(df["service"].unique())

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total analyzed", f"${df['cost'].sum():,.2f}")
with c2:
    st.metric("Billing periods", len(periods))
with c3:
    st.metric("Services", len(services))
with c4:
    st.metric("Records", len(df))

st.caption(f"Source: {source_label} • No live AWS data is queried by this dashboard.")

left, right = st.columns(2)
monthly = df.groupby("billing_period", as_index=False)["cost"].sum().sort_values("billing_period")
service = df.groupby("service", as_index=False)["cost"].sum().sort_values("cost", ascending=False)

with left:
    st.subheader("Monthly cost trend")
    st.line_chart(monthly.set_index("billing_period"), y="cost")

with right:
    st.subheader("Cost by service")
    st.bar_chart(service.set_index("service"), y="cost")

st.subheader("Month-over-month analysis")
monthly["change"] = monthly["cost"].diff()
monthly["change_pct"] = monthly["cost"].pct_change() * 100
st.dataframe(
    monthly.style.format({"cost": "${:,.2f}", "change": "${:+,.2f}", "change_pct": "{:+.1f}%"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Service breakdown")
service_detail = (
    df.groupby(["service", "usage_type"], as_index=False)["cost"]
    .sum()
    .sort_values("cost", ascending=False)
)
st.dataframe(
    service_detail.style.format({"cost": "${:,.2f}"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Evidence & operating mode")
st.warning(
    "This dashboard separates historical/sample billing analysis from live AWS observations. "
    "It does not claim savings, recommendations, or resource changes unless supporting evidence is supplied."
)
