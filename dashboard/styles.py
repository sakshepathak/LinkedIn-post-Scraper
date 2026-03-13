"""
Custom CSS for the LinkedIn Post Scout dashboard.
All styling is centralised here to keep app.py clean.
"""

CUSTOM_CSS = """
<style>
    /* ── Typography ─────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Hide Streamlit deploy bar & hamburger menu chrome ───────────── */
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
    }
    [data-testid="stStatusWidget"],
    [data-testid="stToolbar"],
    [data-testid="stDeployButton"],
    #MainMenu,
    div[data-testid="stDecoration"],
    .stDeployButton,
    button[kind="header"],
    header .stActionButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* ── Global background ──────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(145deg, #0d0d0d 0%, #1a0a14 40%, #12080f 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(13, 8, 12, 0.97);
        border-right: 1px solid rgba(255, 60, 120, 0.12);
    }

    /* ── Primary button → pink gradient ─────────────────────────────── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #ff3c78, #ff7eb3) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 18px rgba(255, 60, 120, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(255, 60, 120, 0.4) !important;
        filter: brightness(1.08) !important;
    }
    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="stBaseButton-primary"]:active {
        transform: translateY(0px) !important;
    }

    /* ── Secondary button → subtle outline ──────────────────────────── */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {
        background: rgba(255, 60, 120, 0.06) !important;
        color: #ff7eb3 !important;
        border: 1px solid rgba(255, 60, 120, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(255, 60, 120, 0.12) !important;
        border-color: rgba(255, 60, 120, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Default / tertiary buttons (e.g. Clear Data) ───────────────── */
    .stButton > button {
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }

    /* ── Expander ───────────────────────────────────────────────────── */
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255, 60, 120, 0.1);
        border-radius: 12px;
    }

    /* ── Text inputs / sliders ──────────────────────────────────────── */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255, 60, 120, 0.15) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 60, 120, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(255, 60, 120, 0.1) !important;
    }
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #ff3c78, #ff7eb3) !important;
    }

    /* ── Post Card ──────────────────────────────────────────────────── */
    .post-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 60, 120, 0.1);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.25s ease;
    }
    .post-card:hover {
        border-color: rgba(255, 60, 120, 0.45);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(255, 60, 120, 0.08);
    }

    /* ── Badges ─────────────────────────────────────────────────────── */
    .author-badge {
        background: linear-gradient(135deg, #ff3c78, #e8356a);
        color: white;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .date-badge {
        background: rgba(255, 60, 120, 0.12);
        color: #ffa0bc;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.78rem;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .search-keyword {
        background: rgba(255, 60, 120, 0.15);
        color: #ffb3cc;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }

    /* ── Metric Cards ──────────────────────────────────────────────── */
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255, 60, 120, 0.12);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: all 0.25s ease;
    }
    .metric-card:hover {
        border-color: rgba(255, 60, 120, 0.35);
        box-shadow: 0 4px 20px rgba(255, 60, 120, 0.06);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ff3c78, #ff7eb3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* ── Dialog section blocks (how-it-works) ───────────────────────── */
    .section-block {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 60, 120, 0.08);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .section-title {
        color: #ffa0bc;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .section-text {
        color: #c4b5bd;
        font-size: 0.92rem;
        line-height: 1.75;
    }

    /* ── Scrollbar polish ──────────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 60, 120, 0.2);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 60, 120, 0.35);
    }

    /* ── Selectbox ──────────────────────────────────────────────────── */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255, 60, 120, 0.15) !important;
        border-radius: 10px !important;
    }

    /* ── Sidebar footer text ───────────────────────────────────────── */
    .sidebar-footer {
        text-align: center;
        color: #64748b;
        font-size: 0.75rem;
    }
</style>
"""


def inject_css():
    """Inject all custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
