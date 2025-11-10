# Gumroad Simplified Setup Guide

## 🎯 Quick Launch Approach

This guide uses Gumroad's **native license key generation** instead of a custom
webhook server. This gets you launched faster with fewer moving parts.

## Workflow Overview

```
Customer Purchase Flow:
1. Customer buys on Gumroad
2. Gumroad auto-generates license key
3. Key sent to customer via email
4. Customer downloads app
5. Customer enters key in app
6. App validates key (online/offline hybrid)
7. Key stored in Supabase on first activation
8. Customer gets full access
```

## ✅ Prerequisites Checklist

- [x] Supabase account with database setup
- [x] License tables created (licenses, activations, usage_logs)
- [x] App configured with Supabase connection
- [ ] Gumroad account with product created
- [ ] License key format decided

## Step 1: Configure Gumroad Product

### A. Enable License Keys

1. Go to your product in Gumroad dashboard
2. Navigate to **Settings** tab
3. Scroll to **License Keys** section
4. Enable "Generate a unique license key for each sale"
5. Choose license key format:
   - **Recommended**: Custom format (see below)
   - Alternative: Gumroad default format

### B. Recommended License Key Format

For consistency with your existing system, use this format:

```
BASIC-XXXX-XXXX-XXXX-XXXX
PRO-XXXX-XXXX-XXXX-XXXX
ENTERPRISE-XXXX-XXXX-XXXX-XXXX
```

Where `XXXX` are random alphanumeric characters.

**Gumroad Configuration:**

- Pattern: `BASIC-{random:4}-{random:4}-{random:4}-{random:4}`
- Max uses: Set based on tier (Basic: 2, Pro: 5, Enterprise: 25)

### C. Configure License Delivery Email

Gumroad's default email will include:

- Purchase confirmation
- Download link (add GitHub releases link)
- License key (automatically included)

**Customize the email:**

1. Go to **Settings** → **License Keys** → **Email Template**
2. Add clear instructions:

```
🎉 Thank you for purchasing AIChemist Transmutation Codex!

Your License Key: {license_key}

📥 Download the app:
[Windows Installer] https://github.com/yourusername/yourrepo/releases/latest

🔑 Activation Instructions:
1. Install the application
2. Launch AIChemist Transmutation Codex
3. Enter your license key when prompted
4. Enjoy full access to all features!

Need help? Contact: support@yourdomain.com
```

## Step 2: Update App Configuration

Your app already supports this workflow! The existing code handles:

✅ **Offline Validation** (`license_manager.py`):

- Validates RSA signature
- Works without internet

✅ **Online Validation** (`supabase_backend.py`):

- Checks Supabase database
- Stores activation on first use
- Tracks machine bindings

✅ **Hybrid Mode**:

- Tries online first
- Falls back to offline if network unavailable

### A. Generate License Keys for Gumroad

Since Gumroad will generate keys, you need to either:

**Option 1: Let Gumroad generate, validate on first activation**

- Gumroad creates key
- Customer enters key
- App contacts Supabase to validate
- Supabase marks key as activated

**Option 2: Pre-generate and upload to Gumroad**

- You generate signed keys
- Upload to Gumroad as CSV
- Gumroad distributes one per purchase

### B. Pre-Generate Keys (Option 2 - Recommended)

Run the key generation script:

```bash
cd scripts/licensing
python generate_license_keys.py --count 1000 --tier basic --output keys_basic.csv
python generate_license_keys.py --count 500 --tier pro --output keys_pro.csv
python generate_license_keys.py --count 100 --tier enterprise --output keys_enterprise.csv
```

This creates CSV files with pre-signed, validated keys.

### C. Upload Keys to Gumroad

1. Go to product → **Settings** → **License Keys**
2. Click "Upload license keys"
3. Upload your CSV file
4. Gumroad will distribute one key per sale

### D. Insert Keys into Supabase

Insert the generated keys into Supabase:

```bash
python scripts/licensing/insert_license_keys.py --csv keys_basic.csv --tier basic
python scripts/licensing/insert_license_keys.py --csv keys_pro.csv --tier pro
python scripts/licensing/insert_license_keys.py --csv keys_enterprise.csv --tier enterprise
```

This ensures:

- Keys exist in database
- Status is "pending" (not activated)
- Ready for customer activation

## Step 3: Test Purchase Flow

### A. Create Test Purchase

1. In Gumroad, enable "Test Mode"
2. Make a test purchase
3. Verify you receive email with:
   - License key
   - Download link
   - Clear instructions

### B. Test Activation

