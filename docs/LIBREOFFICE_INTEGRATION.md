# LibreOffice Integration in Installer

## Overview

The AiChemist Transmutation Codex installer now includes automatic LibreOffice detection and installation. LibreOffice is required for converting DOCX, ODT, and other office document formats to PDF.

## Features

### 1. Automatic Detection ✅

The installer automatically detects if LibreOffice is already installed on your system by checking:

- System-wide installations (HKLM registry)
- User installations (HKCU registry)
- Common installation paths (`Program Files`, `Program Files (x86)`)
- 32-bit installations on 64-bit systems (WOW64 registry)

If LibreOffice is found, the installer skips the installation step and displays the detected version.

### 2. Download & Install ✅

If LibreOffice is not detected, the installer:

1. **Prompts the user**: "Would you like to download and install LibreOffice now?"
2. **Downloads**: Latest stable version (LibreOffice 24.8.3) from official source (~300MB)
3. **Installs**: Runs the LibreOffice MSI installer with optimized settings:
   - Passive mode (shows progress, minimal interaction)
   - No desktop link creation
   - No file type registration (to avoid conflicts)
   - User-level installation (no admin rights required)

### 3. User Choice ✅

Users can choose to:

- **Install Now**: Download and install LibreOffice during setup
- **Skip**: Continue without LibreOffice (with warning about limited functionality)
- **Install Later**: Manual installation from https://www.libreoffice.org/download/

## Installation Flow

```
AiChemist Installer Starts
    ↓
Detect LibreOffice
    ↓
┌─────────────────────┐
│ LibreOffice Found?  │
└─────────────────────┘
    ├─ YES → Skip installation, store version info
    │
    └─ NO  → Prompt user
              ├─ Install Now → Download → Install → Store status
              └─ Skip → Continue with warning
```

## Registry Integration

The installer stores LibreOffice status in the registry:

```
HKCU\Software\AiChemist Transmutation Codex
  - LibreOfficeInstalled: "true" | "false"
  - LibreOfficeVersion: "24.8.3" (if installed)
```

This allows the application to check LibreOffice availability at runtime.

## Installation Options

### Silent Mode

LibreOffice is installed in passive mode, which:
- Shows installation progress
- Requires minimal user interaction
- Allows cancellation
- Provides error feedback

### Custom Settings

