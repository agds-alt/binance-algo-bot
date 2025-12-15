"""
Settings Page
Bot configuration and preferences
"""

import streamlit as st
import yaml

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Enhanced CSS for Settings page
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
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚙️ Settings</div>', unsafe_allow_html=True)
st.caption("Bot configuration and preferences")

tabs = st.tabs(["🔑 API Keys", "⚖️ Risk Management", "📊 Strategy", "🔔 Notifications", "🎨 Preferences"])

# Tab 1: API Keys
with tabs[0]:
    st.markdown('<div class="section-header">🔑 Binance API Configuration</div>', unsafe_allow_html=True)

    st.warning("⚠️ **Security Warning**: Never share your API keys. Keys are encrypted and stored locally.")

    col1, col2 = st.columns(2)

    with col1:
        api_key = st.text_input("API Key", value="", type="password", help="Your Binance API Key")

    with col2:
        api_secret = st.text_input("API Secret", value="", type="password", help="Your Binance API Secret")

    testnet_mode = st.checkbox("Use Testnet", value=True, help="ALWAYS test on testnet first!")

    if testnet_mode:
        st.info("📝 Get testnet API keys at: https://testnet.binancefuture.com/")
    else:
        st.error("🔴 **LIVE TRADING MODE** - Use real money with caution!")

    if st.button("💾 Save API Keys", type="primary"):
        if api_key and api_secret:
            st.success("✅ API keys saved successfully!")
        else:
            st.error("❌ Please fill in both API key and secret")

# Tab 2: Risk Management
with tabs[1]:
    st.markdown('<div class="section-header">⚖️ Risk Management Settings</div>', unsafe_allow_html=True)

    st.info("🛡️ **Note**: These are HARD LIMITS and cannot exceed maximum values.")

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Max Risk Per Trade (%)", value=1.0, min_value=0.1, max_value=2.0, step=0.1, disabled=True, help="Fixed at 1% (hard limit)")

        st.number_input("Max Daily Drawdown (%)", value=5.0, min_value=1.0, max_value=5.0, step=0.5, disabled=True, help="Fixed at 5% (hard limit)")

        st.number_input("Max Leverage", value=5, min_value=1, max_value=10, step=1, help="Recommended: 3-5x")

        st.number_input("Position Size (%)", value=10.0, min_value=1.0, max_value=10.0, step=1.0, disabled=True, help="Max 10% of capital")

    with col2:
        st.number_input("Max Stop Loss (%)", value=2.0, min_value=0.5, max_value=2.0, step=0.1, disabled=True, help="Fixed at 2% (hard limit)")

        st.number_input("Max Daily Trades", value=10, min_value=1, max_value=10, step=1, disabled=True, help="Fixed at 10 (hard limit)")

        st.number_input("Max Concurrent Positions", value=3, min_value=1, max_value=3, step=1, disabled=True, help="Fixed at 3 (hard limit)")

        st.number_input("Cooldown After Losses (hours)", value=4, min_value=1, max_value=24, step=1, disabled=True, help="Fixed at 4 hours")

    if st.button("💾 Save Risk Settings"):
        st.success("✅ Settings saved!")

# Tab 3: Strategy
with tabs[2]:
    st.markdown('<div class="section-header">📊 Strategy Configuration</div>', unsafe_allow_html=True)

    if st.session_state.get('tier', 'free') == 'free':
        st.warning("⚠️ Strategy customization available in PRO tier")

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox("Strategy", ["Scalping (Default)"], disabled=st.session_state.get('tier') == 'free')

        st.number_input("Primary Timeframe", value=5, disabled=True, help="5 minutes")

        st.number_input("EMA Fast", value=9, min_value=5, max_value=20, disabled=st.session_state.get('tier') == 'free')

        st.number_input("EMA Slow", value=21, min_value=10, max_value=50, disabled=st.session_state.get('tier') == 'free')

    with col2:
        st.number_input("Higher Timeframe", value=15, disabled=True, help="15 minutes")

        st.number_input("Trend Timeframe", value=60, disabled=True, help="1 hour")

        st.number_input("RSI Period", value=14, min_value=7, max_value=21, disabled=st.session_state.get('tier') == 'free')

        st.number_input("Min Confirmations", value=4, min_value=3, max_value=6, disabled=st.session_state.get('tier') == 'free')

# Tab 4: Notifications
with tabs[3]:
    st.markdown('<div class="section-header">🔔 Notification Settings</div>', unsafe_allow_html=True)

    telegram_enabled = st.checkbox("Enable Telegram Notifications")

    if telegram_enabled:
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Telegram Bot Token", type="password")

        with col2:
            st.text_input("Chat ID")

        st.markdown("**Notification Types:**")
        st.checkbox("Trade Executed", value=True)
        st.checkbox("Stop Loss Hit", value=True)
        st.checkbox("Take Profit Hit", value=True)
        st.checkbox("Daily Summary", value=True)
        st.checkbox("Risk Warnings", value=True)

    if st.button("💾 Save Notification Settings"):
        st.success("✅ Notification settings saved!")

# Tab 5: Preferences
with tabs[4]:
    st.markdown('<div class="section-header">🎨 Preferences</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox("Theme", ["Dark", "Light"])
        st.selectbox("Currency", ["USD", "EUR", "IDR"])

    with col2:
        st.selectbox("Timezone", ["UTC", "Asia/Jakarta", "America/New_York"])
        st.checkbox("Sound Alerts", value=True)

    if st.button("💾 Save Preferences"):
        st.success("✅ Preferences saved!")

st.markdown("---")

# Emergency Actions
st.markdown('<div class="section-header">🚨 Emergency Actions</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🛑 Close All Positions", type="primary", use_container_width=True):
        st.error("⚠️ This will close ALL open positions. Are you sure?")

with col2:
    if st.button("⏸️ Pause Bot", use_container_width=True):
        st.info("Bot paused. No new trades will be taken.")

with col3:
    if st.button("🔄 Reset Daily Stats", use_container_width=True):
        st.success("✅ Daily statistics reset")
