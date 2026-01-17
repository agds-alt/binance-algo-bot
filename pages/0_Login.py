"""
Login Page
User authentication and session management
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.user_manager import get_user_manager
from modules.auth_helpers import (
    init_session_state,
    is_authenticated,
    login_user,
    get_current_user
)

# Page config
st.set_page_config(
    page_title="Login - BotX",
    page_icon="🔐",
    layout="centered"
)

# Dark Theme CSS with Green Glow
st.markdown("""
<style>
    /* Dark background - full black */
    .stApp {
        background-color: #000000 !important;
    }

    /* Main content area */
    .main {
        background-color: #000000 !important;
    }

    /* Headers with GREEN GLOW */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41 !important;
        animation: glow 2s ease-in-out infinite;
    }

    /* White text for all content */
    p, .stMarkdown, .stText, label, span, div {
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
    .stTextInput>div>div>input {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #00ff41 !important;
        border-radius: 5px !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    .stTextInput>div>div>input:focus {
        border: 2px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4) !important;
    }

    /* Info boxes - dark with green accent */
    .stAlert, [data-testid="stNotification"] {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        color: #ffffff !important;
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
</style>
""", unsafe_allow_html=True)

# Initialize session
init_session_state()

# If already logged in, redirect to dashboard
if is_authenticated():
    st.success(f"✅ Already logged in as **{get_current_user()['username']}**")
    st.info("Redirecting to Market Analysis...")

    if st.button("Go to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Market_Analysis.py")

    if st.button("🚪 Logout", use_container_width=True):
        from modules.auth_helpers import logout_user
        logout_user()
        st.rerun()

    st.stop()


# Login Form
st.title("🔐 Login to BotX")
st.markdown("**Binance Algo Trading Bot** - Professional Edition")

st.markdown("---")

with st.form("login_form", clear_on_submit=False):
    st.subheader("Sign In")

    username_or_email = st.text_input(
        "Username or Email",
        placeholder="Enter your username or email",
        help="You can login with either your username or email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        help="Enter your account password"
    )

    col1, col2 = st.columns(2)

    with col1:
        remember_me = st.checkbox("Remember me", value=True)

    submit = st.form_submit_button("🔑 Login", use_container_width=True)

    if submit:
        if not username_or_email or not password:
            st.error("❌ Please enter both username/email and password")
        else:
            with st.spinner("Authenticating..."):
                user_manager = get_user_manager()
                success, user_data, message = user_manager.authenticate(
                    username_or_email,
                    password
                )

                if success:
                    # Create session
                    session_token = user_manager.create_session(user_data['id'])

                    # Login user
                    login_user(user_data, session_token)

                    st.success(f"✅ {message}")
                    st.success(f"Welcome back, **{user_data['username']}**!")
                    st.balloons()

                    # Redirect
                    st.info("Redirecting to dashboard...")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

st.markdown("---")

# Sign up link
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.info("Don't have an account?")
    if st.button("📝 Sign Up", use_container_width=True):
        st.switch_page("pages/0_Signup.py")

# Forgot password
with st.expander("🔑 Forgot Password?"):
    st.info("Password reset feature coming soon!")
    st.markdown("For now, please contact support at: **support@botx.com**")

# Features info
st.markdown("---")
st.markdown("### 🚀 Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **FREE Tier:**
    - ✅ 1 trade/day
    - ✅ Paper trading
    - ✅ BTC/USDT only
    - ✅ Basic signals
    """)

with col2:
    st.markdown("""
    **PRO Tier:**
    - 🔥 20 trades/day
    - 🔥 Live trading
    - 🔥 5 trading pairs
    - 🔥 Advanced strategies
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>BotX - Binance Algo Trading Bot © 2026</div>",
    unsafe_allow_html=True
)
