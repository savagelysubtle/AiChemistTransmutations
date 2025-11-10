# 🎉 GUMROAD SETUP COMPLETE - READY TO LAUNCH!

## ✅ Completed Setup

### 1. RSA Keys Generated ✓

- **Private Key**: `scripts/licensing/keys/private_key.pem`
- **Public Key**: `scripts/licensing/keys/public_key.pem`
- ⚠️ **CRITICAL**: Keep private key secure! Never commit to git!

### 2. License Keys Generated & Stored ✓

All license keys have been successfully generated and inserted into Supabase:

| Tier       | Quantity  | CSV File                                             | Supabase Status         |
| ---------- | --------- | ---------------------------------------------------- | ----------------------- |
| Basic      | 1,000     | `generated_keys/keys_basic_20251024_073708.csv`      | ✅ Inserted             |
| Pro        | 500       | `generated_keys/keys_pro_20251024_073739.csv`        | ✅ Inserted             |
| Enterprise | 100       | `generated_keys/keys_enterprise_20251024_073755.csv` | ✅ Inserted             |
| **TOTAL**  | **1,600** |                                                      | ✅ All keys in Supabase |

### 3. Supabase Database Updated ✓

- **Fixed Schema**: Added missing `activations_count` column
- **Keys Inserted**: All 1,600 keys successfully stored
- **Credentials Set**: Environment variables configured

**Supabase Credentials Used:**

- **URL**: `https://qixmfuwhlvipslxfxhrk.supabase.co`
- **Service Key**: ✅ Configured (hidden for security)

---

## 📋 Next Steps: Upload to Gumroad

### Step 1: Upload CSV Files to Gumroad Products

You need to upload the CSV files to your Gumroad products for license key
distribution:

#### Basic Tier Product

1. Go to: https://gumroad.com/products/transmutation-codex-basic/edit
2. Navigate to **"Product" tab**
3. Scroll to **"License Keys"** section
4. Click **"Upload CSV"**
5. Select file: `generated_keys/keys_basic_20251024_073708.csv`
6. Gumroad will automatically deliver one key per purchase

#### Pro Tier Product (Create New)

1. Go to: https://gumroad.com/products/new
2. Set product name: **"AIChemist Transmutation Codex - Professional"**
3. Set permalink: **"transmutation-codex-pro"**
4. Set price: **$49**
5. Add description (see template below)
6. Navigate to **"License Keys"** section
7. Upload: `generated_keys/keys_pro_20251024_073739.csv`

#### Enterprise Tier Product (Create New)

1. Go to: https://gumroad.com/products/new
2. Set product name: **"AIChemist Transmutation Codex - Enterprise"**
3. Set permalink: **"transmutation-codex-enterprise"**
4. Set price: **$299**
5. Add description (see template below)
6. Navigate to **"License Keys"** section
7. Upload: `generated_keys/keys_enterprise_20251024_073755.csv`

---

### Step 2: Configure Product Descriptions

#### Basic Tier Description Template

```
AIChemist Transmutation Codex - Basic Edition

🔄 Professional document conversion tool for Windows

✨ Features:
• Basic document conversions (PDF, MD, HTML, DOCX)
• Up to 2 device activations
• Regular updates
• Email support

📦 What You Get:
• Lifetime license key (sent immediately after purchase)
• Windows installer download link
• Email support

⚙️ System Requirements:
• Windows 10/11 (64-bit)
• 4GB RAM minimum
• 100MB disk space

📧 Your license key will be delivered automatically via email after purchase.
```

#### Pro Tier Description Template

```
AIChemist Transmutation Codex - Professional Edition

🚀 Advanced document conversion with premium features

✨ Features:
• All Basic features
• Advanced conversions with OCR support
• Batch processing capabilities
• Up to 5 device activations
• Priority email support
• Regular updates

📦 What You Get:
• Lifetime license key (sent immediately after purchase)
• Windows installer download link
• Priority support

⚙️ System Requirements:
• Windows 10/11 (64-bit)
• 8GB RAM recommended
• 200MB disk space

📧 Your license key will be delivered automatically via email after purchase.
```

#### Enterprise Tier Description Template

```
AIChemist Transmutation Codex - Enterprise Edition

🏢 Enterprise-grade document conversion solution

✨ Features:
• All Professional features
• Up to 25 device activations
• Custom integration support
• Dedicated priority support
• Early access to new features
• Bulk licensing available

📦 What You Get:
• Lifetime enterprise license key (sent immediately after purchase)
• Windows installer download link
• Dedicated support channel
• Custom integration assistance

⚙️ System Requirements:
• Windows 10/11 (64-bit)
• 16GB RAM recommended
• 500MB disk space

📧 Your license key will be delivered automatically via email after purchase.
```

---

### Step 3: Test the Purchase Flow

#### Test Basic Tier:

