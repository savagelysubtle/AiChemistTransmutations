# AiChemist Transmutation Codex - Installer Features

## Overview

The AiChemist Transmutation Codex installer now includes comprehensive installation, upgrade, repair, and uninstallation features powered by NSIS (Nullsoft Scriptable Install System).

## Features

### 🎯 Installation Features

- **Custom Installation Directory**: Users can choose where to install the application
- **Desktop Shortcut**: Automatically creates a desktop shortcut (configurable)
- **Start Menu Integration**: Adds shortcuts to Windows Start Menu with organized menu category
- **License Agreement**: Displays Apache 2.0 license during installation
- **Elevation Support**: Requests admin privileges when needed for system-wide installation
- **Progress Tracking**: Shows detailed installation progress with file operations

### 🔄 Upgrade Features

- **Automatic Upgrade Detection**: Installer detects existing installations automatically
- **Version Comparison**: Compares installed version with new version
- **In-Place Upgrades**: Updates application without losing user data or settings
- **Differential Updates**: Only downloads and installs changed files (smaller update size)
- **Settings Preservation**: All user configurations and data are preserved during upgrades
- **Auto-Update Support**: Built-in support for electron-updater for automatic updates

### 🔧 Repair Features

The Windows Add/Remove Programs entry includes a "Repair" button that allows users to:

- **Fix Corrupted Files**: Reinstall application files without losing data
- **Restore Missing Shortcuts**: Recreate desktop and Start Menu shortcuts
- **Registry Repair**: Restore registry entries and file associations
- **Non-Destructive**: User data and settings remain intact during repair

### 🗑️ Uninstallation Features

- **Clean Uninstallation**: Removes all application files and registry entries
- **User Data Options**: Prompts user to choose whether to keep or remove:
  - Application settings
  - User preferences
  - Log files
  - Cache data
- **Shortcut Removal**: Automatically removes desktop and Start Menu shortcuts
- **Registry Cleanup**: Removes all registry entries created during installation
- **Silent Uninstall**: Supports silent uninstallation with `/S` flag for automated scenarios

## Windows Add/Remove Programs Integration

The installer registers the application with Windows Add/Remove Programs with the following information:

- **Display Name**: AiChemist Transmutation Codex
- **Publisher**: AiChemist
- **Version**: Current application version
- **Installation Location**: Full path to installation directory
- **Estimated Size**: Calculated disk space usage
- **Uninstall String**: Path to uninstaller
- **Modify/Repair**: Enabled for fixing corrupted installations
- **Support Links**:
  - Website: https://aichemist.app
  - Help/Support: https://aichemist.app/support
  - Updates: https://aichemist.app/updates

## Installation Options

### Standard Installation

```powershell
# Run the installer
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe
```

Users will see:
1. Welcome screen
2. License agreement
3. Installation directory selection
4. Installation progress
5. Completion screen with option to launch the application

### Silent Installation

For automated deployments:

```powershell
# Silent install with default options
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe /S

# Silent install to custom directory
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe /S /D=C:\CustomPath\AiChemist
```

### Upgrade Process

When a new version is installed over an existing version:

1. Installer detects existing installation
2. Prompts user to confirm upgrade
3. Closes running application instances
4. Updates files in-place
5. Preserves all user data and settings
6. Updates registry entries with new version
7. Completes with option to launch new version

### Uninstallation Process

#### Interactive Uninstall

```powershell
# From Start Menu
Start Menu → AiChemist Transmutation Codex → Uninstall

# From Add/Remove Programs
Settings → Apps → AiChemist Transmutation Codex → Uninstall

# Direct uninstaller execution
"C:\Users\[Username]\AppData\Local\AiChemist Transmutation Codex\Uninstall AiChemist Transmutation Codex.exe"
```

#### Silent Uninstall

```powershell
# Silent uninstall, removes everything including user data
"C:\Users\[Username]\AppData\Local\AiChemist Transmutation Codex\Uninstall AiChemist Transmutation Codex.exe" /S

# Note: Silent uninstall will remove ALL data without prompting
```

## Auto-Update Support

The installer is configured to work with electron-updater for automatic updates:

