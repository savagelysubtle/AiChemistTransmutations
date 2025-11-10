# 🚀 GUMROAD LAUNCH - READY TO GO!

## ✅ Completed

1. **RSA Keys Generated** ✓

   - Private key: `scripts/licensing/keys/private_key.pem`
   - Public key: `scripts/licensing/keys/public_key.pem`
   - **⚠️ KEEP PRIVATE KEY SECURE!**

2. **License Keys Generated** ✓
   - Basic Tier: 1,000 keys → `generated_keys/keys_basic_20251024_073708.csv`
   - Pro Tier: 500 keys → `generated_keys/keys_pro_20251024_073739.csv`
   - Enterprise Tier: 100 keys →
     `generated_keys/keys_enterprise_20251024_073755.csv`

## 📋 NEXT STEPS (Do These Now!)

### Step 1: Set Up Supabase (5 minutes)

1. Go to https://supabase.com/dashboard/project/_/settings/api
2. Copy your project credentials
3. Set environment variables in PowerShell:

```powershell
$env:SUPABASE_URL="https://your-project-ref.supabase.co"
$env:SUPABASE_SERVICE_KEY="your-service-role-key-here"
```

4. Insert keys into Supabase:

```powershell
python scripts/licensing/insert_license_keys.py --csv generated_keys\keys_basic_20251024_073708.csv --tier basic
python scripts/licensing/insert_license_keys.py --csv generated_keys\keys_pro_20251024_073739.csv --tier pro
python scripts/licensing/insert_license_keys.py --csv generated_keys\keys_enterprise_20251024_073755.csv --tier enterprise
```

### Step 2: Upload Keys to Gumroad (10 minutes)

**For Basic Tier Product ($29):**

1. Go to https://app.gumroad.com/products
2. Click on "AIChemist Transmutation Codex" (or your Basic product)
3. Click **Settings** tab
4. Scroll to **License Keys** section
5. Toggle "Generate a unique license key for each sale" to **ON**
6. Click **"Upload license keys"**
7. Upload: `generated_keys/keys_basic_20251024_073708.csv`
8. Verify: "1,000 keys uploaded"

**Repeat for Pro ($79) and Enterprise ($299) products**

- Pro: Upload `keys_pro_20251024_073739.csv` (500 keys)
- Enterprise: Upload `keys_enterprise_20251024_073755.csv` (100 keys)

### Step 3: Configure Gumroad Email (15 minutes)

For EACH product:

1. Go to product → **Settings** → **Email** (or **License Keys** section)
2. Find the **"License key email" template**
3. Replace with this template:

```
🎉 Thank you for purchasing AIChemist Transmutation Codex [TIER]!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR LICENSE KEY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{license_key}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 DOWNLOAD & INSTALL:
https://github.com/savagelysubtle/AiChemistTransmutations/releases/latest

🔑 ACTIVATION INSTRUCTIONS:

1. Download and install the application
2. Launch AIChemist Transmutation Codex
3. When prompted, enter your license key (copy/paste from above)
4. Click "Activate License"
5. Enjoy full access to all features!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ WHAT YOU GET:

[Basic Tier]
• All standard document conversions
• Up to 2 device activations
• Email support

[Pro Tier]
• Everything in Basic
• Advanced batch processing
• OCR support
• Up to 5 device activations
• Priority email support

[Enterprise Tier]
• Everything in Pro
• Unlimited batch operations
• Custom integrations
• Up to 25 device activations
• Priority support + consulting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION:
https://github.com/savagelysubtle/AiChemistTransmutations#readme

💬 SUPPORT:
simpleflowworks@gmail.com

❓ FAQ:
- Lost your key? Check this email or your Gumroad Library
- Need to move to a new computer? Deactivate from old computer first
- Questions? Email us anytime!

Thank you for your purchase! 🙏

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. Click **Save**

### Step 4: Update Product Details (10 minutes)

For EACH product, verify these settings:

**Basic Tier ($29):**

- ✅ Name: "AIChemist Transmutation Codex - Basic"
- ✅ Price: $29
- ✅ Permalink: `transmutation-codex-basic`
- ✅ License keys: Enabled (1,000 uploaded)
- ✅ Description: Clear feature list
- ✅ Content tab: Add download link or installer upload

**Pro Tier ($79):**

- Same as above but Pro features

**Enterprise Tier ($299):**

- Same as above but Enterprise features

### Step 5: Create GitHub Release (20 minutes)

1. Build your installer:

```powershell
cd gui
npm run electron:build
```

2. Go to https://github.com/savagelysubtle/AiChemistTransmutations/releases
3. Click **"Draft a new release"**
4. Tag: `v1.0.0`
5. Title: `AIChemist Transmutation Codex v1.0.0`
6. Description:

```markdown
# AIChemist Transmutation Codex v1.0.0

