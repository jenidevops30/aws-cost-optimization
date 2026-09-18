"""Reusable visual theme for the FinOps dashboard."""

def inject_theme(st):
    st.markdown("""
    <style>
    .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22); padding: 1rem; border-radius: 14px;}
    .finops-hero {padding: 1.5rem 1.7rem; border: 1px solid rgba(128,128,128,.22); border-radius: 18px; margin-bottom: 1rem; background: linear-gradient(135deg, rgba(0,0,0,.035), rgba(0,0,0,.015));}
    .finops-hero h1 {margin:0 0 .35rem 0; font-size:2.1rem;}
    .finops-hero p {margin:0; opacity:.72; font-size:1rem;}
    .section-card {border:1px solid rgba(128,128,128,.18); border-radius:14px; padding:1rem 1.1rem; margin:.4rem 0 1rem;}
    .kicker {font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; opacity:.6; font-weight:700;}
    </style>
    """, unsafe_allow_html=True)