The installer uses these MSI properties:
- `ALLUSERS=2`: Per-user installation (doesn't require admin)
- `CREATEDESKTOPLINK=0`: No desktop shortcut
- `REGISTER_ALL_MSO_TYPES=0`: Don't override Office file associations

## Error Handling

The installer handles common errors:

| Error Code | Meaning | Action |
|------------|---------|--------|
| 0 | Success | Installation complete |
| 1602 | User cancelled | Show manual download link |
| 1618 | Another installation in progress | Warn user, show manual link |
| 3010 | Restart required | Inform user of restart need |
| Other | Installation failed | Show error code and manual link |

## Download Information

**LibreOffice Version**: 24.8.3 (latest stable)
**Download Size**: ~300MB
**Source**: https://download.documentfoundation.org/
**Download Location**: `%TEMP%\LibreOffice_24.8.3_Win_x86-64.msi`

The installer file is automatically deleted after installation.

## User Messages

### LibreOffice Already Installed
```
LibreOffice is already installed on your system.

Version: 24.8.3

All document conversion features are available.
```

### LibreOffice Not Found - Install Prompt
```
AiChemist Transmutation Codex requires LibreOffice for document conversion features.

LibreOffice was not detected on your system.

Would you like to download and install it now?
```

### Installation Skipped
```
LibreOffice installation skipped.

Note: Some document conversion features (DOCX, ODT, etc.) will not work without LibreOffice.

You can install it later from:
https://www.libreoffice.org/download/
```

### Installation Successful
```
LibreOffice has been installed successfully!
```

### Download Failed
```
Failed to download LibreOffice.

Some document conversion features may not work.

You can install LibreOffice manually from:
https://www.libreoffice.org/download/
```

## Uninstallation

When uninstalling AiChemist Transmutation Codex:

- **LibreOffice is NOT removed** (it may be used by other applications)
- Registry keys for LibreOffice status are removed
- User is notified that LibreOffice remains installed

## Manual Installation

If users skip the automatic installation, they can install LibreOffice manually:

1. Visit https://www.libreoffice.org/download/
2. Download the Windows installer
3. Run the installer
4. Restart AiChemist Transmutation Codex

The application will automatically detect the new installation on next launch.

## Testing

### Test Scenarios

1. **Fresh System (no LibreOffice)**
   - Installer should prompt to install
   - Download should work
   - Installation should complete

2. **LibreOffice Already Installed**
   - Installer should detect and skip
   - Version should be displayed
   - No download/install prompts

3. **User Skips Installation**
   - Warning message should display
   - Installation should continue
   - Registry should show "false"

4. **Download Fails (no internet)**
   - Error message should display
   - Manual installation link provided
   - Installation should continue

5. **Installation Cancelled by User**
   - Cancellation acknowledged
   - Manual installation link provided
   - Installation should continue

### Testing Commands

```powershell
# Test fresh installation
.\gui\scripts\Test-Installer.ps1 -Action install -InstallerPath "release\1.0.2\AiChemist Transmutation Codex Setup 1.0.2.exe"

# Check LibreOffice detection
Test-Path "HKLM:\Software\LibreOffice\LibreOffice"
Test-Path "HKCU:\Software\LibreOffice\LibreOffice"

# Check registry status after installation
Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -Name "LibreOfficeInstalled"
Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -Name "LibreOfficeVersion"
```

## Troubleshooting

### Download Very Slow
- LibreOffice is ~300MB, download time depends on internet speed
- Progress is shown during download
- User can cancel and install manually later

### Installation Fails
- Check antivirus (may block MSI installation)
- Check disk space (~1GB required for LibreOffice)
- Check Windows Installer service is running
- Try manual installation from libreoffice.org

### Detection Fails (LibreOffice installed but not detected)
- Check if LibreOffice is in non-standard location
- Try reinstalling LibreOffice from libreoffice.org
- Check registry keys exist (see testing commands)

## Benefits

### For Users:
- ✅ One-click setup - everything they need
- ✅ Automatic detection avoids duplicate installs
- ✅ Clear messages about what's happening
- ✅ Choice to install now or later
- ✅ No manual dependency hunting

### For Support:
- ✅ Fewer "it doesn't work" tickets
- ✅ Registry tracking of LibreOffice status
- ✅ Clear error messages for troubleshooting
- ✅ Users understand what's required

### For Developers:
- ✅ Modular NSIS scripts
- ✅ Easy to update LibreOffice version
- ✅ Proper error handling
- ✅ Registry integration for runtime checks

## Updating LibreOffice Version

To update to a newer LibreOffice version:

1. Edit `gui/installer-scripts/libreoffice.nsh`
2. Update these constants:
   ```nsis
   !define LIBREOFFICE_URL "https://download.documentfoundation.org/..."
   !define LIBREOFFICE_FILENAME "LibreOffice_X.Y.Z_Win_x86-64.msi"
   !define LIBREOFFICE_VERSION "X.Y"
   ```
3. Rebuild the installer
4. Test on clean system

## Security Considerations

- Downloads from official LibreOffice source only
- MSI signature verification by Windows Installer
- No elevation required (user-level install)
- Downloaded file deleted after installation
- No code execution from untrusted sources

## License Compliance

- LibreOffice is open source (Mozilla Public License v2.0)
- AiChemist Transmutation Codex can bundle/download it freely
- No licensing conflicts or fees
- Users must accept LibreOffice license during installation

---

**Last Updated**: November 2025
**LibreOffice Version**: 24.8.3
**Integration Status**: Fully Functional ✅


