from __future__ import annotations

import pandas as pd
import streamlit as st

from src.alerting import classify_severity
from src.forecasting import forecast_next_month, simulate_savings


def render_intelligence(df: pd.DataFrame) -> None:
    """Render analysis-only forecasts, alert signals, and savings scenarios."""
    st.subheader("FinOps Intelligence")

    monthly = (
        df.groupby("billing_period", as_index=False)["cost"]
        .sum()
        .sort_values("billing_period")
    )
    values = monthly["cost"].astype(float).tolist()
    if len(values) < 2:
        st.info("At least two billing periods are required for forecasting.")
        return

    forecast = forecast_next_month(values)
    latest = values[-1]
    baseline = sum(values[:-1]) / len(values[:-1])
    change_pct = 0.0 if baseline == 0 else ((latest - baseline) / baseline) * 100
    severity = classify_severity(change_pct)

    c1, c2, c3 = st.columns(3)
    c1.metric("Next-period forecast", f"${forecast:,.2f}")
    c2.metric("Latest vs historical baseline", f"{change_pct:+.1f}%")
    c3.metric("Cost signal", severity.upper())

    st.caption("Forecasts and signals are analytical only; no AWS resources are modified.")

    st.markdown("**Savings simulation**")
    scenarios = []
    for percent in (10, 20, 30):
        result = simulate_savings(forecast, percent)
        scenarios.append(
            {
                "scenario": f"{percent}% optimization",
                "projected_monthly_cost": result["projected_cost"],
                "monthly_savings": result["monthly_savings"],
            }
        )
    scenario_df = pd.DataFrame(scenarios)
    st.dataframe(
        scenario_df.style.format(
            {"projected_monthly_cost": "${:,.2f}", "monthly_savings": "${:,.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
