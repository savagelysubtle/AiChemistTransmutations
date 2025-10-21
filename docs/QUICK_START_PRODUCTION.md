# Quick Start Guide for Production Deployment

This guide provides a step-by-step walkthrough for completing the production deployment of AiChemist Transmutation Codex.

## ✅ What's Already Done

All core code has been implemented:

- Production configuration files
- Feature gates (free vs premium tiers)
- Dev mode security (DEV_MODE=true required)
- Gumroad webhook server
- Upgrade dialog UI component
- GitHub Actions CI/CD workflow
- Version management system
- Installer updates

**See `PRODUCTION_IMPLEMENTATION_SUMMARY.md` for complete details.**

## 🎯 What You Need to Do

### Step 1: Create Build Scripts (10 minutes)

Due to workspace restrictions, manually create these files using the templates from `\productio.plan.md`:

**File: `scripts/build/build_msix.ps1`**

- Copy template from plan (Phase 3.2)
- Builds MSIX package for Microsoft Store
- Handles signing with certificate

**File: `scripts/build/build_direct_installer.ps1`**

- Copy template from plan (Phase 5.2)
- Builds Inno Setup installer for direct download
- Includes all dependencies

### Step 2: Create MSIX Assets (1-2 hours)

Create PNG images in `build/msix/Assets/`:

```
build/msix/Assets/
├── StoreLogo.png (50x50)
├── Square44x44Logo.png (44x44)
├── Square71x71Logo.png (71x71)
├── Square150x150Logo.png (150x150)
├── Square310x310Logo.png (310x310)
├── Wide310x150Logo.png (310x150)
└── SplashScreen.png (620x300)
```

**Tips:**

- Use your brand colors
- Add 10% padding for safety
- PNG format with transparency
- Follow Microsoft design guidelines

**Tools:**

- Figma/Sketch for design
- Photoshop for export
- Or hire designer on Fiverr ($20-50)

### Step 3: Purchase Code Signing Certificates (2-3 weeks)

**For Microsoft Store (MSIX):**

- Get EV (Extended Validation) certificate
- Vendors: DigiCert, GlobalSign, Sectigo
- Cost: $300-600/year
- Process: 2-3 weeks (identity validation)

**For Direct Download (Inno Setup):**

- Standard code signing certificate
- Same vendors as above
- Cost: $100-300/year
- Process: 1-2 weeks

**Once you have certificates:**

```powershell
# Sign MSIX
.\scripts\build\build_msix.ps1 -Sign -CertPath "cert.pfx" -CertPassword "your-password"

# Sign Inno Setup installer
signtool sign /fd SHA256 /f cert.pfx /p password dist/installer/AiChemistSetup_1.0.0.exe
```

### Step 4: Deploy Gumroad Webhook (30 minutes)

**Option A: Railway (Recommended)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Set environment variables
railway variables set GUMROAD_WEBHOOK_SECRET=xxx
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_SERVICE_KEY=your-service-key
railway variables set PRIVATE_KEY_PATH=/app/private_key.pem

# Upload private key securely
railway volume create
railway volume upload private_key.pem /app/private_key.pem

# Deploy
railway up

# Get webhook URL
railway domain
```

**Option B: Render**

1. Connect GitHub repository
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn scripts.gumroad.webhook_server:app`
5. Add environment variables in dashboard
6. Deploy

### Step 5: Configure Gumroad Product (15 minutes)

1. Go to <https://gumroad.com/products/new>
2. Set product details:
   - **Name**: AiChemist Transmutation Codex Pro
   - **Price**: $29
   - **Type**: Digital product

3. Configure webhook:
   - Dashboard > Settings > Advanced > Webhooks
   - **URL**: `https://your-webhook-url.com/webhook/gumroad`
   - **Events**: `sale.successful`
   - Save webhook secret

4. Test with "Send Ping"
5. Verify license generated in Supabase

### Step 6: Configure Supabase Security (15 minutes)

Enable Row Level Security:

```sql
-- Run in Supabase SQL Editor

-- Enable RLS on licenses table
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;

-- Allow users to read only their own licenses
CREATE POLICY "Users can read own licenses"
ON licenses FOR SELECT
USING (auth.uid()::text = email);

-- Only service role can insert/update licenses
CREATE POLICY "Service role can manage licenses"
ON licenses FOR ALL
USING (auth.jwt()->>'role' = 'service_role');

-- Enable RLS on activations table
ALTER TABLE activations ENABLE ROW LEVEL SECURITY;

-- Allow users to manage their own activations
CREATE POLICY "Users can manage own activations"
ON activations FOR ALL
USING (license_id IN (
  SELECT id FROM licenses WHERE email = auth.uid()::text
));
```

