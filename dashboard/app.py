from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sample-billing.csv"

st.set_page_config(page_title="AWS FinOps Dashboard", page_icon="☁️", layout="wide")

st.title("AWS FinOps Cost Intelligence")
st.caption("Evidence-driven AWS billing analysis with explicit demo/live operating modes.")

with st.sidebar:
    st.header("Data source")
    mode = st.radio("Operating mode", ["Demo / CSV", "AWS Cost Explorer"], index=0)

    if mode == "Demo / CSV":
        uploaded = st.file_uploader("Upload normalized billing CSV", type=["csv"])
        st.info("Expected columns: billing_period, service, usage_type, region, cost, currency, source")
    else:
        st.info("Read-only: Cost Explorer is queried for service-level UnblendedCost only.")
        default_start = date.today().replace(day=1) - timedelta(days=180)
        start = st.date_input("Start date", value=default_start)
        end = st.date_input("End date (exclusive)", value=date.today().replace(day=1))
        fetch_live = st.button("Fetch AWS costs", type="primary")


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"billing_period", "service", "usage_type", "region", "cost"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    frame = frame.copy()
    frame["cost"] = pd.to_numeric(frame["cost"], errors="coerce")
    frame = frame.dropna(subset=["cost"])
    frame["billing_period"] = frame["billing_period"].astype(str)
    return frame


def load_demo() -> tuple[pd.DataFrame, str]:
    try:
        if uploaded is not None:
            return validate_frame(pd.read_csv(uploaded)), f"Uploaded: {uploaded.name}"
        return validate_frame(pd.read_csv(DEFAULT_DATA)), "Repository sample dataset"
    except Exception as exc:
        st.error(f"Unable to load billing data: {exc}")
        st.stop()


def load_live() -> tuple[pd.DataFrame, str] | None:
    if not fetch_live:
        st.info("Select a date range and click **Fetch AWS costs** to query Cost Explorer.")
        return None
    if end <= start:
        st.error("End date must be after start date.")
        return None
    try:
        from src.aws_cost_explorer import get_service_costs

        records = get_service_costs(start, end)
        frame = pd.DataFrame(
            [
                {
                    "billing_period": r.billing_period,
                    "service": r.service,
                    "usage_type": "SERVICE",
                    "region": r.region,
                    "cost": r.cost,
                    "currency": r.currency,
                    "source": r.source,
                }
                for r in records
            ]
        )
        if frame.empty:
            st.warning("Cost Explorer returned no service-level records for this range.")
            return None
        return validate_frame(frame), "AWS Cost Explorer (live, read-only)"
    except Exception as exc:
        st.error("Unable to query AWS Cost Explorer.")
        st.code(str(exc))
        st.info("Verify AWS credentials and the Cost Explorer read permission for the active identity.")
        return None


loaded = load_demo() if mode == "Demo / CSV" else load_live()
if loaded is None:
    st.stop()

df, source_label = loaded
periods = sorted(df["billing_period"].unique())
services = sorted(df["service"].unique())

if mode == "AWS Cost Explorer":
    st.success("LIVE AWS DATA • READ-ONLY • Cost Explorer service-level costs")
else:
    st.caption("DEMO / CSV MODE")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total analyzed", f"${df['cost'].sum():,.2f}")
with c2:
    st.metric("Billing periods", len(periods))
with c3:
    st.metric("Services", len(services))
with c4:
    st.metric("Records", len(df))

st.caption(f"Source: {source_label}")

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
if mode == "AWS Cost Explorer":
    st.warning(
        "Live data is service-level Cost Explorer data. It is not treated as per-resource cost, "
        "and this dashboard performs no AWS resource mutations."
    )
else:
    st.warning(
        "Historical/sample billing analysis is separate from live AWS observations. "
        "No AWS data is queried in Demo / CSV mode."
    )
