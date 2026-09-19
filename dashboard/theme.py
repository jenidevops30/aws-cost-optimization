"""Visual system for the AWS FinOps Control Center."""


def inject_theme(st):
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1500px;
            padding: 1.5rem 2rem 3rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid var(--border-color, #e5e7eb);
        }

        [data-testid="stMetric"] {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid var(--border-color, #e5e7eb);
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .finops-hero {
            background: linear-gradient(135deg, #111827, #1f2937);
            color: #ffffff;
            padding: 1.8rem 2rem;
            border-radius: 20px;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
        }

        .finops-hero .eyebrow {
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            opacity: 0.7;
            font-weight: 700;
        }

        .finops-hero h1 {
            margin: 0.35rem 0 0.4rem;
            font-size: 2.15rem;
        }

        .finops-hero p {
            margin: 0;
            opacity: 0.78;
            font-size: 1rem;
        }

        .status-strip {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid var(--border-color, #e5e7eb);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin-bottom: 1.2rem;
        }

        .section-title {
            margin: 0.5rem 0 0.75rem;
            font-size: 1.05rem;
            font-weight: 700;
        }

        .insight {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid var(--border-color, #e5e7eb);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            min-height: 105px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }

        .insight-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-color, #6b7280);
            opacity: 0.65;
            font-weight: 700;
        }

        .insight-value {
            font-size: 1.25rem;
            font-weight: 750;
            margin: 0.35rem 0;
            color: var(--text-color, #111827);
        }

        .insight-note {
            font-size: 0.82rem;
            color: var(--text-color, #6b7280);
            opacity: 0.65;
        }

        div[data-testid="stTabs"] button {
            font-weight: 600;
        }

        @media (max-width: 900px) {
            .block-container {
                padding: 1rem 0.75rem 2rem;
            }

            .finops-hero {
                padding: 1.35rem 1.2rem;
                border-radius: 16px;
            }

            .finops-hero h1 {
                font-size: 1.65rem;
            }

            [data-testid="stMetric"] {
                margin-bottom: 0.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
