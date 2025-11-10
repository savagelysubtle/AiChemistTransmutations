# Scripts Directory - Production Ready

This directory contains all scripts for the AiChemist Transmutation Codex project, organized for production readiness with clear separation between development, production, and security-critical scripts.

## 📁 Directory Structure

```
scripts/
├── README.md                          # This file
├── PRODUCTION_READY.md                # Production status documentation
├── CLEANUP_SUMMARY.md                 # Cleanup history
│
├── [PRODUCTION] Root-Level Scripts    # Production-ready
│   ├── check_premium_dependencies.py  # Validate external dependencies
│   ├── start_app.py                   # Application launcher
│   └── auto_activate_dev_license.py   # Dev license auto-activation
│
├── build/                             # Build & Packaging (scripts/build/)
│   ├── README.md                      # Build documentation
│   ├── build_installer.ps1            # Windows installer builder
│   ├── build_installer.sh             # Linux/macOS installer builder
│   ├── transmutation_codex.spec       # PyInstaller specification file
│   ├── installer.iss                  # Inno Setup installer script
│   ├── prepare_dependencies.py        # Windows dependency prep
│   ├── prepare_dependencies_macos.py  # macOS dependency prep
│   ├── runtime_hook_paths.py          # PyInstaller runtime hook
│   └── CONSOLIDATION_COMPLETE.md      # Consolidation summary
│
├── setup/                             # Setup & Installation (scripts/setup/)
│   ├── setup_external_dependencies.ps1  # Master installer
│   ├── install_ghostscript.ps1        # Install Ghostscript
│   ├── install_miktex.ps1             # Install MiKTeX
│   ├── install_pandoc.ps1             # Install Pandoc
│   ├── add_ghostscript_to_path.ps1    # Add Ghostscript to PATH
│   ├── add_miktex_to_path.ps1         # Add MiKTeX to PATH
│   ├── fix_miktex.ps1                 # Fix MiKTeX issues
│   ├── setup_supabase_schema.py       # Database setup
│   └── supabase_setup.sql             # SQL schema
│
├── licensing/                         # License Management ⚠️ SECURITY CRITICAL
│   ├── generate_rsa_keys.py           # One-time: RSA key generation
│   ├── generate_license.py            # Production: Customer licenses
│   ├── generate_dev_license.py        # Development: Dev licenses
│   ├── quick_license_gen.py           # Quick offline generation
│   ├── keys/                          # ⚠️ PRIVATE KEYS (gitignored)
│   └── gumroad/                       # Gumroad webhook integration
│       ├── README.md                  # Gumroad setup guide
│       ├── webhook_server.py          # Webhook server (Flask)
│       ├── gumroad_config.yaml        # Product configuration
│       ├── validate_setup.py          # Configuration validator
│       ├── requirements-webhook.txt   # Python dependencies
│       ├── runtime.txt                # Python version
│       ├── Procfile                   # Deployment config
│       ├── railway.json               # Railway config
│       ├── nixpacks.toml              # Nixpacks config
│       └── DEPLOYMENT_CHECKLIST.md    # Deployment steps
│
└── dev/                               # Development Scripts (scripts/dev/)
    ├── add_licensing_to_converters.py # Add license checks
    ├── show_dev_license.py            # Display dev license
    └── test_supabase_integration.py   # Test database connection
```

## 🎯 Quick Reference

### Production Scripts (Root Level)

**Always include in production builds:**

| Script | Purpose | Usage |
|--------|---------|-------|
| `check_premium_dependencies.py` | Validate Tesseract, Ghostscript, etc. | `python scripts/check_premium_dependencies.py` |
| `start_app.py` | Launch application with proper environment | `python scripts/start_app.py` |
| `auto_activate_dev_license.py` | Auto-activate dev license on startup | Auto-runs in dev mode |

### Build Scripts

**Build installers with bundled dependencies:**

```powershell
# Windows
cd scripts/build
.\build_installer.ps1

# Linux/macOS
cd scripts/build
./build_installer.sh
```

See [scripts/build/README.md](build/README.md) for details.

### Setup Scripts

**Install external dependencies:**

```powershell
# Master installer (installs all)
cd scripts/setup
.\setup_external_dependencies.ps1

# Individual tools
.\install_ghostscript.ps1
.\add_ghostscript_to_path.ps1
```

### Licensing Scripts ⚠️

**SECURITY CRITICAL - Handle with care:**

```powershell
# One-time setup (generates RSA keys)
python scripts/licensing/generate_rsa_keys.py

# Generate customer license
python scripts/licensing/generate_license.py

# Generate dev license
python scripts/licensing/generate_dev_license.py
```

**Gumroad Webhook Setup:**
```bash
# Validate configuration
python scripts/licensing/gumroad/validate_setup.py

# Deploy webhook
cd scripts/licensing/gumroad
railway up
```

See [scripts/licensing/gumroad/README.md](licensing/gumroad/README.md) for deployment.

### Development Scripts

**Development-only utilities:**

