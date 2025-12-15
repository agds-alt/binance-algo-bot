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
import os
import psutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import BINANCE_TESTNET
from modules.bot_state_manager import get_bot_state_manager

st.set_page_config(page_title="Live Trading", page_icon="🤖", layout="wide")

# Enhanced CSS for Live Trading page
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
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 Live Trading</div>', unsafe_allow_html=True)
st.caption("Start, stop, and monitor automated trading bot")

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

# Initialize bot state manager
state_manager = get_bot_state_manager()

# Get actual bot state from state manager
bot_state = state_manager.get_bot_state()
is_bot_running = bot_state.is_running

# Check if bot process is actually running
if is_bot_running and bot_state.pid:
    try:
        # Verify process is actually running
        if not psutil.pid_exists(bot_state.pid):
            # Process died, update state
            state_manager.stop_bot()
            bot_state = state_manager.get_bot_state()
            is_bot_running = False
    except:
        pass

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
st.markdown('<div class="section-header">🎮 Bot Controls</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Status indicator from actual bot state
    if is_bot_running:
        st.success(f"🟢 **Status:** RUNNING (PID: {bot_state.pid})")
        # Update uptime
        state_manager.update_uptime()
        bot_state = state_manager.get_bot_state()
        uptime_mins = bot_state.uptime_seconds // 60
        st.caption(f"⏱️ Uptime: {uptime_mins} minutes")
    else:
        st.info("🔴 **Status:** STOPPED")

with col2:
    st.metric("Mode", bot_state.mode.upper() if is_bot_running else ("TESTNET" if BINANCE_TESTNET else "LIVE"))
    if is_bot_running and bot_state.started_at:
        started = datetime.fromisoformat(bot_state.started_at)
        st.caption(f"Started: {started.strftime('%H:%M:%S')}")

with col3:
    st.metric("Tier", current_tier.upper())
    if is_bot_running:
        st.caption(f"💰 Capital: ${bot_state.capital:,.2f}")

st.markdown("---")

# Control buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Start Bot", disabled=is_bot_running, use_container_width=True, type="primary"):
        try:
            # Get initial capital from config or user input
            initial_capital = 10000  # Default $10k
            mode = "testnet" if BINANCE_TESTNET else "live"

            # Start bot process in background
            bot_script = Path(__file__).parent.parent / "main.py"

            if bot_script.exists():
                # Start bot as subprocess
                process = subprocess.Popen(
                    ["python", str(bot_script), "--mode", mode, "--capital", str(initial_capital)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(bot_script.parent)
                )

                # Update state
                state_manager.start_bot(
                    pid=process.pid,
                    mode=mode,
                    capital=initial_capital
                )

                st.success(f"✅ Bot started successfully! PID: {process.pid}")
                st.info("""
                🤖 **Trading Bot Started**

                The bot will:
                1. Connect to Binance API
                2. Start scanning for signals
                3. Execute trades automatically
                4. Monitor positions 24/7

                Check logs/ directory for real-time logs.
                """)
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ main.py not found. Please ensure the bot script exists.")
        except Exception as e:
            st.error(f"❌ Failed to start bot: {e}")

with col2:
    if st.button("⏸️ Stop Bot", disabled=not is_bot_running, use_container_width=True):
        try:
            if bot_state.pid:
                # Try to terminate gracefully first
                try:
                    os.kill(bot_state.pid, signal.SIGTERM)
                    st.warning("⏸️ Sending stop signal to bot...")
                    time.sleep(2)

                    # If still running, force kill
                    if psutil.pid_exists(bot_state.pid):
                        os.kill(bot_state.pid, signal.SIGKILL)
                except:
                    pass

            # Update state
            state_manager.stop_bot()
            st.success("✅ Bot stopped successfully")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to stop bot: {e}")
            # Update state anyway
            state_manager.stop_bot()
            st.rerun()

with col3:
    if st.button("🔄 Restart Bot", disabled=not is_bot_running, use_container_width=True):
        try:
            # Stop current bot
            if bot_state.pid:
                try:
                    os.kill(bot_state.pid, signal.SIGTERM)
                    time.sleep(1)
                except:
                    pass

            state_manager.stop_bot()
            time.sleep(1)

            # Start new bot
            initial_capital = bot_state.capital or 10000
            mode = bot_state.mode or ("testnet" if BINANCE_TESTNET else "live")

            bot_script = Path(__file__).parent.parent / "main.py"
            if bot_script.exists():
                process = subprocess.Popen(
                    ["python", str(bot_script), "--mode", mode, "--capital", str(initial_capital)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(bot_script.parent)
                )

                state_manager.start_bot(
                    pid=process.pid,
                    mode=mode,
                    capital=initial_capital
                )

                st.success(f"✅ Bot restarted successfully! PID: {process.pid}")
                time.sleep(2)
                st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to restart bot: {e}")

with col4:
    if st.button("🚨 Emergency Stop", use_container_width=True):
        try:
            # Force kill bot immediately
            if is_bot_running and bot_state.pid:
                try:
                    os.kill(bot_state.pid, signal.SIGKILL)
                except:
                    pass

            # Close all positions (if any)
            positions = state_manager.get_positions()
            if positions:
                st.error(f"⚠️ Emergency stop! Found {len(positions)} open positions.")
                # TODO: Close positions via exchange API
                # For now, just clear from state
                state_manager.set_positions([])

            # Update state
            state_manager.stop_bot()
            st.success("✅ Emergency stop executed!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Emergency stop error: {e}")
            state_manager.stop_bot()
            st.rerun()

st.markdown("---")

# Bot activity
if is_bot_running:
    st.markdown('<div class="section-header">📊 Live Activity</div>', unsafe_allow_html=True)

    # Get real-time stats from state manager
    stats = state_manager.get_stats()
    positions = state_manager.get_positions()
    recent_trades = state_manager.get_trades(limit=10)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Recent Actions")

        # Check if log file exists and show last 10 lines
        log_file = Path("logs/trading_bot.log")
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_logs = lines[-10:] if len(lines) > 10 else lines
                    st.code("".join(recent_logs), language="log")
            except:
                st.info("📋 Bot logs will appear here when bot starts generating activity.")
        else:
            st.info("""
            📋 **Bot Activity Logs**

            Logs will appear here once the bot starts:
            - Market scanning
            - Signal detection
            - Trade execution
            - Position management

            Log file: `logs/trading_bot.log`
            """)

    with col2:
        st.markdown("#### Quick Stats")

        # Real stats from state manager
        st.metric("Signals Today", stats.signals_today)
        st.metric("Trades Today", stats.today_trades)
        st.metric("Win Rate", f"{stats.win_rate:.1f}%")

        today_pnl_pct = (stats.today_pnl / bot_state.capital * 100) if bot_state.capital > 0 else 0
        st.metric(
            "Today's P&L",
            f"${stats.today_pnl:+,.2f}",
            f"{today_pnl_pct:+.2f}%"
        )

    st.markdown("---")
    st.markdown("#### 📍 Current Positions")

    # Real positions from state manager
    import pandas as pd

    if positions:
        position_data = []
        for pos in positions:
            position_data.append({
                "Pair": pos.symbol,
                "Side": pos.side,
                "Entry": f"${pos.entry_price:,.2f}",
                "Current": f"${pos.current_price:,.2f}",
                "Size": f"{pos.size:.4f}",
                "P&L": f"${pos.pnl:+,.2f}",
                "P&L %": f"{pos.pnl_percent:+.2f}%"
            })

        positions_df = pd.DataFrame(position_data)
        st.dataframe(positions_df, use_container_width=True)

        st.info(f"💡 Bot monitoring {len(positions)} position(s). Will exit at TP/SL automatically.")
    else:
        st.info("No open positions. Bot is scanning for entry signals.")

    # Show recent trades
    if recent_trades:
        st.markdown("#### 📋 Recent Trades")

        trade_data = []
        for trade in recent_trades[:5]:  # Show last 5
            trade_data.append({
                "Time": datetime.fromisoformat(trade.exit_time).strftime("%H:%M:%S"),
                "Pair": trade.symbol,
                "Side": trade.side,
                "Entry": f"${trade.entry_price:,.2f}",
                "Exit": f"${trade.exit_price:,.2f}",
                "P&L": f"${trade.pnl:+,.2f}",
                "P&L %": f"{trade.pnl_percent:+.2f}%",
                "R": f"{trade.r_multiple:.1f}R"
            })

        trades_df = pd.DataFrame(trade_data)

        # Color code based on P&L
        def color_pnl(val):
            if isinstance(val, str) and '+' in val:
                return 'background-color: rgba(0, 255, 0, 0.2)'
            elif isinstance(val, str) and '-' in val:
                return 'background-color: rgba(255, 0, 0, 0.2)'
            return ''

        st.dataframe(
            trades_df.style.applymap(color_pnl, subset=['P&L', 'P&L %']),
            use_container_width=True
        )

else:
    st.markdown('<div class="section-header">💤 Bot is Idle</div>', unsafe_allow_html=True)

    st.info("""
    Click **"▶️ Start Bot"** to begin automated trading.

    The bot will:
    - Scan markets for signals every minute
    - Execute trades when confirmations meet threshold
    - Manage positions with automatic TP/SL
    - Send Telegram notifications (if configured)
    """)

    st.markdown("---")
    st.markdown('<div class="section-header">📋 How to Run Bot</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">⚙️ Active Configuration</div>', unsafe_allow_html=True)

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

# Auto-refresh when bot is running
if is_bot_running:
    # Poll state files every 5 seconds
    st.markdown("---")
    st.info("🔄 Auto-refreshing every 5 seconds to show live updates...")

    # Use Streamlit's experimental_rerun after delay
    import time
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9rem;">
    <p>⚠️ <strong>Risk Warning:</strong> Trading cryptocurrencies carries significant risk.
    Only trade with capital you can afford to lose.</p>
    <p>This bot uses strict risk management but profits are never guaranteed.</p>
</div>
""", unsafe_allow_html=True)
