"""
Telegram Bot Configuration and Testing Page
"""

import streamlit as st
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.telegram_bot import TelegramNotifier, get_telegram_notifier
from modules.license_state import get_license_state
from dotenv import load_dotenv, set_key

load_dotenv()

st.set_page_config(page_title="Telegram Bot", page_icon="📱", layout="wide")

# ===========================================
# LICENSE CHECK
# ===========================================

license_state = get_license_state()
tier = license_state.get_tier()
is_active = license_state.is_active()

# ===========================================
# HEADER
# ===========================================

st.title("📱 Telegram Bot Configuration")
st.markdown("Configure Telegram notifications and test bot commands")

# ===========================================
# TIER INFO
# ===========================================

tier_colors = {
    'free': '🆓',
    'pro': '⭐',
    'premium': '👑',
    'enterprise': '🏢'
}

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info(f"{tier_colors.get(tier, '🆓')} Current Tier: **{tier.upper()}**")
with col2:
    if is_active:
        st.success("✅ Active")
    else:
        st.warning("⚠️ Inactive")

st.markdown("---")

# ===========================================
# CONFIGURATION SECTION
# ===========================================

st.header("⚙️ Configuration")

with st.expander("📘 How to Get Telegram Bot Token", expanded=False):
    st.markdown("""
    ### Step 1: Create a Bot
    1. Open Telegram and search for **@BotFather**
    2. Send `/newbot` command
    3. Follow instructions to name your bot
    4. Copy the **HTTP API Token** provided

    ### Step 2: Get Your Chat ID
    1. Search for **@userinfobot** on Telegram
    2. Start a chat with it
    3. Copy your **Chat ID**

    ### Step 3: Configure Below
    Paste both values in the fields below and click **Save Configuration**.
    """)

# Get current values
current_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
current_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

col1, col2 = st.columns(2)

with col1:
    bot_token = st.text_input(
        "🤖 Bot Token",
        value=current_token,
        type="password",
        help="Get from @BotFather on Telegram"
    )

with col2:
    chat_id = st.text_input(
        "💬 Chat ID",
        value=current_chat_id,
        help="Get from @userinfobot on Telegram"
    )

if st.button("💾 Save Configuration", type="primary", use_container_width=True):
    try:
        env_file = Path(__file__).parent.parent / '.env'

        # Update .env file
        set_key(env_file, 'TELEGRAM_BOT_TOKEN', bot_token)
        set_key(env_file, 'TELEGRAM_CHAT_ID', chat_id)

        # Update environment
        os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
        os.environ['TELEGRAM_CHAT_ID'] = chat_id

        st.success("✅ Configuration saved! Telegram notifications are now enabled.")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to save configuration: {str(e)}")

st.markdown("---")

# ===========================================
# STATUS SECTION
# ===========================================

st.header("📊 Status")

# Initialize notifier
notifier = get_telegram_notifier()

col1, col2, col3 = st.columns(3)

with col1:
    if notifier.enabled:
        st.success("🟢 Telegram Enabled")
    else:
        st.error("🔴 Telegram Disabled")

with col2:
    if bot_token and chat_id:
        st.info("✅ Credentials Configured")
    else:
        st.warning("⚠️ Missing Credentials")

with col3:
    if notifier.bot:
        st.success("🤖 Bot Initialized")
    else:
        st.error("❌ Bot Not Ready")

st.markdown("---")

# ===========================================
# TEST NOTIFICATIONS
# ===========================================

st.header("🧪 Test Notifications")

st.markdown("Send test notifications to verify your Telegram setup:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📨 Test Simple Message", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.send_message("✅ Test message from Binance Algo Bot!"))
                st.success("✅ Message sent! Check your Telegram.")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

    if st.button("📈 Test Trade Entry", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.notify_trade_entry({
                    'symbol': 'BNBUSDT',
                    'side': 'LONG',
                    'entry_price': 245.30,
                    'quantity': 10.5,
                    'stop_loss': 242.00,
                    'take_profit_1': 250.00,
                    'leverage': 5,
                    'risk_usd': 50.00
                }))
                st.success("✅ Trade entry notification sent!")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

    if st.button("🎯 Test Take Profit", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.notify_take_profit({
                    'symbol': 'BNBUSDT',
                    'tp_level': 1,
                    'price': 250.00,
                    'quantity_closed': 5.25,
                    'profit': 45.30,
                    'percentage': 1.84
                }))
                st.success("✅ Take profit notification sent!")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

