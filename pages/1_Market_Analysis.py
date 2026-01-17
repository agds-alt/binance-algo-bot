"""
Market Analysis Page
Real-time market scanning and signal detection
"""

import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import ALLOWED_PAIRS, SCALPING_CONFIG, BINANCE_TESTNET
from modules.tier_manager import TierManager
from modules.data_fetcher import DataFetcher
from modules.backtester import relaxed_ema_crossover_signals
from modules.pwa_support import inject_pwa_support
from modules.responsive_layout import apply_responsive_layout

st.set_page_config(page_title="Market Analysis", page_icon="📈", layout="wide")

# 💻 PWA Support
inject_pwa_support()

# 📱 Responsive Layout
apply_responsive_layout()

# Dark Theme CSS with Green Glow
st.markdown("""
<style>
    /* Dark background - full black */
    .stApp {
        background-color: #000000 !important;
    }

    /* Main content area */
    .main {
        background-color: #000000 !important;
    }

    /* Sidebar dark */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
    }

    /* Headers with GREEN GLOW */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41 !important;
        animation: glow 2s ease-in-out infinite;
    }

    /* White text for all content */
    p, .stMarkdown, .stText, label, span, div, .stCaption {
        color: #ffffff !important;
    }

    /* Buttons - green neon */
    .stButton>button {
        background: linear-gradient(135deg, #003300 0%, #006600 100%) !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #006600 0%, #009900 100%) !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Metrics - green theme */
    [data-testid="stMetricValue"] {
        color: #00ff41 !important;
        text-shadow: 0 0 10px #00ff41 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }

    /* Dataframes/Tables - dark theme */
    .stDataFrame {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
    }

    /* Plotly charts - dark background */
    .js-plotly-plot {
        background-color: #0a0a0a !important;
    }

    /* Success messages - green glow */
    .stSuccess {
        background-color: #001a00 !important;
        border: 2px solid #00ff41 !important;
        color: #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
    }

    /* Info boxes - dark with green accent */
    .stInfo {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff41 !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    /* Warning - yellow glow */
    .stWarning {
        background-color: #1a1a00 !important;
        border: 2px solid #ffff00 !important;
        color: #ffff00 !important;
        box-shadow: 0 0 15px rgba(255, 255, 0, 0.3) !important;
    }

    /* Glow animation */
    @keyframes glow {
        0%, 100% {
            text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41;
        }
        50% {
            text-shadow: 0 0 15px #00ff41, 0 0 30px #00ff41, 0 0 45px #00ff41;
        }
    }

    /* Divider */
    hr {
        border-color: #00ff41 !important;
        opacity: 0.3 !important;
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00ff41 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00ff41;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #00ff41 !important;
        text-shadow: 0 0 20px #00ff41 !important;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Market Analysis</div>', unsafe_allow_html=True)
st.caption("Real-time market scanning and signal detection")

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

# Initialize data fetcher
@st.cache_resource
def get_data_fetcher():
    return DataFetcher(use_testnet=BINANCE_TESTNET)

fetcher = get_data_fetcher()

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
    auto_refresh = st.checkbox("Auto Refresh", value=False, help="Refresh every 30s")

st.markdown("---")

# Fetch real-time data
@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_live_data(symbol, interval):
    """Fetch live market data from Binance"""
    try:
        # Fetch last 200 candles for indicator calculation
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        df = fetcher.fetch_klines_sync(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=500
        )

        if df.empty:
            return None

        # Calculate indicators
        df = fetcher.calculate_indicators(df)

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Analysis Results
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header">📊 Technical Analysis</div>', unsafe_allow_html=True)

    # Fetch data button
    if st.button("🚀 Scan Market", type="primary", use_container_width=True) or auto_refresh:
        with st.spinner(f"Fetching live {selected_symbol} data from Binance..."):
            df = fetch_live_data(selected_symbol, timeframe)

            if df is not None and len(df) > 0:
                # Get latest candle
                latest = df.iloc[-1]
                prev = df.iloc[-2]

                st.success(f"✅ Live data fetched! Last update: {df.index[-1].strftime('%Y-%m-%d %H:%M:%S')} UTC")

                # Display market condition
                st.markdown("#### Market Condition")

                # Determine trend
                if latest['close'] > latest['ema_50']:
                    trend = "BULLISH 📈"
                    trend_color = "green"
                elif latest['close'] < latest['ema_50']:
                    trend = "BEARISH 📉"
                    trend_color = "red"
                else:
                    trend = "NEUTRAL ➡️"
                    trend_color = "gray"

                # Trend strength
                ema_distance = abs(latest['close'] - latest['ema_50']) / latest['ema_50'] * 100
                if ema_distance > 2:
                    strength = "STRONG"
                elif ema_distance > 1:
                    strength = "MODERATE"
                else:
                    strength = "WEAK"

                # HTF alignment
                htf_aligned = latest['close'] > latest['ema_200']

                st.markdown(f"""
                - **Trend**: :{trend_color}[{trend}]
                - **Strength**: {strength}
                - **HTF Aligned**: {'✅ Yes' if htf_aligned else '❌ No'}
                """)

                # Display indicators
                st.markdown("#### Live Indicators")
                ind_col1, ind_col2, ind_col3 = st.columns(3)

                # Calculate 24h change
                price_change = ((latest['close'] - df.iloc[0]['close']) / df.iloc[0]['close']) * 100

                with ind_col1:
                    st.metric(
                        "Price",
                        f"${latest['close']:,.2f}",
                        f"{price_change:+.2f}%"
                    )
                    st.metric("EMA 8", f"${latest['ema_8']:,.2f}")

                with ind_col2:
                    st.metric("EMA 21", f"${latest['ema_21']:,.2f}")
                    st.metric("EMA 50", f"${latest['ema_50']:,.2f}")

                with ind_col3:
                    st.metric("RSI", f"{latest['rsi']:.1f}")
                    volume_ratio = latest['volume'] / latest['volume_ma'] if latest['volume_ma'] > 0 else 1.0
                    st.metric("Volume", f"{volume_ratio:.2f}x avg")

                # Signal detection using RELAXED algorithm
                st.markdown("#### 🎯 Signal Analysis (RELAXED MODE)")
                st.caption("Using relaxed criteria: 4/6 confirmations, 1.2x volume, 25-75 RSI")

                # Get signal with debug info
                signal_result = relaxed_ema_crossover_signals(df, debug=True)

                if signal_result:
                    has_signal = signal_result.get('has_signal', False)
                    conf_count = signal_result.get('confirmations', 0)
                    checks = signal_result.get('checks', {})

                    signal_type = signal_result.get('side', 'NEUTRAL')
                    signal_color = "green" if signal_type == "LONG" else "red" if signal_type == "SHORT" else "gray"

                    # Display debug info
                    st.markdown("**Confirmation Checks:**")
                    for check_name, check_value in checks.items():
                        st.text(f"{check_name}: {check_value}")

                    st.markdown("---")

                    # Display signal
                    if has_signal and signal_type != "NEUTRAL":
                        # Get trade setup from signal
                        entry = signal_result.get('entry_price', latest['close'])
                        stop_loss = signal_result.get('stop_loss')
                        take_profits = signal_result.get('take_profits', [])

                        tp1 = take_profits[0] if len(take_profits) > 0 else entry
                        tp2 = take_profits[1] if len(take_profits) > 1 else entry
                        tp3 = take_profits[2] if len(take_profits) > 2 else entry

                        sl_pct = abs((entry - stop_loss) / entry) * 100
                        rr_ratio = abs((tp1 - entry) / (entry - stop_loss)) if stop_loss != entry else 0

                        st.success(f"""
🎯 **{signal_type} SIGNAL DETECTED!** ✅

**Confirmations**: {conf_count}/6 (RELAXED: Need 4+)

**Trade Setup**:
- Entry: ${entry:,.2f}
- Stop Loss: ${stop_loss:,.2f} ({sl_pct:.2f}%)
- TP1 (50%): ${tp1:,.2f} (1.5R)
- TP2 (30%): ${tp2:,.2f} (2.5R)
- TP3 (20%): ${tp3:,.2f} (4.0R)

**Risk/Reward**: 1:{rr_ratio:.1f} {'✅' if rr_ratio >= 1.5 else '⚠️'}
                    """)
                    else:
                        # Format checks for display
                        checks_display = '\n'.join([f"- {name.replace('_', ' ').title()}: {value}"
                                                     for name, value in checks.items()])

                        st.info(f"""
ℹ️ **NO CLEAR SIGNAL**

**Confirmations**: {conf_count}/6 (RELAXED: Need 4+ for signal)

**Checks:**
{checks_display}

Waiting for better setup with 4+ confirmations.
                        """)

                if st.session_state.tier == 'free':
                    st.warning("⚠️ FREE tier: Analysis only. Upgrade to PRO for live trading!")

            else:
                st.error("❌ Failed to fetch market data. Please try again.")

with col2:
    st.markdown('<div class="section-header">🎯 Key Levels</div>', unsafe_allow_html=True)

    # Fetch data for support/resistance
    df = fetch_live_data(selected_symbol, timeframe)

    if df is not None and len(df) > 0:
        latest = df.iloc[-1]

        # Calculate S/R based on recent highs/lows
        recent_high = df['high'].tail(50).max()
        recent_low = df['low'].tail(50).min()

        st.markdown("#### Support/Resistance")
        st.markdown(f"""
**Resistance**: ${recent_high:,.2f}
**Current**: ${latest['close']:,.2f}
**Support**: ${recent_low:,.2f}
        """)

        # Price chart
        st.markdown("#### Price Chart (Last 100 bars)")

        if st.session_state.tier != 'free':
            # Plot real price chart
            chart_df = df.tail(100)

            fig = go.Figure()

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=chart_df.index,
                open=chart_df['open'],
                high=chart_df['high'],
                low=chart_df['low'],
                close=chart_df['close'],
                name='Price'
            ))

            # EMAs
            fig.add_trace(go.Scatter(
                x=chart_df.index,
                y=chart_df['ema_8'],
                mode='lines',
                name='EMA 8',
                line=dict(color='blue', width=1)
            ))

            fig.add_trace(go.Scatter(
                x=chart_df.index,
                y=chart_df['ema_21'],
                mode='lines',
                name='EMA 21',
                line=dict(color='orange', width=1)
            ))

            fig.add_trace(go.Scatter(
                x=chart_df.index,
                y=chart_df['ema_50'],
                mode='lines',
                name='EMA 50',
                line=dict(color='red', width=1.5)
            ))

            fig.update_layout(
                title=f"{selected_symbol} - {timeframe}",
                xaxis_title="Time",
                yaxis_title="Price (USDT)",
                height=400,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Interactive chart available in PRO tier")
    else:
        st.info("Click 'Scan Market' to load live data")

# Multi-pair scanner
if st.session_state.tier != 'free':
    st.markdown("---")
    st.markdown('<div class="section-header">🔍 Multi-Pair Scanner</div>', unsafe_allow_html=True)

    if st.button("📡 Scan All Pairs", use_container_width=True):
        scanner_results = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, pair in enumerate(ALLOWED_PAIRS[:5]):  # Scan first 5 pairs
            status_text.text(f"Scanning {pair}...")

            df = fetch_live_data(pair, SCALPING_CONFIG.PRIMARY_TIMEFRAME)

            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                prev = df.iloc[-2]

                # Quick signal check
                ema_cross_bullish = prev['ema_8'] <= prev['ema_21'] and latest['ema_8'] > latest['ema_21']
                ema_cross_bearish = prev['ema_8'] >= prev['ema_21'] and latest['ema_8'] < latest['ema_21']

                if ema_cross_bullish:
                    signal = "LONG"
                elif ema_cross_bearish:
                    signal = "SHORT"
                else:
                    signal = "NEUTRAL"

                # Trend
                if latest['close'] > latest['ema_50']:
                    trend = "BULLISH"
                elif latest['close'] < latest['ema_50']:
                    trend = "BEARISH"
                else:
                    trend = "NEUTRAL"

                # Confirmations
                conf = 0
                if ema_cross_bullish or ema_cross_bearish:
                    conf += 1
                if (signal == "LONG" and latest['close'] > latest['ema_50']) or \
                   (signal == "SHORT" and latest['close'] < latest['ema_50']):
                    conf += 1
                if 30 < latest['rsi'] < 70:
                    conf += 1

                scanner_results.append({
                    "Pair": pair,
                    "Signal": signal,
                    "Confidence": f"{conf}/5",
                    "Trend": trend,
                    "RSI": f"{latest['rsi']:.1f}",
                    "Price": f"${latest['close']:,.2f}"
                })

            progress_bar.progress((i + 1) / 5)

        status_text.text("✅ Scan complete!")

        if scanner_results:
            df_scanner = pd.DataFrame(scanner_results)

            # Color code signals
            def color_signal(val):
                if val == "LONG":
                    return 'background-color: rgba(0, 255, 0, 0.2)'
                elif val == "SHORT":
                    return 'background-color: rgba(255, 0, 0, 0.2)'
                else:
                    return ''

            st.dataframe(
                df_scanner.style.applymap(color_signal, subset=['Signal']),
                use_container_width=True
            )

            st.success(f"✅ Scan complete! Found {len([r for r in scanner_results if r['Signal'] != 'NEUTRAL'])} opportunities.")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Bottom info
st.markdown("---")
st.info("""
**💡 Pro Tip**: Best signals have 4+ confirmations and align with higher timeframe trend.
Data is fetched live from Binance API every 30 seconds.
""")
