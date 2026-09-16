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
.block-container {padding-top:1.5rem; padding-bottom:2rem; max-width:1500px;}
.hero {padding:1.4rem 1.6rem; border:1px solid rgba(128,128,128,.25); border-radius:16px; margin-bottom:1rem;}
.hero h1 {margin:0; font-size:2rem}.hero p {margin:.25rem 0 0; opacity:.7}
.status {padding:.65rem 1rem; border-radius:10px; border:1px solid rgba(128,128,128,.25); margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>☁️ AWS FinOps Control Center</h1><p>Executive cost visibility, anomaly detection, forecasting and savings simulation</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Control Center")
    mode = st.radio("Data source", ["Demo / CSV", "AWS Cost Explorer"], index=0)
    st.divider()
    if mode == "Demo / CSV":
        uploaded = st.file_uploader("Upload normalized billing CSV", type=["csv"])
        st.caption("Required: billing_period, service, usage_type, region, cost")
    else:
        uploaded = None
        st.info("LIVE mode is read-only.")
        default_start = date.today().replace(day=1) - timedelta(days=180)
        start = st.date_input("Start date", value=default_start)
        end = st.date_input("End date (exclusive)", value=date.today().replace(day=1))
        fetch_live = st.button("↻ Refresh AWS costs", type="primary", use_container_width=True)
    st.divider()
    st.caption("Safety: analysis only • no AWS resource mutations")


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


def load_data() -> tuple[pd.DataFrame, str] | None:
    if mode == "Demo / CSV":
        try:
            if uploaded is not None:
                return validate_frame(pd.read_csv(uploaded)), f"Uploaded: {uploaded.name}"
            return validate_frame(pd.read_csv(DEFAULT_DATA)), "Repository sample dataset"
        except Exception as exc:
            st.error(f"Unable to load billing data: {exc}")
            st.stop()
    if not fetch_live:
        st.info("Select a date range and click **Refresh AWS costs** to load live Cost Explorer data.")
        return None
    if end <= start:
        st.error("End date must be after start date.")
        return None
    try:
        from src.aws_cost_explorer import get_service_costs
        records = get_service_costs(start, end)
        frame = pd.DataFrame([{"billing_period":r.billing_period,"service":r.service,"usage_type":"SERVICE","region":r.region,"cost":r.cost,"currency":r.currency,"source":r.source} for r in records])
        if frame.empty:
            st.warning("Cost Explorer returned no service-level records for this range.")
            return None
        return validate_frame(frame), "AWS Cost Explorer (live, read-only)"
    except Exception as exc:
        st.error("Unable to query AWS Cost Explorer.")
        st.code(str(exc))
        return None

loaded = load_data()
if loaded is None:
    st.stop()
df, source_label = loaded

st.markdown(f'<div class="status">Source: <b>{source_label}</b> &nbsp; | &nbsp; Mode: <b>{mode}</b> &nbsp; | &nbsp; Records: <b>{len(df):,}</b></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Filters")
    services = sorted(df["service"].unique())
    selected_services = st.multiselect("Services", services, default=services)

filtered = df[df["service"].isin(selected_services)].copy()
if filtered.empty:
    st.warning("No data matches the selected services.")
    st.stop()

monthly = filtered.groupby("billing_period", as_index=False)["cost"].sum().sort_values("billing_period")
service = filtered.groupby("service", as_index=False)["cost"].sum().sort_values("cost", ascending=False)
latest = float(monthly.iloc[-1]["cost"])
previous = float(monthly.iloc[-2]["cost"]) if len(monthly) > 1 else 0.0
mom_pct = ((latest - previous) / previous * 100) if previous else 0.0

# Navigation keeps the dashboard focused instead of presenting every chart at once.
tab_overview, tab_services, tab_alerts, tab_forecast, tab_evidence = st.tabs(["Overview", "Services", "Alerts", "Forecast & Savings", "Evidence"])

with tab_overview:
    st.subheader("Executive overview")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Latest spend", f"${latest:,.2f}", f"{mom_pct:+.1f}% MoM")
    c2.metric("Analyzed spend", f"${filtered['cost'].sum():,.2f}")
    c3.metric("Services", len(filtered["service"].unique()))
    c4.metric("Billing periods", len(monthly))
    c5.metric("Latest period", str(monthly.iloc[-1]["billing_period"]))
    left,right = st.columns([1.6,1])
    with left:
        st.markdown("#### Monthly spend trend")
        st.line_chart(monthly.set_index("billing_period"), y="cost", height=350)
    with right:
        st.markdown("#### Spend by service")
        st.bar_chart(service.set_index("service"), y="cost", height=350)
    st.markdown("#### Monthly movement")
    overview = monthly.copy(); overview["change"] = overview["cost"].diff(); overview["change_pct"] = overview["cost"].pct_change()*100
    st.dataframe(overview.style.format({"cost":"${:,.2f}","change":"${:+,.2f}","change_pct":"{:+.1f}%"}), use_container_width=True, hide_index=True)

with tab_services:
    st.subheader("Service cost analysis")
    service_view = service.copy(); service_view["share_pct"] = service_view["cost"] / service_view["cost"].sum() * 100
    st.dataframe(service_view.style.format({"cost":"${:,.2f}","share_pct":"{:.1f}%"}), use_container_width=True, hide_index=True)
    selected = st.selectbox("Inspect service", service["service"].tolist())
    detail = filtered[filtered["service"] == selected].groupby("billing_period", as_index=False)["cost"].sum().sort_values("billing_period")
    st.line_chart(detail.set_index("billing_period"), y="cost", height=300)

with tab_alerts:
    st.subheader("Cost alerts & anomalies")
    from src.cost_engine import CostRecord
    from src.intelligence import detect_anomalies
    records = [CostRecord(str(r.billing_period),str(r.service),str(r.usage_type),str(r.region),float(r.cost)) for r in filtered.itertuples(index=False)]
    anomalies = detect_anomalies(records, threshold_pct=20.0)
    if anomalies:
        alert_df = pd.DataFrame([{"period":a.period,"service":a.service,"current_cost":a.cost,"baseline":a.baseline,"change_pct":a.change_pct,"severity":"CRITICAL" if abs(a.change_pct)>=75 else "WARNING"} for a in anomalies])
        st.dataframe(alert_df.style.format({"current_cost":"${:,.2f}","baseline":"${:,.2f}","change_pct":"{:+.1f}%"}), use_container_width=True, hide_index=True)
    else:
        st.success("No anomalies above the 20% threshold.")
    st.caption("Signals are analytical alerts only. They do not trigger AWS changes.")

with tab_forecast:
    st.subheader("Forecast & savings simulation")
    from src.forecasting import forecast_next_month, simulate_savings
    records = [CostRecord(str(r.billing_period),str(r.service),str(r.usage_type),str(r.region),float(r.cost)) for r in filtered.itertuples(index=False)]
    if len(monthly) >= 2:
        forecast = forecast_next_month(records)
        c1,c2,c3 = st.columns(3)
        c1.metric("Forecast period", forecast.forecast_period)
        c2.metric("Projected monthly cost", f"${forecast.projected_cost:,.2f}")
        c3.metric("Confidence", forecast.confidence.upper())
        scenarios = simulate_savings(records)
        scenario_df = pd.DataFrame([{"scenario":s.name,"baseline":s.baseline_cost,"projected_cost":s.projected_cost,"projected_saving":s.projected_saving} for s in scenarios])
        st.dataframe(scenario_df.style.format({"baseline":"${:,.2f}","projected_cost":"${:,.2f}","projected_saving":"${:,.2f}"}), use_container_width=True, hide_index=True)
        st.bar_chart(scenario_df.set_index("scenario"), y="projected_saving", height=300)
    else:
        st.info("At least two billing periods are required for forecasting.")

with tab_evidence:
    st.subheader("Evidence & controls")
    st.write("**Data source:**", source_label)
    st.write("**Operating mode:**", mode)
    st.write("**Cost scope:** service-level billing unless explicitly identified otherwise")
    st.write("**Mutation policy:** no resource creation, deletion, resizing, start/stop, or deployment")
    st.write("**Forecast policy:** historical analytical projection; not a guarantee")
    st.write("**Recommendation policy:** validate usage, sizing, architecture and billing assumptions before action")
    if mode == "AWS Cost Explorer":
        st.warning("Live Cost Explorer data is service-level. It is not represented as per-resource cost.")
    else:
        st.info("Demo/CSV mode performs local analysis and makes no AWS API calls.")
