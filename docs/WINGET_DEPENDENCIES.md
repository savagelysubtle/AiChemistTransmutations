# WinGet-Based Dependency Installation

## Overview

The AiChemist Transmutation Codex installer now uses **Windows Package Manager (winget)** to automatically install all required dependencies. This is much more reliable than Chocolatey and is built into Windows 10/11.

## ✨ What Gets Installed

The installer automatically checks for and installs:

1. **LibreOffice** - For document conversion (DOCX, ODT, etc.)
2. **Tesseract OCR** - For PDF text extraction and OCR features

## 🚀 How It Works

### Installation Flow

```
User runs installer
    ↓
Check if WinGet is available
    ↓
┌─────────────────────┐
│ WinGet Available?   │
└─────────────────────┘
    ├─ YES → Check dependencies
    └─ NO  → Prompt to install WinGet
        ↓
    Check LibreOffice
        ↓
    ┌──────────────────────┐
    │ LibreOffice Installed?│
    └──────────────────────┘
        ├─ YES → Skip
        └─ NO  → Prompt to install
            ↓
        Run: winget install TheDocumentFoundation.LibreOffice
            ↓
    Check Tesseract OCR
        ↓
    ┌──────────────────────┐
    │ Tesseract Installed? │
    └──────────────────────┘
        ├─ YES → Skip
        └─ NO  → Prompt to install
            ↓
        Run: winget install UB-Mannheim.TesseractOCR
            ↓
    Store dependency status in registry
            ↓
    Continue installation
```

## 📦 WinGet Package IDs

| Dependency | WinGet Package ID | Description |
|------------|-------------------|-------------|
| LibreOffice | `TheDocumentFoundation.LibreOffice` | Office suite for document conversion |
| Tesseract OCR | `UB-Mannheim.TesseractOCR` | OCR engine for text extraction |

## 🎯 Benefits Over Chocolatey

### Why WinGet?

✅ **Built into Windows 10/11**
- No separate installation required (usually)
- Part of "App Installer" from Microsoft Store
- Native Windows integration

✅ **More Reliable**
- Official Microsoft tool
- Better package management
- Fewer installation issues
- Silent installation support

✅ **Better Error Handling**
- Clear error codes
- Standardized install behavior
- Automatic dependency resolution

✅ **User-Friendly**
- Simple commands
- Visual progress in terminal
- Works without admin rights (for user installs)

### vs Chocolatey

| Feature | WinGet | Chocolatey |
|---------|--------|------------|
| Built into Windows | ✅ Yes | ❌ No |
| Requires install | ⚠️ Sometimes | ✅ Always |
| Admin required | ❌ No (user mode) | ✅ Often |
| Reliability | ✅ High | ⚠️ Variable |
| Package quality | ✅ Official | ⚠️ Community |
| Install speed | ✅ Fast | ⚠️ Slower |

## 💻 What Happens During Installation

### 1. WinGet Check

**Installer checks:**
```powershell
winget --version
```

**If not found:**
- Prompts user to install from Microsoft Store
- Opens Microsoft Store to "App Installer" page
- User installs, restarts installer

### 2. LibreOffice Check

**Installer checks:**
```powershell
winget list --id TheDocumentFoundation.LibreOffice --exact
```

**If not found:**
- Prompts: "Would you like to install LibreOffice?"
- If YES: Runs `winget install --id TheDocumentFoundation.LibreOffice --silent`
- If NO: Shows warning, continues installation

### 3. Tesseract OCR Check

**Installer checks:**
```powershell
winget list --id UB-Mannheim.TesseractOCR --exact
```

**If not found:**
- Prompts: "Would you like to install Tesseract OCR?"
- If YES: Runs `winget install --id UB-Mannheim.TesseractOCR --silent`
- If NO: Shows warning, continues installation
- Adds Tesseract to user PATH automatically

### 4. Registry Storage

**Stores in registry:**
```
HKCU\Software\AiChemist Transmutation Codex
  - LibreOfficeInstalled: "true"/"false"
  - TesseractInstalled: "true"/"false"
  - TesseractPath: "C:\Program Files\Tesseract-OCR" (if installed)
```

## 📋 User Experience

### Scenario 1: WinGet Available, Nothing Installed

```
Checking for Windows Package Manager (winget)...
✓ WinGet is available: v1.6.3482

--- Checking LibreOffice ---
LibreOffice is not installed

[Prompt] LibreOffice is required for document conversion features.
         Would you like to install it now?
         [Yes] [No]

[User clicks Yes]

Installing LibreOffice via WinGet...
Running: winget install TheDocumentFoundation.LibreOffice
✓ LibreOffice installed successfully

--- Checking Tesseract OCR ---
Tesseract OCR is not installed

[Prompt] Tesseract OCR is required for PDF text extraction features.
         Would you like to install it now?
         [Yes] [No]

[User clicks Yes]

Installing Tesseract OCR via WinGet...
Running: winget install UB-Mannheim.TesseractOCR
✓ Tesseract OCR installed successfully
✓ Added Tesseract to PATH

Dependency check complete
```

### Scenario 2: Everything Already Installed

