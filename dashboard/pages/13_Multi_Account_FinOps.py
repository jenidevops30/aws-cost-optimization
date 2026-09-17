from __future__ import annotations

import streamlit as st

from src.multi_account_finops import AccountCostRecord, account_mom, account_service_totals, account_totals

st.set_page_config(page_title="Multi-Account FinOps", page_icon="🏢", layout="wide")
st.title("🏢 Multi-Account FinOps")
st.caption("Normalized multi-account cost analysis. This page does not assume cross-account access or perform AWS mutations.")

sample = [
    AccountCostRecord("2026-06", "111111111111", "Production", "EC2", "us-east-1", 115.56),
    AccountCostRecord("2026-06", "111111111111", "Production", "RDS", "us-east-1", 79.72),
    AccountCostRecord("2026-06", "222222222222", "Staging", "EC2", "us-east-1", 42.10),
    AccountCostRecord("2026-06", "222222222222", "Staging", "RDS", "us-east-1", 18.40),
]

totals = account_totals(sample)
cols = st.columns(len(totals))
for column, (account_id, total) in zip(cols, totals.items()):
    name = next(record.account_name for record in sample if record.account_id == account_id)
    column.metric(name, f"${total:,.2f}")

st.subheader("Account cost")
st.dataframe(
    [{"account_id": account_id, "cost_usd": round(total, 2)} for account_id, total in totals.items()],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Account × service")
rows = [{"account_id": account_id, "service": service, "cost_usd": round(cost, 2)} for (account_id, service), cost in account_service_totals(sample).items()]
st.dataframe(rows, use_container_width=True, hide_index=True)

st.subheader("Period comparison")
st.dataframe(account_mom(sample), use_container_width=True, hide_index=True)

st.info("For production use, account identifiers and costs must come from approved billing evidence or read-only AWS collection. No cross-account role assumption is implemented by this demo page.")
