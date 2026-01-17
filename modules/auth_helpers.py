"""
Authentication Helpers for Streamlit
Session state management and protected pages
"""

import streamlit as st
from typing import Optional, Dict, Callable
from modules.user_manager import get_user_manager


def init_session_state():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    init_session_state()
    return st.session_state.authenticated


def get_current_user() -> Optional[Dict]:
    """Get current logged in user"""
    init_session_state()
    return st.session_state.user


def login_user(user_data: Dict, session_token: str):
    """Set user as logged in"""
    st.session_state.authenticated = True
    st.session_state.user = user_data
    st.session_state.session_token = session_token


def logout_user():
    """Logout current user"""
    user_manager = get_user_manager()

    # Delete session from database
    if st.session_state.session_token:
        user_manager.delete_session(st.session_state.session_token)

    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.session_token = None


def require_auth(func: Callable):
    """Decorator to require authentication for a page"""
    def wrapper(*args, **kwargs):
        init_session_state()

        if not is_authenticated():
            st.warning("⚠️ Please login to access this page")
            st.info("👉 Go to **Login** page from the sidebar")
            st.stop()
        else:
            return func(*args, **kwargs)

    return wrapper


def get_user_tier() -> str:
    """Get current user's tier"""
    user = get_current_user()
    if user:
        return user.get('tier', 'free')
    return 'free'


def require_tier(required_tier: str):
    """Decorator to require specific tier for a page"""
    tier_hierarchy = {
        'free': 0,
        'pro': 1,
        'premium': 2,
        'enterprise': 3
    }

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            require_auth(lambda: None)()  # First check auth

            user_tier = get_user_tier()
            user_level = tier_hierarchy.get(user_tier, 0)
            required_level = tier_hierarchy.get(required_tier, 999)

            if user_level < required_level:
                st.error(f"🔒 This feature requires **{required_tier.upper()}** tier")
                st.info(f"Your current tier: **{user_tier.upper()}**")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💎 Upgrade Now", use_container_width=True):
                        st.switch_page("pages/5_License.py")
                with col2:
                    if st.button("📊 View Plans", use_container_width=True):
                        st.switch_page("pages/5_License.py")

                st.stop()
            else:
                return func(*args, **kwargs)

        return wrapper
    return decorator


def show_user_info_sidebar():
    """Show user info in sidebar"""
    if is_authenticated():
        user = get_current_user()
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Logged In")
            st.markdown(f"**{user['username']}**")
            st.markdown(f"Tier: **{user['tier'].upper()}** 💎")

            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
    else:
        with st.sidebar:
            st.markdown("---")
            st.info("🔐 Please login to continue")
            if st.button("Login", use_container_width=True):
                st.switch_page("pages/0_Login.py")


def check_session_validity():
    """Check if session is still valid"""
    if is_authenticated() and st.session_state.session_token:
        user_manager = get_user_manager()
        valid, user_data = user_manager.validate_session(st.session_state.session_token)

        if not valid:
            # Session expired
            logout_user()
            st.warning("⏰ Your session has expired. Please login again.")
            st.stop()
        else:
            # Update session state with fresh data
            st.session_state.user = user_data
