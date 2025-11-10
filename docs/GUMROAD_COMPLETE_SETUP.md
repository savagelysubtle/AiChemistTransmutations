# Gumroad Product Setup & License Delivery Guide

**For:** AiChemist Transmutation Codex
**Date:** October 22, 2025
**Status:** Ready for Gumroad integration

---

## 📋 Overview

This guide walks you through:

1. Creating your Gumroad product
2. Setting up license key delivery
3. Deploying the webhook for automatic license generation
4. Testing the complete purchase flow

---

## 🎯 Gumroad Product Setup

### Step 1: Create Product

1. **Go to Gumroad**
   - Navigate to: <https://gumroad.com/products/new>
   - Sign in to your account

2. **Product Details**

   ```
   Product Name: AiChemist Transmutation Codex
   Description: Professional document conversion toolkit for Windows
   Price: $29 (Basic) or create variants
   Product Type: Software > Windows
   ```

3. **Product Variants (Recommended)**
   Create multiple tiers:

   **Basic - $29**
   - All core converters
   - Unlimited conversions
   - Basic support

   **Pro - $79**
   - All converters
   - Advanced features
   - Priority support
   - Lifetime updates

   **Enterprise - Contact**
   - Custom pricing
   - Team licenses
   - Dedicated support

### Step 2: Upload Files

1. **Primary Download**
   - Upload: `AiChemist Transmutation Codex Setup 1.0.0.exe` (176 MB)
   - File Type: Windows Executable

2. **Additional Files** (Optional)
   - User Guide PDF
   - Portable version
   - README.txt

### Step 3: Product Page Content

**Cover Image** (1600x900px recommended)

- Create eye-catching product image
- Show application interface
- Highlight key features

**Product Description**

```markdown
# Transform Your Document Workflow

AiChemist Transmutation Codex is the ultimate document conversion toolkit for Windows.

## ✨ Features

- **12+ Conversion Types**: PDF ↔ Markdown, HTML, DOCX, EPUB, and more
- **Batch Processing**: Convert multiple files at once
- **OCR Support**: Extract text from scanned PDFs
- **PDF Tools**: Merge, split, compress, and encrypt
- **Smart Formatting**: Preserve document structure
- **Fast & Offline**: Works without internet connection

## 🎯 Perfect For

- Content Creators
- Technical Writers
- Researchers
- Students
- Anyone who works with documents

## 📦 What's Included

- Windows application (176 MB download)
- Lifetime license
- Free updates (v1.x)
- Email support
- Comprehensive documentation

## 💻 System Requirements

- Windows 10/11 (64-bit)
- 500 MB disk space
- 4 GB RAM recommended
- Optional: Tesseract OCR, Ghostscript, Pandoc

## 🚀 Get Started in Minutes

1. Download installer
2. Run setup
3. Activate with your license key
4. Start converting!

---

**Purchase includes:** Instant download, license key, and email support.
```

### Step 4: License Key Configuration

1. **Enable License Keys**
   - Go to Product Settings
   - Check "Generate a unique license key"
   - Choose: "One license key per purchase"

2. **License Key Format**
   - Gumroad default format is good: `XXXXX-XXXXX-XXXXX-XXXXX`
   - We'll validate this format in our app

3. **License Email Template**

   ```
   Subject: Your AiChemist Transmutation Codex License Key

   Hi {buyer_name},

   Thanks for purchasing AiChemist Transmutation Codex!

   Your License Key:
   {license_key}

   Installation Instructions:
   1. Download the installer from your purchase page
   2. Run AiChemist Transmutation Codex Setup.exe
   3. Click "Activate License" in the app
   4. Enter your license key above
   5. Start converting!

   Support: support@aichemist.app
   Documentation: https://docs.aichemist.app

   Questions? Just reply to this email!

   Thanks,
   The AiChemist Team
   ```

---

## 🔧 Webhook Setup

### What the Webhook Does

When someone purchases:

1. Gumroad sends webhook to your server
2. Server generates signed license
3. License stored in Supabase
4. Customer receives license key via email

### Step 1: Deploy Webhook Server

**Option A: Heroku (Easiest)**

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
cd scripts/gumroad
heroku create aichemist-webhook

# Set environment variables
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_SERVICE_KEY=your_key
heroku config:set GUMROAD_WEBHOOK_SECRET=your_secret
heroku config:set PRIVATE_KEY="$(cat ../licensing/keys/private_key.pem)"

# Deploy
git init
git add webhook_server.py requirements.txt
git commit -m "Initial webhook server"
git push heroku main
```

**Option B: VPS (DigitalOcean, AWS, etc.)**

```bash
# SSH to your server
ssh root@your-server-ip

# Install dependencies
apt update
apt install python3 python3-pip nginx

# Copy files
scp scripts/gumroad/webhook_server.py root@your-server:/opt/aichemist/
scp scripts/licensing/keys/private_key.pem root@your-server:/opt/aichemist/

# Install Python packages
pip3 install fastapi uvicorn supabase python-dotenv cryptography

# Create environment file
cat > /opt/aichemist/.env << EOF
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key
GUMROAD_WEBHOOK_SECRET=your_secret
PRIVATE_KEY_PATH=/opt/aichemist/private_key.pem
EOF

# Run with systemd (production)
cat > /etc/systemd/system/aichemist-webhook.service << EOF
[Unit]
Description=AiChemist Gumroad Webhook
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aichemist
ExecStart=/usr/bin/python3 -m uvicorn webhook_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable aichemist-webhook
systemctl start aichemist-webhook

