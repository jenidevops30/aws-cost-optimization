from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "sample-billing.csv"

st.set_page_config(page_title="AWS FinOps Control Center", page_icon="☁️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.25rem 1.5rem; border: 1px solid rgba(128,128,128,.25); border-radius: 14px; margin-bottom: 1rem;}
.hero h1 {margin: 0 0 .25rem 0; font-size: 2rem;}
.hero p {margin: 0; opacity: .75;}
.section {margin-top: 1.25rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>☁️ AWS FinOps Control Center</h1><p>Cost visibility • anomaly signals • forecasting • savings simulation</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Data source")
    mode = st.radio("Operating mode", ["Demo / CSV", "AWS Cost Explorer"], index=0)
    if mode == "Demo / CSV":
        uploaded = st.file_uploader("Upload normalized billing CSV", type=["csv"])
        st.caption("Required: billing_period, service, usage_type, region, cost")
    else:
        st.info("LIVE mode is read-only and queries service-level Cost Explorer data.")
        default_start = date.today().replace(day=1) - timedelta(days=180)
        start = st.date_input("Start date", value=default_start)
        end = st.date_input("End date (exclusive)", value=date.today().replace(day=1))
        fetch_live = st.button("↻ Refresh AWS costs", type="primary", use_container_width=True)


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
        st.info("Select a date range and click **Refresh AWS costs** to load live data.")
        return None
    if end <= start:
        st.error("End date must be after start date.")
        return None
    try:
        from src.aws_cost_explorer import get_service_costs
        records = get_service_costs(start, end)
        frame = pd.DataFrame([
            {"billing_period": r.billing_period, "service": r.service, "usage_type": "SERVICE",
             "region": r.region, "cost": r.cost, "currency": r.currency, "source": r.source}
            for r in records
        ])
        if frame.empty:
            st.warning("Cost Explorer returned no service-level records for this range.")
            return None
        return validate_frame(frame), "AWS Cost Explorer (live, read-only)"
    except Exception as exc:
        st.error("Unable to query AWS Cost Explorer.")
        st.code(str(exc))
        st.info("Verify AWS credentials and Cost Explorer read permissions.")
        return None


loaded = load_demo() if mode == "Demo / CSV" else load_live()
if loaded is None:
    st.stop()

df, source_label = loaded
services = sorted(df["service"].unique())
st.sidebar.divider()
st.sidebar.header("Dashboard filters")
selected_services = st.sidebar.multiselect("Services", services, default=services)
filtered = df[df["service"].isin(selected_services)].copy()
if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

st.caption(f"Source: **{source_label}** • Mode: **{mode}** • {len(filtered):,} records")
monthly = filtered.groupby("billing_period", as_index=False)["cost"].sum().sort_values("billing_period")
service = filtered.groupby("service", as_index=False)["cost"].sum().sort_values("cost", ascending=False)
latest_period = monthly.iloc[-1]["billing_period"]
latest_cost = float(monthly.iloc[-1]["cost"])
previous_cost = float(monthly.iloc[-2]["cost"]) if len(monthly) > 1 else 0.0
mom_change = latest_cost - previous_cost if len(monthly) > 1 else 0.0
mom_pct = (mom_change / previous_cost * 100) if previous_cost else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Latest spend", f"${latest_cost:,.2f}", f"{mom_pct:+.1f}% MoM")
c2.metric("Analyzed spend", f"${filtered['cost'].sum():,.2f}")
c3.metric("Services", len(filtered["service"].unique()))
c4.metric("Periods", len(monthly))
c5.metric("Latest period", str(latest_period))

left, right = st.columns([1.6, 1])
with left:
    st.subheader("Spend trend")
    st.line_chart(monthly.set_index("billing_period"), y="cost", height=330)
with right:
    st.subheader("Service spend")
    st.bar_chart(service.set_index("service"), y="cost", height=330)

st.subheader("Service cost overview")
service_view = service.copy()
service_view["share_pct"] = service_view["cost"] / service_view["cost"].sum() * 100
st.dataframe(service_view.style.format({"cost": "${:,.2f}", "share_pct": "{:.1f}%"}), use_container_width=True, hide_index=True)

st.subheader("Cost intelligence")
try:
    from src.intelligence import detect_anomalies
    from src.cost_engine import CostRecord
    records = [CostRecord(str(r.billing_period), str(r.service), str(r.usage_type), str(r.region), float(r.cost)) for r in filtered.itertuples(index=False)]
    anomalies = detect_anomalies(records, threshold_pct=20.0)
except Exception:
    anomalies = []

alert_col, forecast_col = st.columns(2)
with alert_col:
    st.markdown("**🚨 Cost signals**")
    if anomalies:
        alert_df = pd.DataFrame([{"period": a.period, "service": a.service, "cost": a.cost, "change": a.change_pct, "severity": "HIGH" if abs(a.change_pct) >= 75 else "MEDIUM"} for a in anomalies[:10]])
        st.dataframe(alert_df.style.format({"cost": "${:,.2f}", "change": "{:+.1f}%"}), use_container_width=True, hide_index=True)
    else:
        st.success("No cost signals above the 20% anomaly threshold in the selected data.")

with forecast_col:
    st.markdown("**🔮 Forecast & savings scenarios**")
    if len(monthly) >= 2:
        try:
            from src.forecasting import forecast_next_month, simulate_savings
            forecast = float(forecast_next_month(monthly["cost"].astype(float).tolist()))
            st.metric("Next-period forecast", f"${forecast:,.2f}")
            rows = []
            for pct in (10, 20, 30):
                result = simulate_savings(forecast, pct)
                rows.append({"scenario": f"{pct}%", "projected_cost": result["projected_cost"], "savings": result["monthly_savings"]})
            st.dataframe(pd.DataFrame(rows).style.format({"projected_cost": "${:,.2f}", "savings": "${:,.2f}"}), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.warning(f"Forecast unavailable: {exc}")
    else:
        st.info("Add at least two billing periods for forecasting.")

st.subheader("Monthly analysis")
monthly["change"] = monthly["cost"].diff()
monthly["change_pct"] = monthly["cost"].pct_change() * 100
st.dataframe(monthly.style.format({"cost": "${:,.2f}", "change": "${:+,.2f}", "change_pct": "{:+.1f}%"}), use_container_width=True, hide_index=True)

st.subheader("Evidence & operating mode")
if mode == "AWS Cost Explorer":
    st.warning("LIVE AWS DATA • READ-ONLY. Cost Explorer results are service-level and are not presented as per-resource costs. No AWS resource mutations are performed.")
else:
    st.info("DEMO / CSV MODE. Historical or sample billing data is analyzed locally; no AWS API calls are made.")
