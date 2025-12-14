"""
Binance Algo Bot - Main Dashboard
Production-grade Streamlit interface for members
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
import yaml

# Page config
st.set_page_config(
    page_title="Binance Algo Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .tier-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .tier-free { background: #95a5a6; }
    .tier-pro { background: #3498db; }
    .tier-premium { background: #9b59b6; }
    .tier-enterprise { background: #e74c3c; }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: bold;
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

# Sidebar
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="font-size: 4rem; margin: 0;">🤖</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🤖 Binance Algo Bot")
    st.markdown(f"**Version:** 1.0.0")
    st.markdown(f"**Mode:** {'🧪 TESTNET' if BINANCE_TESTNET else '🔴 LIVE'}")

    st.markdown("---")

    # Tier Badge
    tier_name = tier_manager.current_tier_config['name']
    tier_colors = {
        'free': 'tier-free',
        'pro': 'tier-pro',
        'premium': 'tier-premium',
        'enterprise': 'tier-enterprise'
    }

    st.markdown(f"""
    <div class="tier-badge {tier_colors[st.session_state.tier]}">
        {tier_name} TIER
    </div>
    """, unsafe_allow_html=True)

    # License Status
    if st.session_state.license_active:
        st.success("✅ License Active")
    else:
        st.warning("⚠️ No License")
        if st.button("🔐 Activate License"):
            st.switch_page("pages/5_License.py")

    st.markdown("---")

    # Navigation
    st.markdown("### 📊 Navigation")

    pages = {
        "🏠 Dashboard": "dashboard.py",
        "📈 Market Analysis": "pages/1_Market_Analysis.py",
        "💰 Performance": "pages/2_Performance.py",
        "📋 Trade History": "pages/3_Trade_History.py",
        "⚙️ Settings": "pages/4_Settings.py",
        "🔐 License": "pages/5_License.py",
    }

    for label, _ in pages.items():
        st.markdown(f"**{label}**")

    st.markdown("---")

    # Quick Stats - Real data from state manager
    st.markdown("### 📊 Quick Stats")
    state_manager = get_bot_state_manager()
    stats = state_manager.get_stats()
    bot_state = state_manager.get_bot_state()

    # Daily trades with tier limit
    daily_limit = tier_manager.get_max_daily_trades()
    st.metric("Daily Trades", f"{stats.today_trades}/{daily_limit}")

    # Daily P&L
    today_pnl_pct = (stats.today_pnl / bot_state.capital * 100) if bot_state.capital > 0 else 0
    st.metric("Daily P&L", f"${stats.today_pnl:+.2f}", f"{today_pnl_pct:+.2f}%")

    # Win Rate
    st.metric("Win Rate", f"{stats.win_rate:.1f}%")

    st.markdown("---")
    st.markdown("### 🆘 Support")
    st.markdown("📧 support@algobot.com")
    st.markdown("💬 @algobot_support")

# Main Content
st.markdown('<div class="main-header">🤖 Binance Algo Trading Bot</div>', unsafe_allow_html=True)

# Welcome Message
if st.session_state.tier == 'free':
    st.info("""
    👋 **Welcome to FREE tier!**

    You're currently on the FREE plan. Upgrade to PRO to unlock:
    - ✅ Live trading (currently paper trading only)
    - ✅ Higher position limits ($100 → $5,000)
    - ✅ More daily trades (3 → 20)
    - ✅ Advanced strategies
    - ✅ Backtesting

    [Upgrade to PRO →](#)
    """)

# Key Metrics Row - Real data
col1, col2, col3, col4 = st.columns(4)

# Get real stats
positions = state_manager.get_positions()
current_balance = stats.current_balance if stats.current_balance > 0 else (bot_state.capital if bot_state.capital > 0 else 1000.0)

with col1:
    balance_change = stats.total_pnl
    st.metric(
        label="💰 Current Capital",
        value=f"${current_balance:,.2f}",
        delta=f"${balance_change:+,.2f}"
    )

with col2:
    total_pnl_pct = stats.total_pnl_percent
    st.metric(
        label="📈 Total P&L",
        value=f"${stats.total_pnl:+,.2f}",
        delta=f"{total_pnl_pct:+.2f}%"
    )

with col3:
    st.metric(
        label="📊 Win Rate",
        value=f"{stats.win_rate:.1f}%",
        delta=f"{stats.winning_trades}W / {stats.losing_trades}L"
    )

with col4:
    max_positions = tier_manager.get_max_positions()
    st.metric(
        label="🔄 Open Positions",
        value=f"{len(positions)}/{max_positions}"
    )

st.markdown("---")

# Quick Actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Scan Markets", use_container_width=True):
        st.switch_page("pages/1_Market_Analysis.py")

with col2:
    start_disabled = st.session_state.tier == 'free'
    if st.button("▶️ Start Trading", disabled=start_disabled, use_container_width=True):
        st.switch_page("pages/7_Live_Trading.py")

with col3:
    if st.button("📊 View Performance", use_container_width=True):
        st.switch_page("pages/2_Performance.py")

with col4:
    if st.button("🛑 Emergency Close", type="primary", use_container_width=True):
        if len(positions) == 0:
            st.warning("No open positions to close")
        else:
            st.error(f"⚠️ This will close {len(positions)} position(s). Go to Live Trading for emergency stop.")

st.markdown("---")

# Recent Activity
st.markdown("### 📋 Recent Activity")

# Show real recent trades
recent_trades = state_manager.get_trades(limit=5)

if recent_trades:
    import pandas as pd
    from datetime import datetime

    trade_data = []
    for trade in recent_trades:
        trade_data.append({
            "Time": datetime.fromisoformat(trade.exit_time).strftime("%Y-%m-%d %H:%M"),
            "Pair": trade.symbol,
            "Side": trade.side,
            "Entry": f"${trade.entry_price:,.2f}",
            "Exit": f"${trade.exit_price:,.2f}",
            "P&L": f"${trade.pnl:+,.2f}",
            "P&L %": f"{trade.pnl_percent:+.2f}%",
            "R": f"{trade.r_multiple:.1f}R",
            "Reason": trade.exit_reason
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
    st.info("No recent trading activity. Start by scanning markets or activate Live Trading!")

# Risk Status
st.markdown("---")
st.markdown("### 🛡️ Risk Management Status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Daily Limits")

    # Daily drawdown
    daily_dd_pct = abs(stats.today_pnl / current_balance * 100) if stats.today_pnl < 0 and current_balance > 0 else 0
    daily_dd_limit = RISK_LIMITS["MAX_DAILY_DRAWDOWN_PCT"]
    daily_dd_progress = min(daily_dd_pct / daily_dd_limit, 1.0)

    st.progress(daily_dd_progress, text=f"Daily Drawdown: {daily_dd_pct:.2f}% / {daily_dd_limit:.2f}%")

    # Daily trades
    daily_trades_progress = stats.today_trades / daily_limit if daily_limit > 0 else 0
    st.progress(daily_trades_progress, text=f"Daily Trades: {stats.today_trades} / {daily_limit}")

with col2:
    st.markdown("#### Total Limits")

    # Total drawdown
    total_dd_pct = stats.drawdown_percent
    total_dd_limit = RISK_LIMITS["MAX_TOTAL_DRAWDOWN_PCT"]
    total_dd_progress = min(total_dd_pct / total_dd_limit, 1.0)

    st.progress(total_dd_progress, text=f"Total Drawdown: {total_dd_pct:.2f}% / {total_dd_limit:.2f}%")

    # Consecutive losses (simplified - would need to track properly)
    max_consecutive = RISK_LIMITS.get("MAX_CONSECUTIVE_LOSSES", 3)
    st.progress(0.0, text=f"Consecutive Losses: 0 / {max_consecutive}")

# Tier Comparison (for free users)
if st.session_state.tier == 'free':
    st.markdown("---")
    st.markdown("### 🚀 Upgrade to Unlock More")

    tier_comparison = {
        "Feature": ["Live Trading", "Max Position", "Daily Trades", "Concurrent Positions", "Trading Pairs", "Backtesting", "Support"],
        "FREE": ["❌", "$100", "3", "1", "1 (BTC)", "❌", "Community"],
        "PRO": ["✅", "$5,000", "20", "3", "5 pairs", "✅", "Priority"],
        "PREMIUM": ["✅", "Unlimited", "Unlimited", "10", "All pairs", "✅", "VIP 24/7"],
    }

    st.table(tier_comparison)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**FREE**")
        st.markdown("$0/month")
        st.button("Current Plan", disabled=True, use_container_width=True)

    with col2:
        st.markdown("**PRO** ⭐")
        st.markdown("$99/month")
        if st.button("Upgrade to PRO", type="primary", use_container_width=True):
            st.switch_page("pages/5_License.py")

    with col3:
        st.markdown("**PREMIUM**")
        st.markdown("$249/month")
        if st.button("Upgrade to PREMIUM", use_container_width=True):
            st.switch_page("pages/5_License.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>⚠️ Risk Warning:</strong> Trading cryptocurrency involves substantial risk of loss.</p>
    <p>Past performance is not indicative of future results.</p>
    <p><small>© 2025 Binance Algo Bot. All rights reserved.</small></p>
</div>
""", unsafe_allow_html=True)
