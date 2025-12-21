"""
Trade History Page
View and export trade logs - REAL DATA
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.bot_state_manager import get_bot_state_manager

st.set_page_config(page_title="Trade History", page_icon="📋", layout="wide")

# Enhanced CSS for Trade History page
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
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📋 Trade History</div>', unsafe_allow_html=True)
st.caption("Complete trade log with real-time data and export options")

# Initialize state manager
state_manager = get_bot_state_manager()

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox("Status", ["All", "Closed"])

with col2:
    all_trades = state_manager.get_trades(limit=1000)
    symbols = ["All"] + sorted(list(set([t.symbol for t in all_trades]))) if all_trades else ["All"]
    symbol_filter = st.selectbox("Pair", symbols)

with col3:
    period_filter = st.selectbox("Period", ["Today", "This Week", "This Month", "All Time"])

with col4:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Trade table
st.markdown('<div class="section-header">📊 Trades</div>', unsafe_allow_html=True)

# Get real trades from state manager
trades = state_manager.get_trades(limit=1000)

if not trades:
    st.info("No trades yet. Start trading or run test_trading.py to see trade history here!")
else:
    # Filter trades based on selection
    filtered_trades = trades

    # Filter by symbol
    if symbol_filter != "All":
        filtered_trades = [t for t in filtered_trades if t.symbol == symbol_filter]

    # Filter by period
    now = datetime.utcnow()
    if period_filter == "Today":
        start = datetime(now.year, now.month, now.day)
        filtered_trades = [t for t in filtered_trades if datetime.fromisoformat(t.exit_time) >= start]
    elif period_filter == "This Week":
        start = now - timedelta(days=now.weekday())
        filtered_trades = [t for t in filtered_trades if datetime.fromisoformat(t.exit_time) >= start]
    elif period_filter == "This Month":
        start = datetime(now.year, now.month, 1)
        filtered_trades = [t for t in filtered_trades if datetime.fromisoformat(t.exit_time) >= start]

    # Create dataframe
    trade_data = []
    for trade in filtered_trades:
        trade_data.append({
            "ID": trade.id,
            "Time": datetime.fromisoformat(trade.exit_time).strftime("%Y-%m-%d %H:%M:%S"),
            "Pair": trade.symbol,
            "Side": trade.side,
            "Entry": f"${trade.entry_price:,.2f}",
            "Exit": f"${trade.exit_price:,.2f}",
            "Size": f"{trade.size:.4f}",
            "P&L": f"${trade.pnl:+,.2f}",
            "P&L %": f"{trade.pnl_percent:+.2f}%",
            "R": f"{trade.r_multiple:.2f}R",
            "Reason": trade.exit_reason
        })

    df = pd.DataFrame(trade_data)

    # Display info
    st.info(f"📊 Showing {len(filtered_trades)} trades (Total: {len(trades)} trades)")

    # Style P&L
    def color_pnl(val):
        if isinstance(val, str) and '+' in val:
            return 'background-color: rgba(0, 255, 0, 0.2)'
        elif isinstance(val, str) and '-' in val:
            return 'background-color: rgba(255, 0, 0, 0.2)'
        return ''

    # Display with styling only if we have data
    if len(df) > 0 and 'P&L' in df.columns and 'P&L %' in df.columns:
        st.dataframe(
            df.style.applymap(color_pnl, subset=['P&L', 'P&L %']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Export
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        if st.session_state.get('tier', 'free') == 'free':
            st.button("📊 Download Excel", disabled=True, use_container_width=True, help="PRO feature")
        else:
            # Could implement Excel export here
            st.info("Excel export coming soon")

# Summary stats from real data
st.markdown("---")
st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)

stats = state_manager.get_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trades", f"{stats.total_trades}")

with col2:
    st.metric("Wins", f"{stats.winning_trades}", f"{stats.win_rate:.1f}%")

with col3:
    st.metric("Losses", f"{stats.losing_trades}")

with col4:
    total_pnl_pct = stats.total_pnl_percent
    st.metric("Total P&L", f"${stats.total_pnl:+,.2f}", f"{total_pnl_pct:+.2f}%")

# Additional metrics
st.markdown("---")
st.markdown('<div class="section-header">📈 Performance Breakdown</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_win = stats.avg_win if stats.avg_win > 0 else 0
    st.metric("Avg Win", f"${avg_win:,.2f}")

with col2:
    avg_loss = stats.avg_loss if stats.avg_loss < 0 else 0
    st.metric("Avg Loss", f"${avg_loss:,.2f}")

with col3:
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    st.metric("Profit Factor", f"{profit_factor:.2f}")

with col4:
    st.metric("Best Trade", f"${stats.best_trade:+,.2f}" if stats.best_trade else "$0.00")

st.markdown("---")
st.info("💡 **Tip**: Export your trade history regularly for tax reporting and performance analysis.")
