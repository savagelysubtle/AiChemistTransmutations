# Changelog

All notable changes to AiChemist Transmutation Codex will be documented in this
file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-13

### 🎉 Major Features

- **Gumroad Integration**: Native support for Gumroad license keys with
  real-time API validation
- **Supabase Backend**: Online license tracking, activation management, and
  usage analytics
- **Per-Device Licensing**: Simplified single-product model - $29 per device
  activation
- **Multi-Channel Architecture**: Support for multiple sales platforms (Gumroad
  active, Stripe ready)

### ✨ Enhancements

- Real-time license validation via Gumroad API (`/v2/licenses/verify`)
- Offline license caching with 24-hour validity
- Machine fingerprinting for secure activation tracking
- Usage analytics automatically tracked to Supabase cloud database
- Graceful offline fallback mode when internet unavailable
- Comprehensive debug logging for license operations
- Enhanced error messages with purchase links

### 🔧 Changes

- **BREAKING**: Removed RSA-based custom licensing system
- **BREAKING**: Updated license file format from `licenses.json` to
  `gumroad_license.json`
- **BREAKING**: License validation now requires Gumroad product ID
- Environment variables now supported for Supabase configuration (optional)
- License storage moved to platform-specific AppData directories
- Activation limits enforced at 1 device per license key

### 🐛 Bug Fixes

- Improved error messages for license activation failures
- Better handling of network timeouts during API calls
- Fixed trial counter persistence across app restarts
- Resolved license status display issues in UI
- Fixed Python-Electron bridge environment variable passing

### 📚 Documentation

- Added `GUMROAD_INTEGRATION_SUCCESS.md` - Complete integration guide
- Added `SUPABASE_INTEGRATION_COMPLETE.md` - Supabase setup guide
- Added `SUPABASE_QUICK_REFERENCE.md` - SQL queries and management
- Added `MULTI_CHANNEL_LICENSING_ARCHITECTURE.md` - Multi-platform architecture
- Added `PRE_RELEASE_CHECKLIST.md` - Build and release process
- Updated environment variable templates (`.env.template`)

### 🔐 Security

- Enhanced `.gitignore` patterns for sensitive files
- Removed all hardcoded credentials from source code
- Secure environment variable handling for API keys
- Protected Supabase anonymous key usage with RLS policies
- Added Gumroad license data in encrypted JSONB format

### 🗄️ Database

- Created `gumroad_licenses` table for Gumroad license tracking
- Created `license_usage` table for conversion analytics
- Applied database migrations with version tracking
- Enabled Row Level Security (RLS) on all tables
- Added indexes for performance optimization

### 🏗️ Infrastructure

- Supabase project configured: `qixmfuwhlvipslxfxhrk`
- Gumroad product configured: `E7oYHqtGSVBBWcpbCFyF-A==`
- Environment variable system for deployment flexibility
- Webhook server ready for automated license delivery
  (scripts/licensing/gumroad/)

### 📦 Build

- Updated Python package version: `0.1.0` → `0.2.0`
- Updated Electron app version: `1.0.5` → `1.1.0`
- Output directory now includes version: `release/1.1.0/`
- NSIS installer artifact naming includes version

---

## [1.0.5] - 2025-10-22

### Previous Release

- Initial public release with core conversion features
- Trial licensing system (50 conversions)
- All major format converters (PDF, MD, DOCX, HTML)
- Batch processing and PDF merging
- OCR support with Tesseract

---

## Version Guidelines

### Version Numbers (MAJOR.MINOR.PATCH)

**MAJOR** version increments (x.0.0):

- Incompatible API changes
- Major architecture overhauls
- Breaking changes to file formats or configuration

**MINOR** version increments (0.x.0):

- New features added in a backward-compatible manner
- Significant enhancements to existing features
- New converter formats or major integrations

**PATCH** version increments (0.0.x):

- Backward-compatible bug fixes
- Performance improvements
- Documentation updates
- Security patches

### Emoji Guide

- 🎉 Major features
- ✨ Enhancements
- 🔧 Changes
- 🐛 Bug fixes
- 📚 Documentation
- 🔐 Security
- 🗄️ Database
- 🏗️ Infrastructure
- 📦 Build/Package
- ⚠️ Breaking changes
- 🚀 Performance

---

**Project:** AiChemist Transmutation Codex **Repository:**
https://github.com/savagelysubtle/AiChemistTransmutations **Website:**
https://aichemist.app
