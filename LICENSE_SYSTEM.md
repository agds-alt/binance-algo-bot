# 🔐 License System Documentation

Complete guide to the license management system for Binance Algo Bot.

---

## 📋 Overview

The license system provides:
- **Secure license key generation** with HMAC checksums
- **Hardware binding** to prevent unauthorized sharing
- **Tier enforcement** (FREE → PRO → PREMIUM → ENTERPRISE)
- **Expiry management** with automatic tier downgrade
- **Multi-device support** (tier-dependent)
- **Activation tracking** with last-seen timestamps
- **Admin CLI** for license management

---

## 🏗️ Architecture

### Components

1. **`modules/license_manager.py`**
   - Core license management logic
   - License generation, validation, activation
   - Database management (SQLite)
   - Hardware ID generation

2. **`modules/license_state.py`**
   - Local license state management
   - Persistent activation storage
   - Automatic validation (24-hour cache)
   - Singleton instance for application-wide access

3. **`modules/tier_manager.py`** (Updated)
   - Automatic license tier detection
   - Feature gate enforcement
   - Conversion tracking

4. **`admin_license.py`**
   - CLI tool for license administration
   - Generate, validate, extend, upgrade licenses
   - List all licenses
   - Rich terminal UI

5. **`pages/5_License.py`** (Updated)
   - User-facing license activation
   - Real-time license info display
   - Deactivation functionality
   - Pricing and FAQ

---

## 🔑 License Key Format

```
PREFIX-XXXX-XXXX-XXXX-XXXX-CHKS

Examples:
- PRO-1A2B-3C4D-5E6F-7890-AB12
- PREM-5678-9ABC-DEF0-1234-CD34
- FREE-AAAA-BBBB-CCCC-DDDD-EE56
```

### Components:
- **PREFIX**: Tier identifier (FREE, PRO, PREM, ENT)
- **XXXX segments**: Random hex characters (4 segments × 4 chars)
- **CHKS**: HMAC-SHA256 checksum (first 4 chars)

### Security:
- **Checksum validation** prevents tampering
- **HMAC signing** with secret key
- **Hardware binding** prevents sharing
- **Activation limits** enforce device count

---

## 🚀 Quick Start

### For Admins: Generate Licenses

```bash
# Generate PRO license (30 days)
python admin_license.py generate \
  --tier pro \
  --email customer@example.com \
  --days 30

# Generate PREMIUM license (90 days, 2 devices)
python admin_license.py generate \
  --tier premium \
  --email vip@example.com \
  --days 90 \
  --max-activations 2 \
  --save

# Generate trial license (7 days)
python admin_license.py generate \
  --tier pro \
  --email trial@example.com \
  --days 7 \
  --notes "7-day trial"
```

### For Users: Activate License

**Via Dashboard:**
1. Open dashboard → License page
2. Enter license key
3. Click "Activate License"
4. ✅ Done!

**Via Python:**
```python
from modules.license_state import get_license_state

state = get_license_state()
success, message = state.activate("PRO-1A2B-3C4D-5E6F-7890-AB12")

if success:
    print(f"✅ {message}")
    print(f"Current tier: {state.get_current_tier()}")
else:
    print(f"❌ {message}")
```

---

## 📚 Admin CLI Reference

### Generate License
```bash
python admin_license.py generate --tier TIER --email EMAIL [OPTIONS]

Options:
  --tier TIER               License tier (free/pro/premium/enterprise)
  --email EMAIL             Customer email
  --days DAYS               Duration in days (default: 30)
  --max-activations N       Max devices (default: 1)
  --notes TEXT              Additional notes
  --save                    Save to file

Example:
python admin_license.py generate \
  --tier pro \
  --email john@example.com \
  --days 30 \
  --save
```

### Validate License
```bash
python admin_license.py validate LICENSE_KEY

Example:
python admin_license.py validate PRO-1A2B-3C4D-5E6F-7890-AB12
```

### Show License Info
```bash
python admin_license.py info LICENSE_KEY

Example:
python admin_license.py info PRO-1A2B-3C4D-5E6F-7890-AB12
```

### List All Licenses
```bash
python admin_license.py list

# Shows table with:
# - License key
# - Tier
# - Email
# - Expiry date
# - Status (Active/Expired/Inactive)
# - Activation count
```

### Extend License
```bash
python admin_license.py extend LICENSE_KEY --days DAYS

Example:
# Extend by 30 days
python admin_license.py extend PRO-1A2B-3C4D-5E6F-7890-AB12 --days 30
```

### Upgrade License
```bash
python admin_license.py upgrade LICENSE_KEY --tier NEW_TIER

Example:
# Upgrade from PRO to PREMIUM
python admin_license.py upgrade PRO-1A2B-3C4D-5E6F-7890-AB12 --tier premium
```

### Deactivate License
```bash
python admin_license.py deactivate LICENSE_KEY

Example:
python admin_license.py deactivate PRO-1A2B-3C4D-5E6F-7890-AB12
```

---

## 🔒 Hardware Binding

### How It Works

Each license can be bound to specific hardware. The hardware ID is generated from:
- MAC address
- Hostname
- Machine architecture
- Hashed with SHA256

### Example Hardware ID
```
A1B2C3D4E5F6G7H8
```

### Multi-Device Support

| Tier | Default Devices | Max Available |
|------|----------------|---------------|
| FREE | 1 | 1 |
| PRO | 1 | 2 |
| PREMIUM | 1 | 3 |
| ENTERPRISE | Custom | Unlimited |

### Deactivation & Reactivation

Users can deactivate their license to free up the device slot:
1. Dashboard → License → "🔓 Deactivate License"
2. Frees hardware binding
3. Can activate on different device
4. License remains valid until expiry

