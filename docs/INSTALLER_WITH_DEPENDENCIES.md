# Complete Installer with Auto-Dependency Setup

**Goal:** User installs once, everything works automatically

---

## Current Situation

Your installer (`AiChemist Transmutation Codex Setup 1.0.0.exe`) includes:

- ✅ Python backend
- ✅ Electron GUI
- ✅ All Python packages

But requires manual setup of:

- ⚠️ Tesseract OCR
- ⚠️ Ghostscript
- ⚠️ Pandoc
- ⚠️ MiKTeX

---

## Ideal Solution

### Option 1: Include Setup Script in Installer (RECOMMENDED)

**What happens:**

1. User runs `AiChemist Setup.exe`
2. User chooses install location
3. Installer copies all files
4. **Installer automatically runs `setup_external_dependencies.ps1`**
5. Script installs all external tools via winget/chocolatey
6. User is ready to go!

**How to implement:**

Update `gui/package.json` to include the setup script:

```json
{
  "build": {
    "extraResources": [
      {
        "from": "../dist/aichemist_transmutation_codex",
        "to": "python-backend",
        "filter": ["**/*"]
      },
      {
        "from": "../scripts/setup",
        "to": "setup-scripts",
        "filter": ["setup_external_dependencies.ps1", "*.ps1"]
      }
    ],
    "nsis": {
      "oneClick": false,
      "allowElevation": true,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "AiChemist",
      "license": "../LICENSE",
      "perMachine": false,
      "runAfterFinish": true,
      "include": "installer-script.nsh"  // Custom NSIS script
    }
  }
}
```

Create `gui/installer-script.nsh`:

```nsis
; Custom NSIS installer script
; Run dependency setup after installation

Section "Install Dependencies" SEC_DEPS
  SetOutPath "$INSTDIR\resources\setup-scripts"

  ; Ask user if they want to install dependencies now
  MessageBox MB_YESNO "Install required dependencies (Tesseract, Ghostscript, Pandoc)?$\n$\nThis will use winget or chocolatey to install external tools." IDYES install_deps IDNO skip_deps

  install_deps:
    DetailPrint "Installing external dependencies..."
    ExecWait 'powershell.exe -ExecutionPolicy Bypass -File "$INSTDIR\resources\setup-scripts\setup_external_dependencies.ps1"'
    Goto done

  skip_deps:
    DetailPrint "Skipping dependency installation"
    MessageBox MB_OK "You can install dependencies later by running:$\n$INSTDIR\resources\setup-scripts\setup_external_dependencies.ps1"

  done:
SectionEnd
```

**Pros:**

- ✅ User installs once, everything works
- ✅ Professional experience
- ✅ Can skip if dependencies already installed

**Cons:**

- ⚠️ Requires NSIS customization (advanced)
- ⚠️ Installer size stays same (scripts are small)

---

### Option 2: First-Launch Setup (EASIER - RECOMMENDED FOR NOW)

**What happens:**

1. User installs app
2. On **first launch**, app checks for dependencies
3. If missing, shows dialog: "Install required tools?"
4. User clicks "Install"
5. App runs PowerShell script in background
6. Shows progress
7. When done, app is ready!

**How to implement:**

Add to `gui/src/main/main.ts`:

```typescript
import { spawn } from 'child_process';
import path from 'path';

// Check dependencies on first launch
async function checkAndInstallDependencies() {
  const setupScript = path.join(
    process.resourcesPath,
    'setup-scripts',
    'setup_external_dependencies.ps1'
  );

  const { dialog } = require('electron');

  // Check if already installed (check for specific files)
  const tesseractExists = fs.existsSync('C:\\Program Files\\Tesseract-OCR\\tesseract.exe');

  if (!tesseractExists) {
    const result = await dialog.showMessageBox({
      type: 'question',
      buttons: ['Install Now', 'Skip', 'Remind Me Later'],
      defaultId: 0,
      title: 'Install Required Tools',
      message: 'AiChemist needs external tools for full functionality',
      detail: 'This will install:\n• Tesseract OCR (required)\n• Ghostscript (required)\n• Pandoc (optional)\n• MiKTeX (optional)\n\nEstimated time: 5-10 minutes'
    });

    if (result.response === 0) {
      // Install now
      const install = spawn('powershell.exe', [
        '-ExecutionPolicy', 'Bypass',
        '-File', setupScript
      ]);

      // Show progress window
      // (implementation details...)
    }
  }
}

app.whenReady().then(() => {
  createWindow();
  checkAndInstallDependencies();
});
```

