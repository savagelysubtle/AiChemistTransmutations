# Gumroad Webhook Integration

This directory contains the webhook server for automatic license generation when customers purchase via Gumroad.

## 📚 Documentation

- **Complete Setup Guide:** [docs/GUMROAD_SETUP_GUIDE.md](../../docs/GUMROAD_SETUP_GUIDE.md) - Full step-by-step guide
- **Product Configuration:** [gumroad_config.yaml](gumroad_config.yaml) - Product tiers and settings
- **Server Environment Template:** [.env.server.template](.env.server.template) - Environment variables for deployment
- **Validation Tool:** [validate_setup.py](validate_setup.py) - Check your configuration

## Quick Start

### 1. Validate Your Configuration

```bash
# Check configuration
python scripts/gumroad/validate_setup.py

# Check deployed webhook (after deployment)
python scripts/gumroad/validate_setup.py --check-webhook https://your-url.com
```

### 2. Deploy Webhook Server

See [docs/GUMROAD_SETUP_GUIDE.md](../../docs/GUMROAD_SETUP_GUIDE.md) for complete deployment instructions.

**Quick Railway Deployment:**

```bash
cd scripts/gumroad
railway login
railway init
railway up
```

### 3. Configure Gumroad

1. Create products in Gumroad dashboard using permalinks from `gumroad_config.yaml`
2. Add webhook in Gumroad settings → Advanced → Webhooks
3. Update `GUMROAD_WEBHOOK_SECRET` in your deployment
4. Test with a test purchase

## Files in This Directory

- **`webhook_server.py`** - Main webhook server (Flask application)
- **`gumroad_config.yaml`** - Product configuration and settings
- **`.env.server.template`** - Environment variables template for deployment
- **`validate_setup.py`** - Configuration validation tool
- **`requirements-webhook.txt`** - Python dependencies for deployment
- **`README.md`** - This file

## Setup

### 1. Configure Environment Variables

Create a `.env` file with:

```env
# Gumroad Configuration
GUMROAD_WEBHOOK_SECRET=your_webhook_secret_from_gumroad

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# License Signing
PRIVATE_KEY_PATH=scripts/licensing/keys/private_key.pem
```

### 2. Update Product Mapping

Edit `webhook_server.py` and update the `PRODUCT_MAP` dictionary:

```python
PRODUCT_MAP = {
    "your-gumroad-product-permalink": {"type": "pro", "max_activations": 1},
    "your-enterprise-permalink": {"type": "enterprise", "max_activations": 5},
}
```

### 3. Deploy to Production

#### Option A: Railway (Recommended)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Set environment variables in Railway dashboard
5. Deploy: `railway up`
6. Get webhook URL from Railway dashboard

#### Option B: Render

1. Connect GitHub repository to Render
2. Create new Web Service
3. Set environment variables in Render dashboard
4. Deploy automatically on git push

#### Option C: AWS Lambda

1. Package with Serverless Framework
2. Deploy to Lambda
3. Create API Gateway endpoint
4. Set environment variables in Lambda console

### 4. Configure Gumroad Webhook

1. Go to Gumroad Dashboard > Settings > Advanced > Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/gumroad`
3. Select event: `sale.successful`
4. Save webhook secret to environment variables

## Testing

### Local Testing

```bash
# Install dependencies
pip install flask gunicorn

# Run development server
python scripts/gumroad/webhook_server.py

# Test endpoint (development only)
curl -X POST http://localhost:5000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "product_id": "aichemist_pro"}'
```

### Test with Gumroad Ping

1. Go to Gumroad Webhook settings
2. Click "Send test ping"
3. Check server logs for webhook receipt

## Monitoring

### Health Check

```bash
curl https://your-domain.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "aichemist-webhook"
}
```

### Logs

- Railway: `railway logs`
- Render: View in Render dashboard
- AWS Lambda: CloudWatch Logs

## Security Checklist

- [ ] HTTPS enabled (SSL certificate)
- [ ] Webhook signature verification enabled
- [ ] Environment variables secured (not in code)
- [ ] Private key stored securely (not in repository)
- [ ] SUPABASE_SERVICE_KEY is service role key (not anon key)
- [ ] Rate limiting configured (if using custom server)
- [ ] Error logging enabled
- [ ] Monitor for failed webhook attempts

## Troubleshooting

### "Invalid signature" Error

- Verify `GUMROAD_WEBHOOK_SECRET` matches Gumroad dashboard
- Check request is coming from Gumroad IP ranges
- Verify signature verification logic

### "Unknown product ID" Error

- Check `PRODUCT_MAP` contains correct Gumroad product permalink
- Verify product_id in webhook payload matches

### License Not Generated

- Check Supabase connection and credentials
- Verify private key path is correct
- Check server logs for detailed error messages

### Customer Didn't Receive License

- Verify Gumroad webhook is configured for email delivery
- Check webhook response includes license_key
- Test with Gumroad ping to verify webhook is working

## Production Checklist

Before going live:

- [ ] Webhook deployed to production server
- [ ] HTTPS enabled and certificate valid
- [ ] Environment variables configured
- [ ] Gumroad webhook URL configured
- [ ] Test purchase completed successfully
- [ ] License email received by test customer
- [ ] License activates correctly in application
- [ ] Monitoring and alerting configured
- [ ] Backup of private key stored securely

## Email Template

Configure in Gumroad product settings:

```
Thank you for purchasing AiChemist Transmutation Codex!

Your license key:
{{license_key}}

To activate:
1. Open AiChemist Transmutation Codex
2. Click "Enter License" in the menu
3. Paste your license key
4. Click "Activate"

Support: support@yourcompany.com
Documentation: https://docs.yourcompany.com

Thank you for your purchase!
```
