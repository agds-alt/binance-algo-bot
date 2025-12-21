# Adding Fundamental Analysis to Algo Bot

## Current State: 100% Technical Analysis (TA)

Our bot uses:
- EMA crossovers
- RSI momentum
- Volume analysis (basic)
- ATR volatility
- Stochastic RSI

**No fundamental analysis currently!**

---

## Quick Wins: Easy to Add

### 1. Money Flow Index (MFI)

**What it is:** Volume-weighted RSI, tracks money flowing in/out

**How to add:**

```python
# In modules/data_fetcher.py, add to calculate_indicators():

def calculate_mfi(df, period=14):
    """Calculate Money Flow Index"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    money_flow = typical_price * df['volume']

    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)

    positive_mf = positive_flow.rolling(period).sum()
    negative_mf = negative_flow.rolling(period).sum()

    mfi = 100 - (100 / (1 + positive_mf / negative_mf))
    return mfi

# Add to calculate_indicators():
df['mfi'] = calculate_mfi(df, period=14)
```

**Use in strategy:**

```python
# In signal generation:
# 7. MFI confirmation (avoid extremes)
mfi_ok = 30 < current['mfi'] < 70
checks['7_mfi'] = f"{'✅' if mfi_ok else '❌'} MFI: {current['mfi']:.1f}"
if mfi_ok:
    confirmations += 1

# Now require 5/7 confirmations instead of 4/6
```

**Benefits:**
- Filters out low-liquidity pumps/dumps
- Reduces false signals
- Better entry timing

---

### 2. Funding Rate Filter (Futures Trading)

**What it is:** Cost of holding long/short position. High funding = overleveraged market.

**How to add:**

```python
# New file: modules/funding_rate.py

import httpx

async def get_funding_rate(symbol='BTCUSDT'):
    """Get current funding rate from Binance Futures"""
    url = 'https://fapi.binance.com/fapi/v1/premiumIndex'

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={'symbol': symbol})
        data = response.json()

        return {
            'funding_rate': float(data['lastFundingRate']),
            'next_funding_time': data['nextFundingTime'],
            'mark_price': float(data['markPrice'])
        }

def is_funding_rate_reasonable(funding_rate):
    """
    Check if funding rate is reasonable for trading

    Funding Rate Guide:
    - Normal: -0.01% to +0.01%
    - High: > +0.05% (too bullish, avoid long)
    - Very High: > +0.10% (overleveraged, consider short)
    - Negative: < -0.01% (shorts paying, good for long)
    """

    # Avoid longing when funding too high
    if funding_rate > 0.0005:  # 0.05%
        return False, "Funding rate too high (overleveraged longs)"

    # Avoid shorting when funding negative
    if funding_rate < -0.0005:  # -0.05%
        return False, "Funding rate negative (strong buying)"

    return True, "Funding rate reasonable"
```

**Use in strategy:**

```python
# Before entering trade:
funding_data = await get_funding_rate(symbol)
is_reasonable, reason = is_funding_rate_reasonable(funding_data['funding_rate'])

if not is_reasonable:
    print(f"⚠️ Skipping trade: {reason}")
    return None
```

**Benefits:**
- Avoid entering overleveraged markets
- Better risk-adjusted returns
- Catch market regime changes

---

### 3. VWAP (Volume Weighted Average Price)

**What it is:** Average price weighted by volume. Institutional traders use this.

**How to add:**

```python
# In modules/data_fetcher.py:

def calculate_vwap(df):
    """Calculate VWAP"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap

# Add to calculate_indicators():
df['vwap'] = calculate_vwap(df)
```

**Use in strategy:**

```python
# Entry filter:
# For longs: prefer entries near or below VWAP
# For shorts: prefer entries near or above VWAP

distance_from_vwap = (current['close'] - current['vwap']) / current['vwap'] * 100

# For LONG: buy when price near/below VWAP
if side == 'LONG':
    vwap_ok = distance_from_vwap < 0.5  # Within 0.5% above VWAP

# For SHORT: sell when price near/above VWAP
elif side == 'SHORT':
    vwap_ok = distance_from_vwap > -0.5  # Within 0.5% below VWAP
```

**Benefits:**
- Better entry prices
- Align with institutional flow
- Dynamic support/resistance

---

## Medium Complexity Additions

### 4. Order Book Imbalance

**Requires:** Level 2 order book data (Binance WebSocket)