- **Update Server**: https://aichemist.app/releases
- **Update Check**: Application checks for updates on startup
- **Update Download**: Downloads updates in background
- **Update Installation**: Prompts user to install when ready
- **Differential Updates**: Only downloads changed files
- **Rollback Support**: Can revert to previous version if update fails

## Registry Entries

The installer creates the following registry entries:

### Application Registry

```
HKEY_CURRENT_USER\Software\AiChemist Transmutation Codex
  - InstallLocation: [Installation Directory]
  - Version: [Version Number]
  - InstallDate: [Installation Timestamp]
```

### Uninstall Registry

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\AiChemist Transmutation Codex
  - DisplayName: AiChemist Transmutation Codex
  - DisplayVersion: [Version]
  - Publisher: AiChemist
  - DisplayIcon: [Path to icon]
  - UninstallString: [Path to uninstaller]
  - QuietUninstallString: [Path to uninstaller with /S flag]
  - ModifyPath: [Path to application for repair]
  - InstallLocation: [Installation directory]
  - EstimatedSize: [Size in KB]
  - URLInfoAbout: https://aichemist.app
  - HelpLink: https://aichemist.app/support
  - URLUpdateInfo: https://aichemist.app/updates
  - NoModify: 0 (Modify button enabled)
  - NoRepair: 0 (Repair button enabled)
```

## File Locations

### Installation Directory (Default)

```
C:\Users\[Username]\AppData\Local\AiChemist Transmutation Codex\
├── AiChemist Transmutation Codex.exe
├── resources\
│   ├── app.asar
│   └── python-backend\
├── locales\
├── logs\
└── Uninstall AiChemist Transmutation Codex.exe
```

### User Data Directory

```
C:\Users\[Username]\AppData\Roaming\AiChemist Transmutation Codex\
├── config.json
├── preferences.json
└── cache\
```

## Building the Installer

To build the installer with all these features:

```bash
# Navigate to GUI directory
cd gui

# Install dependencies
npm install

# Build the application and installer
npm run electron:build

# Output will be in: gui/release/[version]/
```

## Troubleshooting

### Installer Won't Start

- Check Windows SmartScreen settings
- Run as Administrator
- Temporarily disable antivirus

### Upgrade Fails

- Close all running instances of the application
- Try manual uninstall then fresh install
- Check disk space availability

### Uninstall Leaves Files

- Some user data may be preserved by design
- Manually delete: `%LOCALAPPDATA%\AiChemist Transmutation Codex`
- Manually delete: `%APPDATA%\AiChemist Transmutation Codex`

### Repair Doesn't Fix Issue

- Try complete uninstall and reinstall
- Check event logs: `%LOCALAPPDATA%\AiChemist Transmutation Codex\logs`
- Contact support at https://aichemist.app/support

## Security Considerations

- **Code Signing**: Installer should be code-signed for production releases
- **SmartScreen**: Unsigned installers will trigger Windows SmartScreen warnings
- **Elevation**: Only requests elevation when absolutely necessary
- **User-Level Install**: Default installation doesn't require admin privileges

## Developer Notes

### Configuration Location

All installer configuration is in `gui/package.json` under the `build.nsis` section.

### Key Configuration Options

```json
{
  "nsis": {
    "oneClick": false,           // Allow custom install directory
    "allowElevation": true,      // Request elevation if needed
    "deleteAppDataOnUninstall": false,  // Prompt user about data
    "packElevateHelper": true,   // Include elevation helper
    "differentialPackage": true, // Enable differential updates
    "guid": "c3e3c3f3-3c3e-4c3e-8c3e-3c3e3c3e3c3e"  // Unique app GUID
  }
}
```

### Testing Upgrades

1. Build and install version 1.0.0
2. Update version in package.json to 1.0.1
3. Build new installer
4. Run new installer - should detect and upgrade

### Testing Repair

1. Install application
2. Delete some application files (not in user data)
3. Go to Add/Remove Programs → Modify/Repair
4. Files should be restored

## Support

For issues, questions, or feedback:

- **Website**: https://aichemist.app
- **Support**: https://aichemist.app/support
- **GitHub**: https://github.com/savagelysubtle/AiChemistTransmutations

---

**Last Updated**: November 2025
**Version**: 1.0.0

