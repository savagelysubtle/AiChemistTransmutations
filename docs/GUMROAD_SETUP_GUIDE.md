# Gumroad Setup Guide

**Complete step-by-step guide for setting up Gumroad as a distribution channel for AiChemist Transmutation Codex**

**Last Updated:** October 22, 2025
**Status:** Production Ready

---

## Overview

This guide walks you through the complete process of setting up Gumroad to sell AiChemist Transmutation Codex with automatic license generation and delivery.

### What You'll Set Up

1. **Gumroad Products** - Create product listings for Basic, Pro, and Enterprise tiers
2. **Webhook Server** - Deploy the automatic license generation server
3. **Webhook Configuration** - Connect Gumroad to your webhook server
4. **Testing** - Verify the purchase → license flow works correctly

### Prerequisites

- [x] Gumroad account (create at [gumroad.com](https://gumroad.com))
- [x] Supabase project set up (see `PRODUCTION_DEPLOYMENT_GUIDE.md`)
- [x] RSA keys generated (`python scripts/licensing/generate_rsa_keys.py`)
- [x] Domain name (optional but recommended) or deployment platform URL
- [x] Payment processing set up in Gumroad (bank account, tax info)

---

## Phase 1: Create Gumroad Products

### Step 1: Create Your First Product

1. **Log in to Gumroad**
   - Go to [gumroad.com/login](https://gumroad.com/login)
   - Navigate to Dashboard

2. **Create Product**
   - Click "New Product" → "Digital Product"
   - Choose "Software" as category

3. **Basic Product Settings**
   - **Name:** `AiChemist Transmutation Codex - Pro`
   - **Permalink:** `transmutation-codex-pro` (IMPORTANT: must match config)
   - **Price:** `$79`
   - **Description:** (see template below)

4. **Product Description Template**

```markdown
# AiChemist Transmutation Codex - Pro Edition

Transform documents between formats with professional-grade conversion tools.

## What's Included

✅ All core conversion formats (PDF ↔ Markdown ↔ DOCX ↔ HTML ↔ EPUB)
✅ Advanced OCR with 100+ languages
✅ Batch processing for multiple files
✅ PDF merging and splitting
✅ Custom conversion templates
✅ 3 device activations
✅ Priority email support
✅ Free updates for 1 year

## System Requirements

- Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)
- 4GB RAM minimum (8GB recommended)
- 500MB disk space

## After Purchase

You'll receive your license key immediately via email. Simply:
1. Download and install AiChemist Transmutation Codex
2. Enter your license key in the app
3. Start converting!

## Support

📧 Email: support@aichemist.app
📚 Documentation: https://aichemist.app/docs
💬 Discord Community: https://discord.gg/aichemist

## Refund Policy

30-day money-back guarantee. If you're not satisfied, email support@aichemist.app for a full refund.
```

5. **Upload Product Images**
   - Main product image (1200x630px recommended)
   - Screenshots of the application
   - Feature highlights

6. **Set Purchase Confirmation**
   - Enable "Thank You" page
   - Add custom message (see email template in `scripts/gumroad/gumroad_config.yaml`)

### Step 2: Create Additional Tiers

Repeat Step 1 for the other product tiers:

**Basic Tier:**

- **Name:** `AiChemist Transmutation Codex - Basic`
- **Permalink:** `transmutation-codex-basic`
- **Price:** `$29`
- **Activations:** 1 device

**Enterprise Tier:**

- **Name:** `AiChemist Transmutation Codex - Enterprise`
- **Permalink:** `transmutation-codex-enterprise`
- **Price:** `$299` (can offer custom pricing)
- **Activations:** 10+ devices

### Step 3: Configure Product Settings

For each product:

1. **Pricing Settings**
   - ✅ Enable "I want to let buyers pay what they want"
   - Set minimum price (e.g., $29 for Basic, $79 for Pro)
   - Optional: Add suggested prices ($39, $49, $59)

2. **Licensing**
   - ✅ Enable "Limit number of downloads" → Set to 10
   - ✅ Enable "License keys" (this is where our webhook will send the key)

3. **Email Settings**
   - ✅ Enable "Send license key in email"
   - Use template from `scripts/gumroad/gumroad_config.yaml`

4. **File Attachments**
   - Upload latest installer (optional - can also provide download link)
   - Or link to your website's download page

---

## Phase 2: Deploy Webhook Server

The webhook server automatically generates and delivers license keys when customers purchase.

### Option A: Deploy to Railway (Recommended)

**Why Railway?**

- Free $5/month credit (enough for ~1000 webhooks)
- Automatic HTTPS
- Simple deployment
- No credit card required to start

**Steps:**

1. **Install Railway CLI**

```bash
npm install -g @railway/cli
```

2. **Login to Railway**

```bash
railway login
```

3. **Create Project**

```bash
cd scripts/gumroad
railway init
```

4. **Configure Environment Variables**

In Railway Dashboard:

- Go to your project
- Click "Variables" tab
- Add the following variables:

```env
GUMROAD_WEBHOOK_SECRET=(leave blank for now, will add after webhook creation)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here
PRIVATE_KEY_PATH=/app/scripts/licensing/keys/private_key.pem
FLASK_ENV=production
PORT=5000
LOG_LEVEL=INFO
```

5. **Deploy**

```bash
# From project root
railway up
```

6. **Get Your Webhook URL**

After deployment, Railway will give you a URL like:

```
https://your-app-name.up.railway.app
```

Your webhook endpoint will be:

```
https://your-app-name.up.railway.app/webhook/gumroad
```

**Save this URL** - you'll need it for Gumroad configuration.

### Option B: Deploy to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select branch: `main` or `prep-for-production`

3. **Configure Service**
   - **Name:** `aichemist-webhook`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn scripts.gumroad.webhook_server:app`

4. **Add Environment Variables**
   (Same as Railway, see above)

5. **Deploy**
   - Click "Create Web Service"
   - Render will auto-deploy on every git push

### Option C: Deploy to AWS Lambda (Advanced)

See `scripts/gumroad/README.md` for Lambda deployment instructions.

---

## Phase 3: Configure Gumroad Webhook

### Step 1: Create Webhook in Gumroad

1. **Go to Webhook Settings**
   - Gumroad Dashboard → Settings → Advanced → Webhooks
   - Click "Create webhook"

2. **Configure Webhook**
   - **URL:** `https://your-deployment-url.com/webhook/gumroad`
   - **Events:** Select "Sale"
   - **Format:** JSON
   - Click "Create"

3. **Save Webhook Secret**
   - After creating, Gumroad will show you a webhook secret
   - **IMPORTANT:** Copy this secret immediately
   - Go back to your deployment (Railway/Render)
   - Update `GUMROAD_WEBHOOK_SECRET` environment variable with this secret
   - Restart your deployment

### Step 2: Update Product Mapping

The webhook server needs to know which Gumroad product corresponds to which license type.

1. **Edit `scripts/gumroad/webhook_server.py`:**

Find the `PRODUCT_MAP` dictionary (around line 50):

```python
PRODUCT_MAP = {
    "transmutation-codex-basic": {"type": "basic", "max_activations": 1},
    "transmutation-codex-pro": {"type": "pro", "max_activations": 3},
    "transmutation-codex-enterprise": {"type": "enterprise", "max_activations": 10},
}
```

**Update the keys** to match your actual Gumroad product permalinks.

2. **Redeploy**

```bash
# Railway
railway up

# Render
git commit -am "Update product mapping"
git push origin main
```

---

## Phase 4: Testing

### Test 1: Webhook Health Check

Verify your webhook server is running:

```bash
curl https://your-deployment-url.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "aichemist-webhook"
}
```

### Test 2: Send Test Ping from Gumroad

1. Go to Gumroad Dashboard → Webhooks
2. Find your webhook
3. Click "Send test ping"
4. Check your server logs (Railway logs / Render logs)
5. Should see webhook received and processed

### Test 3: Manual Test Request

If you have `FLASK_ENV=development`:

```bash
curl -X POST https://your-deployment-url.com/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "product_id": "transmutation-codex-pro",
    "order_id": "TEST-12345"
  }'
```

Check your Supabase `licenses` table - should see a new license entry.

### Test 4: Real Purchase Test

**Use Gumroad's Test Mode:**

1. Go to your product
2. Enable "Test mode" (gear icon → Test mode)
3. Click "View product"
4. Complete a test purchase (Gumroad provides test card: 4242 4242 4242 4242)
5. Check email - should receive license key
6. Check Supabase - should see license in `licenses` table
7. Try activating in the app - should work

---

## Phase 5: Go Live

### Pre-Launch Checklist

- [ ] **Products created** for all tiers (Basic, Pro, Enterprise)
- [ ] **Descriptions and images** added to all products
- [ ] **Webhook deployed** and responding to health checks
- [ ] **Webhook secret** configured in environment variables
- [ ] **Product mapping** matches Gumroad permalinks
- [ ] **Test purchase** completed successfully end-to-end
- [ ] **License activation** tested in application
- [ ] **Email template** configured in Gumroad
- [ ] **Payment information** verified (bank account, tax forms)
- [ ] **Refund policy** clearly stated
- [ ] **Support email** monitored (<support@aichemist.app>)

### Going Live

1. **Disable Test Mode**
   - Go to each product
   - Gear icon → Disable test mode

2. **Publish Products**
   - Set products to "Published" status
   - Products will now be visible at `https://aichemist.gumroad.com/l/transmutation-codex-pro`

3. **Update Website/Marketing**
   - Add "Buy Now" buttons linking to Gumroad products
   - Update pricing page
   - Add to documentation

4. **Monitor First Purchases**
   - Watch webhook logs for first 24 hours
   - Verify license emails are being sent
   - Check for any errors in Supabase

---

## Monitoring and Maintenance

### Daily Checks

```bash
# Check webhook health
curl https://your-deployment-url.com/health

# Check Railway/Render logs for errors
railway logs --tail 100
```

### Weekly Review

- Review Supabase `licenses` table for anomalies
- Check Gumroad analytics
- Review support tickets related to licensing
- Verify webhook is still active in Gumroad dashboard

### Common Issues

#### Issue: Customer didn't receive license

**Solution:**

1. Check Gumroad webhook logs - did webhook fire?
2. Check your server logs - any errors?
3. Check Supabase `licenses` table - was license created?
4. Manually generate license: `python scripts/licensing/generate_license.py --email customer@email.com --type pro --order-id GUMROAD-123`
5. Send license to customer via support email

#### Issue: "Unknown product ID" error

**Solution:**

1. Check `PRODUCT_MAP` in `webhook_server.py`
2. Verify Gumroad product permalink matches exactly
3. Redeploy webhook server

#### Issue: "Invalid signature" error

**Solution:**

1. Verify `GUMROAD_WEBHOOK_SECRET` is set correctly
2. Check webhook secret in Gumroad dashboard matches
3. Restart deployment after updating secret

---

## Analytics and Reporting

### Gumroad Dashboard

- **Sales:** Track revenue, conversions, refunds
- **Customers:** View customer list, email exports
- **Affiliates:** Set up affiliate program (optional)

### Supabase Analytics

Query licenses table:

```sql
-- Total licenses by type
SELECT type, COUNT(*) as count
FROM licenses
GROUP BY type;

-- Licenses created today
SELECT COUNT(*) FROM licenses
WHERE created_at > NOW() - INTERVAL '1 day';

-- Active licenses
SELECT COUNT(*) FROM licenses
WHERE status = 'active';
```

### Webhook Monitoring

Add to your monitoring dashboard:

- Total webhook requests
- Successful license generations
- Failed requests (investigate immediately)
- Average response time

---

## Advanced Configuration

### Custom Domain

Instead of `your-app.up.railway.app`, use your own domain:

1. **Railway:**
   - Settings → Domains → Add custom domain
   - Add CNAME record: `webhook.aichemist.app` → `your-app.up.railway.app`
   - Railway automatically provisions SSL

2. **Render:**
   - Settings → Custom Domains
   - Follow verification steps

3. **Update Gumroad:**
   - Update webhook URL to use custom domain
   - Test with ping

### Multiple Environments

Create separate deployments for dev/staging/production:

```bash
# Development webhook (use test Supabase)
railway up --environment development

# Production webhook (use production Supabase)
railway up --environment production
```

### Webhook Retry Logic

Gumroad automatically retries failed webhooks:

- Immediate retry
- 1 hour later
- 6 hours later
- 24 hours later

Monitor your logs to ensure webhooks aren't repeatedly failing.

### Rate Limiting

If you receive high volume, add rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per minute"]
)

@app.route("/webhook/gumroad", methods=["POST"])
@limiter.limit("60 per minute")
def gumroad_webhook():
    # ... existing code
```

---

## Security Best Practices

1. **Never commit secrets**
   - Use environment variables
   - Keep `.env` files out of git (.gitignore)

2. **Rotate keys regularly**
   - Webhook secrets: every 6 months
   - Private keys: every year
   - Supabase keys: every year

3. **Monitor for suspicious activity**
   - Unusual license generation patterns
   - Failed authentication attempts
   - Webhook requests from non-Gumroad IPs

4. **Backup private keys**
   - Store encrypted backup in password manager
   - Keep offline backup in secure location
   - Document key rotation procedure

5. **Use HTTPS everywhere**
   - Never use HTTP for webhooks
   - Verify SSL certificates are valid

---

## Support and Resources

### Documentation

- **Gumroad Docs:** [help.gumroad.com](https://help.gumroad.com)
- **Webhook API:** [help.gumroad.com/article/266-webhooks](https://help.gumroad.com/article/266-webhooks)
- **Our Docs:** `docs/PRODUCTION_DEPLOYMENT_GUIDE.md`

### Getting Help

- **Email:** <support@aichemist.app>
- **Discord:** <https://discord.gg/aichemist>
- **GitHub Issues:** Report bugs or feature requests

### Related Guides

- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `scripts/gumroad/README.md` - Technical webhook documentation
- `docs/USER_GUIDE.md` - End-user license activation instructions

---

## Appendix

### A. Gumroad Product URLs

After creating products, your URLs will be:

- Basic: `https://aichemist.gumroad.com/l/transmutation-codex-basic`
- Pro: `https://aichemist.gumroad.com/l/transmutation-codex-pro`
- Enterprise: `https://aichemist.gumroad.com/l/transmutation-codex-enterprise`

### B. Environment Variables Reference

Complete list for webhook server:

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `GUMROAD_WEBHOOK_SECRET` | Yes | `abc123...` | From Gumroad dashboard |
| `SUPABASE_URL` | Yes | `https://xyz.supabase.co` | From Supabase dashboard |
| `SUPABASE_SERVICE_KEY` | Yes | `eyJhbG...` | Service role key (admin) |
| `PRIVATE_KEY_PATH` | Yes | `/app/keys/private_key.pem` | Path to RSA private key |
| `FLASK_ENV` | No | `production` | Set to production |
| `PORT` | No | `5000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

### C. Webhook Payload Example

What Gumroad sends to your webhook:

```json
{
  "seller_id": "abc123",
  "product_id": "transmutation-codex-pro",
  "product_name": "AiChemist Transmutation Codex - Pro",
  "permalink": "transmutation-codex-pro",
  "sale_id": "ABC123DEF456",
  "email": "customer@example.com",
  "full_name": "John Doe",
  "price": "7900",
  "currency": "usd",
  "quantity": "1",
  "discover_fee_charged": "false",
  "variants": "",
  "offer_code": "",
  "test": "false",
  "custom_fields": {},
  "shipping_information": {},
  "recurrence": "None",
  "license_key": ""
}
```

### D. Deployment Commands Reference

**Railway:**

```bash
railway login
railway init
railway up
railway logs
railway restart
```

**Render:**

```bash
# Auto-deploys on git push
git push origin main

# View logs in Render dashboard
```

**Manual (for testing):**

```bash
pip install flask gunicorn
python scripts/gumroad/webhook_server.py
gunicorn scripts.gumroad.webhook_server:app
```

---

**Status:** ✅ Ready for Production
**Last Verified:** October 22, 2025
**Maintainer:** @savagelysubtle
**Support:** <support@aichemist.app>
