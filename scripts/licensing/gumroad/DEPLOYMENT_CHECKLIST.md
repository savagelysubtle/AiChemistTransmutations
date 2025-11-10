# Gumroad Deployment Checklist

**Use this checklist when setting up Gumroad for production**

## Pre-Deployment Preparation

### Local Setup

- [ ] **RSA keys generated**

  ```bash
  python scripts/licensing/generate_rsa_keys.py
  ```

  - [ ] Private key exists: `scripts/licensing/keys/private_key.pem`
  - [ ] Public key exists: `scripts/licensing/keys/public_key.pem`
  - [ ] Private key backed up securely (password manager, encrypted backup)

- [ ] **Supabase project ready**
  - [ ] Database schema created
  - [ ] `licenses` table exists
  - [ ] Row Level Security (RLS) policies configured
  - [ ] Service role key obtained (for webhook server)

- [ ] **Configuration validated**

  ```bash
  python scripts/gumroad/validate_setup.py
  ```

  - [ ] All product tiers defined in `gumroad_config.yaml`
  - [ ] Product permalinks finalized
  - [ ] Email templates reviewed

---

## Phase 1: Webhook Server Deployment

### Choose Deployment Platform

Select one:

- [ ] **Railway** (Recommended - Free tier, automatic HTTPS)
- [ ] **Render** (Free tier, git-based deployment)
- [ ] **AWS Lambda** (Pay-as-you-go, scalable)
- [ ] **DigitalOcean App Platform** (Simple, predictable pricing)

### Railway Deployment (Most Common)

- [ ] **Install Railway CLI**

  ```bash
  npm install -g @railway/cli
  ```

- [ ] **Login and initialize**

  ```bash
  railway login
  cd scripts/gumroad
  railway init
  ```

- [ ] **Set environment variables in Railway dashboard**
  - [ ] `GUMROAD_WEBHOOK_SECRET` (leave blank for now, will add after webhook creation)
  - [ ] `SUPABASE_URL` = `https://your-project-id.supabase.co`
  - [ ] `SUPABASE_SERVICE_KEY` = Your service role key (starts with `eyJhbG...`)
  - [ ] `PRIVATE_KEY_PATH` = `/app/scripts/licensing/keys/private_key.pem`
  - [ ] `FLASK_ENV` = `production`
  - [ ] `PORT` = `5000`
  - [ ] `LOG_LEVEL` = `INFO`

- [ ] **Deploy**

  ```bash
  railway up
  ```

- [ ] **Get webhook URL**
  - [ ] Note Railway URL: `https://your-app-name.up.railway.app`
  - [ ] Full webhook endpoint: `https://your-app-name.up.railway.app/webhook/gumroad`

- [ ] **Test health endpoint**

  ```bash
  curl https://your-app-name.up.railway.app/health
  ```

  Should return: `{"status": "healthy", "service": "aichemist-webhook"}`

### Alternative: Render Deployment

- [ ] Create Render account and link GitHub repo
- [ ] Create new Web Service
- [ ] Configure:
  - [ ] Runtime: Python 3
  - [ ] Build Command: `pip install -r scripts/gumroad/requirements-webhook.txt`
  - [ ] Start Command: `gunicorn scripts.gumroad.webhook_server:app`
- [ ] Add same environment variables as Railway
- [ ] Deploy (auto-deploys on git push)

---

## Phase 2: Gumroad Product Setup

### Create Products

For each tier (Basic, Pro, Enterprise):

- [ ] **Basic Tier** ($29)
  - [ ] Product created in Gumroad dashboard
  - [ ] Name: "AiChemist Transmutation Codex - Basic"
  - [ ] Permalink: `transmutation-codex-basic` (MUST match config)
  - [ ] Price: $29
  - [ ] Description added (from `gumroad_config.yaml`)
  - [ ] Features list added
  - [ ] Screenshots uploaded
  - [ ] License key delivery enabled
  - [ ] Email template configured
  - [ ] Published

- [ ] **Pro Tier** ($79)
  - [ ] Product created in Gumroad dashboard
  - [ ] Name: "AiChemist Transmutation Codex - Pro"
  - [ ] Permalink: `transmutation-codex-pro` (MUST match config)
  - [ ] Price: $79
  - [ ] Description added
  - [ ] Features list added
  - [ ] Screenshots uploaded
  - [ ] License key delivery enabled
  - [ ] Email template configured
  - [ ] Published