Test with non-admin Supabase client.

### Step 7: Add Premium Badges to GUI (30 minutes)

**File: `gui/src/renderer/components/ConversionTypeSelect.tsx`**

Add this helper function:

```tsx
const PREMIUM_CONVERTERS = [
  'pdf2md_ocr', 'html2pdf', 'docx2md', 'docx2pdf',
  'pdf2docx', 'excel2pdf', 'pptx2pdf', 'epub2pdf',
  'rst2pdf', 'pdf2images', 'merge_pdf', 'batch'
];

const isPremiumConverter = (type: string) => {
  return PREMIUM_CONVERTERS.includes(type);
};
```

Then in the converter options rendering:

```tsx
{conversionTypes.map((type) => (
  <option key={type} value={type}>
    {type}
    {isPremiumConverter(type) && !isPremiumUser ? ' ⭐ Premium' : ''}
  </option>
))}
```

Import and show UpgradeDialog when premium feature clicked without license.

### Step 8: Build and Test (1-2 hours)

```powershell
# Set production mode
$env:NODE_ENV = "production"
$env:DEV_MODE = "false"

# Build Python backend
pyinstaller transmutation_codex.spec --clean

# Build Electron GUI
cd gui
npm run build
npm run electron:build
cd ..

# Build MSIX
.\scripts\build\build_msix.ps1 -Version "1.0.0.0"

# Build Inno Setup installer
.\scripts\build\build_direct_installer.ps1 -Version "1.0.0"

# Test on clean Windows VM
# - Install from MSIX
# - Install from Inno Setup
# - Test free tier limits
# - Purchase test license
# - Activate and test premium features
```

### Step 9: Submit to Microsoft Store (1-2 days)

1. Create Partner Center account: <https://partner.microsoft.com/dashboard>
2. Reserve app name
3. Create new submission
4. Upload signed MSIX
5. Fill store listing:
   - **Description**: Professional document conversion toolkit
   - **Screenshots**: 4+ required
   - **Privacy policy**: Required URL
   - **Age rating**: EVERYONE
6. Set pricing (FREE with in-app purchases OR paid app)
7. Submit for certification
8. Wait 24-72 hours for review

### Step 10: Launch! 🚀

Once Microsoft Store is approved:

1. **Enable Gumroad product** for sales
2. **Update website** with download links:
   - Microsoft Store badge
   - Direct download button
3. **Announce on social media**:
   - Twitter/X
   - LinkedIn
   - Reddit (r/software, r/productivity)
   - Product Hunt
4. **Monitor systems**:
   - Webhook server logs
   - Supabase activations
   - Support emails
   - Download counts

## 📋 Pre-Launch Checklist

- [ ] Build scripts created from templates
- [ ] MSIX assets created (7 images)
- [ ] Code signing certificates obtained
- [ ] Webhook server deployed
- [ ] Gumroad product configured
- [ ] Supabase RLS enabled and tested
- [ ] Premium badges added to GUI
- [ ] Installers built and tested
- [ ] Test purchase flow end-to-end
- [ ] Microsoft Store listing prepared
- [ ] Website updated with download links
- [ ] Support email configured
- [ ] Privacy policy published
- [ ] Terms of service published

## 📞 Support

If you get stuck:

- **Build Issues**: See `scripts/build/README.md`
- **Webhook Issues**: See `scripts/gumroad/README.md`
- **Full Deployment Guide**: See `docs/PRODUCTION_DEPLOYMENT.md`
- **Implementation Details**: See `PRODUCTION_IMPLEMENTATION_SUMMARY.md`
- **Original Plan**: See `\productio.plan.md`

## 💰 Pricing Recommendation

- **Free Tier**: 4 converters, 50 conversions, 5MB limit
- **Premium**: $29 one-time payment
  - Unlimited conversions
  - Unlimited file sizes
  - All 20+ converters
  - OCR support
  - Batch processing

## 🎯 Success Metrics

Track these after launch:

- Downloads (Microsoft Store + direct)
- Free to premium conversion rate
- Average conversions per user
- Most popular converters
- Support ticket volume
- User reviews/ratings

## 🚨 Emergency Contacts

- **Gumroad Support**: <help@gumroad.com>
- **Microsoft Partner Support**: <https://partner.microsoft.com/support>
- **Supabase Support**: <https://supabase.com/support>
- **Railway Support**: <https://railway.app/help>

---

**Good luck with your launch!** 🎉

The hard part (coding) is done. Now it's just configuration, assets, and deployment.

**Estimated time to launch**: 1-2 weeks (mostly waiting for certificates)