with col2:
    if st.button("🛑 Test Stop Loss", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.notify_stop_loss({
                    'symbol': 'BNBUSDT',
                    'price': 242.00,
                    'loss': -34.65,
                    'percentage': -1.35,
                    'reason': 'Stop Loss Hit'
                }))
                st.success("✅ Stop loss notification sent!")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

    if st.button("⚠️ Test Risk Warning", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.notify_risk_warning({
                    'type': 'DAILY_LOSS_LIMIT',
                    'message': 'Daily loss limit approaching (4.2% of 5%)',
                    'severity': 'warning'
                }))
                st.success("✅ Risk warning sent!")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

    if st.button("📊 Test Daily Summary", use_container_width=True):
        if not notifier.enabled:
            st.error("❌ Please configure Telegram first!")
        else:
            try:
                asyncio.run(notifier.send_daily_summary({
                    'total_trades': 12,
                    'wins': 8,
                    'losses': 4,
                    'pnl': 234.56,
                    'win_rate': 66.67,
                    'balance': 10234.56
                }))
                st.success("✅ Daily summary sent!")
            except Exception as e:
                st.error(f"❌ Failed to send: {str(e)}")

st.markdown("---")

# ===========================================
# BOT COMMANDS
# ===========================================

st.header("🤖 Bot Commands")

st.markdown("""
Once configured, you can interact with the bot directly on Telegram using these commands:

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and get welcome message |
| `/help` | Show available commands |
| `/status` | Get current bot status and open positions |
| `/balance` | Check account balance |
| `/positions` | View all open positions |
| `/stats` | Get daily trading statistics |
| `/pause` | Pause trading (stop opening new positions) |
| `/resume` | Resume trading |
| `/close` | Close all positions (⚠️ use carefully!) |

**Note:** Bot command functionality will be fully implemented in the live trading module.
""")

st.markdown("---")

# ===========================================
# NOTIFICATION TYPES
# ===========================================

st.header("📬 Notification Types")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Trade Notifications")
    st.markdown("""
    - ✅ **Trade Entry**: When a new position is opened
    - 🎯 **Take Profit**: When TP levels are hit
    - 🛑 **Stop Loss**: When SL is triggered
    - 💼 **Trade Closed**: When position is manually closed
    """)

    st.subheader("Risk Alerts")
    st.markdown("""
    - ⚠️ **Risk Warnings**: General risk alerts
    - 📉 **Daily Loss Limit**: When daily drawdown reached
    - 🚨 **Max Drawdown**: When total drawdown exceeded
    - ❄️ **Cooldown**: Consecutive losses cooldown
    """)

with col2:
    st.subheader("Daily Reports")
    st.markdown("""
    - 📊 **Daily Summary**: End-of-day P&L report
    - 📈 **Performance Stats**: Win rate, trades, profits
    - 💰 **Balance Updates**: Account balance changes
    """)

    st.subheader("System Notifications")
    st.markdown("""
    - 🚀 **Bot Started**: When trading bot starts
    - 🛑 **Bot Stopped**: When trading bot stops
    - ❌ **Errors**: System errors and issues
    - ⚙️ **Updates**: Important system updates
    """)

st.markdown("---")

# ===========================================
# SETTINGS
# ===========================================

st.header("⚙️ Notification Settings")

st.markdown("*Coming soon: Customize which notifications you want to receive*")

notification_settings = {
    'Trade Entry': st.checkbox("📈 Trade Entry Notifications", value=True, disabled=True),
    'Take Profit': st.checkbox("🎯 Take Profit Notifications", value=True, disabled=True),
    'Stop Loss': st.checkbox("🛑 Stop Loss Notifications", value=True, disabled=True),
    'Risk Warnings': st.checkbox("⚠️ Risk Warning Alerts", value=True, disabled=True),
    'Daily Summary': st.checkbox("📊 Daily Summary (8 PM)", value=True, disabled=True),
    'System Alerts': st.checkbox("🔔 System Notifications", value=True, disabled=True),
}

st.info("💡 **Tip**: Make sure to enable notifications on your Telegram app to receive real-time alerts!")

# ===========================================
# FOOTER
# ===========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>📱 Telegram Integration | Binance Algo Bot</p>
    <p>Stay updated with real-time trading notifications</p>
</div>
""", unsafe_allow_html=True)
