# Stripe Payment Integration Setup Guide

**Complete guide to enable payment processing and automated license delivery**

---

## 📋 Prerequisites

1. **Stripe Account**
   - Sign up at https://stripe.com
   - Complete account verification
   - Get API keys from Dashboard

2. **Ngrok** (for webhook testing)
   - Download from https://ngrok.com
   - Sign up and get auth token
   - Install ngrok CLI

---

## 🔑 Step 1: Get Stripe API Keys

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **API keys**
3. Copy your keys:
   - **Publishable key**: `pk_test_...` (for frontend)
   - **Secret key**: `sk_test_...` (for backend)

4. **IMPORTANT**: Use test keys for testing, live keys for production!

---

## ⚙️ Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your Stripe keys to `.env`:
   ```bash
   # Stripe API Keys
   STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
   STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
   ```

3. **Note**: Webhook secret comes later after setting up webhooks

---

## 🎯 Step 3: Create Products in Stripe (Optional)

You can create products in Stripe Dashboard or use the built-in pricing from `stripe_manager.py`.

### Built-in Pricing (Default):
- **PRO Monthly**: $49/month
- **PRO Yearly**: $399/year (save $189)
- **Premium Monthly**: $99/month
- **Premium Yearly**: $799/year (save $389)

### Or Create Custom Products:
1. Go to **Products** in Stripe Dashboard
2. Click **Add Product**
3. Set name, description, and price
4. Copy the **Price ID** (e.g., `price_xxx`)
5. Update `.env` with your Price IDs

---

## 🔌 Step 4: Setup Webhook Endpoint

### For Development (Local Testing):

1. **Start the webhook server**:
   ```bash
   python webhook_server.py
   ```
   This starts a Flask server on `http://localhost:5000`

2. **Expose with ngrok**:
   ```bash
   ngrok http 5000
   ```
   You'll get a URL like: `https://abc123.ngrok.io`

3. **Add webhook to Stripe**:
   - Go to **Developers** → **Webhooks** in Stripe Dashboard
   - Click **Add endpoint**
   - Enter URL: `https://abc123.ngrok.io/webhook/stripe`
   - Select events:
     - `checkout.session.completed`
     - `payment_intent.succeeded`
   - Click **Add endpoint**

4. **Copy webhook secret**:
   - After creating, click on the webhook
   - Reveal and copy the **Signing secret** (starts with `whsec_`)
   - Add to `.env` as `STRIPE_WEBHOOK_SECRET`

### For Production:

Deploy `webhook_server.py` to:
- Heroku
- Railway
- Vercel (as serverless function)
- DigitalOcean App Platform
- AWS Lambda

Then add the production URL to Stripe webhooks.

---

## 🚀 Step 5: Test Payment Flow

1. **Start the dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

2. **Start webhook server** (in separate terminal):
   ```bash
   python webhook_server.py
   ```

3. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 5000
   ```

4. **Test checkout**:
   - Go to **Pricing** page in dashboard
   - Click "Buy Monthly" for PRO plan
   - Enter test email
   - Click the Stripe checkout link
   - Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC

5. **Verify**:
   - Payment should succeed
   - Webhook receives event
   - License auto-generated
   - Check webhook server logs for license key
   - License shown on success page

---

## 🧪 Stripe Test Cards

Use these for testing (test mode only):

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 9995` | Payment declined |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |
| `4000 0000 0000 0341` | Attach and charge succeed |

**Expiry**: Any future date
**CVC**: Any 3 digits
**ZIP**: Any 5 digits

---

## 📊 Payment Flow Diagram

```
┌─────────────┐
│   User      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. Click "Buy PRO"
       │
       ▼
┌─────────────┐
│   Pricing   │
│    Page     │
└──────┬──────┘
       │
       │ 2. Enter email, create checkout
       │
       ▼
┌─────────────┐
│   Stripe    │
│  Checkout   │
└──────┬──────┘
       │
       │ 3. Complete payment
       │
       ▼
┌─────────────┐
│   Webhook   │
│   Server    │
└──────┬──────┘
       │
       │ 4. Verify payment
       │ 5. Generate license
       │
       ▼
┌─────────────┐
│  Success    │
│    Page     │ ← 6. Show license key
└─────────────┘
```

---

## 🔒 Security Best Practices

1. **Never commit API keys**:
   - Add `.env` to `.gitignore`
   - Use environment variables only

2. **Verify webhook signatures**:
   - Always use `STRIPE_WEBHOOK_SECRET`
   - Prevents fake webhook events

3. **Use HTTPS in production**:
   - Webhooks must be HTTPS
   - Use SSL certificates

4. **Test mode first**:
   - Always test with `sk_test_` keys
   - Switch to `sk_live_` only when ready

5. **Log everything**:
   - Track all payments
   - Store license generation records
   - Monitor webhook failures

---

## 📧 Email Delivery (Optional)

To automatically email licenses to customers:

1. **Install email library**:
   ```bash
   pip install sendgrid==6.11.0
   # or
   pip install resend==2.0.0
   ```

2. **Update webhook_server.py**:
   - Add email sending function
   - Send license key after generation
   - Include activation instructions

3. **Recommended services**:
   - SendGrid (free tier: 100 emails/day)
   - Resend (free tier: 100 emails/day)
   - Mailgun
   - AWS SES

---

## 🐛 Troubleshooting

### Webhook not receiving events:
- Check ngrok is running
- Verify webhook URL in Stripe Dashboard
- Check webhook_server.py logs
- Test with Stripe CLI: `stripe listen --forward-to localhost:5000/webhook/stripe`

### Payment succeeds but no license generated:
- Check webhook_server.py logs for errors
- Verify LicenseManager is working: `python admin_license.py list`
- Check database permissions

### Checkout session creation fails:
- Verify `STRIPE_SECRET_KEY` in `.env`
- Check Stripe API key is valid
- Ensure pricing amounts are in cents (e.g., 4900 = $49.00)

### Signature verification fails:
- Ensure `STRIPE_WEBHOOK_SECRET` is correct
- Copy exact secret from Stripe Dashboard
- Restart webhook server after updating `.env`

---

## 📚 Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Webhook Best Practices](https://stripe.com/docs/webhooks/best-practices)
- [Stripe Python Library](https://stripe.com/docs/api?lang=python)

---

## ✅ Production Checklist

Before going live:

- [ ] Switch to live Stripe API keys (`sk_live_`, `pk_live_`)
- [ ] Deploy webhook server to production
- [ ] Update webhook URL in Stripe Dashboard to production
- [ ] Test end-to-end with live keys (small amount)
- [ ] Setup email delivery for license keys
- [ ] Configure error monitoring (Sentry, etc.)
- [ ] Setup backup of license database
- [ ] Test refund flow
- [ ] Document customer support process
- [ ] Enable Stripe Radar (fraud prevention)

---

**Need help?** Contact support@binancealgobot.com
