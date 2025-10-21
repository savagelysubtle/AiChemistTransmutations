# AiChemist Transmutation Codex - Scripts Directory

This directory contains utility scripts for development, licensing, setup, and build operations.

## Directory Structure

```
scripts/
├── README.md                        # This file
├── check_premium_dependencies.py    # Production: Check external dependencies
├── start_app.py                     # Production: Application launcher
│
├── dev/                            # Development-only scripts
│   ├── add_licensing_to_converters.py
│   ├── show_dev_license.py
│   └── test_supabase_integration.py
│
├── licensing/                      # License management scripts
│   ├── generate_rsa_keys.py        # One-time: Generate RSA key pair
│   ├── generate_license.py         # Production: Generate customer licenses
│   ├── generate_dev_license.py     # Development: Generate dev licenses
│   ├── quick_license_gen.py        # Quick license generation
│   └── keys/                       # RSA keys (gitignored for security)
│
├── setup/                          # Setup and installation scripts
│   ├── setup_external_dependencies.ps1  # Install all external dependencies
│   ├── install_tesseract.ps1
│   ├── install_ghostscript.ps1
│   ├── install_pandoc.ps1
│   ├── install_miktex.ps1
│   ├── add_ghostscript_to_path.ps1
│   ├── add_miktex_to_path.ps1
│   ├── fix_miktex.ps1
│   ├── setup_supabase_schema.py
│   └── supabase_setup.sql
│
└── build/                          # Build and packaging scripts
    ├── build_installer.ps1         # Windows installer builder
    ├── build_installer.sh          # Linux/macOS installer builder
    └── runtime_hook_paths.py       # PyInstaller runtime hook
```

## Production Scripts

### `check_premium_dependencies.py`

**Purpose**: Check availability and configuration of external dependencies (Tesseract, Ghostscript, Pandoc, MiKTeX)
**Usage**: `python scripts/check_premium_dependencies.py`
**When to use**: Before deployment, during CI/CD, or troubleshooting dependency issues

### `start_app.py`

**Purpose**: Launch the application with proper environment setup
**Usage**: `python scripts/start_app.py`
**When to use**: Alternative application launcher for development or testing

## Development Scripts (`dev/`)

### `add_licensing_to_converters.py`

**Purpose**: Automatically add licensing checks to converter files
**Usage**: `python scripts/dev/add_licensing_to_converters.py`
**When to use**: One-time script already executed; kept for reference

### `show_dev_license.py`

**Purpose**: Display current development license information
**Usage**: `python scripts/dev/show_dev_license.py`
**When to use**: Verify dev license status during development

### `test_supabase_integration.py`

**Purpose**: Test Supabase license backend integration
**Usage**: `python scripts/dev/test_supabase_integration.py`
**When to use**: Verify Supabase connection and license validation

## Licensing Scripts (`licensing/`)

### `generate_rsa_keys.py` ⚠️ SECURITY CRITICAL

**Purpose**: Generate RSA-2048 key pair for license signing
**Usage**: `python scripts/licensing/generate_rsa_keys.py`
**When to use**: ONE-TIME ONLY during initial setup
**Security**:

- Keep `private_key.pem` SECRET and SECURE
- Only `public_key.pem` should be in the application
- Store private key in password manager or HSM
- Never commit private keys to version control

### `generate_license.py` 🔐 PRODUCTION

**Purpose**: Generate signed license keys for customers
**Usage**:

```bash
# Single license
python scripts/licensing/generate_license.py \
  --email customer@example.com \
  --type pro \
  --activations 1

# Batch licenses
python scripts/licensing/generate_license.py \
  --email test@test.com \
  --type trial \
  --batch 10 \
  --output licenses.json
```

**Options**:

- `--type`: `trial`, `pro`, `enterprise`
- `--activations`: Number of allowed device activations (default: 1)
- `--expiry-days`: Days until expiry (omit for perpetual)
- `--name`: Customer name (optional)
- `--order-id`: Order/transaction ID (optional)

### `generate_dev_license.py` 🔧 DEVELOPMENT

**Purpose**: Generate perpetual enterprise license for development
**Usage**:

```bash
# Print only
python scripts/licensing/generate_dev_license.py --print-only

# Generate and insert into Supabase
python scripts/licensing/generate_dev_license.py
```

**Requirements**: `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` environment variables

### `quick_license_gen.py` ⚡

**Purpose**: Quick license generation without Supabase dependency
**Usage**: `python scripts/licensing/quick_license_gen.py`
**When to use**: Fast license generation for testing (offline mode)

## Setup Scripts (`setup/`)

### `setup_external_dependencies.ps1` 🔧 PRIMARY SETUP

**Purpose**: Master script to install all external dependencies
**Usage**: `powershell -ExecutionPolicy Bypass -File scripts/setup/setup_external_dependencies.ps1`
**What it does**:

- Installs Tesseract OCR
- Installs Ghostscript
- Installs Pandoc
- Installs MiKTeX (optional)
- Configures PATH environment variables
- Verifies installations

### Individual Installers

- `install_tesseract.ps1`: Install Tesseract OCR for PDF text extraction
- `install_ghostscript.ps1`: Install Ghostscript for PDF processing
- `install_pandoc.ps1`: Install Pandoc for document conversions
- `install_miktex.ps1`: Install MiKTeX for LaTeX-based PDF generation

### PATH Configuration

- `add_ghostscript_to_path.ps1`: Add Ghostscript to system PATH
- `add_miktex_to_path.ps1`: Add MiKTeX to system PATH
- `fix_miktex.ps1`: Fix MiKTeX installation issues

### Supabase Setup

