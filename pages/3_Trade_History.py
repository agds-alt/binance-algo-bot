"""
Trade History Page
View and export trade logs
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Trade History", page_icon="📋", layout="wide")

st.title("📋 Trade History")

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox("Status", ["All", "Open", "Closed", "Stopped"])

with col2:
    symbol_filter = st.selectbox("Pair", ["All", "BTCUSDT", "ETHUSDT", "BNBUSDT"])

with col3:
    period_filter = st.selectbox("Period", ["Today", "This Week", "This Month", "All Time"])

with col4:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Trade table
st.markdown("### 📊 Trades")

# Mock data
if True:  # No trades yet
    st.info("No trades yet. Start trading or run a backtest to see trade history here!")

    # Show example for demo
    if st.checkbox("Show Example Trades"):
        mock_trades = {
            "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
            "Pair": ["BTCUSDT", "ETHUSDT", "BTCUSDT", "SOLUSDT", "BTCUSDT"],
            "Side": ["LONG", "SHORT", "LONG", "LONG", "SHORT"],
            "Entry": [42000, 2200, 41500, 145, 42500],
            "Exit": [42800, 2180, 41200, 150, 42300],
            "P&L": [800, -20, -300, 5, -200],
            "P&L %": [1.9, -0.9, -0.7, 3.4, -0.5],
            "Status": ["Closed", "Closed", "Stopped", "Closed", "Stopped"],
        }

        df = pd.DataFrame(mock_trades)

        # Style P&L
        def color_pnl(val):
            return 'color: green' if val > 0 else 'color: red'

        styled_df = df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Export
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "trades.csv",
                "text/csv",
                use_container_width=True
            )

        with col2:
            if st.session_state.get('tier', 'free') == 'free':
                st.button("📊 Download Excel", disabled=True, use_container_width=True, help="PRO feature")
            else:
                st.button("📊 Download Excel", use_container_width=True)

# Summary stats
st.markdown("---")
st.markdown("### 📊 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trades", "0")

with col2:
    st.metric("Wins", "0", "0%")

with col3:
    st.metric("Losses", "0", "0%")

with col4:
    st.metric("Break Even", "0")

st.markdown("---")
st.info("💡 **Tip**: Export your trade history regularly for tax reporting and performance analysis.")
