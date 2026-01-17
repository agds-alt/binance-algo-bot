# 💰 Railway Cost Optimization Guide
## Stay Within $5 FREE Credit Forever!

---

## 📊 Current Setup (Optimized)

Your bot is configured to use **minimal resources**:
- **Memory**: 512MB (lowest tier)
- **CPU**: 0.5 vCPU (shared)
- **Region**: us-west1 (cheapest)
- **Restart Policy**: ON_FAILURE only (3 retries max)

**Estimated Cost**: **$3-4/month** ✅ (Within free $5!)

---

## 🎯 How to Stay FREE Forever

### **1. Monitor Usage Daily**

Check usage dashboard:
```
Railway Dashboard → Project → Usage Tab
```

**Red Flags:**
- Usage > $4/month = Getting close!
- Sudden spikes = Check logs for errors (restart loops)

### **2. Set Spending Limit**

**IMPORTANT! Do this NOW:**

1. Go to: https://railway.app/account/billing
2. Click **"Usage Limits"**
3. Set **Monthly Limit: $5.00**
4. Enable **"Hard Limit"** (stop service if exceeded)

This **prevents surprise charges!** 🛡️

### **3. Optimize Streamlit Dashboard**

Already configured in `railway.json`:
- ✅ `maxUploadSize=5` (limit file uploads)
- ✅ Reduced restart retries (3 max)
- ✅ Minimal memory allocation

### **4. Monitor for Restart Loops**

**Restart loops = 💸 EXPENSIVE!**

Check if bot keeps crashing:
```bash
# In Railway dashboard
Deployments → View Logs
```

If you see repeated restarts:
- Fix the error
- Or disable auto-restart temporarily

### **5. Regional Selection**

Stay in **us-west1** (cheapest region)

Don't change to:
- ❌ `eu-west1` (more expensive)
- ❌ `ap-southeast1` (most expensive)

### **6. Database Optimization**

SQLite is **FREE** (no extra cost!)

Don't migrate to:
- ❌ PostgreSQL Plugin ($5-10/month extra)
- ❌ MySQL Plugin ($5-10/month extra)

Keep using SQLite for now!

### **7. Remove Unused Services**

Only run **ONE service** (dashboard):
- ✅ Dashboard (Streamlit) = $3-4/month
- ❌ Don't add separate worker/bot service

Run everything in ONE process!

---

## 💡 Advanced Cost Saving Tips

### **Option 1: Sleep Schedule (Future)**

If you want to save MORE:
```yaml
# Add to railway.json (future feature)
"schedule": {
  "sleep": "0 2 * * *",    # Sleep at 2 AM UTC
  "wake": "0 8 * * *"      # Wake at 8 AM UTC
}
```

This can reduce cost to **$1-2/month**!

### **Option 2: Cron-based Deployment**

For non-24/7 usage:
- Deploy only when needed
- Use Railway API to start/stop service
- Cost: **$0-1/month**

### **Option 3: Reduce Memory (Risky)**

If dashboard is stable:
```json
"service": {
  "memory": 256,  // Down from 512MB
  "cpu": 0.25      // Down from 0.5
}
```

⚠️ **Warning**: Might cause crashes if not enough memory!

---

## 🚨 Emergency: If Usage Spikes

**If you see usage > $4.50:**

### **Immediate Actions:**

1. **Pause Service**:
   ```
   Railway Dashboard → Service → Settings → Pause
   ```

2. **Check Logs**:
   ```
   Deployments → View Logs
   ```
   Look for:
   - Error loops
   - Memory leaks
   - Excessive API calls

3. **Clear Logs** (if too large):
   ```
   Logs can consume storage = $$
   ```

4. **Restart Service** (after fixing):
   ```
   Settings → Restart
   ```

---

## 📈 Monthly Cost Breakdown

**Best Case** (Normal usage):
```
Dashboard:     $2.50
Database:      $0.00 (SQLite)
Bandwidth:     $0.50
Total:         $3.00/month ✅ FREE!
```

**Worst Case** (Heavy usage):
```
Dashboard:     $4.00
Database:      $0.00
Bandwidth:     $1.00
Total:         $5.00/month ✅ Still FREE!
```

**Over Budget** (Need to optimize):
```
Dashboard:     $6.00
Total:         $6.00/month ❌ $1 charge
```

---

## 🎯 Goal: Stay Under $5

**Current Settings = $3-4/month**

**You have $1-2 buffer!** ✅

---

## 📞 If You Exceed $5

**Don't panic!**

1. Check what caused spike
2. Optimize (see tips above)
3. Consider alternatives:
   - Render.com (free with sleep)
   - PythonAnywhere (free tier)
   - Self-host on Raspberry Pi ($0!)

---

## ✅ Checklist

- [x] Set $5 spending limit
- [x] Monitor usage weekly
- [x] Optimized railway.json
- [x] Using SQLite (not PostgreSQL)
- [x] Single service deployment
- [x] Minimal memory/CPU config

**You're all set to stay FREE! 🎉**

---

## 📊 Usage Monitoring Commands

Check current usage:
```bash
# Via Railway CLI
railway status

# Via Dashboard
https://railway.app/project/[your-project-id]/usage
```

---

**Last Updated**: 2026-01-17
**Est. Monthly Cost**: $3-4 (Within $5 free tier) ✅