- [ ] **Enterprise Tier** ($299+)
  - [ ] Product created in Gumroad dashboard
  - [ ] Name: "AiChemist Transmutation Codex - Enterprise"
  - [ ] Permalink: `transmutation-codex-enterprise` (MUST match config)
  - [ ] Price: $299
  - [ ] Description added
  - [ ] Features list added
  - [ ] Screenshots uploaded
  - [ ] License key delivery enabled
  - [ ] Email template configured
  - [ ] Published

### Payment & Tax Setup

- [ ] **Gumroad account fully verified**
- [ ] **Bank account connected** for payouts
- [ ] **Tax information submitted** (W-9/W-8BEN)
- [ ] **Payout method configured**

---

## Phase 3: Webhook Configuration

### Create Webhook in Gumroad

- [ ] **Navigate to webhook settings**
  - Gumroad Dashboard → Settings → Advanced → Webhooks

- [ ] **Create webhook**
  - [ ] URL: `https://your-deployment-url.com/webhook/gumroad`
  - [ ] Event: `sale` (checked)
  - [ ] Format: JSON
  - [ ] Webhook created successfully

- [ ] **Copy webhook secret**
  - [ ] Secret copied from Gumroad dashboard
  - [ ] Secret added to deployment environment variables as `GUMROAD_WEBHOOK_SECRET`
  - [ ] Deployment restarted after adding secret

### Update Product Mapping

- [ ] **Verify product permalinks** in `webhook_server.py`

  ```python
  PRODUCT_MAP = {
      "transmutation-codex-basic": {"type": "basic", "max_activations": 1},
      "transmutation-codex-pro": {"type": "pro", "max_activations": 3},
      "transmutation-codex-enterprise": {"type": "enterprise", "max_activations": 10},
  }
  ```

  - [ ] Permalinks match Gumroad products exactly
  - [ ] License types match configuration
  - [ ] Max activations correct for each tier

- [ ] **Redeploy if product mapping changed**

  ```bash
  railway up  # or git push for Render
  ```

---

## Phase 4: Testing

### Test 1: Health Check

- [ ] **Verify webhook server is running**

  ```bash
  curl https://your-deployment-url.com/health
  ```

  Expected: `{"status": "healthy", "service": "aichemist-webhook"}`

### Test 2: Gumroad Ping

- [ ] **Send test ping from Gumroad**
  - Gumroad Dashboard → Webhooks → Click your webhook → "Send test ping"
  - [ ] Ping sent successfully
  - [ ] Check deployment logs - webhook received

### Test 3: Manual Test Request (Development)

- [ ] **Send test webhook manually** (if `FLASK_ENV=development`)

  ```bash
  curl -X POST https://your-deployment-url.com/webhook/test \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "product_id": "transmutation-codex-pro",
      "order_id": "TEST-12345"
    }'
  ```

  - [ ] Request successful
  - [ ] Check Supabase `licenses` table - new license created

### Test 4: Real Test Purchase

- [ ] **Enable test mode** in Gumroad product settings
- [ ] **Complete test purchase**
  - [ ] Used test card: 4242 4242 4242 4242
  - [ ] Purchase completed successfully
  - [ ] Email received with license key
  - [ ] License key in email is valid (starts with correct prefix)

- [ ] **Verify in Supabase**
  - [ ] New license entry in `licenses` table
  - [ ] Email matches test purchase email
  - [ ] License type matches product tier
  - [ ] Status is "active"
  - [ ] Order ID matches Gumroad order

- [ ] **Test license activation in app**
  - [ ] Opened AiChemist app
  - [ ] Entered license key from email
  - [ ] Activation successful
  - [ ] Premium features unlocked

---

## Phase 5: Production Launch

### Pre-Launch Validation

- [ ] **Run validation script one more time**

  ```bash
  python scripts/gumroad/validate_setup.py --check-webhook https://your-url.com
  ```

  - [ ] All checks pass

- [ ] **Security review**
  - [ ] `.env` files not committed to git
  - [ ] Private keys not in repository
  - [ ] Webhook signature verification enabled
  - [ ] HTTPS enabled on deployment
  - [ ] Service role key (not anon key) used for webhook