```python
# Detect large buy/sell walls
def get_order_book_imbalance(symbol):
    # Get top 20 bid/ask levels
    bids = sum(bid['quantity'] for bid in top_20_bids)
    asks = sum(ask['quantity'] for ask in top_20_asks)

    imbalance = (bids - asks) / (bids + asks)

    # imbalance > 0.3 = strong buy pressure
    # imbalance < -0.3 = strong sell pressure

    return imbalance
```

### 5. Exchange Flow Monitoring

**Requires:** Whale Alert API or similar

```python
# Track large transfers to/from exchanges
def check_whale_activity(symbol, last_hour=1):
    # Get large transactions (>$1M)
    large_deposits = get_exchange_deposits(symbol, min_value=1000000)
    large_withdrawals = get_exchange_withdrawals(symbol, min_value=1000000)

    # Many deposits = selling pressure
    # Many withdrawals = accumulation

    net_flow = sum(withdrawals) - sum(deposits)
    return net_flow
```

---

## Advanced Additions

### 6. On-Chain Metrics (Glassnode/CryptoQuant)

**Requires:** Paid API subscription ($50-200/month)

```python
# Examples:
- NUPL (Net Unrealized Profit/Loss)
- MVRV (Market Value to Realized Value)
- Active Addresses
- Exchange Reserves
- Miner Outflow

# Use as macro filters
if nupl < 0:  # Market in loss
    increase_position_size()  # Better risk/reward
elif nupl > 0.7:  # Market in extreme profit
    reduce_position_size()  # Take profits
```

### 7. Sentiment Analysis

**Requires:** Twitter API, Reddit API, or LunarCrush

```python
# Aggregate social sentiment
def get_market_sentiment(symbol):
    twitter_sentiment = analyze_twitter_mentions(symbol)
    reddit_sentiment = analyze_reddit_discussions(symbol)

    overall_sentiment = (twitter_sentiment + reddit_sentiment) / 2

    # -1 to +1 scale
    # Contrarian: Buy at -0.7, Sell at +0.7

    return overall_sentiment
```

---

## Recommended Implementation Order

### Phase 1 (Start Here):
1. ✅ MFI (Money Flow Index) - Easy, high impact
2. ✅ VWAP - Better entries
3. ✅ Funding Rate - Risk filter

**Estimated time:** 2-3 hours
**Impact:** 10-20% improvement in win rate

### Phase 2 (After validation):
4. Order Book Imbalance
5. Basic Sentiment (Fear & Greed Index)

**Estimated time:** 1-2 days
**Impact:** 5-10% improvement

### Phase 3 (Advanced):
6. On-Chain Metrics (paid APIs)
7. Full Sentiment Analysis
8. Machine Learning (predict next move)

**Estimated time:** 1-2 weeks
**Impact:** Potentially 15-25% improvement

---

## Testing Fundamental Additions

**IMPORTANT:** Each addition must be backtested!

```bash
# After adding MFI:
python backtest_with_local_data.py --strategy ema_with_mfi

# Compare results:
# Before: 60% win rate, 14% return
# After: 65% win rate, 18% return = GOOD
# After: 45% win rate, 8% return = BAD, remove MFI
```

**Rule:** Only add fundamental indicator if it improves:
- Win rate by >5%
- OR Profit factor by >0.3
- OR Reduces max drawdown by >5%

---

## Sample Enhanced Strategy

```python
def enhanced_ema_with_fundamentals(df):
    """EMA + TA + Fundamentals"""

    # Technical Analysis (existing)
    ema_cross = check_ema_crossover(df)
    rsi_ok = 30 < df['rsi'].iloc[-1] < 70
    volume_ok = df['volume'].iloc[-1] > df['volume_ma'].iloc[-1] * 1.2

    # Fundamental Filters (NEW)
    mfi_ok = 30 < df['mfi'].iloc[-1] < 70
    vwap_ok = abs(df['close'].iloc[-1] - df['vwap'].iloc[-1]) / df['vwap'].iloc[-1] < 0.005
    funding_ok = check_funding_rate()

    # Combine
    confirmations = sum([
        ema_cross,      # 1
        rsi_ok,         # 2
        volume_ok,      # 3
        mfi_ok,         # 4 (NEW)
        vwap_ok,        # 5 (NEW)
        funding_ok      # 6 (NEW)
    ])

    # Require 5/6 confirmations
    if confirmations >= 5:
        return generate_signal(df)

    return None
```

---

## Conclusion

**Current:** 100% Technical Analysis ✅
**Recommended:** Add 2-3 fundamental filters for better results
**Start with:** MFI, VWAP, Funding Rate
**Test everything:** Backtest before deploying

**Remember:** More indicators ≠ better strategy. Only add what improves performance!