**Pros:**

- ✅ Easy to implement (JavaScript only)
- ✅ User can skip or defer
- ✅ Works with current build
- ✅ No NSIS customization needed

**Cons:**

- ⚠️ Dependency check happens after install (not during)

---

### Option 3: Manual (Current Approach)

**What happens:**

1. User installs app
2. User tries to convert
3. Conversion fails (missing Tesseract)
4. App shows error: "Please install Tesseract"
5. User manually runs setup script
6. User retries conversion

**How to guide users:**

In your `docs/USER_GUIDE.md`, add:

```markdown
## First Time Setup

After installation, run this command to install required tools:

**Option A - From Start Menu:**
1. Open Start Menu
2. Search "AiChemist"
3. Right-click → "Open file location"
4. Navigate to resources/setup-scripts
5. Right-click setup_external_dependencies.ps1
6. "Run with PowerShell"

**Option B - From PowerShell:**
```powershell
cd "C:\Program Files\AiChemist Transmutation Codex\resources\setup-scripts"
powershell -ExecutionPolicy Bypass -File setup_external_dependencies.ps1
```

This will automatically install:

- Tesseract OCR (required for PDF OCR)
- Ghostscript (required for PDF operations)
- Pandoc (optional, for DOCX conversions)
- MiKTeX (optional, for LaTeX)

```

**Pros:**
- ✅ Works right now
- ✅ No code changes needed

**Cons:**
- ⚠️ Extra step for users
- ⚠️ Less professional
- ⚠️ Many users will skip it

---

## Recommendation

**For your FIRST LAUNCH (this week):**

Use **Option 3 (Manual)** because:
- ✅ Your installer is ready NOW
- ✅ You can launch immediately
- ✅ Add better solution in v1.1

**Include in documentation:**
- Clear setup instructions
- Troubleshooting for missing dependencies
- Link to setup script

**For v1.1 (next month):**

Upgrade to **Option 2 (First-Launch Setup)**:
- Add dependency check on first app launch
- Show friendly dialog
- Auto-run setup script
- Better user experience

**For v2.0 (future):**

Ultimate solution with **Option 1 (NSIS customization)**:
- Everything installs automatically
- Professional one-click experience
- No user action needed

---

## Quick Implementation (Option 2 - First Launch)

I can help you add this to your current app. It requires:

1. **Copy setup script to resources** (add to `package.json`)
2. **Add dependency check** (in `main.ts`)
3. **Show install dialog** (Electron dialog)
4. **Run PowerShell script** (child_process)
5. **Show progress** (window with output)

Estimated time: 1-2 hours of development

Would you like me to implement this?

---

## Your Installers

**Current Location:**
```

D:\Coding\AiChemistCodex\AiChemistTransmutations\gui\release\1.0.0\
├── AiChemist Transmutation Codex Setup 1.0.0.exe  (176 MB) ← Use this
└── AiChemist Transmutation Codex 1.0.0.exe        (176 MB) ← Portable

```

**What to do NOW:**

1. **Test your current installer** on clean Windows
2. **Manually run setup script** after install
3. **Document the process** in user guide
4. **Launch with manual setup**
5. **Plan automatic setup** for v1.1

---

## Bottom Line

**Your installers are READY to distribute!**

They just need users to run the setup script after installation. This is **acceptable for launch** - many professional apps do this (Docker, VS Code extensions, etc.).

You can improve it after launch based on user feedback.

**Launch NOW, iterate later!** 🚀

