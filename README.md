# 🤖 Binance Futures Algorithmic Trading Bot

**Production-Grade** scalping bot dengan strict risk management dan freemium tier system.

⚠️ **DISCLAIMER**: Trading cryptocurrency berisiko tinggi. Bot ini BUKAN jaminan profit. Use at your own risk.

---

## ✨ Features

### Core Features (All Tiers)
- ✅ Multi-timeframe technical analysis (5m/15m/1h)
- ✅ Strict risk management (hard limits)
- ✅ Partial take profits (50%/30%/20%)
- ✅ Automatic position sizing
- ✅ Emergency close all
- ✅ Telegram notifications

### FREE Tier
- 📊 Paper trading only
- 💰 Max $100 per trade
- 📈 Max 3 trades/day
- 🔄 1 concurrent position
- 🪙 BTC/USDT only

### PRO Tier ($99/mo)
- 🚀 **Live trading enabled**
- 💰 Max $5k per trade
- 📈 Max 20 trades/day
- 🔄 3 concurrent positions
- 🪙 5 trading pairs
- 📊 Advanced strategies
- 📉 Backtesting
- ⚡ Priority support

### PREMIUM Tier ($249/mo)
- 🌟 Everything in PRO +
- 💰 Unlimited position size
- 📈 Unlimited trades
- 🔄 10 concurrent positions
- 🪙 All pairs
- 🔄 Multi-exchange (Binance, Bybit, OKX)
- 🎯 Custom strategies
- 📞 24/7 VIP support

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd binance-algo-bot

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add your API keys
```

### 2. Get API Keys

**TESTNET** (Recommended for testing):
1. Visit https://testnet.binancefuture.com/
2. Login and generate API key
3. Add to `.env`

**PRODUCTION**:
1. Visit https://www.binance.com/en/my/settings/api-management
2. Create API with Futures enabled
3. Add to `.env` and set `BINANCE_TESTNET=false`

### 3. Run Bot

```bash
# Command Line Interface
python main.py --mode scan --capital 1000

# Web Dashboard (Recommended)
streamlit run dashboard.py
```

### 4. License Activation (For PRO/PREMIUM)

```bash
# Via Dashboard (Easiest):
# 1. Open dashboard
# 2. Go to License page
# 3. Enter license key
# 4. Click "Activate License"

# Via Python:
python -c "from modules.license_state import get_license_state; \
state = get_license_state(); \
print(state.activate('YOUR-LICENSE-KEY-HERE'))"
```

---

## 🔐 License System

### For Customers

**Activate Your License:**
1. Purchase a license (PRO or PREMIUM)
2. Receive license key via email
3. Open the dashboard
4. Go to "License" page
5. Enter your license key
6. Click "✅ Activate License"
7. ✅ Done! You now have full access

**Features:**
- ✅ Secure hardware binding (one device per license)
- ✅ Automatic tier detection
- ✅ Easy deactivation/reactivation
- ✅ License expiry tracking
- ✅ Multi-device support (PREMIUM tier)

### For Admins

**Generate Licenses:**
```bash
# Generate PRO license (30 days)
python admin_license.py generate --tier pro --email user@example.com --days 30

# Generate PREMIUM license (90 days, 2 devices)
python admin_license.py generate --tier premium --email vip@example.com --days 90 --max-activations 2

# List all licenses
python admin_license.py list

# Extend license
python admin_license.py extend LICENSE-KEY --days 30

# Upgrade tier
python admin_license.py upgrade LICENSE-KEY --tier premium
```

**Full Documentation:** See [LICENSE_SYSTEM.md](LICENSE_SYSTEM.md) for complete guide

---

## 📊 Risk Management

### Hard Limits (Cannot Be Overridden)

| Parameter | Limit | Description |
|-----------|-------|-------------|
| Risk/Trade | 1% | Max loss per trade |
| Daily Drawdown | 5% | Stop if lose 5% today |
| Total Drawdown | 15% | Stop if lose 15% total |
| Leverage | 10x | Maximum leverage |
| Stop Loss | 2% | Max SL distance |
| Min R:R | 1.5:1 | Minimum risk:reward |
| Concurrent Positions | 3 | Max open trades |
| Daily Trades | 10 | Max trades per day |
| Consecutive Losses | 3 | Cooldown after 3 losses |
| Cooldown | 4h | Break after loss streak |

---

## 📈 Strategy: Scalping

### Entry Criteria (Min 4/6 confirmations)
- ✅ EMA crossover (9/21)
- ✅ Price vs trend EMA (50)
- ✅ RSI confirmation
- ✅ Volume spike (> 120% avg)
- ✅ Higher timeframe alignment
- ✅ Spread check (< 0.05%)

### Exit Strategy
- TP1: 50% @ 1.5R
- TP2: 30% @ 2.0R
- TP3: 20% @ 3.0R
- SL: ATR-based (max 2%)

---

## 🖥️ Web Dashboard

Access full-featured dashboard at `http://localhost:8501`

Features:
- 📊 Live market analysis
- 📈 Performance charts
- 💰 P&L tracking
- 🎯 Trade history
- ⚙️ Settings
- 🔐 License management

```bash
streamlit run dashboard.py
```

---

## 🔐 Licensing

### Activate License

```bash
python -c "from modules.license_manager import LicenseManager; \
    lm = LicenseManager(); \
    lm.activate('YOUR_LICENSE_KEY', 'your@email.com')"
```

### Check Status

```bash
python -c "from modules.license_manager import LicenseManager; \
    lm = LicenseManager(); \
    print(lm.get_tier_info())"
```

---

## 📁 Project Structure

```
binance-algo-bot/
├── modules/
│   ├── config.py              # Configuration
│   ├── binance_client.py      # Exchange API
│   ├── risk_manager.py        # Risk management
│   ├── tier_manager.py        # Tier system
│   ├── scalping_strategy.py  # TA & signals
│   ├── trade_executor.py      # Order execution
│   ├── license_manager.py     # Licensing
│   └── telegram_bot.py        # Notifications
├── config/
│   ├── config.yaml            # Main config
│   └── tiers.yaml             # Tier definitions
├── dashboard.py               # Streamlit GUI
├── main.py                    # CLI interface
├── requirements.txt           # Dependencies
├── .env.example               # Env template
└── README.md                  # This file
```

---

## 🚨 Emergency Commands

### Close All Positions

```bash
python main.py --mode close-all
```

### Stop Bot

```bash
# Press Ctrl+C or
pkill -f "python main.py"
```

---

## 📞 Support

- 📧 Email: support@your-domain.com
- 💬 Telegram: @your_support_bot
- 📚 Docs: https://docs.your-domain.com

---

## ⚖️ License

Proprietary - Commercial use requires valid license key.

---

**Made with ❤️ for algorithmic traders**