```powershell
# Add licensing to converters
python scripts/dev/add_licensing_to_converters.py

# Show current dev license
python scripts/dev/show_dev_license.py

# Test Supabase connection
python scripts/dev/test_supabase_integration.py
```

## 🔒 Security Guidelines

### Private Keys (CRITICAL)

**NEVER commit these files:**
- `scripts/licensing/keys/private_key.pem`
- `scripts/licensing/keys/*.pem`
- Any `.env` files with credentials

**Storage:**
- Store private keys in password manager or HSM
- Use separate keys for dev/test/production
- Rotate keys if compromised

### Environment Variables

Required for production:
```bash
SUPABASE_URL=your_project_url
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_ANON_KEY=your_anon_key
GUMROAD_WEBHOOK_SECRET=your_webhook_secret
```

### Secrets Detection

Before committing:
```powershell
# Check for hardcoded secrets
grep -r "SUPABASE" scripts/ --include="*.py"
grep -r "-----BEGIN" scripts/ --include="*.py"
```

## 📦 Production Deployment

### Include in Builds

**✅ Always Include:**
- `check_premium_dependencies.py`
- `start_app.py`
- `scripts/setup/` (for user installation)
- Documentation (README.md)

**❌ Never Include:**
- `scripts/dev/` (development only)
- `scripts/licensing/` (except on license server)
- `scripts/licensing/keys/` (NEVER distribute)
- Build scripts (unless needed for rebuild)
- `.env` files

### Gumroad Webhook Deployment

**Platform:** Railway, Heroku, or any Python hosting

**Requirements:**
- Python 3.13+
- Flask
- Supabase account
- Gumroad account

**Steps:**
1. Configure products in `gumroad_config.yaml`
2. Set environment variables
3. Deploy webhook server
4. Add webhook URL to Gumroad settings
5. Test with test purchase

See [scripts/licensing/gumroad/README.md](licensing/gumroad/README.md)

## 📋 Script Naming Conventions

### Python Scripts
- **Descriptive names:** `check_premium_dependencies.py` not `check_deps.py`
- **Action prefixes:** `generate_`, `install_`, `setup_`, `fix_`
- **Module docstrings** required
- **Type hints** required

### PowerShell Scripts
- **Descriptive names:** `install_ghostscript.ps1` not `install_gs.ps1`
- **Action prefixes:** `install_`, `add_`, `fix_`, `setup_`
- **Comment-based help** at top

### Documentation
- **Status docs:** SCREAMING_SNAKE_CASE (e.g., `PRODUCTION_READY.md`)
- **Guides:** Title Case (e.g., `README.md`, `CLEANUP_SUMMARY.md`)

## 🔧 Common Tasks

### Check Dependencies
```powershell
python scripts/check_premium_dependencies.py
```

### Install All Dependencies
```powershell
cd scripts/setup
.\setup_external_dependencies.ps1
```

### Build Windows Installer
```powershell
cd scripts/build
.\build_installer.ps1
```

### Generate Dev License
```powershell
python scripts/licensing/generate_dev_license.py
```

### Auto-Activate Dev License
```powershell
python scripts/auto_activate_dev_license.py
```

## 📚 Related Documentation

- **Build Guide:** [gui/BUILD_GUIDE.md](../gui/BUILD_GUIDE.md)
- **Build Issues:** [gui/BUILD_ISSUES.md](../gui/BUILD_ISSUES.md)
- **Development Setup:** [AGENTS.md](../AGENTS.md)
- **AI Guidelines:** [CLAUDE.md](../CLAUDE.md)
- **Gumroad Setup:** [docs/GUMROAD_SETUP_GUIDE.md](../docs/GUMROAD_SETUP_GUIDE.md)

## 🎯 Script Organization Rules

Following [.cursor/rules/050-scripts-directory-layout.mdc](.cursor/rules/050-scripts-directory-layout.mdc):

1. **Production scripts** → `scripts/` (root)
2. **Development scripts** → `scripts/dev/`
3. **License management** → `scripts/licensing/` (⚠️ SECURITY CRITICAL)
4. **Setup scripts** → `scripts/setup/`
5. **Build scripts** → `scripts/build/`

**Enforcement:** All new scripts MUST follow this structure. Scripts in wrong locations will be rejected in code review.

## ✅ Recent Changes

### November 2025 - Directory Consolidation
- ✅ Consolidated build scripts (7 redundant files removed)
- ✅ Moved `transmutation_codex.spec` to `scripts/build/`
- ✅ Moved `installer.iss` to `scripts/build/`
- ✅ Updated all paths in spec and installer files
- ✅ Moved `gumroad/` to `licensing/gumroad/` (proper organization)
- ✅ Moved `prepare_dependencies.py` and `runtime_hook_paths.py` to `scripts/build/`
- ✅ Deleted empty `.keys/` directory
- ✅ Updated all documentation

**Result:** Clean, organized, production-ready structure with all build files together.

---

**Last Updated:** November 9, 2025
**Maintained By:** @savagelysubtle
**Status:** ✅ Production Ready
