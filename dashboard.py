"""
Binance Algo Bot - Main Dashboard
Production-grade Streamlit interface - OPTIMIZED LAYOUT
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.config import RISK_LIMITS, BINANCE_TESTNET
from modules.tier_manager import TierManager, TierLevel
from modules.bot_state_manager import get_bot_state_manager
from modules.auth_helpers import (
    init_session_state,
    is_authenticated,
    get_current_user,
    show_user_info_sidebar,
    check_session_validity
)
from modules.pwa_support import inject_pwa_support, show_install_button
from modules.responsive_layout import apply_responsive_layout
from datetime import datetime
import yaml

# Initialize auth session
init_session_state()

# Check if user is authenticated
if not is_authenticated():
    st.warning("⚠️ Please login to access the dashboard")
    st.info("Click the button below to go to the login page")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔑 Go to Login", use_container_width=True):
            st.switch_page("pages/0_Login.py")

    st.stop()

# Check session validity
check_session_validity()

# Page config
st.set_page_config(
    page_title="BotX - Binance Algo Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 💻 PWA Support
inject_pwa_support()

# 📱 Responsive Layout
apply_responsive_layout()

# 🎨 DARK THEME WITH GREEN NEON GLOW - Cyberpunk Style
st.markdown("""
<style>
    /* ============================================ */
    /* DARK BACKGROUND - FULL BLACK */
    /* ============================================ */

    /* Main app background */
    .stApp {
        background-color: #000000 !important;
    }

    /* Main container */
    .main {
        background-color: #000000 !important;
    }

    .main > div {
        padding-top: 2rem;
        background-color: #000000 !important;
    }

    /* Block container */
    .block-container {
        background-color: #000000 !important;
        padding-top: 2rem !important;
    }

    /* ============================================ */
    /* SIDEBAR - FULL BLACK */
    /* ============================================ */

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #000000 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #000000 !important;
    }

    /* Sidebar text white */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Sidebar headers green */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }

    /* ============================================ */
    /* TEXT COLORS - WHITE */
    /* ============================================ */

    /* All text white */
    .stApp, .main, p, span, div, label {
        color: #ffffff !important;
    }

    /* Headers with GREEN GLOW */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41 !important;
        font-weight: 800 !important;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #00ff41 !important;
        text-shadow: 0 0 15px #00ff41, 0 0 30px #00ff41, 0 0 45px #00ff41 !important;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00ff41 !important;
        box-shadow: 0 1px 10px rgba(0, 255, 65, 0.5) !important;
    }

    /* ============================================ */
    /* METRIC CARDS - DARK WITH GREEN ACCENT */
    /* ============================================ */

    .metric-card {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #00ff41 !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3), inset 0 0 20px rgba(0, 255, 65, 0.1) !important;
        transition: all 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.5), inset 0 0 30px rgba(0, 255, 65, 0.2) !important;
        border-color: #00ff88 !important;
    }

    /* Streamlit metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 1px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ============================================ */
    /* TIER BADGES - NEON GLOW */
    /* ============================================ */

    .tier-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 2px solid #00ff41;
        background: rgba(0, 0, 0, 0.8);
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.5), inset 0 0 15px rgba(0, 255, 65, 0.2);
    }

    .tier-free {
        color: #00ff41 !important;
        border-color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }
    .tier-pro {
        color: #00ffff !important;
        border-color: #00ffff !important;
        text-shadow: 0 0 10px #00ffff !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5), inset 0 0 15px rgba(0, 255, 255, 0.2) !important;
    }
    .tier-premium {
        color: #ff00ff !important;
        border-color: #ff00ff !important;
        text-shadow: 0 0 10px #ff00ff !important;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5), inset 0 0 15px rgba(255, 0, 255, 0.2) !important;
    }
    .tier-enterprise {
        color: #ff0000 !important;
        border-color: #ff0000 !important;
        text-shadow: 0 0 10px #ff0000 !important;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5), inset 0 0 15px rgba(255, 0, 0, 0.2) !important;
    }

    /* ============================================ */
    /* BUTTONS - GREEN NEON */
    /* ============================================ */

    .stButton>button {
        background: linear-gradient(135deg, #003300 0%, #006600 100%) !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 8px;
        height: 3rem;
        font-weight: 700 !important;
        font-size: 0.95rem;
        text-shadow: 0 0 5px #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #004400 0%, #008800 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.6), 0 5px 15px rgba(0, 0, 0, 0.5) !important;
        border-color: #00ff88 !important;
    }

    /* ============================================ */
    /* SIDEBAR - DARK WITH GREEN ACCENT */
    /* ============================================ */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #0a0a0a 100%) !important;
        border-right: 2px solid #00ff41 !important;
        box-shadow: 2px 0 20px rgba(0, 255, 65, 0.2) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }

    /* ============================================ */
    /* ALERTS & INFO BOXES */
    /* ============================================ */

    .stAlert {
        background-color: rgba(0, 255, 65, 0.1) !important;
        border: 1px solid #00ff41 !important;
        border-left: 4px solid #00ff41 !important;
        border-radius: 10px;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2) !important;
    }

    .stSuccess {
        background-color: rgba(0, 255, 65, 0.15) !important;
        border-color: #00ff41 !important;
    }

    .stError {
        background-color: rgba(255, 0, 0, 0.15) !important;
        border-color: #ff0000 !important;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.2) !important;
    }

    .stWarning {
        background-color: rgba(255, 255, 0, 0.15) !important;
        border-color: #ffff00 !important;
        box-shadow: 0 0 15px rgba(255, 255, 0, 0.2) !important;
    }

    /* ============================================ */
    /* INPUTS & FORMS - DARK WITH GREEN BORDER */
    /* ============================================ */

    input, textarea, select {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #00ff41 !important;
        border-radius: 5px !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    input:focus, textarea:focus, select:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.4) !important;
        outline: none !important;
    }

    /* ============================================ */
    /* DIVIDERS - GREEN GLOW */
    /* ============================================ */

    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #00ff41 !important;
        box-shadow: 0 1px 10px rgba(0, 255, 65, 0.3) !important;
    }

    /* ============================================ */
    /* CARDS - DARK WITH GREEN BORDER */
    /* ============================================ */

    .info-card {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2) !important;
        color: #ffffff !important;
    }

    /* Dataframe/Table */
    [data-testid="stDataFrame"], table {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2) !important;
    }

    table thead {
        background-color: #003300 !important;
        color: #00ff41 !important;
    }

    table tbody tr {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border-bottom: 1px solid rgba(0, 255, 65, 0.2) !important;
    }

    table tbody tr:hover {
        background-color: rgba(0, 255, 65, 0.1) !important;
    }

    /* ============================================ */
    /* CHARTS - DARK THEME */
    /* ============================================ */

    .js-plotly-plot {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2) !important;
    }

    /* ============================================ */
    /* SCROLLBAR - GREEN THEME */
    /* ============================================ */

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #0a0a0a;
        border: 1px solid rgba(0, 255, 65, 0.1);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #003300, #006600);
        border-radius: 5px;
        border: 1px solid #00ff41;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #004400, #008800);
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.5);
    }

    /* ============================================ */
    /* GLOW ANIMATION */
    /* ============================================ */

    @keyframes glow {
        0%, 100% { text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41; }
        50% { text-shadow: 0 0 15px #00ff41, 0 0 30px #00ff41, 0 0 45px #00ff41; }
    }

    .main-header, h1 {
        animation: glow 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with license detection
if 'tier' not in st.session_state:
    # Check if license is active
    try:
        from modules.license_state import get_license_state
        license_state = get_license_state()

        # Load current license info from state dict
        if license_state.state.get('license_key') and license_state.state.get('is_valid'):
            st.session_state.tier = license_state.state.get('tier', 'free')
            st.session_state.license_active = True
            st.session_state.license_key = license_state.state.get('license_key')
        else:
            st.session_state.tier = 'free'
            st.session_state.license_active = False
            st.session_state.license_key = None
    except Exception as e:
        # Fallback to free tier if license check fails
        st.session_state.tier = 'free'
        st.session_state.license_active = False
        st.session_state.license_key = None

if 'license_active' not in st.session_state:
    st.session_state.license_active = False

# Load configs
@st.cache_resource
def load_configs():
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    with open('config/tiers.yaml', 'r') as f:
        tiers = yaml.safe_load(f)
    return config, tiers

try:
    config, tier_config = load_configs()
    tier_manager = TierManager(tier_config, st.session_state.tier)
except Exception as e:
    st.error(f"Error loading configuration: {e}")
    st.stop()

# OPTIMIZED SIDEBAR
with st.sidebar:
    # Logo & Title
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🤖</div>
        <h2 style="color: #00ff41; margin: 0; font-weight: 700; font-size: 1.5rem; text-shadow: 0 0 10px #00ff41;">BotX</h2>
        <p style="color: #00ff41; margin-top: 0.5rem; font-size: 0.85rem; text-shadow: 0 0 5px #00ff41;">v1.0.0 • {}</p>
    </div>
    """.format('🧪 TESTNET' if BINANCE_TESTNET else '🔴 LIVE'), unsafe_allow_html=True)

    # Show user info (includes tier badge, license status, and user profile)
    show_user_info_sidebar()

    st.markdown("---")

    # Quick Stats - Real data from state manager
    st.markdown("### 📊 Quick Stats")
    state_manager = get_bot_state_manager()
    stats = state_manager.get_stats()
    bot_state = state_manager.get_bot_state()

    # Daily trades with tier limit
    daily_limit = tier_manager.get_max_daily_trades()
    trades_color = "🟢" if stats.today_trades < daily_limit else "🔴"
    st.metric(
        "Trades Today",
        f"{stats.today_trades}/{daily_limit}",
        help="Daily trades executed"
    )

    # Daily P&L
    today_pnl_pct = (stats.today_pnl / bot_state.capital * 100) if bot_state.capital > 0 else 0
    pnl_icon = "📈" if stats.today_pnl >= 0 else "📉"
    st.metric(
        "Today's P&L",
        f"${stats.today_pnl:+,.2f}",
        f"{today_pnl_pct:+.2f}%",
        help="Profit/Loss today"
    )

    # Win Rate
    win_icon = "🎯" if stats.win_rate >= 60 else "⚠️"
    st.metric(
        "Win Rate",
        f"{stats.win_rate:.1f}%",
        help="Percentage of winning trades"
    )

    # Total P&L
    st.metric(
        "Total P&L",
        f"${stats.total_pnl:+,.2f}",
        help="All-time profit/loss"
    )

    st.markdown("---")

    # Bot Status
    st.markdown("### 🤖 Bot Status")
    if bot_state.is_running:
        st.success("🟢 **RUNNING**", icon="✅")
        uptime_mins = bot_state.uptime_seconds // 60
        st.caption(f"⏱️ Uptime: {uptime_mins}m")
    else:
        st.info("⚪ **STOPPED**", icon="⏸️")
        st.caption("Bot is idle")

    st.markdown("---")

    # Support
    st.markdown("### 🆘 Support")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #9ca3af;">
        📧 support@algobot.com<br>
        💬 @algobot_support<br>
        📚 <a href="#" style="color: #3b82f6;">Documentation</a>
    </div>
    """, unsafe_allow_html=True)

# MAIN CONTENT
st.markdown('<div class="main-header">🤖 Binance Algo Trading Bot</div>', unsafe_allow_html=True)
st.caption("Automated cryptocurrency trading with advanced risk management")

# Welcome/Upgrade Message for Free Users
if st.session_state.tier == 'free':
    st.info("""
    **👋 Welcome to FREE tier!** You're currently on the FREE plan.

    **Upgrade to PRO** to unlock:
    • Live trading (currently paper only) • Higher position limits ($100 → $5,000)
    • More daily trades (3 → 20) • Advanced strategies • Backtesting & Analytics

    [**🚀 Upgrade to PRO →**](#)
    """, icon="🎁")

st.markdown("---")

# Key Metrics Row - Real data
st.markdown('<div class="section-header">📊 Performance Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Get real stats
positions = state_manager.get_positions()
current_balance = stats.current_balance if stats.current_balance > 0 else (bot_state.capital if bot_state.capital > 0 else 10000.0)

with col1:
    balance_change = stats.total_pnl
    st.metric(
        label="💰 Current Capital",
        value=f"${current_balance:,.2f}",
        delta=f"${balance_change:+,.2f}",
        help="Total capital including P&L"
    )

with col2:
    total_pnl_pct = stats.total_pnl_percent
    st.metric(
        label="📈 Total P&L",
        value=f"${stats.total_pnl:+,.2f}",
        delta=f"{total_pnl_pct:+.2f}%",
        help="All-time profit/loss"
    )

with col3:
    st.metric(
        label="🎯 Win Rate",
        value=f"{stats.win_rate:.1f}%",
        delta=f"{stats.winning_trades}W / {stats.losing_trades}L",
        help="Percentage of winning trades"
    )

with col4:
    max_positions = tier_manager.get_max_positions()
    pos_color = "normal" if len(positions) < max_positions else "inverse"
    st.metric(
        label="🔄 Open Positions",
        value=f"{len(positions)}/{max_positions}",
        help="Current vs maximum positions"
    )

st.markdown("---")

# Quick Actions
st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 **Scan Markets**", use_container_width=True):
        st.switch_page("pages/1_Market_Analysis.py")

with col2:
    start_disabled = st.session_state.tier == 'free'
    if st.button("▶️ **Start Trading**", disabled=start_disabled, use_container_width=True, type="primary"):
        st.switch_page("pages/7_Live_Trading.py")
    if start_disabled:
        st.caption("⚠️ PRO feature")

with col3:
    if st.button("📊 **View Performance**", use_container_width=True):
        st.switch_page("pages/2_Performance.py")

with col4:
    if st.button("📋 **Trade History**", use_container_width=True):
        st.switch_page("pages/3_Trade_History.py")

st.markdown("---")

# Recent Activity
st.markdown('<div class="section-header">📋 Recent Activity</div>', unsafe_allow_html=True)

# Show real recent trades
recent_trades = state_manager.get_trades(limit=10)

if recent_trades:
    import pandas as pd

    trade_data = []
    for trade in recent_trades[:5]:  # Show top 5
        trade_data.append({
            "Time": datetime.fromisoformat(trade.exit_time).strftime("%m/%d %H:%M"),
            "Pair": trade.symbol.replace("USDT", ""),
            "Side": f"{'🟢' if trade.side == 'LONG' else '🔴'} {trade.side}",
            "Entry": f"${trade.entry_price:,.2f}",
            "Exit": f"${trade.exit_price:,.2f}",
            "P&L": f"${trade.pnl:+,.2f}",
            "P&L %": f"{trade.pnl_percent:+.2f}%",
            "R": f"{trade.r_multiple:.1f}R",
        })

    trades_df = pd.DataFrame(trade_data)

    # Color code based on P&L
    def color_pnl(val):
        if isinstance(val, str) and '+' in val:
            return 'background-color: rgba(34, 197, 94, 0.2); color: rgb(22, 163, 74); font-weight: 600'
        elif isinstance(val, str) and '-' in val:
            return 'background-color: rgba(239, 68, 68, 0.2); color: rgb(220, 38, 38); font-weight: 600'
        return ''

    st.dataframe(
        trades_df.style.applymap(color_pnl, subset=['P&L', 'P&L %']),
        use_container_width=True,
        hide_index=True
    )

    # View all button
    if st.button("📜 View All Trades", use_container_width=True):
        st.switch_page("pages/3_Trade_History.py")
else:
    st.info("📭 No recent trading activity. Start by scanning markets or running a backtest!", icon="💡")

st.markdown("---")

# Risk Management Status
st.markdown('<div class="section-header">🛡️ Risk Management</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Daily Limits")

    # Daily drawdown
    daily_dd_pct = abs(stats.today_pnl / current_balance * 100) if stats.today_pnl < 0 and current_balance > 0 else 0
    daily_dd_limit = RISK_LIMITS.MAX_DAILY_DRAWDOWN * 100  # Convert to percentage
    daily_dd_progress = min(daily_dd_pct / daily_dd_limit, 1.0)

    st.progress(daily_dd_progress, text=f"📉 Daily Drawdown: {daily_dd_pct:.2f}% / {daily_dd_limit:.2f}%")

    # Daily trades
    daily_trades_progress = min(stats.today_trades / daily_limit, 1.0) if daily_limit > 0 else 0
    st.progress(daily_trades_progress, text=f"🔄 Daily Trades: {stats.today_trades} / {daily_limit}")

with col2:
    st.markdown("#### Total Limits")

    # Total drawdown
    total_dd_pct = stats.drawdown_percent
    total_dd_limit = RISK_LIMITS.MAX_TOTAL_DRAWDOWN * 100  # Convert to percentage
    total_dd_progress = min(total_dd_pct / total_dd_limit, 1.0)

    st.progress(total_dd_progress, text=f"📊 Total Drawdown: {total_dd_pct:.2f}% / {total_dd_limit:.2f}%")

    # Positions used
    positions_progress = len(positions) / max_positions if max_positions > 0 else 0
    st.progress(positions_progress, text=f"💼 Positions: {len(positions)} / {max_positions}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem 1rem;'>
    <p style='font-weight: 600; margin-bottom: 0.5rem;'>⚠️ Risk Warning</p>
    <p style='font-size: 0.85rem; margin-bottom: 1rem;'>
        Trading cryptocurrency involves substantial risk of loss. Past performance is not indicative of future results.
    </p>
    <p style='font-size: 0.75rem; color: #9ca3af;'>
        © 2025 Binance Algo Bot. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)
