# Complete Application Build & Distribution Guide

**Goal:** Create a complete installable Windows application with Gumroad license activation

**Date:** October 22, 2025

---

## 📋 Overview

We need to:

1. Build the Electron GUI
2. Package Python backend with Electron
3. Create Windows installer
4. Setup Gumroad for license delivery
5. Test the complete flow

---

## Step 1: Build Electron GUI

### Prerequisites

```powershell
cd gui
npm ci  # Install dependencies
```

### Update electron-builder Configuration

The `gui/package.json` needs to bundle the Python backend.

**Check current configuration:**

- extraResources should point to `../dist/aichemist_transmutation_codex`
- Build targets should include NSIS and portable

### Build Command

```powershell
cd gui
npm run build
```

This will:

- Build React frontend with Vite
- Bundle Electron app
- Include Python backend in resources
- Create installer in `gui/release/`

---

## Step 2: Package Everything Together

### Electron Builder Config

Update `gui/package.json` build section:

```json
{
  "build": {
    "appId": "app.aichemist.transmutation-codex",
    "productName": "AiChemist Transmutation Codex",
    "directories": {
      "output": "release/${version}"
    },
    "extraResources": [
      {
        "from": "../dist/aichemist_transmutation_codex",
        "to": "python-backend",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        }
      ],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "AiChemist"
    }
  }
}
```

---

## Step 3: Test License Activation

### License Flow

1. User purchases on Gumroad
2. Receives license key via email
3. Opens app (trial mode)
4. Clicks "Activate License"
5. Enters key
6. App validates with Supabase
7. App unlocks all features

### Test Commands

```powershell
# Check if license system works
.\dist\aichemist_transmutation_codex\aichemist_transmutation_codex.exe --check-license

# Activate a test license
python scripts/licensing/generate_dev_license.py
```

---

## Step 4: Create Complete Installer

### Build Complete Application

```powershell
# 1. Build Python backend (already done)
# Located in: dist/aichemist_transmutation_codex/

# 2. Build Electron GUI with Python bundled
cd gui
npm run build

# Output will be in: gui/release/1.0.0/
```

### Installer Contents

The NSIS installer will include:

- Electron application
- Python backend (bundled)
- External tools (Tesseract, Ghostscript, Pandoc) - optional
- Desktop shortcut
- Start menu shortcut
- Uninstaller

---

## Step 5: Setup Gumroad

### Product Configuration

**On Gumroad:**

1. Create product: "AiChemist Transmutation Codex"
2. Set price tiers:
   - Basic: $29
   - Pro: $79
   - Enterprise: Contact
3. Configure webhook: `https://your-server.com/webhook/gumroad`
4. Enable license key delivery

### Webhook Server

Deploy `scripts/gumroad/webhook_server.py` to your server:

```bash
# On your server
pip install fastapi uvicorn supabase python-dotenv cryptography
uvicorn webhook_server:app --host 0.0.0.0 --port 8000
```

### Test Purchase Flow

1. Use Gumroad test mode
2. Complete a test purchase
3. Verify license key email arrives
4. Test activation in app

---

## Step 6: Distribution Files

### What Users Download

**Installer (Recommended):**

- `AiChemist-Transmutation-Codex-Setup-1.0.0.exe` (~300-400 MB)
  - Includes everything
  - Installs to Program Files
  - Creates shortcuts
  - Adds to Windows Apps list

**Portable (Advanced Users):**

- `AiChemist-Transmutation-Codex-1.0.0-portable.exe` (~300-400 MB)
  - No installation required
  - Run from anywhere
  - USB-friendly

---

## Quick Build Commands

### Complete Build Process

```powershell
# Step 1: Ensure Python backend is built
cd D:\Coding\AiChemistCodex\AiChemistTransmutations
uv run pyinstaller transmutation_codex.spec --noconfirm

# Step 2: Build Electron GUI with bundled backend
cd gui
npm ci
npm run build

# Step 3: Test the installer
cd release/1.0.0
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe

# Step 4: Test portable version
.\AiChemist-Transmutation-Codex-1.0.0-portable.exe
```

---

## Testing Checklist

### Before Distribution

- [ ] Python backend builds successfully
- [ ] Electron GUI builds successfully
- [ ] Installer creates correctly
- [ ] App launches after install
- [ ] All converters work
- [ ] License activation works
- [ ] Trial mode works (50 conversions)
- [ ] External tools found (Tesseract, etc.)
- [ ] Uninstaller works
- [ ] No console window (for GUI version)

### Gumroad Setup

- [ ] Product created
- [ ] Pricing configured
- [ ] Webhook deployed
- [ ] License generation tested
- [ ] Email delivery tested
- [ ] Test purchase completed
- [ ] Test activation successful

---

## Common Issues & Solutions

### Issue: Python backend not found

**Solution:** Check `extraResources` path in `package.json`

### Issue: Installer too large

**Solution:** Exclude dev dependencies, use compression

### Issue: Antivirus blocks installer

**Solution:** Code signing certificate needed

### Issue: License activation fails

**Solution:** Check Supabase connection, verify webhook

---

## Next Steps

1. **Build Electron GUI** - Run the build command
2. **Test installation** - Install on clean system
3. **Setup Gumroad** - Create product and webhook
4. **Test purchase flow** - End-to-end test
5. **Distribute** - Upload to Gumroad/website

---

**Ready to start?** Let's begin with building the Electron GUI!