# Setup nginx reverse proxy
cat > /etc/nginx/sites-available/aichemist << EOF
server {
    listen 80;
    server_name webhook.aichemist.app;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/aichemist /etc/nginx/sites-enabled/
systemctl reload nginx

# Get SSL certificate
apt install certbot python3-certbot-nginx
certbot --nginx -d webhook.aichemist.app
```

### Step 2: Configure Webhook in Gumroad

1. **Go to Gumroad Settings**
   - Settings → Advanced → Webhooks

2. **Add Webhook URL**

   ```
   URL: https://webhook.aichemist.app/webhook/gumroad
   or: https://your-app.herokuapp.com/webhook/gumroad
   ```

3. **Select Events**
   - ✅ Sale
   - ✅ Refund
   - ✅ Dispute

4. **Secret**
   - Generate a secret: `openssl rand -hex 32`
   - Save it in your webhook server environment

5. **Test**
   - Click "Send test ping"
   - Check server logs for successful receipt

---

## 🧪 Testing the Complete Flow

### Test 1: Manual License Generation

```powershell
# Generate a test license
cd D:\Coding\AiChemistCodex\AiChemistTransmutations
python scripts/licensing/generate_dev_license.py

# This creates DEV_LICENSE.txt
# Copy the license key
```

### Test 2: License Activation in App

1. **Run the installed app**

   ```powershell
   cd "gui\release\1.0.0\win-unpacked"
   .\AiChemist Transmutation Codex.exe
   ```

2. **Check trial mode**
   - App should show "Trial: 50/50 conversions remaining"
   - Limited features active

3. **Activate license**
   - Click "Activate License" or "Upgrade"
   - Enter the license key from DEV_LICENSE.txt
   - Click "Activate"

4. **Verify activation**
   - App should show "Licensed"
   - All features unlocked
   - No conversion limit

### Test 3: Gumroad Test Purchase

1. **Enable Test Mode**
   - Gumroad → Settings → Enable test mode

2. **Make Test Purchase**
   - Use test credit card: `4242 4242 4242 4242`
   - Complete purchase flow

3. **Verify Webhook**
   - Check webhook server logs
   - Verify license created in Supabase
   - Check email delivery

4. **Test Activation**
   - Use received license key
   - Activate in the app
   - Verify full unlock

---

## 📊 License Management

### Supabase Schema

Your licenses are stored in Supabase with this structure:

```sql
CREATE TABLE licenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  license_key TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  product_id TEXT NOT NULL,
  variant_id TEXT,
  tier TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  activated_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  machine_id TEXT,
  activation_count INTEGER DEFAULT 0,
  max_activations INTEGER DEFAULT 1,
  metadata JSONB
);
```

### Common Queries

**Check license status:**

```sql
SELECT * FROM licenses WHERE license_key = 'XXXXX-XXXXX-XXXXX-XXXXX';
```

**List recent purchases:**

```sql
SELECT * FROM licenses ORDER BY created_at DESC LIMIT 10;
```

**Deactivate license (for refunds):**

```sql
UPDATE licenses
SET status = 'revoked'
WHERE license_key = 'XXXXX-XXXXX-XXXXX-XXXXX';
```

---

## 🔐 Security Checklist

- [ ] Private key stored securely (NOT in git)
- [ ] Webhook secret configured
- [ ] HTTPS enabled for webhook endpoint
- [ ] Supabase RLS policies configured
- [ ] Environment variables set correctly
- [ ] Test mode disabled before launch
- [ ] Backup of private key in secure location

---

## 📈 Launch Checklist

### Pre-Launch

- [ ] Webhook deployed and tested
- [ ] Supabase configured
- [ ] Test purchase completed successfully
- [ ] License activation tested
- [ ] Email template looks good
- [ ] Product page complete
- [ ] Screenshots added
- [ ] Description finalized
- [ ] Price confirmed

### Launch Day

- [ ] Disable test mode
- [ ] Monitor webhook logs
- [ ] Check email deliverability
- [ ] Test real purchase
- [ ] Verify activation works
- [ ] Support inbox ready

### Post-Launch

- [ ] Monitor purchases
- [ ] Respond to support requests
- [ ] Collect feedback
- [ ] Fix any issues
- [ ] Plan updates

---

## 🆘 Troubleshooting

### License key not received

1. Check spam folder
2. Verify Gumroad email settings
3. Check webhook logs
4. Manually resend from Gumroad

### Webhook not firing

1. Check webhook URL is correct
2. Verify server is running
3. Check firewall/ports
4. Test with curl:

   ```bash
   curl -X POST https://your-webhook-url/webhook/gumroad \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

### License won't activate

1. Check Supabase connection
2. Verify license exists in database
3. Check license status (active/revoked)
4. Verify public key in app matches private key

### Customer reports activation fails

1. Get license key from customer
2. Check in Supabase database
3. Verify status is 'active'
4. Check activation_count < max_activations
5. Generate new key if needed

---

## 💡 Tips for Success

1. **Start with test mode** - Don't go live until you've tested everything
2. **Monitor closely** - Watch your webhook logs for the first few days
3. **Respond quickly** - Answer support emails within 24 hours
4. **Collect feedback** - Ask early customers what they think
5. **Iterate fast** - Fix bugs and improve based on feedback

---

## 📞 Support Resources

**Documentation:**

- Gumroad Docs: <https://help.gumroad.com/>
- Supabase Docs: <https://supabase.com/docs>
- FastAPI Docs: <https://fastapi.tiangolo.com/>

**Your Resources:**

- Webhook Server: `scripts/gumroad/webhook_server.py`
- License Generator: `scripts/licensing/generate_license.py`
- Config: `scripts/gumroad/gumroad_config.yaml`
- Deployment Guide: `scripts/gumroad/DEPLOYMENT_CHECKLIST.md`

---

**Ready to launch?** Follow this guide step-by-step and you'll have a fully automated sales system! 🚀

**Questions?** Check the troubleshooting section or create an issue.
