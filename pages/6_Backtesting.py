"""
Backtesting Page
Run strategy backtests and view results
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import Backtester, simple_ema_crossover_signals

st.set_page_config(page_title="Backtesting", page_icon="📊", layout="wide")

# Enhanced CSS for Backtesting page
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
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Strategy Backtesting</div>', unsafe_allow_html=True)
st.caption("Test strategies on historical data before live trading")

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
    st.warning("⚠️ Backtesting is a **PRO** feature. Upgrade to access!")

    st.info("""
    ### 🎯 Why Backtest?

    - ✅ Test strategies on historical data
    - ✅ See performance metrics (win rate, Sharpe ratio, etc)
    - ✅ Optimize parameters
    - ✅ Build confidence before live trading

    **Upgrade to PRO to unlock backtesting!**
    """)

    if st.button("🚀 Upgrade to PRO", type="primary"):
        st.switch_page("pages/5_License.py")

    st.stop()

# PRO feature unlocked
st.success("✅ Backtesting enabled (PRO feature)")

# Backtest configuration
st.markdown('<div class="section-header">⚙️ Backtest Configuration</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    symbol = st.selectbox(
        "Trading Pair",
        ["BNBUSDT", "BTCUSDT", "ETHUSDT"],
        help="Select trading pair to backtest"
    )

with col2:
    timeframe = st.selectbox(
        "Timeframe",
        ["5m", "15m", "1h", "4h"],
        help="Candle timeframe"
    )

with col3:
    days_back = st.number_input(
        "Days to Backtest",
        min_value=7,
        max_value=90,
        value=30,
        help="Number of days of historical data"
    )

# Capital and risk settings
col1, col2, col3 = st.columns(3)

with col1:
    initial_capital = st.number_input(
        "Initial Capital (USDT)",
        min_value=100,
        max_value=100000,
        value=10000,
        step=1000
    )

with col2:
    risk_per_trade = st.slider(
        "Risk per Trade (%)",
        min_value=0.5,
        max_value=3.0,
        value=1.5,
        step=0.1
    ) / 100

with col3:
    fee_percent = st.number_input(
        "Trading Fee (%)",
        min_value=0.0,
        max_value=0.1,
        value=0.04,
        step=0.01,
        format="%.3f"
    ) / 100

# Run backtest button
if st.button("🚀 Run Backtest", type="primary", use_container_width=True):

    with st.spinner(f"Fetching {days_back} days of {symbol} {timeframe} data..."):
        # Fetch data
        fetcher = DataFetcher(use_testnet=False)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)

        df = fetcher.fetch_klines_sync(
            symbol=symbol,
            interval=timeframe,
            start_time=start_time,
            end_time=end_time
        )

        if df.empty:
            st.error("❌ Failed to fetch data. Please try again.")
            st.stop()

        st.success(f"✅ Fetched {len(df)} candles from {df.index[0]} to {df.index[-1]}")

    with st.spinner("Calculating indicators..."):
        # Calculate indicators
        df = fetcher.calculate_indicators(df)
        st.success("✅ Indicators calculated")

    with st.spinner("Running backtest..."):
        # Run backtest
        backtester = Backtester(
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade,
            fee_percent=fee_percent
        )

        result = backtester.run_backtest(
            df=df,
            symbol=symbol,
            generate_signals_func=simple_ema_crossover_signals,
            timeframe=timeframe
        )

        # Store in session state
        st.session_state['backtest_result'] = result
        st.success("✅ Backtest completed!")

# Display results if available
if 'backtest_result' in st.session_state:
    result = st.session_state['backtest_result']

    st.markdown("---")
    st.markdown("## 📈 Backtest Results")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Return",
            f"${result.total_return:.2f}",
            f"{result.total_return_percent:.2f}%"
        )

    with col2:
        st.metric(
            "Win Rate",
            f"{result.win_rate:.1f}%",
            f"{result.winning_trades}/{result.total_trades} wins"
        )

    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{result.sharpe_ratio:.2f}",
            "Higher is better"
        )

    with col4:
        st.metric(
            "Max Drawdown",
            f"{result.max_drawdown_percent:.2f}%",
            f"${result.max_drawdown:.2f}"
        )

    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Trades", result.total_trades)

    with col2:
        st.metric("Profit Factor", f"{result.profit_factor:.2f}")

    with col3:
        st.metric("Avg R-Multiple", f"{result.average_rr:.2f}R")

    with col4:
        st.metric("Duration", f"{result.duration_days} days")

    # Equity curve
    st.markdown('<div class="section-header">📊 Equity Curve</div>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=result.equity_dates,
        y=result.equity_curve,
        mode='lines',
        name='Equity',
        fill='tozeroy',
        line=dict(color='#1f77b4', width=2)
    ))

    fig.update_layout(
        title=f"{result.symbol} - Equity Curve",
        xaxis_title="Date",
        yaxis_title="Equity (USDT)",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Drawdown curve
    st.markdown('<div class="section-header">📉 Drawdown</div>', unsafe_allow_html=True)

    fig_dd = go.Figure()

    fig_dd.add_trace(go.Scatter(
        x=result.equity_dates,
        y=result.drawdown_curve,
        mode='lines',
        name='Drawdown',
        fill='tozeroy',
        line=dict(color='#d62728', width=2)
    ))

    fig_dd.update_layout(
        title="Drawdown Over Time",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode='x unified',
        height=300
    )

    st.plotly_chart(fig_dd, use_container_width=True)

    # Performance breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">💰 P&L Breakdown</div>', unsafe_allow_html=True)

        st.markdown(f"""
        **Gross Profit:** ${result.gross_profit:.2f}
        **Gross Loss:** ${result.gross_loss:.2f}
        **Net Profit:** ${result.net_profit:.2f}

        **Average Win:** ${result.average_win:.2f}
        **Average Loss:** ${result.average_loss:.2f}
        **Largest Win:** ${result.largest_win:.2f}
        **Largest Loss:** ${result.largest_loss:.2f}
        """)

    with col2:
        st.markdown('<div class="section-header">📊 Trade Statistics</div>', unsafe_allow_html=True)

        st.markdown(f"""
        **Total Trades:** {result.total_trades}
        **Winning Trades:** {result.winning_trades} ({result.win_rate:.1f}%)
        **Losing Trades:** {result.losing_trades}
        **Breakeven Trades:** {result.breakeven_trades}

        **Win Rate:** {result.win_rate:.1f}%
        **Profit Factor:** {result.profit_factor:.2f}
        **Avg R-Multiple:** {result.average_rr:.2f}R
        """)

    # Trade log
    st.markdown('<div class="section-header">📋 Trade Log</div>', unsafe_allow_html=True)

    if result.trades:
        # Convert to DataFrame
        trades_df = pd.DataFrame(result.trades)

        # Format columns
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])

        # Display table
        st.dataframe(
            trades_df[[
                'entry_time', 'exit_time', 'side', 'entry_price',
                'exit_price', 'pnl', 'pnl_percent', 'r_multiple',
                'exit_reason', 'status'
            ]].style.format({
                'entry_price': '${:.2f}',
                'exit_price': '${:.2f}',
                'pnl': '${:.2f}',
                'pnl_percent': '{:.2f}%',
                'r_multiple': '{:.2f}R'
            }),
            height=400,
            use_container_width=True
        )

        # Export button
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("📥 Export CSV"):
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"backtest_{result.symbol}_{result.timeframe}.csv",
                    "text/csv"
                )

        with col2:
            if st.button("📊 Export JSON"):
                import json
                json_data = json.dumps(result.to_dict(), indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    f"backtest_{result.symbol}_{result.timeframe}.json",
                    "application/json"
                )
    else:
        st.info("No trades were generated during the backtest period.")

    # Performance summary
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Summary</div>', unsafe_allow_html=True)

    # Color code performance
    if result.total_return_percent > 10:
        perf_color = "🟢"
        perf_text = "Excellent"
    elif result.total_return_percent > 5:
        perf_color = "🟡"
        perf_text = "Good"
    elif result.total_return_percent > 0:
        perf_color = "🟠"
        perf_text = "Positive"
    else:
        perf_color = "🔴"
        perf_text = "Negative"

    st.info(f"""
    **Performance:** {perf_color} {perf_text}

    - Strategy generated **{result.total_return_percent:.2f}%** return over **{result.duration_days} days**
    - Win rate of **{result.win_rate:.1f}%** with **{result.total_trades} trades**
    - Sharpe ratio: **{result.sharpe_ratio:.2f}** | Sortino ratio: **{result.sortino_ratio:.2f}**
    - Maximum drawdown: **{result.max_drawdown_percent:.2f}%**

    **Risk Assessment:** {'✅ Acceptable' if result.max_drawdown_percent < 15 else '⚠️ High risk'}
    """)

else:
    st.info("👆 Configure backtest parameters above and click '🚀 Run Backtest' to get started!")

    # Example results
    st.markdown("---")
    st.markdown('<div class="section-header">📚 What You\'ll Get</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Performance Metrics:**
        - Total return & return %
        - Win rate & profit factor
        - Sharpe & Sortino ratios
        - Maximum drawdown
        - Average R-multiple

        **Visual Analysis:**
        - Equity curve chart
        - Drawdown curve
        - Trade distribution
        """)

    with col2:
        st.markdown("""
        **Trade Analysis:**
        - Complete trade log
        - Entry/exit prices
        - P&L per trade
        - Exit reasons
        - R-multiples

        **Export Options:**
        - CSV export
        - JSON export
        - HTML report (coming soon)
        """)
