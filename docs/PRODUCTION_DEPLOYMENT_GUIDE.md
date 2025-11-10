# Production Deployment Guide

## AiChemist Transmutation Codex

**Version:** 1.0.0
**Last Updated:** October 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Build Process](#build-process)
5. [Distribution Channels](#distribution-channels)
6. [Post-Deployment](#post-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete process of deploying AiChemist Transmutation Codex to production, including building, packaging, distribution, and post-deployment monitoring.

### Production Readiness Status

✅ **Phase 1: Core Infrastructure** - COMPLETE

- AppData logging with dev/prod detection
- Production configuration files
- Telemetry system with user consent

✅ **Phase 2: Build System** - COMPLETE

- Dependency bundling (prepare_dependencies.py, runtime_hook_paths.py)
- Windows build script placeholder
- macOS and Linux build scripts (to be implemented)

✅ **Phase 3: GUI & Integration** - COMPLETE

- Updated LicenseDialog with Gumroad URL and legal links
- Telemetry consent dialog
- Electron-Python bridge with telemetry integration
- Updated package.json with publisher information

✅ **Phase 4: Legal Documents** - COMPLETE

- Privacy Policy (GDPR compliant)
- Terms of Service
- EULA

⚠️ **Remaining Tasks:**

- macOS and Linux build scripts
- Gumroad product setup and webhook deployment
- Microsoft Store submission
- User documentation (User Guide, FAQ)
- End-to-end testing on all platforms
- Security audit

---

## Prerequisites

### Development Environment

**Required Software:**

- Python 3.13+ with UV package manager
- Node.js 18+
- Git

**Platform-Specific Requirements:**

**Windows:**

- PyInstaller
- Inno Setup (for NSIS installer)
- Windows SDK (for MSIX packaging)
- EV Code Signing Certificate ($300-500/year)

**macOS:**

- Xcode Command Line Tools
- Apple Developer Account ($99/year)
- Code signing certificate

**Linux:**

- AppImage tools
- Debian packaging tools (for .deb)

### Services and Accounts

1. **Supabase Project**
   - Database for license management
   - Telemetry storage (if enabled)
   - RLS policies configured

2. **Gumroad Account**
   - Product pages created
   - Webhook configured
   - Payment processing setup

3. **Microsoft Partner Center** (optional)
   - Account created ($19 one-time)
   - MSIX package configured

4. **Code Signing Certificates**
   - Windows: EV Code Signing Certificate
   - macOS: Apple Developer certificate

---

## Pre-Deployment Checklist

### Code Readiness

- [ ] All tests passing (`pytest`)
- [ ] No linter errors (`ruff check`)
- [ ] Code formatted (`ruff format`)
- [ ] Version number updated in `pyproject.toml` and `gui/package.json`
- [ ] CHANGELOG.md updated with release notes

### Configuration

- [ ] `.env.production.template` reviewed and validated
- [ ] `config/production_config.yaml` configured
- [ ] Supabase credentials set in environment variables
- [ ] Gumroad webhook URL configured
- [ ] Code signing certificates available

### Security

- [ ] No secrets in codebase (`grep -r "SUPABASE" --include="*.py"`)
- [ ] Private keys stored securely (NOT in repository)
- [ ] `.gitignore` includes sensitive files
- [ ] RLS policies tested in Supabase
- [ ] Webhook signature validation enabled

### Legal and Documentation

- [ ] Privacy Policy reviewed and published
- [ ] Terms of Service reviewed and published
- [ ] EULA included in installer
- [ ] License agreement displayed during installation

---

## Build Process

### 1. Prepare External Dependencies

```powershell
# Windows
cd scripts
python prepare_dependencies.py --verbose
```

```bash
# macOS/Linux
cd scripts
python3 prepare_dependencies.py --verbose
```

**This script:**

- Locates Tesseract, Ghostscript, and Pandoc installations
- Copies them to `build/resources/` for bundling
- Validates that all dependencies are present

### 2. Build Python Backend

```powershell
# Windows
uv sync --all-groups
pyinstaller transmutation_codex.spec --clean --noconfirm
```

```bash
# macOS/Linux
uv sync --all-groups
pyinstaller transmutation_codex.spec --clean --noconfirm
```

**Output:** `dist/transmutation_codex/` executable bundle

### 3. Build Electron Frontend

```powershell
# Windows
cd gui
npm install
npm run build
npm run electron:build
```

**Output:** `gui/release/{version}/` installer files

### 4. Code Signing

**Windows:**

```powershell
$env:CODE_SIGNING_CERT_PATH="path/to/cert.pfx"
$env:CODE_SIGNING_CERT_PASSWORD="cert_password"
signtool sign /f $env:CODE_SIGNING_CERT_PATH /p $env:CODE_SIGNING_CERT_PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 installer.exe
```

**macOS:**

```bash
codesign --force --options runtime --sign "Developer ID Application: Your Name" "AiChemist.app"
xcrun notarytool submit "AiChemist.dmg" --apple-id "your@email.com" --password "app-specific-password" --team-id "TEAM_ID"
```

### 5. Verify Build

- [ ] Installer runs on clean machine
- [ ] Application launches without errors
- [ ] License activation works
- [ ] All converters function correctly
- [ ] Logs write to AppData directory
- [ ] Telemetry consent dialog appears on first launch

---

## Distribution Channels

### 1. Gumroad (Direct Download)

**Setup:**

1. Create products on Gumroad:
   - Basic License ($29)
   - Pro License ($79)
   - Enterprise License (Custom pricing)

2. Configure webhook:
   - Webhook URL: `https://your-server.com/webhook/gumroad`
   - Deploy webhook server (Railway or AWS Lambda)
   - Test webhook with sample purchase

3. Upload installers:
   - Windows: `.exe` installer
   - macOS: `.dmg` file
   - Linux: `.AppImage` or `.deb`

**License Generation Flow:**

1. Customer purchases on Gumroad
2. Webhook receives purchase notification
3. `scripts/licensing/generate_license.py` creates license key
4. License stored in Supabase
5. Email sent to customer with license key

**Files:**

- Webhook server: `scripts/gumroad/webhook_server.py`
- License generator: `scripts/licensing/generate_license.py`

### 2. Microsoft Store

**Preparation:**

1. Create MSIX package:

   ```powershell
   cd gui
   npm run electron:build -- --win --config.win.target=appx
   ```

2. Test package locally:

   ```powershell
   Add-AppxPackage -Path "release/AiChemist-1.0.0.appx"
   ```

3. Submit to Partner Center:
   - Package: Upload `.appx` file
   - Listing: Add screenshots, description
   - Pricing: Set pricing tier
   - Availability: Select markets
   - Age rating: Complete questionnaire

**Review Time:** 1-3 business days

**Files:**

- MSIX configuration: `gui/package.json` (appx section)

### 3. GitHub Releases (Fallback)

1. Tag release:

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. Create GitHub Release:
   - Upload installers for all platforms
   - Include SHA256 checksums
   - Add release notes from CHANGELOG.md

---

## Post-Deployment

### Immediate Actions (Day 1)

1. **Monitor Errors:**
   - Check Supabase logs for errors
   - Monitor webhook server logs
   - Review application telemetry (if users consent)

2. **Test License Activation:**
   - Purchase test license
   - Verify webhook fires
   - Confirm license key generated
   - Test activation in app

3. **Verify Analytics:**
   - Confirm telemetry events arriving (for users who opted in)
   - Check license validation calls
   - Monitor server load

### Week 1

- Respond to early user feedback
- Monitor crash reports and error telemetry
- Fix critical bugs with hotfix releases
- Update FAQ based on support requests

### Ongoing

- Monitor Supabase usage and costs
- Review telemetry data for usage patterns
- Plan feature improvements based on analytics
- Maintain support documentation

---

## Monitoring and Maintenance

### Metrics to Track

**License Metrics:**

- Total active licenses
- Trial conversions to paid
- License activations per day
- Failed activations (investigate)

**Usage Telemetry** (anonymous, with consent):

- Most used converters
- Average conversion time
- Error rates by converter
- File size distributions

**Technical Metrics:**

- Supabase database size and performance
- Webhook response times
- Average license validation time
- Application crash rates

### Alerting

Set up alerts for:

- Webhook failures (> 5% failure rate)
- Database errors
- High error rates in telemetry
- Supabase usage approaching limits

### Tools

- **Supabase Dashboard:** Database, auth, storage monitoring
- **Gumroad Dashboard:** Sales, refunds, product analytics
- **Microsoft Partner Center:** App analytics, crash reports
- **Custom Dashboard:** Aggregate telemetry and license data

---

## Rollback Procedures

### If Critical Bug Found

1. **Immediate:** Remove download links from website
2. **Communication:** Email users about issue
3. **Fix:** Create hotfix branch, fix bug, test thoroughly
4. **Deploy:** Release hotfix version (e.g., 1.0.1)
5. **Notify:** Update users and restore download links

### If License System Fails

1. **Activate Offline Mode:** All users can activate offline
2. **Extend Grace Period:** Modify `production_config.yaml`
3. **Communicate:** Inform users via email/social media
4. **Fix:** Debug Supabase connection, webhook, or Python backend
5. **Restore:** Once fixed, users auto-sync on next validation

### If Installer Issues

1. **Previous Version:** Re-upload previous working installer
2. **Update Links:** Point download links to working version
3. **Fix Build:** Debug PyInstaller spec or electron-builder config
4. **Test:** Verify fix on clean machines
5. **Redeploy:** Upload new installer

---

## Troubleshooting

### Build Failures

**Issue:** PyInstaller fails to bundle dependencies

**Solution:**

```bash
# Clean previous build
rm -rf build/ dist/
# Rebuild with verbose output
pyinstaller transmutation_codex.spec --clean --noconfirm --log-level DEBUG
```

**Issue:** Electron build fails with "Module not found"

**Solution:**

```bash
cd gui
rm -rf node_modules package-lock.json
npm install
npm run build
```

### License Activation Issues

**Issue:** Users report "License validation failed"

**Checklist:**

- [ ] Supabase URL and key in `.env` are correct
- [ ] RLS policies allow public read access to licenses table
- [ ] User's internet connection is stable
- [ ] License key format is correct (AICHEMIST-XXXXX-XXXXX-XXXXX)

**Debug:**

```bash
# Test license validation locally
python scripts/dev/test_supabase_integration.py
```

### Telemetry Not Working

**Issue:** No telemetry events arriving

**Checklist:**

- [ ] User granted consent
- [ ] Supabase telemetry_events table exists
- [ ] SUPABASE_URL and SUPABASE_ANON_KEY are set
- [ ] RLS policy allows authenticated inserts

**Debug:**

```python
from transmutation_codex.core import telemetry
telemetry.init_telemetry()
telemetry.track_event("test_event", {"test": "data"})
telemetry.flush_events()
```

### Installer Not Signed

**Issue:** Windows shows "Unknown publisher" warning

**Solution:**

- Obtain EV Code Signing Certificate
- Sign installer with signtool before distribution
- Upload to Microsoft Store for additional trust

---

## Next Steps

### Before First Production Release

1. ⚠️ **Complete Build Scripts:** Create macOS and Linux build scripts
2. ⚠️ **Setup Gumroad:** Create products, configure webhook, deploy server
3. ⚠️ **Test End-to-End:** Full installation and activation testing on all platforms
4. ⚠️ **Security Audit:** Verify no secrets, test RLS, validate webhook security
5. ⚠️ **User Documentation:** Create User Guide, FAQ, troubleshooting docs

### Post-Release

1. Monitor metrics daily for first week
2. Respond to user feedback promptly
3. Plan feature roadmap based on telemetry and requests
4. Consider additional distribution channels (Mac App Store, Snapcraft, etc.)

---

## Support and Resources

**Email:** <support@aichemist.app>
**Website:** <https://aichemist.app>
**Documentation:** <https://aichemist.app/docs>
**GitHub:** <https://github.com/savagelysubtle/AiChemistTransmutations>

**Internal Resources:**

- `scripts/README.md` - Scripts documentation
- `AGENTS.md` - Development guide
- `CLAUDE.md` - AI agent instructions
- `.cursor/rules/` - Coding conventions

---

**Document Version:** 1.0.0
**Last Updated:** October 2025
**Author:** AiChemist Development Team (@savagelysubtle)
