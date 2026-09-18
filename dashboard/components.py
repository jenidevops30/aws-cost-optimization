from __future__ import annotations


def insight_card(st, label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="insight"><div class="insight-label">{label}</div>'
        f'<div class="insight-value">{value}</div>'
        f'<div class="insight-note">{note}</div></div>',
        unsafe_allow_html=True,
    )
