"""
License Management Page
Real license activation and tier management
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.license_state import get_license_state

st.set_page_config(page_title="License", page_icon="🔐", layout="wide")

# Initialize license state
license_state = get_license_state()

# Validate and get current tier
is_valid, validation_msg, current_tier = license_state.validate()
license_info = license_state.get_license_info()

st.title("🔐 License Management")

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

# Tier badge
st.markdown(f"""
<div style='background: {tier_colors[current_tier]}; padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
    <h2>Current Tier: {tier_names[current_tier]}</h2>
    <p>{"📝 Paper trading only" if current_tier == 'free' else "🚀 Live trading enabled"}</p>
</div>
""", unsafe_allow_html=True)

# License activation section
st.markdown("### 🔑 License Activation")

# Show current license info if activated
if license_info:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", "🟢 Active" if license_info['is_active'] and not license_info['is_expired'] else "🔴 Inactive")

    with col2:
        st.metric("Days Remaining", license_info['days_remaining'])

    with col3:
        st.metric("Activations", f"{license_info['activation_count']} / {license_info['max_activations']}")

    with st.expander("📋 License Details", expanded=False):
        st.markdown(f"""
**License Key:** `{license_info['license_key']}`

**Account Information:**
- Email: {license_info['email']}
- Tier: {license_info['tier']}

**Dates:**
- Issued: {license_info['issued_date']}
- Expires: {license_info['expiry_date']}

**Device Information:**
- Hardware ID: `{license_info['hardware_id'] or 'Not bound'}`
- Locally Activated: {license_info.get('locally_activated_at', 'N/A')[:10] if license_info.get('locally_activated_at') else 'N/A'}
- Last Validated: {license_info.get('last_validated', 'N/A')[:10] if license_info.get('last_validated') else 'N/A'}
        """)

    # Deactivate button
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🔓 Deactivate License", use_container_width=True):
            success, message = license_state.deactivate()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

else:
    # Activation form
    st.info("💡 Enter your license key below to unlock PRO or PREMIUM features")

    license_key_input = st.text_input(
        "License Key",
        placeholder="PRO-XXXX-XXXX-XXXX-XXXX-ABCD",
        help="Enter the license key you received after purchase"
    )

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("✅ Activate License", type="primary", use_container_width=True):
            if license_key_input:
                with st.spinner("Activating license..."):
                    success, message = license_state.activate(license_key_input)

                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Activation failed: {message}")
            else:
                st.warning("⚠️ Please enter a license key")

    st.markdown("---")
    st.markdown("**Don't have a license?** Choose a plan below to get started!")

# Pricing tiers
st.markdown("### 💰 Pricing & Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='border: 2px solid #95a5a6; border-radius: 10px; padding: 1.5rem; height: 100%;'>
        <h3 style='color: #95a5a6;'>FREE</h3>
        <h2>$0<small>/month</small></h2>

        <strong>Features:</strong>
        <ul>
            <li>📊 Paper trading</li>
            <li>💰 Max $100/trade</li>
            <li>📈 3 trades/day</li>
            <li>🔄 1 position</li>
            <li>🪙 BTC/USDT only</li>
            <li>📚 Community support</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.button("Current Plan" if current_tier == 'free' else "Downgrade", disabled=True, use_container_width=True)

with col2:
    is_current_plan = current_tier == 'pro'

    st.markdown(f"""
    <div style='border: {"3px" if is_current_plan else "2px"} solid #3498db; border-radius: 10px; padding: 1.5rem; height: 100%; background: {"#ecf0f1" if is_current_plan else "white"};'>
        <h3 style='color: #3498db;'>PRO ⭐</h3>
        <h2 style='color: #3498db;'>$99<small>/month</small></h2>

        <strong>Features:</strong>
        <ul>
            <li>🚀 <strong>Live trading</strong></li>
            <li>💰 Max $5k/trade</li>
            <li>📈 20 trades/day</li>
            <li>🔄 3 concurrent positions</li>
            <li>🪙 5 trading pairs</li>
            <li>📊 Backtesting</li>
            <li>⚡ Priority support</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if current_tier == 'free':
        if st.button("🚀 Get PRO License", type="primary", use_container_width=True):
            st.info("💳 Contact sales@algobot.com to purchase a PRO license")
    elif is_current_plan:
        st.button("✅ Current Plan", disabled=True, use_container_width=True)
    else:
        st.button("Downgrade to PRO", use_container_width=True, disabled=True)

