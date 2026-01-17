"""
License Management Page
User-based license activation and tier management
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.auth_helpers import require_auth, get_current_user, show_user_info_sidebar
from modules.user_manager import get_user_manager
from modules.license_manager import LicenseManager

st.set_page_config(page_title="License", page_icon="🔐", layout="wide")

# Require authentication
@require_auth
def main():
    # Show user info in sidebar
    show_user_info_sidebar()

    # Enhanced CSS
    st.markdown("""
    <style>
        .section-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1f2937;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #e5e7eb;
        }
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .tier-card {
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border: 2px solid;
        }
    </style>
    """, unsafe_allow_html=True)

    # Get current user
    user = get_current_user()
    user_manager = get_user_manager()
    license_manager = LicenseManager()

    st.markdown('<div class="main-title">🔐 License Management</div>', unsafe_allow_html=True)
    st.caption(f"Manage your subscription • User: **{user['username']}**")

    # Current tier status
    tier_colors = {
        'free': '#95a5a6',
        'pro': '#3498db',
        'premium': '#9b59b6',
        'enterprise': '#e74c3c'
    }

    tier_names = {
        'free': 'FREE',
        'pro': 'PRO',
        'premium': 'PREMIUM',
        'enterprise': 'ENTERPRISE'
    }

    current_tier = user.get('tier', 'free')

    # Tier badge
    st.markdown(f"""
    <div style='background: {tier_colors[current_tier]}; padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
        <h2>Current Tier: {tier_names[current_tier]}</h2>
        <p>{"📝 Paper trading only" if current_tier == 'free' else "🚀 Live trading enabled"}</p>
    </div>
    """, unsafe_allow_html=True)

    # License activation section
    st.markdown('<div class="section-header">🔑 Activate License</div>', unsafe_allow_html=True)

    # Check if user already has a license
    if user.get('license_key'):
        st.success(f"✅ **Active License:** `{user['license_key']}`")
        st.info(f"**Current Tier:** {current_tier.upper()}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Change License", use_container_width=True):
                # Allow changing license
                st.session_state.show_license_form = True
                st.rerun()

        with col2:
            if st.button("❌ Deactivate License", use_container_width=True, type="secondary"):
                # Deactivate license
                user_manager.update_user_tier(user['id'], 'free', None)
                st.session_state.user['tier'] = 'free'
                st.session_state.user['license_key'] = None
                st.success("License deactivated! Reverted to FREE tier.")
                st.rerun()
    else:
        st.session_state.show_license_form = True

    # Show license activation form
    if st.session_state.get('show_license_form', False):
        with st.form("activate_license"):
            st.subheader("Enter License Key")

            license_key = st.text_input(
                "License Key",
                placeholder="PRO-XXXX-XXXX-XXXX-XXXX-XXXX",
                help="Enter your license key (format: TIER-XXXX-XXXX-XXXX-XXXX-XXXX)"
            )

            email = st.text_input(
                "Email (for verification)",
                value=user['email'],
                disabled=True,
                help="Email must match license registration"
            )

            submit = st.form_submit_button("✅ Activate License", use_container_width=True)

            if submit:
                if not license_key:
                    st.error("❌ Please enter a license key")
                else:
                    with st.spinner("Validating license..."):
                        # Validate license
                        success, message = license_manager.activate(license_key, user['email'])

                        if success:
                            # Get license info to determine tier
                            license_info = license_manager.get_license_info(license_key)

                            if license_info:
                                tier = license_info['tier']

                                # Update user's tier and license
                                user_manager.update_user_tier(user['id'], tier, license_key)

                                # Update session state
                                st.session_state.user['tier'] = tier
                                st.session_state.user['license_key'] = license_key
                                st.session_state.tier = tier

                                st.success(f"🎉 {message}")
                                st.success(f"**Tier Upgraded to: {tier.upper()}!**")
                                st.balloons()

                                # Hide form
                                st.session_state.show_license_form = False
                                st.rerun()
                            else:
                                st.error("❌ Could not retrieve license info")
                        else:
                            st.error(f"❌ {message}")

    # Pricing comparison
    st.markdown('<div class="section-header">💎 Upgrade Plans</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="tier-card" style="border-color: #95a5a6;">
            <h3 style="color: #95a5a6;">FREE</h3>
            <h2>$0<span style="font-size: 1rem;">/month</span></h2>
            <hr>
            <ul style="text-align: left;">
                <li>✅ 1 trade/day</li>
                <li>✅ Paper trading</li>
                <li>✅ BTC/USDT only</li>
                <li>✅ Basic signals</li>
                <li>✅ Community support</li>
            </ul>
            <p style="margin-top: 1rem; font-weight: bold;">Current Plan</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tier-card" style="border-color: #3498db;">
            <h3 style="color: #3498db;">PRO ⭐</h3>
            <h2>$99<span style="font-size: 1rem;">/month</span></h2>
            <hr>
            <ul style="text-align: left;">
                <li>🔥 20 trades/day</li>
                <li>🔥 Live trading</li>
                <li>🔥 5 trading pairs</li>
                <li>🔥 Advanced strategies</li>
                <li>🔥 Backtesting engine</li>
                <li>🔥 Priority support</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Most Popular!</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="tier-card" style="border-color: #9b59b6;">
            <h3 style="color: #9b59b6;">PREMIUM 💎</h3>
            <h2>$249<span style="font-size: 1rem;">/month</span></h2>
            <hr>
            <ul style="text-align: left;">
                <li>🚀 Unlimited trades</li>
                <li>🚀 Multi-exchange</li>
                <li>🚀 All pairs</li>
                <li>🚀 Custom strategies</li>
                <li>🚀 API access</li>
                <li>🚀 VIP support</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>For Professionals</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Contact support
    st.markdown("---")
    st.info("**Need a license?** Contact sales at: **sales@botx.com**")

    # FAQ
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **How do I get a license key?**
        Contact our sales team at sales@botx.com

        **Can I use one license on multiple devices?**
        - FREE: 1 device
        - PRO: 1 device
        - PREMIUM: 2 devices
        - ENTERPRISE: Unlimited

        **What payment methods do you accept?**
        - Credit Card
        - Cryptocurrency (USDT, BTC)
        - Bank Transfer (Enterprise)

        **Can I cancel anytime?**
        Yes! No long-term commitments. Cancel anytime.

        **Is there a refund policy?**
        7-day money-back guarantee for all paid plans.
        """)

main()
