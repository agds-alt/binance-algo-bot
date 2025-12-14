"""
Performance Dashboard
Charts, metrics, and analytics - REAL DATA
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.bot_state_manager import get_bot_state_manager

st.set_page_config(page_title="Performance", page_icon="💰", layout="wide")

st.title("💰 Performance Dashboard")

# Initialize state manager
state_manager = get_bot_state_manager()
stats = state_manager.get_stats()
bot_state = state_manager.get_bot_state()
trades = state_manager.get_trades(limit=1000)

# Time period selector
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    period = st.selectbox(
        "Time Period",
        ["Today", "This Week", "This Month", "All Time"],
        index=3
    )

with col2:
    if st.button("📊 Generate Report", use_container_width=True):
        if st.session_state.get('tier', 'free') == 'free':
            st.info("Report generation available in PRO tier")
        else:
            st.info("Report generation coming soon")

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Key Performance Metrics - REAL DATA
st.markdown("### 📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_pnl_pct = stats.total_pnl_percent
    st.metric("Total P&L", f"${stats.total_pnl:+,.2f}", f"{total_pnl_pct:+.2f}%", help="Total profit/loss")

with col2:
    st.metric("Win Rate", f"{stats.win_rate:.1f}%", help="Percentage of winning trades")

with col3:
    avg_win = stats.avg_win if stats.avg_win > 0 else 0
    avg_loss = stats.avg_loss if stats.avg_loss < 0 else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    st.metric("Profit Factor", f"{profit_factor:.2f}", help="Gross profit / Gross loss")

with col4:
    st.metric("Total Trades", f"{stats.total_trades}", help="Number of completed trades")

with col5:
    # Simplified Sharpe-like metric
    if trades and len(trades) > 1:
        returns = [t.pnl_percent for t in trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe = (avg_return / std_return) if std_return > 0 else 0
        st.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Risk-adjusted returns")
    else:
        st.metric("Sharpe Ratio", "0.00", help="Need more trades")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Equity Curve")

    if not trades:
        st.info("📊 Equity curve available after first trades. Run test_trading.py or start live trading!")
    else:
        # Build equity curve from trades
        sorted_trades = sorted(trades, key=lambda t: t.exit_time)

        initial_capital = bot_state.capital if bot_state.capital > 0 else 10000
        equity = [initial_capital]
        dates = [datetime.fromisoformat(sorted_trades[0].entry_time)]

        running_capital = initial_capital
        for trade in sorted_trades:
            running_capital += trade.pnl
            equity.append(running_capital)
            dates.append(datetime.fromisoformat(trade.exit_time))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity,
            mode='lines+markers',
            name='Equity',
            fill='tozeroy',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))

        fig.add_hline(y=initial_capital, line_dash="dash", line_color="gray", annotation_text=f"Initial: ${initial_capital:,.0f}")

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Date",
            yaxis_title="Capital ($)",
            hovermode='x unified',
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📊 Daily P&L")

    if not trades:
        st.info("📊 Daily P&L tracking will appear after trades")
    else:
        # Group trades by day
        daily_pnl = {}
        for trade in trades:
            day = datetime.fromisoformat(trade.exit_time).date()
            if day not in daily_pnl:
                daily_pnl[day] = 0
            daily_pnl[day] += trade.pnl

        dates = sorted(daily_pnl.keys())
        pnl_values = [daily_pnl[d] for d in dates]
        colors = ['green' if x > 0 else 'red' for x in pnl_values]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates,
            y=pnl_values,
            marker_color=colors,
            name='Daily P&L',
            text=[f"${x:+.0f}" for x in pnl_values],
            textposition='outside'
        ))

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Date",
            yaxis_title="P&L ($)",
            hovermode='x unified',
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

# More charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Win Rate by Pair")

    if not trades:
        st.info("⚠️ Analytics will appear after trades")
    else:
        # Calculate win rate per pair
        pair_stats = {}
        for trade in trades:
            if trade.symbol not in pair_stats:
                pair_stats[trade.symbol] = {'wins': 0, 'total': 0}
            pair_stats[trade.symbol]['total'] += 1
            if trade.pnl > 0:
                pair_stats[trade.symbol]['wins'] += 1

        pairs = list(pair_stats.keys())
        win_rates = [(pair_stats[p]['wins'] / pair_stats[p]['total'] * 100) for p in pairs]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pairs,
            y=win_rates,
            marker_color='#1f77b4',
            text=[f"{x:.1f}%" for x in win_rates],
            textposition='outside'
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Trading Pair",
            yaxis_title="Win Rate (%)",
            yaxis_range=[0, 100],
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📉 Drawdown")

    if not trades:
        st.info("⚠️ Drawdown tracking will appear after trades")
    else:
        # Calculate running drawdown
        sorted_trades = sorted(trades, key=lambda t: t.exit_time)

        initial_capital = bot_state.capital if bot_state.capital > 0 else 10000
        equity = initial_capital
        peak = initial_capital
        drawdown = [0]
        dates = [datetime.fromisoformat(sorted_trades[0].entry_time)]

        for trade in sorted_trades:
            equity += trade.pnl
            if equity > peak:
                peak = equity
            dd_pct = ((peak - equity) / peak * 100) if peak > 0 else 0
            drawdown.append(dd_pct)
            dates.append(datetime.fromisoformat(trade.exit_time))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=drawdown,
            mode='lines',
            fill='tozeroy',
            line=dict(color='red', width=2),
            name='Drawdown'
        ))

        fig.add_hline(y=5, line_dash="dash", line_color="orange", annotation_text="Max Daily DD (5%)")
        fig.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="Max Total DD (15%)")

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Statistics Table - REAL DATA
st.markdown("### 📋 Detailed Statistics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Trading Stats")

    stats_data = {
        "Metric": [
            "Total Trades",
            "Winning Trades",
            "Losing Trades",
            "Win Rate",
            "Average Win",
            "Average Loss",
            "Largest Win",
            "Largest Loss",
            "Profit Factor",
        ],
        "Value": [
            f"{stats.total_trades}",
            f"{stats.winning_trades}",
            f"{stats.losing_trades}",
            f"{stats.win_rate:.1f}%",
            f"${stats.avg_win:,.2f}" if stats.avg_win > 0 else "$0.00",
            f"${stats.avg_loss:,.2f}" if stats.avg_loss < 0 else "$0.00",
            f"${stats.best_trade:,.2f}" if stats.best_trade else "$0.00",
            f"${stats.worst_trade:,.2f}" if stats.worst_trade else "$0.00",
            f"{profit_factor:.2f}",
        ]
    }

    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### Risk Metrics")

    # Calculate from real data
    max_dd = max(drawdown) if trades else 0
    current_dd = drawdown[-1] if drawdown else 0

    # Calculate avg R-multiple
    avg_r = np.mean([t.r_multiple for t in trades]) if trades else 0

    # Calculate expectancy
    expectancy = stats.avg_win * (stats.win_rate/100) + stats.avg_loss * (1 - stats.win_rate/100) if trades else 0

    risk_data = {
        "Metric": [
            "Max Drawdown",
            "Current Drawdown",
            "Sharpe Ratio",
            "Avg R-Multiple",
            "Expectancy",
            "Today P&L",
            "Today Trades",
            "Signals Today",
        ],
        "Value": [
            f"{max_dd:.2f}%",
            f"{current_dd:.2f}%",
            f"{sharpe:.2f}" if trades and len(trades) > 1 else "0.00",
            f"{avg_r:.2f}R",
            f"${expectancy:+,.2f}",
            f"${stats.today_pnl:+,.2f}",
            f"{stats.today_trades}",
            f"{stats.signals_today}",
        ]
    }

    st.dataframe(pd.DataFrame(risk_data), use_container_width=True, hide_index=True)

# Monthly Performance (if enough data)
if trades and len(trades) > 5:
    st.markdown("---")
    st.markdown("### 📅 Monthly Performance")

    # Group by month
    monthly_pnl = {}
    for trade in trades:
        month = datetime.fromisoformat(trade.exit_time).strftime("%Y-%m")
        if month not in monthly_pnl:
            monthly_pnl[month] = 0
        monthly_pnl[month] += trade.pnl

    months = sorted(monthly_pnl.keys())
    returns = [monthly_pnl[m] for m in months]

    fig = go.Figure(data=go.Bar(
        x=months,
        y=returns,
        marker_color=['green' if x > 0 else 'red' for x in returns],
        text=[f"${x:+,.0f}" for x in returns],
        textposition='outside'
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Month",
        yaxis_title="Return ($)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# Upgrade CTA for free users
if st.session_state.get('tier', 'free') == 'free':
    st.markdown("---")
    st.warning("""
    ### 🚀 Unlock Full Analytics with PRO

    Get access to:
    - 📈 Real-time equity curve
    - 📊 Advanced performance metrics
    - 🎯 Per-pair analytics
    - 📉 Drawdown tracking
    - 📅 Historical performance

    **Upgrade to PRO for $99/month**
    """)

    if st.button("Upgrade Now", type="primary"):
        st.switch_page("pages/5_License.py")

# Footer
st.markdown("---")
st.info("""
**💡 Performance Tip**: Focus on consistency over big wins. Aim for positive expectancy and good risk/reward ratios.
""")
