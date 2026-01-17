"""
Dark Theme CSS with Green Glow
Reusable dark theme for all pages
"""

DARK_THEME_CSS = """
<style>
    /* Dark background - full black */
    .stApp {
        background-color: #000000 !important;
    }

    /* Main content area */
    .main {
        background-color: #000000 !important;
    }

    /* Sidebar dark - full black */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #000000 !important;
    }

    /* Sidebar content */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #000000 !important;
    }

    /* Headers with GREEN GLOW */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41 !important;
        animation: glow 2s ease-in-out infinite;
    }

    /* White text for all content */
    p, .stMarkdown, .stText, label, span, div, .stCaption {
        color: #ffffff !important;
    }

    /* Buttons - green neon */
    .stButton>button {
        background: linear-gradient(135deg, #003300 0%, #006600 100%) !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #006600 0%, #009900 100%) !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Input fields - dark with green border */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #00ff41 !important;
        border-radius: 5px !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border: 2px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4) !important;
    }

    /* Metrics - green theme */
    [data-testid="stMetricValue"] {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }

    /* Dataframes/Tables - dark theme */
    .stDataFrame {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
    }

    /* Plotly charts - dark background */
    .js-plotly-plot {
        background-color: #0a0a0a !important;
    }

    /* Cards with green border */
    [data-testid="stVerticalBlock"] > div {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    /* Success messages - green glow */
    .stSuccess {
        background-color: #001a00 !important;
        border: 2px solid #00ff41 !important;
        color: #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
    }

    /* Error messages - red glow */
    .stError {
        background-color: #1a0000 !important;
        border: 2px solid #ff0000 !important;
        color: #ff4444 !important;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.3) !important;
    }

    /* Info boxes - dark with green accent */
    .stInfo, .stAlert, [data-testid="stNotification"] {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    /* Warning - yellow glow */
    .stWarning {
        background-color: #1a1a00 !important;
        border: 2px solid #ffff00 !important;
        color: #ffff00 !important;
        box-shadow: 0 0 15px rgba(255, 255, 0, 0.3) !important;
    }

    /* Expander - dark with green */
    .streamlit-expanderHeader {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        color: #00ff41 !important;
    }

    /* Checkbox */
    .stCheckbox>label {
        color: #ffffff !important;
    }

    /* Forms */
    [data-testid="stForm"] {
        background-color: #0a0a0a !important;
        border: 2px solid #00ff41 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.2) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
        border: 1px solid #00ff41 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #003300 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
    }

    /* Glow animation */
    @keyframes glow {
        0%, 100% {
            text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41;
        }
        50% {
            text-shadow: 0 0 15px #00ff41, 0 0 30px #00ff41, 0 0 45px #00ff41;
        }
    }

    /* Divider */
    hr {
        border-color: #00ff41 !important;
        opacity: 0.3 !important;
    }

    /* Custom section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00ff41 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00ff41;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #00ff41 !important;
        text-shadow: 0 0 20px #00ff41 !important;
        margin-bottom: 0.5rem;
    }

    /* Scrollbar - green theme */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #003300 0%, #006600 100%);
        border-radius: 5px;
        border: 1px solid #00ff41;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #006600 0%, #009900 100%);
    }
</style>
"""


def apply_dark_theme():
    """Apply the dark theme to the current page"""
    import streamlit as st
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