- `setup_supabase_schema.py`: Initialize Supabase database schema
- `supabase_setup.sql`: SQL schema for licenses, activations, and usage tracking

**Usage**:

```bash
# Run schema setup
python scripts/setup/setup_supabase_schema.py

# Or manually execute SQL in Supabase Dashboard
# Copy contents of supabase_setup.sql
```

## Build Scripts (`build/`)

### `build_installer.ps1` 📦 WINDOWS

**Purpose**: Build Windows installer with PyInstaller
**Usage**: `powershell -ExecutionPolicy Bypass -File scripts/build/build_installer.ps1`
**Output**: Standalone `.exe` installer in `dist/`

### `build_installer.sh` 📦 LINUX/MACOS

**Purpose**: Build Linux/macOS installer with PyInstaller
**Usage**: `bash scripts/build/build_installer.sh`
**Output**: Standalone executable in `dist/`

### `runtime_hook_paths.py` ⚙️

**Purpose**: PyInstaller runtime hook to configure bundled executable paths
**Usage**: Automatically executed by PyInstaller during runtime
**What it does**: Adds bundled Tesseract, Ghostscript, and Pandoc to PATH

## Environment Variables

### Required for Production

```bash
# Licensing (for customer license generation)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Optional: Application configuration
AICHEMIST_CONFIG_PATH=/path/to/config.yaml
AICHEMIST_LOG_LEVEL=INFO
```

### Required for Development

```bash
# Development license generation and testing
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Development mode
AICHEMIST_DEV_MODE=true
AICHEMIST_LOG_LEVEL=DEBUG
```

## Security Best Practices

### 🔐 Private Key Management

1. **NEVER** commit `licensing/keys/private_key.pem` to version control
2. Store private key in secure location (password manager, HSM, encrypted storage)
3. Use separate key pairs for dev/test/production environments
4. Rotate keys if compromised

### 🔒 Supabase Credentials

1. Use environment variables for `SUPABASE_URL` and keys
2. Never hardcode credentials in scripts
3. Use `SERVICE_ROLE_KEY` only for admin operations (license generation)
4. Use `ANON_KEY` for client-side operations (license validation)

### 📋 License File Security

- Generated licenses are saved to:
  - Development: `.licenses/dev_license.txt` (gitignored)
  - Batch: `licenses.json` (gitignored)
- Add these to `.gitignore` to prevent accidental commits

## Common Workflows

### Initial Setup (First Time)

```bash
# 1. Generate RSA keys
python scripts/licensing/generate_rsa_keys.py

# 2. Update public key in application
# Copy output to src/transmutation_codex/core/licensing/crypto.py

# 3. Setup Supabase (if using online licensing)
python scripts/setup/setup_supabase_schema.py

# 4. Generate dev license
python scripts/licensing/generate_dev_license.py

# 5. Install external dependencies
powershell -ExecutionPolicy Bypass -File scripts/setup/setup_external_dependencies.ps1
```

### Generate Customer License

```bash
# Professional license (1 activation, perpetual)
python scripts/licensing/generate_license.py \
  --email customer@example.com \
  --type pro \
  --name "John Doe" \
  --order-id "ORD-12345"

# Enterprise license (5 activations)
python scripts/licensing/generate_license.py \
  --email enterprise@company.com \
  --type enterprise \
  --activations 5 \
  --name "Acme Corp"

# Trial license (30 days)
python scripts/licensing/generate_license.py \
  --email trial@test.com \
  --type trial \
  --expiry-days 30
```

### Build Installer

```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/build/build_installer.ps1

# Linux/macOS
bash scripts/build/build_installer.sh
```

### Check Dependencies

```bash
# Check all external dependencies
python scripts/check_premium_dependencies.py

# Output shows:
# - Availability of each dependency
# - Versions installed
# - Configuration issues
# - Recommendations
```

## Troubleshooting

### "Private key not found" Error

**Solution**: Run `python scripts/licensing/generate_rsa_keys.py` first

### "Supabase connection failed" Error

**Solution**:

1. Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` environment variables
2. Verify Supabase project is active
3. Check network connectivity

### "External dependency not found" Error

**Solution**: Run `powershell -ExecutionPolicy Bypass -File scripts/setup/setup_external_dependencies.ps1`

### PyInstaller build fails

**Solution**:

1. Check all dependencies are installed
2. Verify `runtime_hook_paths.py` is in build folder
3. Check `transmutation_codex.spec` configuration

## Development vs Production

### Development Scripts (Keep in source control)

- ✅ All scripts in `dev/` folder
- ✅ `generate_dev_license.py`, `quick_license_gen.py`
- ✅ `test_supabase_integration.py`

### Production Scripts (Include in releases)

- ✅ `check_premium_dependencies.py`
- ✅ `start_app.py`
- ✅ `generate_license.py` (for license server/admin only)

### Never in Production

- ❌ Private keys (`licensing/keys/private_key.pem`)
- ❌ Generated license files (`.licenses/`, `licenses.json`)
- ❌ Development licenses (`DEV_LICENSE.txt`)
- ❌ Supabase service keys (use environment variables)

## Maintenance

### Regular Tasks

- Review and update dependency versions in setup scripts
- Rotate RSA keys annually (for high-security deployments)
- Audit generated licenses and activations in Supabase
- Test license generation and validation flows

### Before Each Release

1. Run `python scripts/check_premium_dependencies.py`
2. Test build process on all platforms
3. Verify license validation works offline and online
4. Update documentation with any script changes

---

**Last Updated**: October 2025
**Maintained by**: AiChemist Development Team
**Questions**: See AGENTS.md and CLAUDE.md for additional guidance
