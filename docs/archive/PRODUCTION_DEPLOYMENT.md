# Production Deployment Guide

This document provides comprehensive guidance for deploying AiChemist Transmutation Codex to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Build Process](#build-process)
4. [Distribution Channels](#distribution-channels)
5. [License Server Setup](#license-server-setup)
6. [Monitoring and Analytics](#monitoring-and-analytics)
7. [Post-Deployment](#post-deployment)

## Pre-Deployment Checklist

### Code Preparation

- [ ] All tests passing (`pytest`)
- [ ] No linter errors (`ruff check`)
- [ ] Version updated in `version.py`
- [ ] Changelog updated with release notes
- [ ] DEV_MODE environment variable defaults to false
- [ ] DEV_LICENSE.txt excluded from build
- [ ] Supabase SERVICE_KEY not included in app (only in webhook server)
- [ ] Private key not in repository (only public key embedded)

### Configuration

- [ ] Production config created (`.env.production`, `config/production_config.yaml`)
- [ ] Free tier limits configured (50 conversions, 5MB files, 4 converters)
- [ ] Premium features defined in `TrialManager`
- [ ] Supabase Row Level Security policies enabled
- [ ] Telemetry and analytics configured (anonymous only)

### Licensing

- [ ] RSA keys generated and secured
- [ ] Public key embedded in application
- [ ] Private key stored securely (password manager/HSM)
- [ ] Supabase license database configured
- [ ] Gumroad webhook server deployed
- [ ] Test license generation and activation workflow

### External Dependencies

- [ ] Tesseract OCR bundled or installer included
- [ ] Ghostscript installer included
- [ ] Pandoc installer included
- [ ] All dependencies check script updated

## Environment Setup

### Production Environment Variables

Create `.env` for production (DO NOT commit):

```env
NODE_ENV=production
DEV_MODE=false

# Supabase (public credentials only)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Application settings
AICHEMIST_LOG_LEVEL=INFO
AICHEMIST_TELEMETRY_ENABLED=true
```

### Webhook Server Environment

For the Gumroad webhook server (separate deployment):

```env
GUMROAD_WEBHOOK_SECRET=your-webhook-secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key  # ADMIN ACCESS - SECURE THIS!
PRIVATE_KEY_PATH=/secure/path/to/private_key.pem
```

## Build Process

### 1. Clean Build Environment

```powershell
# Remove old builds
Remove-Item -Path dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path build -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path gui/dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path gui/dist-electron -Recurse -Force -ErrorAction SilentlyContinue

# Clean Python cache
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
```

### 2. Set Production Environment

```powershell
$env:NODE_ENV = "production"
$env:DEV_MODE = "false"
```

### 3. Build Python Backend

```powershell
pyinstaller transmutation_codex.spec --clean
```

### 4. Build Electron GUI

```powershell
cd gui
npm run build
npm run electron:build
cd ..
```

### 5. Create Installers

```powershell
# Microsoft Store MSIX
.\scripts\build\build_msix.ps1 -Version "1.0.0.0" -Sign -CertPath "cert.pfx"

# Direct Download Inno Setup
.\scripts\build\build_direct_installer.ps1 -Version "1.0.0"
```

## Distribution Channels

### Microsoft Store

**Pros:**

- Automatic updates
- Trusted distribution
- Microsoft security scanning
- Built-in payment processing (if using Store payments)

**Cons:**

- 15% revenue share (if using Store payments)
- Longer review process
- Must follow Microsoft guidelines

**Submission Process:**

1. Create Partner Center account
2. Reserve app name
3. Upload signed MSIX
4. Fill in store listing
5. Submit for certification
6. Wait 24-72 hours for review

**Requirements:**

- EV code signing certificate
- Age rating
- Privacy policy
- Screenshots (4 required)
- App description (< 10,000 characters)

### Direct Download (Gumroad)

**Pros:**

- Higher profit margin (10% vs 15%)
- Full control over pricing/licensing
- Immediate deployment
- Flexible payment options

**Cons:**

- Manual update notification
- Trust/security concerns from users
- Requires own website/hosting

**Setup:**

1. Create Gumroad product
2. Upload installer to hosting (GitHub Releases, S3, etc.)
3. Configure webhook for license generation
4. Set up product page with features/pricing
5. Test purchase flow end-to-end

## License Server Setup

### Deploy Webhook Server

#### Option A: Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Set environment variables
railway variables set GUMROAD_WEBHOOK_SECRET=xxx
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_SERVICE_KEY=xxx
railway variables set PRIVATE_KEY_PATH=/app/private_key.pem

# Deploy
railway up
```

#### Option B: AWS Lambda

```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml
# Deploy
serverless deploy

# Get endpoint URL
serverless info
```

### Configure Gumroad Webhook

1. Go to Gumroad Dashboard > Settings > Advanced > Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/gumroad`
3. Select events: `sale.successful`
4. Save webhook secret
5. Test with "Send Ping"

### Test License Flow

```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "product_id": "aichemist_pro",
    "order_id": "TEST-001"
  }'

# Verify license created in Supabase
# Test activation in application
```

## Monitoring and Analytics

### Application Telemetry

Configured in `config/production_config.yaml`:

```yaml
telemetry:
  enabled: true
  anonymous: true  # NO PII collected
  collect_pii: false
```

### Metrics to Track

- Total installations (Microsoft Store analytics)
- Active users (monthly/daily)
- Conversion attempts (free vs premium)
- License activations
- Feature usage (which converters most popular)
- Error rates
- Update adoption rate

### Supabase Analytics

Monitor in Supabase dashboard:

- License table size
- Activation count per license
- Failed activation attempts
- Usage logs

### Webhook Monitoring

- Successful license generations
- Failed webhook calls
- Response times
- Error rates

Tools:

- Railway logs: `railway logs`
- AWS CloudWatch (if using Lambda)
- Sentry for error tracking (optional)

## Post-Deployment

### Day 1

- [ ] Monitor webhook for first purchases
- [ ] Verify license delivery emails
- [ ] Test license activation flow
- [ ] Check for crash reports
- [ ] Monitor support emails

### Week 1

- [ ] Review analytics dashboard
- [ ] Check for common issues
- [ ] Collect user feedback
- [ ] Update documentation if needed
- [ ] Fix critical bugs

### Month 1

- [ ] Analyze conversion rates (free to paid)
- [ ] Review feature usage data
- [ ] Plan next version features
- [ ] Update marketing based on data
- [ ] Consider A/B testing pricing

## Rollback Plan

If critical issues arise:

### Microsoft Store

1. Remove app from Store temporarily
2. Fix issues
3. Submit updated package
4. Wait for re-certification

### Direct Download

1. Replace installer on download server
2. Send email to recent purchasers
3. Update version on website
4. Monitor social media/support

### License Issues

1. Disable webhook temporarily
2. Manually generate licenses for pending orders
3. Fix webhook code
4. Redeploy
5. Re-enable webhook

## Security Checklist

- [ ] HTTPS enabled on all services
- [ ] Webhook signature verification active
- [ ] Private keys never in code/repository
- [ ] Environment variables used for all secrets
- [ ] Supabase RLS policies enforced
- [ ] Rate limiting on webhook endpoint
- [ ] Error messages don't leak sensitive info
- [ ] Logs don't contain PII or secrets
- [ ] Code signing certificates secured
- [ ] Backup of private key in secure location

## Support Resources

### Documentation

- User Guide: Include in installer
- FAQ: Website/docs site
- API Documentation: Sphinx generated docs
- Video Tutorials: YouTube channel (optional)

### Support Channels

- Email: <support@yourcompany.com>
- GitHub Issues: For bug reports
- Discord/Slack: Community support (optional)
- Documentation site: docs.yourcompany.com

### Common Issues

Document solutions for:

- License activation failures
- External dependency missing (Tesseract, etc.)
- File conversion errors
- Performance issues
- Update problems

## Legal Requirements

- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] EULA included in installer
- [ ] Cookie policy (if using website analytics)
- [ ] GDPR compliance (if serving EU users)
- [ ] Refund policy documented
- [ ] Support contact information provided

## Launch Announcement

### Marketing Channels

- Product Hunt launch
- Reddit (r/productivity, r/software, etc.)
- Twitter/X announcement
- LinkedIn post
- Newsletter to mailing list
- Blog post with features/pricing
- YouTube demo video

### Press Kit

- App icon (various sizes)
- Screenshots
- Feature list
- Pricing information
- Company background
- Press release
- Demo video link

## Ongoing Maintenance

### Regular Tasks

- Monitor error logs daily
- Review analytics weekly
- Update dependencies monthly
- Security patches as needed
- Respond to support within 24h
- Process refunds within 48h

### Quarterly Reviews

- Analyze conversion funnel
- Review pricing strategy
- Plan feature additions
- Update marketing materials
- Check competitor landscape
- Collect user testimonials

---

**Deployment Date**: TBD
**Version**: 1.0.0
**Deployment Lead**: [Your Name]
**Status**: Pre-Production

**Next Steps**: Complete pre-deployment checklist and schedule deployment date.
