from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src.aws_budgets import get_budgets, summarize_budgets


st.set_page_config(page_title="Budget Governance", page_icon="💰", layout="wide")
st.title("AWS Budget Governance")
st.caption("Read-only budget vs actual/forecast investigation")

st.warning("Analysis-only: this page reads AWS Budgets. It does not create, update, delete, or subscribe to budgets.")

region = st.text_input("AWS region", value=os.getenv("AWS_REGION", "us-east-1"))
account_id = st.text_input("AWS account ID", value=os.getenv("AWS_ACCOUNT_ID", ""), type="password")

if st.button("Load budgets", type="primary"):
    if not account_id.strip():
        st.error("Provide the AWS account ID for the Budgets API request.")
    else:
        try:
            records = get_budgets(account_id.strip(), region=region.strip() or "us-east-1")
            st.session_state["budget_records"] = records
        except Exception:
            st.error("Budget data could not be loaded. Check read-only permissions and AWS connectivity.")

records = st.session_state.get("budget_records", [])
if records:
    summary = summarize_budgets(records)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Budgets", summary["budget_count"])
    c2.metric("Over budget", summary["over_budget_count"])
    c3.metric("Near limit", summary["near_limit_count"])
    c4.metric("Forecast", f"${summary['forecast_usd']:,.2f}")

    rows = [{
        "Budget": r.name,
        "Type": r.budget_type,
        "Limit (USD)": r.limit_usd,
        "Actual (USD)": r.actual_usd,
        "Forecast (USD)": r.forecast_usd,
        "Time Unit": r.time_unit,
        "Status": r.status,
        "Period Start": r.time_period_start,
        "Period End": r.time_period_end,
    } for r in records]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.info("Governance status is a threshold-based investigation signal: forecast is preferred when AWS provides it; otherwise actual spend is used. It is not a forecast guarantee.")
else:
    st.info("No budget data loaded yet.")