- [ ] **Documentation review**
  - [ ] Email template tested and looks good
  - [ ] Support email monitored: `support@aichemist.app`
  - [ ] User guide includes activation instructions
  - [ ] FAQ updated with licensing questions

### Go Live

- [ ] **Disable test mode** on all Gumroad products
- [ ] **Verify products are published** and visible
- [ ] **Test purchase flow** one more time with real card (then refund)
- [ ] **Monitor webhook logs** for first 24 hours

### Marketing Launch

- [ ] **Update website** with product links
  - Basic: `https://aichemist.gumroad.com/l/transmutation-codex-basic`
  - Pro: `https://aichemist.gumroad.com/l/transmutation-codex-pro`
  - Enterprise: `https://aichemist.gumroad.com/l/transmutation-codex-enterprise`

- [ ] **Social media announcements** scheduled
- [ ] **Email list** notified (if applicable)
- [ ] **Product Hunt** submission (optional)

---

## Phase 6: Post-Launch Monitoring

### Daily Checks (First Week)

- [ ] **Check webhook health** daily

  ```bash
  curl https://your-deployment-url.com/health
  ```

- [ ] **Review webhook logs** daily

  ```bash
  railway logs --tail 100  # or check Render dashboard
  ```

- [ ] **Check Supabase** for successful license creations

  ```sql
  SELECT COUNT(*) FROM licenses WHERE created_at > NOW() - INTERVAL '1 day';
  ```

- [ ] **Monitor support inbox** for license issues

### Weekly Review

- [ ] **Review Gumroad analytics**
  - Sales count
  - Revenue
  - Conversion rate
  - Refund requests

- [ ] **Check for failed webhooks**
  - Gumroad Dashboard → Webhooks → Failed deliveries
  - Investigate and resolve any issues

- [ ] **License activation rate**
  - Compare licenses issued vs. licenses activated in app
  - Follow up with customers who haven't activated

### Monthly Maintenance

- [ ] **Review and optimize**
  - Analyze which tier sells best
  - Gather customer feedback
  - Update product descriptions if needed

- [ ] **Security audit**
  - Rotate webhook secret (every 6 months)
  - Review Supabase logs for unusual activity
  - Check for failed authentication attempts

- [ ] **Backup verification**
  - Verify private key backup is accessible
  - Test recovery procedure

---

## Troubleshooting

### Issue: Customer didn't receive license

**Steps:**

1. [ ] Check Gumroad webhook logs - did it fire?
2. [ ] Check deployment logs - any errors?
3. [ ] Check Supabase `licenses` table - was license created?
4. [ ] If not created, manually generate:

   ```bash
   python scripts/licensing/generate_license.py \
     --email customer@email.com \
     --type pro \
     --order-id GUMROAD-123
   ```

5. [ ] Email license to customer via <support@aichemist.app>

### Issue: "Unknown product ID" error

**Steps:**

1. [ ] Check `PRODUCT_MAP` in `webhook_server.py`
2. [ ] Verify Gumroad product permalink matches exactly
3. [ ] Update mapping if needed
4. [ ] Redeploy: `railway up`

### Issue: "Invalid signature" error

**Steps:**

1. [ ] Verify `GUMROAD_WEBHOOK_SECRET` is set correctly in deployment
2. [ ] Check webhook secret in Gumroad dashboard matches
3. [ ] Restart deployment after updating secret

### Issue: Webhook times out

**Steps:**

1. [ ] Check deployment platform status (Railway, Render)
2. [ ] Verify Supabase is responding
3. [ ] Check webhook timeout settings (default 30s)
4. [ ] Review logs for slow queries

---

## Success Criteria

✅ **All boxes checked** = Ready for production launch
✅ **Test purchase successful** = License generation working
✅ **License activation successful** = End-to-end flow working
✅ **No errors in logs** = System stable

---

## Resources

- **Setup Guide:** [docs/GUMROAD_SETUP_GUIDE.md](../../docs/GUMROAD_SETUP_GUIDE.md)
- **Configuration:** [scripts/gumroad/gumroad_config.yaml](gumroad_config.yaml)
- **Validation:** [scripts/gumroad/validate_setup.py](validate_setup.py)
- **Gumroad Docs:** <https://help.gumroad.com>
- **Support:** <support@aichemist.app>

---

**Last Updated:** October 22, 2025
**Status:** Production Ready
**Maintained by:** @savagelysubtle
