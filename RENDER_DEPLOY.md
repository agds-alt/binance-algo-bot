# 🚀 Deploy BotX to Render.com

**100% FREE** - No Credit Card Required!

---

## ✅ Why Render.com?

- ✅ **$0/month** - Completely FREE forever
- ✅ **No credit card** needed
- ✅ **750 hours/month** free (enough for testing)
- ✅ **Auto-deploy** from GitHub
- ✅ **SSL included** (HTTPS)
- ⚠️ **Sleep after 15 min idle** (cold start ~30s)

**Perfect for**: Testing, demos, low-traffic bots

---

## 🎯 Quick Deploy (5 Minutes!)

### **Step 1: Sign Up**

1. Go to: https://render.com/
2. Click **"Get Started"**
3. **Sign up with GitHub** (easiest!)
4. Authorize Render to access your repos

### **Step 2: Create New Web Service**

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - Repository: `agds-alt/binance-algo-bot`
3. Click **"Connect"**

### **Step 3: Configure Service**

Render will auto-detect `render.yaml` but double-check:

**Basic Settings:**
- **Name**: `botx-dashboard` (or your choice)
- **Region**: Oregon (Free)
- **Branch**: `master`
- **Root Directory**: (leave empty)

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**:
  ```
  streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```

**Plan:**
- ✅ Select **"Free"** ($0/month)

### **Step 4: Add Environment Variables**

Click **"Advanced"** → **"Environment Variables"**

**Required Variables:**
```env
PYTHON_VERSION=3.11.0
BINANCE_TESTNET=true
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

**Optional (if you have API keys):**
```env
BINANCE_API_KEY=your_testnet_key
BINANCE_API_SECRET=your_testnet_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### **Step 5: Deploy!**

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Build the app
   - Deploy!
3. Wait **3-5 minutes** for first deploy

### **Step 6: Access Your Bot**

1. Once deployed, you'll get a URL:
   ```
   https://botx-dashboard.onrender.com
   ```
2. Click the URL to open your dashboard!
3. ✅ **Bot is LIVE!**

---

## 🔄 Auto-Deploy Setup

Render **automatically deploys** when you push to GitHub!

```bash
# Make changes locally
git add .
git commit -m "Update bot"
git push

# Render auto-deploys in 2-3 minutes! 🚀
```

---

## ⚠️ Free Tier Limitations

### **Sleep Mode:**
- Service **sleeps after 15 minutes** of inactivity
- First request after sleep = **~30 seconds cold start**
- Subsequent requests = fast!

### **Workaround (Keep Awake):**

**Option 1: Use UptimeRobot** (Free)
1. Sign up: https://uptimerobot.com/
2. Create monitor:
   - URL: `https://your-app.onrender.com`
   - Interval: 5 minutes
3. Free tier pings every 5 min = **no sleep!**

**Option 2: Cron Job** (Local)
```bash
# Ping every 10 minutes
*/10 * * * * curl https://your-app.onrender.com
```

### **Monthly Limits:**
- **750 hours/month FREE**
- With UptimeRobot = **720 hours** (24/7 for 30 days) ✅
- **Within free tier!**

---

## 📊 Monitor Your App

### **View Logs:**
1. Render Dashboard → Your Service
2. Click **"Logs"** tab
3. See real-time logs

### **Deployment History:**
1. Click **"Events"** tab
2. See all deployments
3. Rollback if needed

### **Metrics:**
1. Click **"Metrics"** tab
2. See:
   - CPU usage
   - Memory usage
   - Response times

---

## 🔧 Troubleshooting

### **Problem: Build Failed**

**Check logs:**
```
Render Dashboard → Logs → Build Logs
```

**Common fixes:**
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Port configuration

### **Problem: App Crashes**

**Check runtime logs:**
```
Logs → Runtime Logs
```

**Common issues:**
- Missing environment variables
- Database connection errors
- Port binding issues

### **Problem: Slow Cold Start**

**Solutions:**
1. Use UptimeRobot (keep alive)
2. Upgrade to paid tier ($7/month - no sleep)
3. Accept 30s first load (free tier limitation)

---

## 💰 Cost Comparison

| Feature | Render Free | Render Paid | Railway |
|---------|-------------|-------------|---------|
| **Cost** | $0 | $7/month | $5/month |
| **Sleep** | Yes (15 min) | No | No |
| **Hours** | 750/month | Unlimited | Unlimited |
| **Memory** | 512MB | 512MB-16GB | 512MB-32GB |
| **Build Time** | Free | Priority | Fast |

**Verdict**: Render Free = Best for testing! 🏆

---

## 🔐 Security Setup

### **Add Custom Domain (Optional):**

1. Render Dashboard → Service Settings
2. **"Custom Domains"** section
3. Add your domain
4. Update DNS records

**Free SSL included!** ✅

### **Environment Variables Security:**

- ✅ All env vars **encrypted**
- ✅ Not visible in logs
- ✅ Rotate keys regularly

---

## 📈 Upgrade Path

### **When to Upgrade:**

Upgrade to **Render Paid** ($7/month) if:
- ⚠️ Cold starts annoying users
- ⚠️ Need 24/7 uptime
- ⚠️ More than 750 hours/month

### **How to Upgrade:**

1. Service Settings
2. **"Plan"** section
3. Select **"Starter"** ($7/month)
4. Add payment method
5. Instant upgrade!

---

## 🆚 Render vs Railway

| Aspect | Render | Railway |
|--------|--------|---------|
| **Free Tier** | ✅ True $0 | ⚠️ $5 credit (may charge) |
| **Setup** | ✅ Easier | ⚠️ More complex |
| **Sleep Mode** | ⚠️ Yes | ✅ No |
| **Build Time** | ⚠️ Slower | ✅ Faster |
| **Reliability** | ✅ High | ✅ High |

**Recommendation**:
- **Testing/Demo**: Render (FREE!)
- **Production**: Railway or Render Paid

---

## ✅ Post-Deployment Checklist

- [ ] Bot accessible via URL
- [ ] Login/Signup working
- [ ] License activation tested
- [ ] Environment variables set
- [ ] UptimeRobot configured (optional)
- [ ] Custom domain added (optional)
- [ ] Auto-deploy tested

---

## 🎯 Next Steps

### **1. Test Your Bot:**
```
https://your-app.onrender.com
```

### **2. Setup UptimeRobot:**
Keep bot awake 24/7 (free!)

### **3. Configure API Keys:**
Dashboard → Settings → Add Binance keys

### **4. Activate License:**
Dashboard → License → Enter key

### **5. Start Trading!**
Dashboard → Market Analysis → Scan

---

## 🆘 Need Help?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com/
- Status: https://status.render.com/

**Bot Support:**
- GitHub: https://github.com/agds-alt/binance-algo-bot
- Issues: Create GitHub issue

---

## 🎉 Congratulations!

Your bot is now **LIVE on Render.com** - 100% FREE! 🚀

**Benefits:**
- ✅ No credit card needed
- ✅ Auto-deploy from GitHub
- ✅ Free SSL/HTTPS
- ✅ 750 hours/month
- ✅ Professional URL

**Happy Trading!** 💰📈

---

**Last Updated**: 2026-01-17
**Deployment Platform**: Render.com (Free Tier)
**Estimated Deploy Time**: 3-5 minutes
