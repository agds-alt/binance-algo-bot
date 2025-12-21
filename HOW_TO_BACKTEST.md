# 📊 How to Run Backtests

## Method 1: Streamlit Dashboard (RECOMMENDED ⭐)

The easiest and best way to run backtests is through the web dashboard.

### Step 1: Start Dashboard

```bash
cd /home/dracarys/binance-algo-bot
source venv/bin/activate
streamlit run dashboard.py
```

The dashboard will open at: `http://localhost:8501`

### Step 2: Navigate to Backtesting Page

1. Open browser to `http://localhost:8501`
2. Click on **"📊 6_Backtesting"** in the sidebar
3. If you see "PRO feature" warning:
   - Go to **"🔐 5_License"** page first
   - Enter any license key to activate PRO features
   - Or generate one using: `python admin_license.py generate --tier pro --email test@test.com --days 365`

### Step 3: Configure Backtest

**Recommended Test Scenarios:**

#### Scenario A: Conservative (BTC 1h)
- **Trading Pair:** BTCUSDT
- **Timeframe:** 1h
- **Days to Backtest:** 60
- **Initial Capital:** $10,000
- **Risk per Trade:** 1.0%
- **Trading Fee:** 0.04%

**Expected Results:**
- Win Rate: 50-60%
- Return: 5-15% (60 days)
- Max Drawdown: <15%
- Good for: Beginners, steady growth

#### Scenario B: Balanced (ETH 15m)
- **Trading Pair:** ETHUSDT
- **Timeframe:** 15m
- **Days to Backtest:** 45
- **Initial Capital:** $10,000
- **Risk per Trade:** 1.5%
- **Trading Fee:** 0.04%

**Expected Results:**
- Win Rate: 45-55%
- Return: 8-20% (45 days)
- Max Drawdown: 10-20%
- Good for: Intermediate traders

#### Scenario C: Aggressive (BNB 5m)
- **Trading Pair:** BNBUSDT
- **Timeframe:** 5m
- **Days to Backtest:** 30
- **Initial Capital:** $10,000
- **Risk per Trade:** 2.0%
- **Trading Fee:** 0.04%

**Expected Results:**
- Win Rate: 40-50%
- Return: 10-30% (30 days)
- Max Drawdown: 15-30%
- Good for: Experienced scalpers

### Step 4: Click "Run Backtest"

The system will:
1. Fetch historical data from Binance
2. Calculate all indicators
3. Simulate all trades
4. Generate comprehensive metrics
5. Display interactive charts

### Step 5: Analyze Results

Look at these key metrics:

✅ **Must Pass Criteria:**
- Win Rate > 50%
- Profit Factor > 1.5
- Sharpe Ratio > 1.0
- Max Drawdown < 20%
- Total Trades >= 20

🟢 **Excellent Performance:**
- Win Rate > 60%
- Profit Factor > 2.0
- Sharpe Ratio > 2.0
- Max Drawdown < 10%

🔴 **Not Ready for Live Trading:**
- Win Rate < 45%
- Profit Factor < 1.2
- Max Drawdown > 25%
- Total Trades < 10

### Step 6: Export Results

- Click **"📥 Export CSV"** to save trade log
- Click **"📊 Export JSON"** to save full results
- Compare multiple backtests side-by-side

---

## Method 2: Command Line (Alternative)

If dashboard doesn't work, use synthetic data test:

```bash
cd /home/dracarys/binance-algo-bot
source venv/bin/activate
python test_backtest_demo.py
```

This uses synthetic data but verifies the system works.

---

## 📝 Backtesting Best Practices

### 1. Test Multiple Scenarios

Run at least 3 different combinations:
- Different symbols (BTC, ETH, BNB)
- Different timeframes (5m, 15m, 1h)
- Different periods (30, 45, 60 days)

### 2. Look for Consistency

A good strategy should:
- ✅ Work across multiple symbols
- ✅ Work in different market conditions
- ✅ Have consistent profit factor
- ✅ Have manageable drawdowns

Red flags:
- ❌ Only works on one symbol
- ❌ Huge variance in results
- ❌ Occasional huge wins masking many losses

### 3. Be Realistic

**DON'T expect:**
- 50% returns per month
- 90% win rate
- Zero drawdowns
- Consistent daily profits

**DO expect:**
- 5-15% monthly returns (excellent)
- 50-65% win rate (good)
- 10-20% max drawdown (acceptable)
- Losing streaks (normal)

### 4. Paper Trade First

Even if backtest looks great:
1. Paper trade for 2 weeks
2. Compare paper vs backtest
3. Only go live if similar
4. Start with small capital ($100-500)

---

## 🎯 Next Steps After Backtesting

### If Results Are Good (4/5 criteria passed):

```bash
# Step 1: Activate PRO license (if not already)
python admin_license.py generate --tier pro --email your@email.com --days 365

# Step 2: Configure for paper trading
# Edit .env file:
BINANCE_TESTNET=true
BINANCE_API_KEY=your_testnet_key
BINANCE_API_SECRET=your_testnet_secret

# Step 3: Run paper trading for 2 weeks
streamlit run dashboard.py
# Go to "7_Live_Trading" page
# Monitor performance daily

# Step 4: If paper trading matches backtest, go live with small capital
```

### If Results Are Poor (< 3 criteria):

1. **Optimize Parameters:**
   - Try different EMA periods
   - Adjust RSI thresholds
   - Test different confirmations (3/6, 4/6, 5/6)

2. **Try Different Timeframes:**
   - If 5m fails, try 15m
   - If 15m fails, try 1h
   - Higher timeframes = less noise

3. **Test Different Market Conditions:**
   - Trending markets (Aug-Sep 2024)
   - Ranging markets (Oct-Nov 2024)
   - High volatility periods

4. **Consider Strategy Changes:**
   - Optimized EMA (stricter)
   - Relaxed EMA (easier)
   - Stochastic RSI (mean reversion)

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if port 8501 is in use
lsof -i :8501
# Kill if needed
pkill -f streamlit
# Try again
streamlit run dashboard.py
```

### Can't fetch data
```bash
# Test Binance API
curl https://fapi.binance.com/fapi/v1/ping

# If fails, check firewall/network
# Or use VPN if Binance is blocked in your region
```

### "PRO feature" blocked
```bash
# Generate free PRO license
python admin_license.py generate --tier pro --email test@test.com --days 365

# Copy the license key
# Paste in dashboard "5_License" page
```

---

## 📞 Support

If you need help:
1. Check logs: `tail -f trading_bot.log`
2. Check data: `ls -lh data/`
3. Verify environment: `source venv/bin/activate && python --version`

---

**Remember:** Backtesting is not a guarantee of future performance, but it's the best tool we have to validate strategies before risking real money! 🎯
