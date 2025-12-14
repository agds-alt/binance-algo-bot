"""
Market Analysis Page
Real-time market scanning and signal detection
"""

import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import ALLOWED_PAIRS, SCALPING_CONFIG
from modules.tier_manager import TierManager

st.set_page_config(page_title="Market Analysis", page_icon="📈", layout="wide")

st.title("📈 Market Analysis")

# Load tier
if 'tier' not in st.session_state:
    st.session_state.tier = 'free'

# Symbol selector
allowed_pairs_display = ALLOWED_PAIRS if st.session_state.tier != 'free' else ['BTCUSDT']

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    selected_symbol = st.selectbox(
        "Trading Pair",
        allowed_pairs_display,
        help="Select pair to analyze" if st.session_state.tier != 'free' else "FREE tier: BTC/USDT only"
    )

with col2:
    timeframe = st.selectbox(
        "Timeframe",
        [SCALPING_CONFIG.PRIMARY_TIMEFRAME, SCALPING_CONFIG.HIGHER_TIMEFRAME, SCALPING_CONFIG.TREND_TIMEFRAME],
        index=0
    )

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Analysis Results
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Technical Analysis")

    # Placeholder for analysis
    with st.container():
        st.info("🔍 Click 'Scan Market' to analyze current conditions")

        # Mock data for demonstration
        if st.button("🚀 Scan Market", type="primary", use_container_width=True):
            with st.spinner("Analyzing market..."):
                # Simulate analysis
                import time
                time.sleep(2)

                st.success("✅ Analysis Complete!")

                # Display mock analysis
                st.markdown("#### Market Condition")
                st.markdown(f"""
                - **Trend**: BULLISH 📈
                - **Strength**: MODERATE
                - **HTF Aligned**: ✅ Yes
                """)

                st.markdown("#### Indicators")
                ind_col1, ind_col2, ind_col3 = st.columns(3)

                with ind_col1:
                    st.metric("Price", "$42,350", "+2.5%")
                    st.metric("EMA 9", "$42,100")

                with ind_col2:
                    st.metric("EMA 21", "$41,800")
                    st.metric("EMA 50", "$41,200")

                with ind_col3:
                    st.metric("RSI", "58.3")
                    st.metric("Volume", "1.25x avg")

                st.markdown("#### Signal")
                st.success("""
                🎯 **LONG SIGNAL DETECTED**

                **Confirmations**: 5/6
                - ✅ EMA crossover (bullish)
                - ✅ Price above trend EMA
                - ✅ RSI in range (30-70)
                - ✅ Volume confirmed (>120% avg)
                - ✅ HTF trend aligned
                - ❌ Spread slightly high (0.06%)

                **Trade Setup**:
                - Entry: $42,350
                - Stop Loss: $41,920 (1.02%)
                - TP1 (50%): $42,995 (1.5R)
                - TP2 (30%): $43,425 (2.5R)
                - TP3 (20%): $44,070 (4.0R)

                **Risk/Reward**: 1:1.5 ✅
                """)

                if st.session_state.tier == 'free':
                    st.warning("⚠️ FREE tier: Analysis only. Upgrade to PRO for live trading!")

with col2:
    st.markdown("### 🎯 Key Levels")

    # Support/Resistance
    st.markdown("#### Support/Resistance")
    st.markdown("""
    **Resistance**: $43,500
    **Current**: $42,350
    **Support**: $41,000
    """)

    # Price chart placeholder
    st.markdown("#### Price Chart")
    st.info("📊 Interactive chart available in PRO tier")

    if st.session_state.tier != 'free':
        # Mock price chart
        import numpy as np

        dates = pd.date_range(start='2025-01-01', periods=50, freq='5min')
        prices = 42000 + np.cumsum(np.random.randn(50) * 100)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Time",
            yaxis_title="Price",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Multi-pair scanner
st.markdown("### 🔍 Multi-Pair Scanner")

if st.session_state.tier == 'free':
    st.warning("⚠️ Multi-pair scanning requires PRO tier. Upgrade to scan all markets simultaneously!")

    if st.button("🚀 Upgrade to PRO"):
        st.switch_page("pages/5_License.py")
else:
    if st.button("🔍 Scan All Pairs", use_container_width=True):
        with st.spinner("Scanning markets..."):
            import time
            time.sleep(3)

            # Mock scanner results
            scanner_data = {
                "Pair": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
                "Signal": ["LONG", "SHORT", "NEUTRAL", "LONG", "NEUTRAL"],
                "Confidence": ["5/6", "4/6", "2/6", "5/6", "3/6"],
                "Trend": ["BULLISH", "BEARISH", "NEUTRAL", "BULLISH", "NEUTRAL"],
                "RSI": [58.3, 42.1, 51.5, 62.3, 48.9],
                "Entry": ["$42,350", "$2,245", "-", "$145.80", "-"],
            }

            df = pd.DataFrame(scanner_data)

            # Color code signals
            def highlight_signal(val):
                if val == 'LONG':
                    return 'background-color: #90EE90'
                elif val == 'SHORT':
                    return 'background-color: #FFB6C1'
                return ''

            st.dataframe(
                df.style.applymap(highlight_signal, subset=['Signal']),
                use_container_width=True
            )

            st.success("✅ Scan complete! 2 trading opportunities found.")

# Bottom info
st.markdown("---")
st.info("""
**💡 Pro Tip**: Best signals have 5+ confirmations and align with higher timeframe trend.
Set up alerts in Settings to get notified when signals appear!
""")