```
Checking for Windows Package Manager (winget)...
✓ WinGet is available: v1.6.3482

--- Checking LibreOffice ---
✓ LibreOffice is already installed, skipping

--- Checking Tesseract OCR ---
✓ Tesseract OCR is already installed, skipping

Dependency check complete
```

### Scenario 3: WinGet Not Available

```
Checking for Windows Package Manager (winget)...
✗ WinGet is not available

[Prompt] Windows Package Manager (winget) is required to install dependencies.
         Would you like to install it now?
         (This will open the Microsoft Store)
         [Yes] [No]

[User clicks Yes]

[Opens Microsoft Store to "App Installer" page]

[Prompt] Please install 'App Installer' from the Microsoft Store.
         Click OK when installation is complete, then restart this installer.
```

## 🔧 Manual Installation

If users skip automatic installation, they can install manually:

### Install WinGet
1. Open Microsoft Store
2. Search for "App Installer"
3. Install/Update it
4. Restart terminal/PowerShell

### Install LibreOffice
```powershell
winget install TheDocumentFoundation.LibreOffice
```

Or visit: https://www.libreoffice.org/

### Install Tesseract OCR
```powershell
winget install UB-Mannheim.TesseractOCR
```

Or visit: https://github.com/UB-Mannheim/tesseract/wiki

## 📊 Registry Keys

After installation, check dependency status:

```powershell
# Check if LibreOffice is installed
Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -Name "LibreOfficeInstalled"

# Check if Tesseract is installed
Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -Name "TesseractInstalled"

# Get Tesseract path
Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -Name "TesseractPath"
```

## 🎯 For Developers

### Testing the Installer

```powershell
# Build installer with new WinGet integration
cd gui
bun run electron:build

# Test installer
.\release\1.0.3\AiChemist Transmutation Codex Setup 1.0.3.exe
```

### Verifying WinGet Commands

```powershell
# Check if WinGet is available
winget --version

# List installed packages
winget list

# Check specific package
winget list --id TheDocumentFoundation.LibreOffice

# Install package silently
winget install --id TheDocumentFoundation.LibreOffice --silent --accept-source-agreements --accept-package-agreements

# Get package info
winget show --id TheDocumentFoundation.LibreOffice
```

### Adding New Dependencies

To add a new dependency to the installer:

1. **Find WinGet package ID:**
   ```powershell
   winget search "application name"
   ```

2. **Add to `winget-dependencies.nsh`:**
   ```nsis
   !define NEWAPP_WINGET_ID "Publisher.ApplicationName"
   ```

3. **Create detection function:**
   ```nsis
   Function DetectNewAppWinGet
     ; Detection logic here
   FunctionEnd
   ```

4. **Create installation function:**
   ```nsis
   Function InstallNewAppWinGet
     ; Installation logic here
   FunctionEnd
   ```

5. **Add to `InstallAllDependencies`:**
   ```nsis
   Call DetectNewAppWinGet
   ${If} $0 == ""
     Call InstallNewAppWinGet
   ${EndIf}
   ```

## ⚠️ Important Notes

### WinGet Requirements

**Windows Version:**
- Windows 10 1809 (October 2018 Update) or later
- Windows 11 (included by default)

**App Installer:**
- Usually pre-installed
- Available from Microsoft Store
- Must be version 1.11 or later for full functionality

### Installation Behavior

**Silent Installation:**
- All packages install with `--silent` flag
- No user interaction during install
- Progress shown in installer terminal

**User vs System Install:**
- Packages install per-user when possible
- No admin elevation required
- Can be overridden if needed

**PATH Management:**
- Tesseract automatically added to user PATH
- Effective immediately (for new terminals)
- No system PATH modification

### Uninstallation

**Dependencies NOT Removed:**
- LibreOffice remains installed
- Tesseract OCR remains installed
- May be used by other applications

**Manual Removal:**
```powershell
# Remove LibreOffice
winget uninstall TheDocumentFoundation.LibreOffice

# Remove Tesseract
winget uninstall UB-Mannheim.TesseractOCR
```

**Or via Windows Settings:**
- Settings → Apps → Installed apps
- Search for application
- Click ⋮ → Uninstall

## 🚀 Benefits Summary

### For Users
- ✅ One-click installation of all dependencies
- ✅ Reliable, official packages
- ✅ No manual downloads
- ✅ Automatic PATH configuration
- ✅ Clear prompts and messages

### For Developers
- ✅ No Chocolatey installation issues
- ✅ Native Windows integration
- ✅ Easy to test and debug
- ✅ Standardized package IDs
- ✅ Simple to add new dependencies

### For Support
- ✅ Fewer "dependency not found" issues
- ✅ Registry tracking of installations
- ✅ Clear error messages
- ✅ Known package versions

## 📚 References

- **WinGet Documentation**: https://learn.microsoft.com/en-us/windows/package-manager/winget/
- **WinGet Package Repository**: https://github.com/microsoft/winget-pkgs
- **App Installer**: https://apps.microsoft.com/detail/9NBLGGH4NNS1

---

**Last Updated**: November 2025
**Version**: 1.0.3
**Status**: Production Ready ✅