Transform documents between formats with ease!

## Features

- PDF ↔ Markdown conversions
- HTML ↔ PDF conversions
- DOCX → Markdown
- Batch processing
- OCR support (Pro/Enterprise)

## Installation

1. Download the installer for your platform
2. Run the installer
3. Launch the application
4. Enter your license key (from Gumroad purchase email)

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 500MB disk space

## Support

- Email: simpleflowworks@gmail.com
- Docs: https://github.com/savagelysubtle/AiChemistTransmutations#readme
```

7. Upload installer files
8. Click **"Publish release"**
9. Copy release URL and update Gumroad email template

### Step 6: Test Purchase Flow (30 minutes)

**CRITICAL: Test before announcing!**

1. **Enable Gumroad Test Mode:**

   - Dashboard → Settings → Payments
   - Toggle **"Test mode"** ON

2. **Make Test Purchase:**

   - Go to your product page
   - Click "I want this!"
   - Complete checkout (use test credit card: 4242 4242 4242 4242)
   - Check email for license key

3. **Test Activation:**

   - Download app from GitHub release
   - Install on clean machine (or VM)
   - Enter license key from test email
   - Verify activation works
   - Test core features

4. **Verify Supabase:**

   - Go to Supabase dashboard
   - Check `licenses` table
   - Verify key status changed to "active"
   - Check `activations` table for machine fingerprint

5. **Test Deactivation:**
   - In app, go to Settings → License
   - Click "Deactivate"
   - Try activating on "different" machine (same machine, but simulates
     transfer)
   - Verify works correctly

### Step 7: Launch! 🚀

1. **Disable Gumroad Test Mode**
2. **Publish all 3 products**
3. **Announce on social media**
4. **Email your list** (if you have one)
5. **Post on relevant forums/communities**

## 📊 Post-Launch Monitoring

### Day 1-3: Watch closely

- Check Gumroad sales dashboard hourly
- Monitor email for support requests
- Check Supabase for activation issues
- Test that keys are being distributed correctly

### Week 1: Daily checks

- Review sales numbers
- Respond to support emails within 24 hours
- Check key inventory (regenerate if running low)
- Monitor for any activation failures

### Ongoing:

- Weekly sales review
- Monthly key inventory check
- Quarterly product updates

## 🆘 Troubleshooting

### "Keys not in email"

- Check Gumroad Settings → License Keys is enabled
- Verify email template has `{license_key}` placeholder
- Test with a test purchase

### "Activation failed"

- Check Supabase connection in app
- Verify keys were inserted into Supabase
- Check logs: `logs/python/license_manager.log`

### "Keys running out"

- Generate more:
  `python scripts/licensing/generate_gumroad_keys.py --count 1000 --tier basic`
- Upload new CSV to Gumroad
- Insert into Supabase

### "Customer can't activate on new machine"

- Check activations count in Supabase
- If at limit, manually deactivate old machines
- Update `activations` table: set `is_active = false`

## 📞 Support Contact

**Customer Support:** simpleflowworks@gmail.com **Developer (you!):** Check logs
and Supabase dashboard

## 🎉 YOU'RE READY!

All the hard work is done. The keys are generated, scripts are ready, and you
just need to:

1. Set Supabase credentials
2. Upload CSVs to Gumroad
3. Configure emails
4. Test
5. **LAUNCH!**

Good luck! 🚀