1. Download and install app
2. Enter test license key
3. Verify:
   - ✅ Key validates successfully
   - ✅ Features unlock
   - ✅ Supabase shows activation
   - ✅ Machine fingerprint recorded

### C. Test Edge Cases

Test these scenarios:

- ❌ Invalid key format
- ❌ Already activated key (on different machine)
- ❌ Expired key (if using time limits)
- ✅ Offline activation (disconnect internet)
- ✅ Re-activation on same machine

## Step 4: Production Checklist

### Before Launch:

- [ ] Generate sufficient keys for each tier
- [ ] Upload keys to Gumroad
- [ ] Insert keys into Supabase
- [ ] Test complete purchase flow
- [ ] Update product description with clear activation steps
- [ ] Set correct pricing ($29 Basic, $79 Pro, $299 Enterprise)
- [ ] Configure correct activation limits per tier
- [ ] Test customer support email
- [ ] Create FAQ page
- [ ] Set up analytics/monitoring

### Gumroad Settings:

- [ ] Product published (not draft)
- [ ] License keys enabled
- [ ] Email template customized
- [ ] Download link added
- [ ] Refund policy set
- [ ] Taxes configured
- [ ] Payment methods enabled

### App Settings:

- [ ] Production Supabase credentials
- [ ] Production API keys
- [ ] Error logging enabled
- [ ] User analytics enabled (with consent)
- [ ] Crash reporting configured
- [ ] Update checking enabled

## Step 5: Customer Support

### Common Issues:

**"My license key doesn't work"**

- Verify key format (no spaces, correct dashes)
- Check if already activated
- Verify internet connection for first activation
- Check Supabase logs for error details

**"I need to move to a new computer"**

- Deactivate from old computer (if accessible)
- Or contact support to manually deactivate
- Activate on new computer

**"I lost my license key"**

- Check purchase confirmation email
- Gumroad dashboard → Purchases → View license
- Resend email from Gumroad

### Support Queries:

Check activation status:

```sql
SELECT
  license_key,
  status,
  activated_at,
  expires_at,
  activations_count,
  max_activations
FROM licenses
WHERE email = 'customer@example.com';
```

Check machine activations:

```sql
SELECT
  machine_fingerprint,
  activated_at,
  last_verified_at,
  is_active
FROM activations
WHERE license_key = 'BASIC-XXXX-XXXX-XXXX-XXXX';
```

## Advantages of This Approach

### ✅ Pros:

- **No server hosting costs** - No webhook server needed
- **Simpler architecture** - Fewer moving parts
- **Faster to launch** - Setup in hours, not days
- **Offline support** - Works without internet (after first activation)
- **Gumroad handles email** - Professional purchase emails
- **Built-in refund handling** - Gumroad manages refunds
- **Customer dashboard** - Customers can view purchases in Gumroad

### ⚠️ Limitations:

- **Manual key generation** - Need to pre-generate keys
- **No automatic revocation** - Manual process for refunds
- **Key pool management** - Need to monitor key inventory

## Future Enhancements

When you're ready to scale, you can add:

1. **Webhook Server** (Optional)

   - Auto-generate keys on purchase
   - Auto-revoke on refund
   - Real-time inventory tracking

2. **Admin Dashboard**

   - View all activations
   - Manually activate/deactivate
   - Generate reports

3. **Advanced Analytics**
   - Usage tracking
   - Feature adoption
   - Customer insights

## Migration Path to Webhook

If you later want to add a webhook server, you can:

1. Deploy webhook server (Railway, Heroku, etc.)
2. Configure webhook URL in Gumroad
3. Webhook generates keys dynamically
4. Existing keys still work
5. New purchases use webhook-generated keys

Your code already supports both approaches!

## Troubleshooting

### Gumroad Issues:

**License keys not appearing in email**

- Check Settings → License Keys is enabled
- Verify email template includes {license_key}
- Test in Test Mode first

**Keys running out**

- Generate more keys
- Upload new CSV to Gumroad
- Set up low-inventory alerts

### App Issues:

**"Unable to validate license"**

- Check Supabase connection
- Verify API keys in config
- Check logs for specific error
- Try offline validation

**"License already activated"**

- Check activations table in Supabase
- Verify max_activations limit
- Deactivate old machines if needed

## Next Steps

1. ✅ Complete Gumroad product setup
2. ✅ Generate and upload license keys
3. ✅ Test complete purchase flow
4. ✅ Publish product
5. 🚀 **Launch!**

---

**Questions or Issues?**

- Check logs in `logs/python/license_manager.log`
- Review Supabase dashboard for activation data
- Contact support: simpleflowworks@gmail.com




