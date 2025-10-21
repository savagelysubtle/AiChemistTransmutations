# Production Setup Guide for AiChemist Transmutation Codex

This guide walks you through setting up AiChemist for production deployment with licensing enabled.

## Prerequisites

- Python 3.13+
- Node.js 18+
- Supabase account (for online license validation)
- Secure key storage solution (password manager, HSM, or secure server)

## Step 1: Generate RSA Keys for License Signing

### 1.1 Generate Key Pair

```bash
# Generate RSA-2048 key pair
python scripts/generate_rsa_keys.py
```

This will create:
- `scripts/keys/private_key.pem` (KEEP SECRET!)
- `scripts/keys/public_key.pem` (embed in app)

### 1.2 Secure the Private Key

**CRITICAL:** The private key is the most important secret in your licensing system. If compromised, attackers can generate valid license keys.

**Recommended storage options:**

1. **Hardware Security Module (HSM)**
   - AWS CloudHSM
   - Azure Key Vault
   - YubiHSM

2. **Password Manager** (for small teams)
   - 1Password
   - LastPass
   - Bitwarden

3. **Encrypted Vault** (minimum requirement)
   ```bash
   # Encrypt with GPG
   gpg --symmetric --cipher-algo AES256 scripts/keys/private_key.pem
   
   # Delete unencrypted file
   rm scripts/keys/private_key.pem
   ```

4. **Environment Variable** (production server only)
   ```bash
   # Never commit to git!
   export AICHEMIST_PRIVATE_KEY="$(cat private_key.pem)"
   ```

### 1.3 Update Public Key in Application

1. Copy the contents of `scripts/keys/public_key.pem`
2. Open `src/transmutation_codex/core/licensing/crypto.py`
3. Replace the `_public_key_pem` constant with your generated public key:

```python
_public_key_pem = b"""-----BEGIN PUBLIC KEY-----
[YOUR PUBLIC KEY HERE]
-----END PUBLIC KEY-----"""
```

### 1.4 Add to .gitignore

Ensure these are in `.gitignore`:

```gitignore
# License keys - NEVER COMMIT THESE
scripts/keys/
.keys/
*.pem
private_key*
*.key

# Environment files
.env
.env.local
.env.production
```

## Step 2: Set Up Supabase Backend

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to be provisioned (~2 minutes)
3. Note your project URL and API keys

### 2.2 Create Database Schema

```bash
# Print SQL schema
python scripts/setup_supabase_schema.py --print-only

# Copy the output and paste into Supabase SQL Editor
# Dashboard > SQL Editor > New Query
```

Execute the following tables will be created:
- `licenses` - License records with type, status, expiration
- `activations` - Machine activation tracking
- `usage_logs` - Usage analytics for paid features

### 2.3 Set Up Row Level Security (RLS)

Execute this SQL in Supabase SQL Editor:

```sql
-- Enable RLS on all tables
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE activations ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Allow anon users to read active licenses (for validation)
CREATE POLICY "Allow license validation" ON licenses
  FOR SELECT
  TO anon
  USING (status = 'active');

-- Allow anon users to record activations
CREATE POLICY "Allow recording activations" ON activations
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Allow anon users to update last_seen timestamp
CREATE POLICY "Allow updating last seen" ON activations
  FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

-- Allow anon users to read their own activations (by machine_id hash)
CREATE POLICY "Allow reading own activations" ON activations
  FOR SELECT
  TO anon
  USING (true);

-- Allow anon users to log usage for valid licenses
CREATE POLICY "Allow usage logging" ON usage_logs
  FOR INSERT
  TO anon
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM licenses 
      WHERE licenses.id = usage_logs.license_id 
      AND licenses.status = 'active'
    )
  );

-- Service role has full access (for admin operations)
CREATE POLICY "Service role full access licenses" ON licenses
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access activations" ON activations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access usage_logs" ON usage_logs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
```

### 2.4 Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: Service key for admin operations
# WARNING: Never expose this in client code!
# SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:** 
- The `ANON_KEY` is safe for client use (protected by RLS)
- The `SERVICE_KEY` should ONLY be used server-side for admin operations
- Add `.env` to `.gitignore` to prevent committing credentials

## Step 3: Generate Development License

For testing during development:

```bash
# Generate a perpetual enterprise license for dev@aichemist.local
python scripts/generate_dev_license.py
```

This creates a license with:
- Email: `dev@aichemist.local`
- Type: `enterprise`
- Max activations: 999
- Expires: Never
- Features: All

**Save this license key for testing!**

## Step 4: Set Up Payment Processing

### 4.1 Choose Payment Provider

#### Option A: Gumroad (Recommended for Digital Products)

**Pros:**
- Designed for digital products
- Handles EU VAT automatically
- Simple integration
- Built-in affiliate system

**Setup:**
1. Create account at [gumroad.com](https://gumroad.com)
2. Create products for each license tier:
   - Basic License ($49/year)
   - Professional License ($99/year) 
   - Enterprise License ($299/year or contact)

3. Set up webhooks:
   - Go to Settings > Advanced > Webhooks
   - Add webhook URL: `https://your-api.com/webhooks/gumroad`
   - Events to listen for: `sale`, `refund`, `dispute`

4. Implement webhook handler (see `Step 5` below)

#### Option B: Stripe

**Pros:**
- More flexible
- Better for SaaS/subscriptions
- Supports more payment methods

**Setup:**
1. Create account at [stripe.com](https://stripe.com)
2. Create products and prices
3. Set up webhook endpoint
4. Implement Stripe Checkout integration

### 4.2 Update Purchase URL in LicenseDialog

Edit `gui/src/renderer/components/LicenseDialog.tsx`:

```typescript
const purchaseUrl = 'https://gumroad.com/l/aichemist-codex'; // Your actual URL
```

## Step 5: Implement License Generation Webhook

Create a secure server endpoint that generates licenses when purchases are completed.

### 5.1 Example Webhook Handler (Python/Flask)

```python
"""Webhook handler for automatic license generation."""

import hmac
import hashlib
import os
from flask import Flask, request, jsonify
from transmutation_codex.core.licensing.crypto import LicenseCrypto

app = Flask(__name__)

# Load private key from secure storage
PRIVATE_KEY = os.getenv("AICHEMIST_PRIVATE_KEY")
WEBHOOK_SECRET = os.getenv("GUMROAD_WEBHOOK_SECRET")

@app.route("/webhooks/gumroad", methods=["POST"])
def gumroad_webhook():
    """Handle Gumroad sale webhook."""
    
    # Verify webhook signature
    signature = request.headers.get("X-Gumroad-Signature")
    if not verify_gumroad_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    data = request.json
    
    # Extract purchase details
    email = data.get("email")
    product_id = data.get("product_id")
    
    # Determine license type based on product
    license_type = get_license_type(product_id)
    
    # Generate license
    crypto = LicenseCrypto(PRIVATE_KEY.encode())
    license_data = {
        "email": email,
        "type": license_type,
        "max_activations": get_max_activations(license_type),
        "expires_at": get_expiration_date(license_type),
    }
    
    license_key = crypto.generate_license_key(license_data)
    
    # Store in Supabase
    from supabase import create_client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    supabase.table("licenses").insert({
        "email": email,
        "license_key": license_key,
        "type": license_type,
        "status": "active",
        "max_activations": license_data["max_activations"],
        "expires_at": license_data.get("expires_at"),
    }).execute()
    
    # Send license to customer via email
    send_license_email(email, license_key, license_type)
    
    return jsonify({"success": True}), 200

def verify_gumroad_signature(payload, signature):
    """Verify Gumroad webhook signature."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def get_license_type(product_id):
    """Map product ID to license type."""
    mapping = {
        "basic_product_id": "basic",
        "pro_product_id": "professional",
        "enterprise_product_id": "enterprise",
    }
    return mapping.get(product_id, "basic")

def get_max_activations(license_type):
    """Get max activations for license type."""
    return {
        "basic": 1,
        "professional": 3,
        "enterprise": 999,
    }.get(license_type, 1)

def get_expiration_date(license_type):
    """Get expiration date for license type."""
    from datetime import datetime, timedelta
    
    if license_type == "enterprise":
        return None  # Perpetual
    
    # 1 year from now
    return (datetime.utcnow() + timedelta(days=365)).isoformat()

def send_license_email(email, license_key, license_type):
    """Send license key to customer via email."""
    # Use SendGrid, Mailgun, or your email service
    # Include instructions for activation
    pass
```

### 5.2 Deploy Webhook Handler

Deploy to:
- AWS Lambda + API Gateway
- Google Cloud Functions
- Vercel Serverless Functions
- Your own server

**Security checklist:**
- ✅ Verify webhook signatures
- ✅ Use HTTPS only
- ✅ Rate limit webhook endpoint
- ✅ Store private key securely (environment variable)
- ✅ Log all license generations
- ✅ Monitor for suspicious activity

## Step 6: Test End-to-End Flow

### 6.1 Test License Generation

```bash
# Generate a test license
python scripts/generate_license.py \
  --email "test@example.com" \
  --type "professional" \
  --max-activations 3 \
  --expires-in 365

# Output will be a license key like:
# AICHEMIST-XXXXX-XXXXX-XXXXX-XXXXX
```

### 6.2 Test License Activation

```bash
# Run the licensing test suite
python tests/test_licensing_system.py

# Test activation in GUI
cd gui
npm run dev
```

In the GUI:
1. Click "Activate License"
2. Enter generated license key
3. Verify activation succeeds
4. Check Supabase dashboard for activation record

### 6.3 Test Conversion with License

1. Activate a license
2. Try converting with a paid converter (e.g., PDF→MD)
3. Verify conversion succeeds
4. Check Supabase for usage log entry

### 6.4 Test Trial Mode

1. Deactivate license (or test on new machine)
2. Try MD→PDF conversion (free tier)
3. Verify trial counter increments
4. After 10 conversions, verify trial expired message

## Step 7: Build for Production

### 7.1 Build Python Package

```bash
# Install dependencies
uv sync --all-groups

# Run tests
pytest

# Build distribution
python -m build

# Output will be in dist/
# - aichemist_transmutation_codex-x.x.x.tar.gz
# - aichemist_transmutation_codex-x.x.x-py3-none-any.whl
```

### 7.2 Build Electron App

```bash
cd gui

# Install dependencies
npm install

# Build for production
npm run build

# Build platform-specific installers
npm run electron:build

# Outputs will be in gui/dist-electron/
```

### 7.3 Code Signing (Important for Production)

#### Windows

```bash
# Sign with Authenticode certificate
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 AiChemist-Setup.exe
```

#### macOS

```bash
# Sign with Apple Developer certificate
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" AiChemist.app

# Notarize with Apple
xcrun altool --notarize-app --primary-bundle-id "com.aichemist.transmutations" --username "your@email.com" --password "@keychain:AC_PASSWORD" --file AiChemist.dmg
```

## Step 8: Distribution

### 8.1 Hosting Options

1. **Gumroad** (recommended for simplicity)
   - Upload installer
   - Set price
   - Gumroad handles delivery

2. **Self-hosted**
   - Host on S3/CloudFront
   - Implement download authentication
   - Track downloads

3. **Microsoft Store / Mac App Store**
   - Requires review process
   - Built-in distribution
   - 30% commission

### 8.2 Update Mechanism

Implement auto-update using:
- **Electron Builder Auto-Update** (built-in)
- **electron-updater**

Example configuration in `package.json`:

```json
{
  "build": {
    "publish": [
      {
        "provider": "github",
        "owner": "your-username",
        "repo": "aichemist-transmutations"
      }
    ]
  }
}
```

## Step 9: Monitoring & Analytics

### 9.1 Set Up Monitoring

Monitor via Supabase Dashboard:
- Active licenses count
- Daily activation attempts
- Usage by converter type
- Trial conversion rates

### 9.2 Create Analytics Queries

```sql
-- Active licenses by type
SELECT type, COUNT(*) as count, COUNT(*) FILTER (WHERE expires_at > NOW() OR expires_at IS NULL) as active
FROM licenses
WHERE status = 'active'
GROUP BY type;

-- Conversion usage last 30 days
SELECT 
  converter_name,
  COUNT(*) as conversions,
  SUM(input_file_size) / 1024 / 1024 as total_mb
FROM usage_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY converter_name
ORDER BY conversions DESC;

-- Trial to paid conversion rate
SELECT 
  COUNT(*) FILTER (WHERE type = 'trial') as trials,
  COUNT(*) FILTER (WHERE type != 'trial') as paid,
  ROUND(100.0 * COUNT(*) FILTER (WHERE type != 'trial') / NULLIF(COUNT(*), 0), 2) as conversion_rate
FROM licenses;
```

### 9.3 Set Up Alerts

Create alerts for:
- Suspicious activation patterns (too many from same email)
- Failed activation attempts spike
- License validation errors
- Payment webhook failures

## Step 10: Legal & Compliance

### 10.1 Update License Agreement

Create `LICENSE_AGREEMENT.md` with:
- Terms of use
- Refund policy
- Privacy policy
- GDPR compliance

### 10.2 Display in Application

Show license agreement:
- During first launch
- In Help > License Agreement menu
- On website

### 10.3 GDPR Compliance

Implement:
- Data export (user can download their license data)
- Data deletion (user can request account deletion)
- Consent for analytics tracking

Add to Supabase:

```sql
-- Add GDPR fields
ALTER TABLE licenses ADD COLUMN gdpr_consent BOOLEAN DEFAULT true;
ALTER TABLE licenses ADD COLUMN data_retention_until TIMESTAMPTZ;
```

## Troubleshooting

### License Activation Fails

1. Check Supabase connection:
   ```python
   from transmutation_codex.core.licensing import get_license_manager
   manager = get_license_manager()
   print(manager.supabase_backend.is_online_available())
   ```

2. Verify public key matches private key used for generation
3. Check activation limit not exceeded
4. Verify license not expired/revoked

### Webhook Not Receiving Events

1. Check webhook URL is publicly accessible
2. Verify signature validation logic
3. Check Gumroad/Stripe webhook logs
4. Test with webhook testing tools (webhook.site)

### Offline Mode Not Working

1. Verify RSA public key is correctly embedded
2. Check license key format (should start with AICHEMIST-)
3. Test with known-good license from `generate_dev_license.py`

## Security Checklist

Before going live, verify:

- [ ] Private key is secured and not in version control
- [ ] `.env` file is in `.gitignore`
- [ ] Public key is correctly embedded in application
- [ ] Webhook signatures are validated
- [ ] RLS policies are enabled on all Supabase tables
- [ ] Service role key is not exposed in client code
- [ ] HTTPS is enforced for all API calls
- [ ] Rate limiting is enabled on webhook endpoints
- [ ] License validation cannot be bypassed in code
- [ ] Error messages don't leak sensitive information
- [ ] Logging doesn't include license keys or private data
- [ ] Application is code-signed for distribution
- [ ] Auto-update mechanism is implemented

## Support

For questions or issues:
- Check logs in `~/.aichemist/` (Linux/Mac) or `%APPDATA%/AiChemist/` (Windows)
- Review Supabase logs in dashboard
- Enable debug logging in `config/default_config.yaml`

## Appendix: License Tiers

| Feature | Trial | Basic | Professional | Enterprise |
|---------|-------|-------|--------------|------------|
| **Price** | Free | $49/year | $99/year | $299/year |
| **Conversions** | 10 total | Unlimited | Unlimited | Unlimited |
| **Activations** | 1 | 1 | 3 | 999 |
| **MD→PDF** | ✅ | ✅ | ✅ | ✅ |
| **PDF→MD** | ❌ | ✅ | ✅ | ✅ |
| **PDF→HTML** | ❌ | ✅ | ✅ | ✅ |
| **HTML→PDF** | ❌ | ✅ | ✅ | ✅ |
| **DOCX→MD** | ❌ | ✅ | ✅ | ✅ |
| **TXT→PDF** | ❌ | ✅ | ✅ | ✅ |
| **PDF Merge** | ❌ | ✅ | ✅ | ✅ |
| **OCR Support** | ❌ | ✅ | ✅ | ✅ |
| **File Size Limit** | 5MB | Unlimited | Unlimited | Unlimited |
| **Support** | Community | Email | Priority | Phone + Dedicated |
| **Updates** | - | 1 year | 1 year | Perpetual |
| **Commercial Use** | ❌ | ✅ | ✅ | ✅ |

## Next Steps

1. Generate production RSA keys → Store securely
2. Set up Supabase project → Configure RLS
3. Create Gumroad products → Set up webhooks
4. Deploy webhook handler → Test license generation
5. Build production installers → Code sign
6. Launch! 🚀

