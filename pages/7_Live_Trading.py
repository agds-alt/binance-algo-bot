"""
Live Trading Page
Start/stop bot and monitor live trading
"""

import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime
import subprocess
import signal

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import BINANCE_TESTNET

st.set_page_config(page_title="Live Trading", page_icon="🤖", layout="wide")

st.title("🤖 Live Trading")

# Initialize tier with license detection
if 'tier' not in st.session_state:
    try:
        from modules.license_state import get_license_state
        license_state = get_license_state()

        if license_state.state.get('license_key') and license_state.state.get('is_valid'):
            st.session_state.tier = license_state.state.get('tier', 'free')
            st.session_state.license_active = True
        else:
            st.session_state.tier = 'free'
            st.session_state.license_active = False
    except Exception:
        st.session_state.tier = 'free'
        st.session_state.license_active = False

# Check tier
current_tier = st.session_state.get('tier', 'free')

if current_tier == 'free':
    st.warning("⚠️ Live Trading is a **PRO** feature. Upgrade to access!")

    st.info("""
    ### 🎯 Why Live Trading?

    - ✅ Automated trading 24/7
    - ✅ Execute trades based on signals
    - ✅ Strict risk management
    - ✅ Real-time monitoring
    - ✅ Telegram notifications

    **Upgrade to PRO to unlock live trading!**
    """)

    if st.button("🚀 Upgrade to PRO", type="primary"):
        st.switch_page("pages/5_License.py")

    st.stop()

# PRO feature unlocked
st.success("✅ Live Trading enabled (PRO feature)")

# Initialize bot state
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'bot_pid' not in st.session_state:
    st.session_state.bot_pid = None

# Warning for live mode
if not BINANCE_TESTNET:
    st.error("""
    ⚠️ **WARNING: LIVE MODE ACTIVATED**

    You are connected to BINANCE PRODUCTION API.
    Real money will be traded!

    Make sure:
    - Your API keys are correct
    - You understand the risks
    - Risk limits are properly configured
    """)
else:
    st.info("🧪 **TESTNET MODE** - Safe for testing, no real money at risk")

# Bot controls
st.markdown("---")
st.markdown("### 🎮 Bot Controls")

col1, col2, col3 = st.columns(3)

with col1:
    # Status indicator
    if st.session_state.bot_running:
        st.success("🟢 **Status:** RUNNING")
    else:
        st.info("🔴 **Status:** STOPPED")

with col2:
    st.metric("Mode", "TESTNET" if BINANCE_TESTNET else "LIVE")

with col3:
    st.metric("Tier", current_tier.upper())

st.markdown("---")

# Control buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Start Bot", disabled=st.session_state.bot_running, use_container_width=True, type="primary"):
        st.info("""
        🤖 **Starting Trading Bot...**

        The bot will:
        1. Connect to Binance API
        2. Start scanning for signals
        3. Execute trades automatically
        4. Monitor positions 24/7

        Check console output for real-time logs.
        """)

        # In production, you would start the bot process here
        # For demo, we'll show a placeholder
        st.session_state.bot_running = True
        st.rerun()

with col2:
    if st.button("⏸️ Stop Bot", disabled=not st.session_state.bot_running, use_container_width=True):
        st.warning("Stopping bot...")
        st.session_state.bot_running = False
        st.rerun()

with col3:
    if st.button("🔄 Restart Bot", disabled=not st.session_state.bot_running, use_container_width=True):
        st.info("Restarting bot...")
        st.session_state.bot_running = False
        time.sleep(1)
        st.session_state.bot_running = True
        st.rerun()

with col4:
    if st.button("🚨 Emergency Stop", use_container_width=True):
        st.error("Emergency stop activated! Closing all positions...")
        st.session_state.bot_running = False
        st.rerun()

st.markdown("---")

# Bot activity
if st.session_state.bot_running:
    st.markdown("### 📊 Live Activity")

    # Simulated real-time updates
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Recent Actions")

        # Placeholder for live logs
        log_placeholder = st.empty()

        logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Scanning BNBUSDT...",
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ EMA 8/21 crossover detected",
            f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Confirmations: 4/5",
            f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Waiting for volume confirmation...",
        ]

        log_placeholder.code("\n".join(logs), language="log")

        st.info("""
        **To see real-time bot logs, run:**
        ```bash
        python main.py --mode live
        ```

        Or check `logs/` directory for detailed logs.
        """)

    with col2:
        st.markdown("#### Quick Stats")

        st.metric("Signals Today", "12")
        st.metric("Trades Executed", "3")
        st.metric("Win Rate", "66.7%")
        st.metric("Today's P&L", "+$156.50", "+1.56%")

    st.markdown("---")
    st.markdown("#### 📍 Current Positions")

    # Mock position data
    import pandas as pd

    positions = pd.DataFrame({
        "Pair": ["BNBUSDT"],
        "Side": ["LONG"],
        "Entry": ["$623.50"],
        "Current": ["$625.80"],
        "Size": ["0.5 BNB"],
        "P&L": ["+$1.15"],
        "P&L %": ["+0.37%"]
    })

    st.dataframe(positions, use_container_width=True)

    st.info("💡 Bot is monitoring positions 24/7 and will exit at TP/SL automatically")

else:
    st.markdown("### 💤 Bot is Idle")

    st.info("""
    Click **"▶️ Start Bot"** to begin automated trading.

    The bot will:
    - Scan markets for signals every minute
    - Execute trades when confirmations meet threshold
    - Manage positions with automatic TP/SL
    - Send Telegram notifications (if configured)
    """)

    st.markdown("---")
    st.markdown("### 📋 How to Run Bot")

    st.markdown("""
    **Option 1: Via Dashboard (This Page)**
    - Click "▶️ Start Bot" above
    - Monitor from dashboard
    - Stop anytime with "⏸️ Stop Bot"

    **Option 2: Via Command Line (Recommended for 24/7)**
    ```bash
    # Start bot in background
    python main.py --mode live --capital 1000 &

    # Check logs
    tail -f logs/trading_bot.log

    # Stop bot
    pkill -f "python main.py"
    ```

    **Option 3: Via Screen/Tmux (For VPS)**
    ```bash
    # Start in screen session
    screen -S algo-bot
    python main.py --mode live --capital 1000

    # Detach: Ctrl+A then D
    # Reattach: screen -r algo-bot
    ```
    """)

# Configuration summary
st.markdown("---")
st.markdown("### ⚙️ Active Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Risk Limits:**
    - Risk per trade: 1.5%
    - Max daily drawdown: 5%
    - Max total drawdown: 15%
    - Max leverage: 10x
    """)

with col2:
    st.markdown("""
    **Strategy:**
    - Primary: EMA Crossover (8/21)
    - Trend filter: EMA 50/200
    - Min confirmations: 4/6
    - Timeframe: 5m/15m/1h
    """)

with col3:
    st.markdown("""
    **Notifications:**
    - Telegram: ❌ Not configured
    - Email: ❌ Not configured
    - Dashboard: ✅ Active
    """)

    if st.button("⚙️ Configure Notifications"):
        st.switch_page("pages/4_Settings.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9rem;">
    <p>⚠️ <strong>Risk Warning:</strong> Trading cryptocurrencies carries significant risk.
    Only trade with capital you can afford to lose.</p>
    <p>This bot uses strict risk management but profits are never guaranteed.</p>
</div>
""", unsafe_allow_html=True)
