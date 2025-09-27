# ============================================================================
# FILE: ui/styles/themes.py
# ============================================================================
"""Custom theme and CSS helpers for the Streamlit UI."""

CUSTOM_THEME = {
    "primaryColor": "#4f46e5",
    "backgroundColor": "#f8fafc",
    "secondaryBackgroundColor": "#eef2ff",
    "textColor": "#1e293b",
    "font": "sans serif",
}

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

    :root {
        --primary-500: #4f46e5;
        --primary-600: #4338ca;
        --neutral-50: #f8fafc;
        --neutral-100: #eef2ff;
        --neutral-200: #e2e8f0;
        --neutral-600: #475569;
        --success-500: #22c55e;
        --warning-500: #f59e0b;
        --info-500: #38bdf8;
    }

    html, body, [class^="st"] {
        font-family: 'Inter', sans-serif;
        color: var(--neutral-600);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header branding */
    .app-header {
        padding: 1.5rem 1.75rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%);
        border: 1px solid var(--neutral-200);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .app-header__branding {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header__logo {
        height: 48px;
        width: 48px;
        border-radius: 14px;
        background: var(--primary-500);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .app-header__title {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0;
    }
    .app-header__tagline {
        font-size: 0.95rem;
        color: var(--neutral-600);
        margin: 0;
    }

    /* Buttons */
    .stButton button,
    .stDownloadButton button {
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid transparent;
        background-color: var(--primary-500);
        color: white;
        box-shadow: 0 8px 16px 0 rgba(79, 70, 229, 0.12);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }
    .stButton button:hover,
    .stDownloadButton button:hover {
        background-color: var(--primary-600);
        border-color: var(--primary-600);
        box-shadow: 0 10px 20px 0 rgba(67, 56, 202, 0.18);
    }
    .stButton button:focus,
    .stDownloadButton button:focus {
        outline: 3px solid rgba(79, 70, 229, 0.25);
        outline-offset: 2px;
    }

    /* Secondary button tone */
    .stButton [data-testid="baseButton-secondary"] button {
        background: white;
        color: var(--primary-500);
        border: 1px solid var(--neutral-200);
        box-shadow: none;
    }
    .stButton [data-testid="baseButton-secondary"] button:hover {
        background: var(--neutral-100);
        border-color: var(--primary-500);
    }

    /* Export button group */
    .export-group {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.75rem;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }
    .export-group .stButton button,
    .export-group .stDownloadButton button {
        background-color: white;
        color: var(--neutral-600);
        border: 1px solid var(--neutral-200);
        justify-content: flex-start;
        padding: 0.75rem 1rem;
        font-weight: 500;
        box-shadow: none;
    }
    .export-group .stButton button:hover,
    .export-group .stDownloadButton button:hover {
        background-color: var(--neutral-100);
        color: var(--primary-500);
        border-color: var(--primary-500);
    }

    .export-group .stDownloadButton button .material-icons-outlined,
    .export-group .stButton button .material-icons-outlined {
        font-size: 1.2rem;
    }

    /* Agent selection cards */
    [data-testid="stCheckbox"] > label {
        border: 1px solid var(--neutral-200);
        border-radius: 14px;
        padding: 1rem;
        background: white;
        width: 100%;
        display: flex;
        flex-direction: row;
        gap: 0.75rem;
        align-items: flex-start;
        transition: all 0.2s ease;
        position: relative;
    }
    [data-testid="stCheckbox"] > label:hover {
        border-color: var(--primary-500);
        box-shadow: 0 8px 16px rgba(79, 70, 229, 0.08);
    }
    [data-testid="stCheckbox"] input:checked + div {
        border: none;
    }
    [data-testid="stCheckbox"] input:checked + div + div {
        color: var(--primary-500);
        font-weight: 600;
    }
    [data-testid="stCheckbox"] input:checked ~ span.material-icons-outlined {
        color: var(--primary-500);
    }

    .agent-card-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: var(--neutral-100);
        color: var(--neutral-600);
        border-radius: 12px;
        width: 40px;
        height: 40px;
        flex-shrink: 0;
        font-size: 1.2rem;
    }
    .agent-card-content {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    .agent-card-description {
        font-size: 0.85rem;
        color: #64748b;
    }

    /* Info badges */
    .info-strip {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .info-strip__card {
        flex: 1;
        min-width: 180px;
        border-radius: 14px;
        background: white;
        border: 1px solid var(--neutral-200);
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 6px 12px rgba(15, 23, 42, 0.06);
    }
    .info-strip__icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .info-strip__icon--green { background: #10b981; }
    .info-strip__icon--amber { background: #f59e0b; }
    .info-strip__icon--blue { background: #3b82f6; }
    .info-strip__label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #94a3b8;
        margin-bottom: 0.15rem;
    }
    .info-strip__value {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--neutral-600);
    }

    /* Results cards */
    .result-card {
        border-radius: 16px;
        border: 1px solid var(--neutral-200);
        background: white;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
    }
    .result-card__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .result-card__title {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    .result-card__meta {
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* Session summary */
    .session-summary {
        margin-top: 2rem;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        background: white;
        border: 1px solid var(--neutral-200);
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        flex-wrap: wrap;
    }
    .session-summary__item {
        flex: 1;
        min-width: 160px;
    }
    .session-summary__label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.25rem;
    }
    .session-summary__value {
        font-size: 1.25rem;
        font-weight: 600;
    }

    /* Dividers */
    hr.soft-divider {
        border: none;
        border-top: 1px solid rgba(148, 163, 184, 0.35);
        margin: 1.5rem 0;
    }

    /* Accessibility tweaks */
    button:focus-visible {
        outline: 3px solid rgba(79, 70, 229, 0.35) !important;
    }
</style>
"""

def apply_custom_theme():
    """Apply custom theme to Streamlit app."""
    import streamlit as st
    st.set_page_config(
        page_title="Multi-Agent AI Deep Researcher",
        page_icon="📘",
        layout="wide",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
