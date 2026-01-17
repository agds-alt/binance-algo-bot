"""
Signup/Registration Page
New user registration
"""

import streamlit as st
import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.user_manager import get_user_manager
from modules.auth_helpers import init_session_state, is_authenticated, get_current_user

# Page config
st.set_page_config(
    page_title="Sign Up - BotX",
    page_icon="📝",
    layout="centered"
)

# Initialize session
init_session_state()

# If already logged in, redirect
if is_authenticated():
    st.success(f"✅ Already logged in as **{get_current_user()['username']}**")
    if st.button("Go to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Market_Analysis.py")
    st.stop()


# Signup Form
st.title("📝 Create Your Account")
st.markdown("**BotX** - Join thousands of algo traders!")

st.markdown("---")

with st.form("signup_form", clear_on_submit=True):
    st.subheader("Register")

    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            help="Your full name"
        )

    with col2:
        username = st.text_input(
            "Username *",
            placeholder="johndoe",
            help="Choose a unique username (letters, numbers, underscore only)"
        )

    email = st.text_input(
        "Email *",
        placeholder="john@example.com",
        help="Your email address"
    )

    col1, col2 = st.columns(2)

    with col1:
        password = st.text_input(
            "Password *",
            type="password",
            placeholder="Min. 8 characters",
            help="At least 8 characters"
        )

    with col2:
        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Re-enter password"
        )

    st.markdown("---")

    # Terms checkbox
    terms_accepted = st.checkbox(
        "I agree to the Terms of Service and Privacy Policy",
        help="You must accept to create an account"
    )

    # Marketing checkbox
    marketing = st.checkbox(
        "Send me updates about new features and promotions",
        value=True
    )

    submit = st.form_submit_button("🚀 Create Account", use_container_width=True)

    if submit:
        # Validation
        errors = []

        if not username or not email or not password:
            errors.append("❌ Username, email, and password are required")

        if username and not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            errors.append("❌ Username must be 3-20 characters (letters, numbers, underscore only)")

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("❌ Invalid email format")

        if len(password) < 8:
            errors.append("❌ Password must be at least 8 characters")

        if password != confirm_password:
            errors.append("❌ Passwords do not match")

        if not terms_accepted:
            errors.append("❌ You must accept the Terms of Service")

        # Show errors
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Register user
            with st.spinner("Creating your account..."):
                user_manager = get_user_manager()
                success, message = user_manager.register_user(
                    email=email,
                    username=username,
                    password=password,
                    full_name=full_name if full_name else None
                )

                if success:
                    st.success("🎉 " + message)
                    st.balloons()

                    st.info("**Your account has been created!**")
                    st.markdown("""
                    ### 🎁 Welcome Bonus:
                    - ✅ **FREE Tier** activated
                    - ✅ 1 trade per day
                    - ✅ Paper trading enabled
                    - ✅ Access to BTC/USDT signals

                    ### 🔐 Next Steps:
                    1. Login with your credentials
                    2. Configure your API keys (Settings page)
                    3. Start your first paper trade!
                    """)

                    # Redirect to login
                    if st.button("🔑 Go to Login", use_container_width=True):
                        st.switch_page("pages/0_Login.py")
                else:
                    st.error("❌ " + message)

st.markdown("---")

# Login link
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.info("Already have an account?")
    if st.button("🔑 Login", use_container_width=True):
        st.switch_page("pages/0_Login.py")

# Features comparison
st.markdown("---")
st.markdown("### 💎 Choose Your Plan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **FREE**
    - $0/month
    - 1 trade/day
    - Paper trading
    - BTC/USDT only
    - Community support
    """)

with col2:
    st.markdown("""
    **PRO** ⭐
    - $99/month
    - 20 trades/day
    - Live trading
    - 5 pairs
    - Priority support
    - Backtesting
    """)

with col3:
    st.markdown("""
    **PREMIUM** 💎
    - $249/month
    - Unlimited trades
    - Multi-exchange
    - All pairs
    - VIP support
    - API access
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>BotX - Binance Algo Trading Bot © 2026</div>",
    unsafe_allow_html=True
)
