from __future__ import annotations

from pathlib import Path

import streamlit as st

from security.compliance import compliance_ready, scan_repository


st.set_page_config(page_title="Security & Compliance", page_icon="🛡️", layout="wide")
st.title("🛡️ Security & Compliance")
st.caption("Repository-level security controls for the FinOps platform. These checks are not a compliance certification.")

root = Path(__file__).resolve().parents[2]
checks = scan_repository(root)
ready = compliance_ready(checks)

st.metric("Security readiness", "READY" if ready else "ACTION REQUIRED")

for check in checks:
    if check.status == "ready":
        st.success(f"{check.name}: {check.detail}")
    else:
        st.error(f"{check.name}: {check.detail}")

st.subheader("Controls covered")
st.write(
    "• Secret-pattern detection without displaying matched values\n"
    "• Docker build-context exclusions\n"
    "• Read-only IAM action validation\n"
    "• CI dependency audit"
)

st.warning(
    "This page performs static repository checks only. It does not prove regulatory compliance, scan live AWS resources, or perform remediation."
)
