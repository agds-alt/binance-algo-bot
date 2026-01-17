# 🚀 Deploy Binance Algo Bot to Railway

Railway is a deployment platform that makes it easy to deploy Python apps with a free tier ($5/month credit).

## 📋 Prerequisites

- GitHub account
- Railway account (free signup)
- Binance API keys (testnet or production)

---

## 🎯 Step-by-Step Deployment Guide

### Step 1: Sign Up for Railway

1. Go to **https://railway.app/**
2. Click **"Start a New Project"** or **"Login"**
3. Sign in with your **GitHub account**
4. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Choose repository: **`agds-alt/binance-algo-bot`**
4. Railway will automatically detect it's a Python project

### Step 3: Configure Environment Variables

Click on your deployed service → **"Variables"** tab → Add these variables:

#### Required Variables:
```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_TESTNET=true
```

#### Optional Variables (if using features):
```env
# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# License (for PRO/PREMIUM features)
LICENSE_KEY=your_license_key
USER_EMAIL=your@email.com
TIER=free

# Stripe (for payment processing)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### Step 4: Deploy!

1. Click **"Deploy"** button
2. Railway will:
   - Install Python dependencies from `requirements.txt`
   - Build the project
   - Start the Streamlit dashboard
3. Wait 2-3 minutes for deployment to complete

### Step 5: Access Your Bot

1. Go to **"Settings"** tab
2. Click **"Generate Domain"** to get a public URL
3. Example: `https://binance-algo-bot-production.up.railway.app`
4. Open the URL in your browser
5. ✅ Your dashboard is live!

---

## 🔧 Advanced Configuration

### Running the Trading Bot (Worker)

By default, Railway runs the **Streamlit dashboard**. To run the trading bot:

1. Go to service **Settings**
2. Find **"Start Command"**
3. Change to: `python main.py --mode scan --capital 1000`
4. Redeploy

Or you can create **two services**:
- Service 1: Dashboard (Streamlit)
- Service 2: Bot (main.py worker)

### Auto-Deploy from GitHub

Railway automatically redeploys when you push to GitHub!

```bash
# Make changes locally
git add .
git commit -m "Update bot strategy"
git push

# Railway auto-deploys in 1-2 minutes!
```

### View Logs

1. Go to your service
2. Click **"Deployments"** tab
3. Click on latest deployment
4. View **"Logs"** in real-time

### Restart Service

1. Go to service page
2. Click **"⋮"** (three dots)
3. Select **"Restart"**

---

## 💰 Pricing & Usage

### Free Tier:
- **$5 USD credit per month**
- 500 hours of execution time
- Perfect for testing and small-scale trading

### Usage Tips:
- Dashboard uses ~0.5GB RAM (~$3-4/month)
- Trading bot uses ~0.2GB RAM (~$1-2/month)
- Total: Can run 24/7 within free tier!

### Monitor Usage:
1. Go to **"Usage"** tab
2. See real-time cost
3. Set spending limits if needed

---

## 🚨 Troubleshooting

### Bot Won't Start
**Error**: `Module not found: streamlit`

**Fix**:
- Check `requirements.txt` exists
- Verify Python version in `runtime.txt` (optional)
- Rebuild: Settings → Redeploy

### Environment Variables Not Working
**Error**: API keys not loaded

**Fix**:
- Double-check variable names (case-sensitive)
- No spaces in values
- Restart service after adding variables

### Port Binding Error
**Error**: `Port already in use`

**Fix**: Railway provides `$PORT` variable automatically. Streamlit config in `Procfile` handles this.

### Database/State Not Persisting
**Problem**: Trades/licenses lost on restart

**Fix**:
- Railway uses ephemeral storage
- For persistent data, add Railway PostgreSQL:
  - Click "New" → "Database" → "PostgreSQL"
  - Connect to bot via DATABASE_URL

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   - `.env` is in `.gitignore`
   - Use Railway Variables instead

2. **Use Testnet first**
   - Set `BINANCE_TESTNET=true`
   - Test all features before production

3. **Enable 2FA on Railway**
   - Settings → Security → Enable 2FA

4. **API Key Permissions**
   - Only enable "Read" + "Futures Trading"
   - Disable "Withdrawals"

---

## 📊 Monitoring Your Bot

### Health Checks
Railway auto-monitors your service:
- HTTP health checks every 30s
- Auto-restart on failure
- Email notifications on downtime

### Custom Monitoring
Add to your `main.py`:
```python
import requests

def send_health_ping():
    """Ping external monitoring service"""
    requests.get("https://hc-ping.com/your-check-id")
```

Recommended services:
- **UptimeRobot** (free)
- **Healthchecks.io** (free tier)

---

## 🎯 Next Steps

After deployment:

1. ✅ Test dashboard at your Railway URL
2. ✅ Configure API keys in Settings page
3. ✅ Run backtest to verify strategy
4. ✅ Start with paper trading (FREE tier)
5. ✅ Activate PRO license for live trading
6. ✅ Set up Telegram notifications
7. ✅ Monitor logs and performance

---

## 🆘 Support

If you have issues:

1. **Check Railway Logs** first
2. **GitHub Issues**: https://github.com/agds-alt/binance-algo-bot/issues
3. **Railway Docs**: https://docs.railway.app/
4. **Discord**: Join Railway Discord for help

---

**🎉 Congratulations! Your trading bot is now deployed to the cloud!**

Happy trading! 🚀💰

---

## Quick Commands Reference

```bash
# Local development
streamlit run dashboard.py
python main.py --mode scan

# Railway CLI (optional)
railway login
railway link
railway up
railway logs
railway open

# Git deployment
git add .
git commit -m "Update"
git push  # Auto-deploys to Railway!
```