---

## 📊 Tier Enforcement

### Automatic Detection

The `TierManager` automatically detects the activated license tier:

```python
from modules.tier_manager import TierManager
import yaml

# Load tier config
with open('config/tiers.yaml') as f:
    tier_config = yaml.safe_load(f)

# Auto-detect from license (default behavior)
tier_manager = TierManager(tier_config, auto_detect_license=True)

# Current tier is automatically set from activated license
print(tier_manager.user_tier)  # 'pro' if PRO license activated
```

### Manual Override (for testing)

```python
# Force specific tier (disable auto-detection)
tier_manager = TierManager(
    tier_config,
    user_tier='free',
    auto_detect_license=False
)
```

---

## 🗄️ Database Schema

### `licenses` Table
```sql
CREATE TABLE licenses (
    license_key TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    issued_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    hardware_id TEXT,
    is_active INTEGER DEFAULT 1,
    max_activations INTEGER DEFAULT 1,
    activation_count INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}'
);
```

### `activations` Table
```sql
CREATE TABLE activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL,
    hardware_id TEXT NOT NULL,
    activated_at TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    ip_address TEXT,
    FOREIGN KEY (license_key) REFERENCES licenses(license_key)
);
```

---

## 🔐 Security Best Practices

### 1. Secret Key Management

**CRITICAL:** Change the default secret key in production!

```python
# In modules/license_manager.py
# DEFAULT (change this!):
self.secret_key = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"

# PRODUCTION:
# Use environment variable
import os
self.secret_key = os.getenv("LICENSE_SECRET_KEY")
```

**Generate a secure secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Database Protection

Store `data/licenses.db` securely:
- ✅ Restrict file permissions: `chmod 600 data/licenses.db`
- ✅ Backup regularly
- ✅ Encrypt at rest (production)
- ❌ Never commit to Git (already in .gitignore)

### 3. License Validation

- ✅ Validate checksum before activation
- ✅ Check hardware binding
- ✅ Verify expiry date
- ✅ Enforce activation limits
- ✅ Cache validation (24 hours) to reduce DB hits

---

## 📈 Business Workflows

### Workflow 1: New Customer Purchase

1. **Customer purchases PRO tier**
2. **Admin generates license:**
   ```bash
   python admin_license.py generate \
     --tier pro \
     --email customer@example.com \
     --days 30 \
     --save
   ```
3. **Send license key to customer via email**
4. **Customer activates in dashboard**
5. **✅ Customer now has PRO access**

### Workflow 2: Trial to Paid Conversion

1. **Customer requests trial**
2. **Admin generates 7-day trial:**
   ```bash
   python admin_license.py generate \
     --tier pro \
     --email trial@example.com \
     --days 7 \
     --notes "Trial user"
   ```
3. **Customer tries PRO features**
4. **Trial expires → auto-downgrades to FREE**
5. **Customer purchases → Admin generates paid license**
6. **Customer activates new license**

### Workflow 3: License Renewal

1. **License expiring soon (7 days)**
2. **Send renewal reminder email**
3. **Customer pays renewal**
4. **Admin extends license:**
   ```bash
   python admin_license.py extend LICENSE_KEY --days 30
   ```
5. **Customer continues with no interruption**

### Workflow 4: Upgrade Tier

1. **PRO customer wants PREMIUM**
2. **Customer pays upgrade fee**
3. **Admin upgrades license:**
   ```bash
   python admin_license.py upgrade LICENSE_KEY --tier premium
   ```
4. **Customer gets immediate PREMIUM access**
5. **No re-activation needed**

---

## 🧪 Testing

### Test License Generation
```bash
# Generate test license
python admin_license.py generate \
  --tier pro \
  --email test@test.com \
  --days 365

# Copy the license key shown
```

### Test Activation (Python)
```python
from modules.license_state import get_license_state

state = get_license_state()

# Activate
success, msg = state.activate("PRO-XXXX-XXXX-XXXX-XXXX-XXXX")
print(msg)

# Check tier
print(f"Current tier: {state.get_current_tier()}")

# Get info
info = state.get_license_info()
print(info)

# Deactivate
success, msg = state.deactivate()
print(msg)
```

### Test Activation (Dashboard)
1. Run dashboard: `./run_dashboard.sh`
2. Go to License page
3. Enter test license key
4. Click "Activate License"
5. Verify tier changes to PRO
6. Check license details in expander
7. Test deactivation

---

## 🐛 Troubleshooting

### Issue: "Invalid license key format"
- **Cause**: Checksum validation failed
- **Fix**: Ensure license key copied correctly (no spaces/typos)

### Issue: "License key not found"
- **Cause**: License doesn't exist in database
- **Fix**: Verify license key, check `data/licenses.db`

### Issue: "License activated on different device"
- **Cause**: License already bound to another hardware ID
- **Fix**: Deactivate first, then re-activate

### Issue: "License has expired"
- **Cause**: Expiry date passed
- **Fix**: Extend license or generate new one

### Issue: "Maximum activations reached"
- **Cause**: All device slots used
- **Fix**: Deactivate unused device or upgrade max_activations

---

## 📞 Support

For license issues:
- 📧 Email: sales@algobot.com
- 💬 Telegram: @algobotSupport
- 📚 Docs: docs.algobot.com

---

## 🎉 Success!

Your license system is now fully functional and ready for commercial use!

**Next steps:**
1. ✅ Change secret key in production
2. ✅ Test license generation
3. ✅ Test activation flow
4. ✅ Set up automated renewal reminders
5. ✅ Integrate with payment system (Stripe)