with col3:
    is_current_plan = current_tier == 'premium'

    st.markdown(f"""
    <div style='border: {"3px" if is_current_plan else "2px"} solid #9b59b6; border-radius: 10px; padding: 1.5rem; height: 100%; background: {"#ecf0f1" if is_current_plan else "white"};'>
        <h3 style='color: #9b59b6;'>PREMIUM</h3>
        <h2>$249<small>/month</small></h2>

        <strong>Features:</strong>
        <ul>
            <li>✨ Everything in PRO</li>
            <li>💰 Unlimited position size</li>
            <li>📈 Unlimited trades</li>
            <li>🔄 10 positions</li>
            <li>🪙 All pairs</li>
            <li>🌐 Multi-exchange</li>
            <li>🎯 Custom strategies</li>
            <li>📞 VIP support 24/7</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if current_tier in ['free', 'pro']:
        if st.button("💎 Get PREMIUM License", use_container_width=True):
            st.info("💳 Contact sales@algobot.com to purchase a PREMIUM license")
    elif is_current_plan:
        st.button("✅ Current Plan", disabled=True, use_container_width=True)

# Payment methods
st.markdown("---")
st.markdown("### 💳 Payment Methods")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**💳 Credit Card**")
    st.markdown("Visa, Mastercard, Amex")

with col2:
    st.markdown("**₿ Cryptocurrency**")
    st.markdown("BTC, ETH, USDT")

with col3:
    st.markdown("**🏦 Bank Transfer**")
    st.markdown("For Enterprise")

with col4:
    st.markdown("**💰 Stripe**")
    st.markdown("Recurring billing")

# Trial information
if current_tier == 'free':
    st.markdown("---")
    st.info("""
    ### 🎁 Free Trial Available!

    **7-Day PRO Trial** - Try live trading risk-free!

    Contact us to request your trial license.
    """)

# FAQ
st.markdown("---")
st.markdown("### ❓ Frequently Asked Questions")

with st.expander("How do I get a license key?"):
    st.markdown("""
    **Option 1: Purchase**
    - Contact sales@algobot.com
    - Choose your tier (PRO or PREMIUM)
    - Receive license key via email

    **Option 2: Trial**
    - Request 7-day PRO trial
    - Get trial license key
    - Upgrade to paid anytime

    **Option 3: Admin Generated**
    - If you're the admin, use `python admin_license.py generate`
    """)

with st.expander("Can I use my license on multiple devices?"):
    st.markdown("""
    Each license is bound to one device by default.

    **Multi-Device Options:**
    - PRO: 1 device included, up to 2 devices available
    - PREMIUM: Up to 3 devices
    - ENTERPRISE: Custom device limits

    Contact sales to add additional device activations.
    """)

with st.expander("What happens when my license expires?"):
    st.markdown("""
    When your license expires:
    - 🔴 Bot switches to FREE tier automatically
    - 📊 Live trading is disabled (paper trading only)
    - 💾 All your data and settings are preserved
    - 🔄 Renew anytime to restore access

    **Auto-Renewal:**
    - Set up auto-renewal for uninterrupted service
    - Email notification 7 days before expiry
    """)

with st.expander("Can I upgrade or downgrade my tier?"):
    st.markdown("""
    **Upgrading:**
    - ✅ Available anytime
    - Pro-rated billing
    - Instant tier change
    - Contact sales@algobot.com

    **Downgrading:**
    - ⏰ Takes effect at next billing cycle
    - No refunds for remaining period
    - Data remains intact
    """)

with st.expander("What if I need to deactivate my license?"):
    st.markdown("""
    **Deactivation:**
    - Use the "🔓 Deactivate License" button above
    - Frees up the device slot
    - Can reactivate on same or different device
    - License remains valid until expiry

    **Use Cases:**
    - Switching to a new computer
    - Reinstalling the bot
    - Temporary deactivation
    """)

st.markdown("---")

# Support contact
st.markdown("""
<div style='background: #ecf0f1; padding: 1.5rem; border-radius: 10px; text-align: center;'>
    <h3>💬 Need Help?</h3>
    <p>Contact our support team for assistance with licenses, billing, or technical issues.</p>
    <p>
        📧 <strong>sales@algobot.com</strong> |
        💬 <strong>Telegram: @algobotSupport</strong> |
        🌐 <strong>docs.algobot.com</strong>
    </p>
</div>
""", unsafe_allow_html=True)
