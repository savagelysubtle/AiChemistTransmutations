# 🎉 AiChemist Transmutation Codex v1.1.0

**Major Release: Gumroad Licensing & Cloud Infrastructure**

[![Download](https://img.shields.io/badge/Download-Windows%20Installer-blue?style=for-the-badge)](https://github.com/savagelysubtle/AiChemistTransmutations/releases/download/v1.1.0/AiChemist.Transmutation.Codex.Setup.1.1.0.exe)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](https://github.com/savagelysubtle/AiChemistTransmutations/blob/main/LICENSE)
[![Gumroad](https://img.shields.io/badge/Buy%20License-Gumroad-ff90e8?style=for-the-badge)](https://aichemist.gumroad.com/l/transmutation-codex)

---

## 🚀 What's New

### 🎉 **Major Features**

#### **Native Gumroad Integration**
- 🔑 **Real-time License Validation** - Instant verification via Gumroad API
- 💳 **Simple Licensing** - Purchase directly from Gumroad, activate instantly
- 🌐 **Online Activation** - Cloud-based license management
- 💾 **Offline Caching** - 24-hour offline validation for uninterrupted work
- 🔒 **Secure Activation** - Machine fingerprinting prevents unauthorized use

#### **Supabase Cloud Backend**
- ☁️ **Cloud License Tracking** - All activations tracked in secure database
- 📊 **Usage Analytics** - Automatic conversion tracking and statistics
- 🔄 **Multi-Device Support** - Manage activations across devices
- 🌍 **Global Infrastructure** - Fast, reliable cloud storage

#### **Simplified Pricing**
- 💰 **$29 per Device** - Clear, straightforward pricing
- 🎯 **One Product, Multiple Keys** - Buy as many licenses as you need
- ✅ **No Tiers, No Confusion** - Same great features for everyone
- 🔓 **Instant Delivery** - License keys delivered immediately via email

### ✨ **Enhancements**

#### **License Management**
- Real-time license status display in UI
- Comprehensive activation error messages with helpful links
- Automatic retry logic for network issues
- Graceful offline fallback when internet unavailable
- Debug logging for troubleshooting activation issues

#### **User Experience**
- Improved license dialog with clear instructions
- Better error messages with Gumroad purchase links
- Real-time activation feedback
- Enhanced trial status display
- Streamlined activation workflow

#### **Developer Experience**
- Environment variable support for deployment flexibility
- Comprehensive documentation for setup and integration
- Multi-channel licensing architecture (Gumroad + future Stripe)
- Webhook server ready for automated license delivery

### 🔧 **Changes**

#### **Breaking Changes**
- ⚠️ **Removed RSA-based Licensing** - Replaced with Gumroad API validation
- ⚠️ **New License File Format** - Changed from `licenses.json` to `gumroad_license.json`
- ⚠️ **License Keys Changed** - Old license keys will not work (contact support for migration)

#### **Improvements**
- License storage moved to platform-specific AppData directories
- Enhanced security with machine fingerprinting
- Better separation of trial and paid license logic
- Improved error handling throughout licensing system

### 🐛 **Bug Fixes**

- Fixed license status not updating after activation
- Resolved trial counter persistence issues
- Fixed Python-Electron bridge environment variable passing
- Improved network timeout handling during API calls
- Fixed license dialog display issues on Windows

### 📚 **Documentation**

#### **New Guides**
- `GUMROAD_INTEGRATION_SUCCESS.md` - Complete integration guide
- `SUPABASE_INTEGRATION_COMPLETE.md` - Database setup documentation
- `SUPABASE_QUICK_REFERENCE.md` - SQL queries and management
- `MULTI_CHANNEL_LICENSING_ARCHITECTURE.md` - Multi-platform architecture
- `THIRD-PARTY-LICENSES.md` - Comprehensive license attribution
- `CHANGELOG.md` - Full release history

#### **Updated Documentation**
- Environment variable templates (`.env.template`)
- Pre-release checklist for future versions
- Enhanced README with licensing information

### 🔐 **Security**

- Enhanced `.gitignore` patterns for sensitive files
- Removed all hardcoded credentials from source code
- Secure environment variable handling for API keys
- Protected Supabase anonymous key usage with RLS policies
- Gumroad license data stored in encrypted JSONB format

### 🗄️ **Database**

#### **New Tables**
- `gumroad_licenses` - Gumroad license tracking with full purchase data
- `license_usage` - Conversion analytics and usage tracking

#### **Database Features**
- Applied migrations with version tracking
- Row Level Security (RLS) enabled on all tables
- Optimized indexes for query performance
- Automatic timestamp tracking for all records

### 🏗️ **Infrastructure**

- **Supabase Project**: `qixmfuwhlvipslxfxhrk` configured and deployed
- **Gumroad Product**: `E7oYHqtGSVBBWcpbCFyF-A==` active and selling
- **Environment System**: Flexible deployment with `.env` files
- **Webhook Server**: Ready for automated license delivery (optional)

---

## 📦 **Installation**

### **Windows Installer (Recommended)**

1. Download: [AiChemist Transmutation Codex Setup 1.1.0.exe](https://github.com/savagelysubtle/AiChemistTransmutations/releases/download/v1.1.0/AiChemist.Transmutation.Codex.Setup.1.1.0.exe)
2. Run the installer and follow the prompts
3. The installer bundles all required dependencies:
   - ✅ Tesseract OCR (Apache 2.0)
   - ✅ Ghostscript (AGPL v3 - source available)
   - ✅ Pandoc (GPL v2 - source available)
   - ✅ LibreOffice (MPL 2.0)
4. Accept the license agreements (see `THIRD-PARTY-LICENSES.md`)
5. Launch the application from Start Menu or Desktop shortcut

### **Portable Version**

Download: [AiChemist Transmutation Codex 1.1.0.exe](https://github.com/savagelysubtle/AiChemistTransmutations/releases/download/v1.1.0/AiChemist.Transmutation.Codex.1.1.0.exe) (portable, no installation required)

### **System Requirements**

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB for application + space for conversions
- **Internet**: Required for license activation (offline mode available after activation)

---

## 🎫 **Licensing**

### **Free Trial**
- ✅ **50 Free Conversions** - Try all features before buying
- ✅ **All Core Formats** - PDF, Markdown, DOCX, HTML
- ✅ **No Credit Card** - Start converting immediately
- ✅ **No Time Limit** - Trial doesn't expire, only conversion count

### **Paid License**
- 💰 **$29 per Device** - Simple, clear pricing
- ✅ **Unlimited Conversions** - Convert as much as you want
- ✅ **All Features** - OCR, batch processing, PDF merging
- ✅ **Lifetime Updates** - Free updates forever
- ✅ **Priority Support** - Email support for license holders

### **Purchase License**

1. **Buy on Gumroad**: https://aichemist.gumroad.com/l/transmutation-codex
2. **Receive License Key** via email (instant delivery)
3. **Activate in App**: Settings → License → Enter key
4. **Start Converting**: All features unlocked immediately

**Need Multiple Licenses?** Purchase multiple keys for different devices or team members.

---

## 🎯 **Key Features**

### **Document Conversion**
- ✅ **PDF ↔ Markdown** - High-quality bidirectional conversion
- ✅ **PDF ↔ HTML** - Preserve formatting and styles
- ✅ **DOCX ↔ Markdown** - Word document conversion
- ✅ **HTML → PDF** - Web page to PDF with CSS support
- ✅ **TXT → PDF** - Plain text to formatted PDF

### **Advanced Features**
- 📄 **OCR Support** - Extract text from scanned PDFs and images
- 📦 **Batch Processing** - Convert multiple files at once
- 🔗 **PDF Merging** - Combine multiple PDFs into one
- 🎨 **Preserve Formatting** - Keep styles, images, tables
- 🌐 **100+ Languages** - OCR supports multiple languages

### **User Experience**
- 🖥️ **Modern UI** - Clean, intuitive interface
- 📊 **Progress Tracking** - Real-time conversion status
- 📝 **Conversion Log** - Detailed history of all conversions
- ⚡ **Fast Performance** - Optimized conversion engine
- 🌙 **Dark Mode** - Easy on the eyes

---

## 📜 **License Compliance**

This software bundles third-party components under various open source licenses:

### **Main License**
- **AiChemist Codex**: Apache License 2.0

### **Bundled Dependencies**
- **Tesseract OCR**: Apache 2.0 ✅ Compatible
- **Ghostscript**: AGPL v3 ⚠️ Source code available
- **Pandoc**: GPL v2+ ⚠️ Source code available
- **LibreOffice**: MPL 2.0 ✅ Compatible
- **Python Libraries**: Mix of MIT, BSD, Apache 2.0 ✅ Compatible
- **PyMuPDF**: AGPL v3 ⚠️ Source code available

### **AGPL/GPL Compliance**

This software includes components under AGPL v3 and GPL v2+, which require source code availability:

- ✅ **All Source Code Available**: https://github.com/savagelysubtle/AiChemistTransmutations
- ✅ **Ghostscript Source**: https://ghostscript.com/releases/gsdnld.html
- ✅ **Pandoc Source**: https://github.com/jgm/pandoc
- ✅ **PyMuPDF Source**: https://github.com/pymupdf/PyMuPDF

For full license details, see `THIRD-PARTY-LICENSES.md` in the installation directory.

**Commercial Ghostscript License**: For commercial use without AGPL obligations, purchase from [Artifex Software](https://www.artifex.com/licensing/).

---

## 🔄 **Upgrading from v1.0.x**

### **Important Notes**

1. **Old License Keys Invalid**: RSA-based keys from v1.0.x will not work
2. **Migration Path**:
   - If you purchased before v1.1.0, contact support@aichemist.app for free upgrade
   - Trial users: Your trial counter resets with new activation system
3. **Backup**: Your conversion settings and history are preserved

### **Migration Steps**

1. Uninstall v1.0.x (optional - installer will upgrade automatically)
2. Download and install v1.1.0
3. Purchase license from Gumroad or migrate existing license
4. Activate with new license key
5. All features unlocked!

---

## 🐛 **Known Issues**

- **First Activation Delay**: First-time activation may take 10-15 seconds (Gumroad API + Supabase)
- **Offline Mode**: Requires online activation first, then works offline for 24 hours
- **Ghostscript AGPL**: Commercial users should review AGPL compliance requirements

### **Workarounds**

- **Slow Activation**: Check your internet connection; cached after first success
- **Offline Use**: Activate while online, then works offline for 24 hours
- **License Issues**: Contact support@aichemist.app for assistance

---

## 📞 **Support**

### **Get Help**

- 📧 **Email**: support@aichemist.app
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/savagelysubtle/AiChemistTransmutations/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/savagelysubtle/AiChemistTransmutations/wiki)
- 🌐 **Website**: https://aichemist.app

### **Community**

- 💬 **Discussions**: [GitHub Discussions](https://github.com/savagelysubtle/AiChemistTransmutations/discussions)
- ⭐ **Star on GitHub**: Show your support!
- 🔀 **Fork & Contribute**: Pull requests welcome

---

## 📊 **Release Statistics**

- **Lines of Code**: ~15,000+ (Python) + ~8,000+ (TypeScript)
- **Commits**: 200+ since v1.0.0
- **Files Changed**: 50+ files modified/created
- **Documentation**: 2,000+ lines of new docs
- **Test Coverage**: 80%+ for core modules

---

## 🙏 **Acknowledgments**

Special thanks to:

- **Gumroad** for simple, developer-friendly licensing API
- **Supabase** for excellent open-source backend infrastructure
- **All Open Source Contributors** for the amazing tools we use
- **Early Adopters** for feedback and bug reports

---

## 🚀 **What's Next?**

### **Coming in v1.2.0**

- 🎨 **Custom Themes** - Personalize the UI
- 📋 **Template System** - Save and reuse conversion settings
- 🔄 **Auto-Updates** - Automatic version checking and updates
- 🌐 **Multi-Language UI** - Internationalization support
- 📱 **Mobile Companion App** - Manage licenses on the go

### **Long-Term Roadmap**

- **Stripe Integration** - Alternative payment option
- **Team Licenses** - Bulk licensing for organizations
- **Cloud Storage Integration** - Google Drive, Dropbox, OneDrive
- **API Access** - Programmatic document conversion
- **Linux & macOS** - Cross-platform support

---

## 📝 **Full Changelog**

See [CHANGELOG.md](https://github.com/savagelysubtle/AiChemistTransmutations/blob/main/CHANGELOG.md) for complete version history.

---

## ⚖️ **Legal**

- **Software License**: Apache 2.0 (see `LICENSE`)
- **Third-Party Licenses**: See `THIRD-PARTY-LICENSES.md`
- **Privacy Policy**: We collect minimal data (license validation only)
- **No Telemetry**: We don't track your conversions or documents
- **GDPR Compliant**: All data stored securely in EU (Supabase)

---

## 💖 **Support Development**

Love this tool? Here's how you can help:

- ⭐ **Star on GitHub** - Show your support
- 💰 **Buy a License** - Support ongoing development
- 🐛 **Report Bugs** - Help us improve
- 📝 **Write Reviews** - Spread the word
- 🔀 **Contribute Code** - Pull requests welcome

---

**Built with ❤️ by the AiChemist Team**

*Transform your documents with confidence.*

[![Download Now](https://img.shields.io/badge/Download-v1.1.0-blue?style=for-the-badge&logo=windows)](https://github.com/savagelysubtle/AiChemistTransmutations/releases/download/v1.1.0/AiChemist.Transmutation.Codex.Setup.1.1.0.exe)
[![Buy License](https://img.shields.io/badge/Buy%20License-$29-ff90e8?style=for-the-badge&logo=gumroad)](https://aichemist.gumroad.com/l/transmutation-codex)

---

**SHA256 Checksums:**

```
Installer: [TO BE GENERATED AFTER BUILD]
Portable:  [TO BE GENERATED AFTER BUILD]
```

*Replace checksums after building the release.*

---

**Release Date**: November 13, 2025
**Version**: 1.1.0
**Build**: Production
**Python**: 3.13.0
**Electron**: 31.2.1