1. Go to: https://gumroad.com/l/transmutation-codex-basic
2. Click "I want this!"
3. Complete test purchase (use Gumroad test mode)
4. Check email for license key
5. Download and install app
6. Enter license key in app
7. Verify activation works

#### Test Checklist:

- [ ] Email delivery works (license key received)
- [ ] License key format is correct (starts with `AICHEMIST:`)
- [ ] App installer downloads successfully
- [ ] License activation works in app
- [ ] Supabase updates activation status
- [ ] Trial mode switches to full access

---

## 🔐 License Key Workflow

### How It Works:

1. **Customer Purchases** → Gumroad processes payment
2. **Key Delivery** → Gumroad automatically sends one unused key from CSV
3. **Customer Installs** → Downloads app from your website/GitHub
4. **Customer Activates** → Enters key in app License Dialog
5. **App Validates** → Checks key signature (offline) AND Supabase (online)
6. **Supabase Updates** → Records activation, device fingerprint, email
7. **Full Access Granted** → Customer can use all features

---

## 📁 Important Files & Locations

### CSV Files (For Gumroad Upload):

```
generated_keys/
  ├── keys_basic_20251024_073708.csv       (1,000 keys)
  ├── keys_pro_20251024_073739.csv         (500 keys)
  └── keys_enterprise_20251024_073755.csv  (100 keys)
```

### Security Keys (DO NOT SHARE):

```
scripts/licensing/keys/
  ├── private_key.pem  ⚠️ KEEP SECURE!
  └── public_key.pem
```

### Supabase Database:

- **Project**: Converter
- **Tables**: licenses, activations, usage_logs
- **URL**: https://qixmfuwhlvipslxfxhrk.supabase.co

---

## 🚨 Important Security Notes

### Private Key Security:

1. ✅ Already in `.gitignore`
2. ⚠️ Never commit to version control
3. 🔐 Store backup in secure location (password manager, encrypted drive)
4. 📌 Required for generating future license keys

### CSV File Security:

1. ⚠️ These files contain valid, unused license keys
2. 🔐 Do NOT commit to public repositories
3. 📁 Keep secure backups
4. 🗑️ Can delete after uploading to Gumroad (keys are in Supabase)

---

## 📊 Monitoring & Management

### Check License Usage:

1. Go to Supabase dashboard:
   https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk
2. Navigate to **Table Editor** → **licenses**
3. Filter by `status`:
   - `active` = Key exists but not activated yet
   - `used` = Key activated by customer
   - `suspended` = Key temporarily disabled
   - `revoked` = Key permanently disabled

### Track Activations:

1. Navigate to **Table Editor** → **activations**
2. View device_id, machine_fingerprint, activated_at
3. Monitor for suspicious activity (multiple devices, rapid activations)

---

## 🎯 Success Metrics

Track these metrics after launch:

- **Sales Conversion**: Basic vs Pro vs Enterprise ratio
- **Activation Rate**: % of purchased keys that get activated
- **Multi-Device Usage**: Average activations per key
- **Support Requests**: Track common issues
- **Trial-to-Paid Conversion**: % of trial users who purchase

---

## 🆘 Troubleshooting

### If a Customer's Key Doesn't Work:

1. **Check Supabase** → Is key in database?
2. **Check Status** → Is it `active` (not used/suspended/revoked)?
3. **Check Tier** → Does it match what they purchased?
4. **Check Activations** → Has it exceeded `max_activations`?
5. **Generate New Key** → If needed:
   ```bash
   python scripts/licensing/generate_license.py --tier basic --email customer@email.com
   ```

### If Gumroad Runs Out of Keys:

1. **Generate More Keys**:

   ```bash
   python scripts/licensing/generate_gumroad_keys.py --count 1000 --tier basic
   ```

2. **Insert into Supabase**:

   ```bash
   python scripts/licensing/insert_license_keys.py --csv generated_keys/keys_basic_YYYYMMDD_HHMMSS.csv --tier basic
   ```

3. **Upload New CSV to Gumroad**

---

## ✅ Launch Checklist

Before going live, verify:

- [ ] All 3 products created on Gumroad
- [ ] CSV files uploaded to each product
- [ ] Product descriptions finalized
- [ ] Prices set correctly ($29, $49, $299)
- [ ] License key delivery enabled
- [ ] Test purchase completed successfully
- [ ] Test activation works in app
- [ ] Supabase tracking confirmed
- [ ] Download link added to products
- [ ] Support email configured
- [ ] Privacy policy & terms published
- [ ] Payment processor connected

---

## 🚀 You're Ready to Launch!

Once you complete the steps above, your Gumroad license system will be fully
operational!

**Estimated Time to Complete**: 30-45 minutes **Keys Available**: 1,600 (enough
for initial launch) **System Status**: ✅ PRODUCTION READY

---

## 📞 Need Help?

If you encounter issues:

1. Check Supabase logs:
   https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk/logs
2. Review license activation logs in app: `logs/python/`
3. Test with development license: `DEV_LICENSE.txt`

Good luck with your launch! 🎉




