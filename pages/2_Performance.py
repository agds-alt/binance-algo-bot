"""
Performance Dashboard
Charts, metrics, and analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Performance", page_icon="💰", layout="wide")

st.title("💰 Performance Dashboard")

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
        st.info("Report generation available in PRO tier")

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Key Performance Metrics
st.markdown("### 📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total P&L", "$0.00", "0%", help="Total profit/loss")

with col2:
    st.metric("Win Rate", "0%", help="Percentage of winning trades")

with col3:
    st.metric("Profit Factor", "0.00", help="Gross profit / Gross loss")

with col4:
    st.metric("Total Trades", "0", help="Number of completed trades")

with col5:
    st.metric("Sharpe Ratio", "0.00", help="Risk-adjusted returns")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Equity Curve")

    # Mock equity curve
    if st.session_state.get('tier', 'free') == 'free':
        st.info("📊 Equity curve available after first trades. Start with paper trading!")
    else:
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        equity = 1000 + np.cumsum(np.random.randn(30) * 50)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity,
            mode='lines',
            name='Equity',
            fill='tozeroy',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.add_hline(y=1000, line_dash="dash", line_color="gray", annotation_text="Initial Capital")

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

    if st.session_state.get('tier', 'free') == 'free':
        st.info("📊 Daily P&L tracking available in PRO tier")
    else:
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        daily_pnl = np.random.randn(30) * 50

        colors = ['green' if x > 0 else 'red' for x in daily_pnl]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates,
            y=daily_pnl,
            marker_color=colors,
            name='Daily P&L'
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

    if st.session_state.get('tier', 'free') == 'free':
        st.warning("⚠️ Advanced analytics require PRO tier")
    else:
        pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        win_rates = [65, 58, 72, 61]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pairs,
            y=win_rates,
            marker_color='#1f77b4',
            text=[f"{x}%" for x in win_rates],
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

    if st.session_state.get('tier', 'free') == 'free':
        st.warning("⚠️ Drawdown tracking requires PRO tier")
    else:
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        drawdown = np.abs(np.minimum(np.cumsum(np.random.randn(30) * 2), 0))

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

# Statistics Table
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
            "0",
            "0",
            "0",
            "0%",
            "$0.00",
            "$0.00",
            "$0.00",
            "$0.00",
            "0.00",
        ]
    }

    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### Risk Metrics")

    risk_data = {
        "Metric": [
            "Max Drawdown",
            "Current Drawdown",
            "Sharpe Ratio",
            "Sortino Ratio",
            "Calmar Ratio",
            "Recovery Factor",
            "Risk/Reward Avg",
            "Expectancy",
            "Consecutive Wins/Losses",
        ],
        "Value": [
            "0%",
            "0%",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "0.00",
            "$0.00",
            "0/0",
        ]
    }

    st.dataframe(pd.DataFrame(risk_data), use_container_width=True, hide_index=True)

# Monthly Performance
st.markdown("---")
st.markdown("### 📅 Monthly Performance")

if st.session_state.get('tier', 'free') != 'premium':
    st.info("📊 Monthly heatmap available in PREMIUM tier")
else:
    # Mock monthly heatmap
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    returns = np.random.randn(12) * 5

    fig = go.Figure(data=go.Bar(
        x=months,
        y=returns,
        marker_color=['green' if x > 0 else 'red' for x in returns],
        text=[f"{x:.1f}%" for x in returns],
        textposition='outside'
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Month",
        yaxis_title="Return (%)",
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
