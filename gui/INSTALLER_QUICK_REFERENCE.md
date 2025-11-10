# Quick Reference: Installer Features

## For End Users

### Installing

1. Download `AiChemist Transmutation Codex Setup 1.0.0.exe`
2. Double-click to run
3. Follow the installation wizard:
   - Accept license
   - Choose installation directory (optional)
   - Wait for installation to complete
   - Launch the application

### Upgrading

1. Download the new version installer
2. Run the installer
3. Installer will automatically detect your existing installation
4. Click "Yes" to upgrade
5. Your settings and data will be preserved

### Repairing

If the application is corrupted or not working properly:

1. Open **Settings** → **Apps** → **Apps & features**
2. Find **AiChemist Transmutation Codex**
3. Click **Modify** or **Repair**
4. Follow the repair wizard
5. Application files will be restored

### Uninstalling

#### Option 1: Windows Settings
1. Open **Settings** → **Apps** → **Apps & features**
2. Find **AiChemist Transmutation Codex**
3. Click **Uninstall**
4. Choose whether to keep or remove your data

#### Option 2: Start Menu
1. Open **Start Menu**
2. Find **AiChemist Transmutation Codex** folder
3. Click **Uninstall**
4. Follow the uninstallation wizard

## For IT Administrators

### Silent Installation

```powershell
# Install to default location
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe /S

# Install to custom location
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe /S /D=C:\Program Files\AiChemist
```

### Silent Uninstall

```powershell
# Locate uninstaller
$uninstaller = "C:\Users\[Username]\AppData\Local\AiChemist Transmutation Codex\Uninstall AiChemist Transmutation Codex.exe"

# Run silent uninstall (removes all data)
& $uninstaller /S
```

### Registry Check

```powershell
# Check if installed
Test-Path "HKCU:\Software\AiChemist Transmutation Codex"

# Get installed version
(Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").Version

# Get install location
(Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").InstallLocation
```

### Deployment Script

```powershell
# Check if already installed
$installed = Test-Path "HKCU:\Software\AiChemist Transmutation Codex"

if ($installed) {
    $version = (Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").Version
    Write-Host "Version $version is already installed. Upgrading..."
}

# Install or upgrade
.\AiChemist-Transmutation-Codex-Setup-1.0.0.exe /S

# Wait for installation to complete
Start-Sleep -Seconds 30

# Verify installation
$newVersion = (Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex" -ErrorAction SilentlyContinue).Version
if ($newVersion) {
    Write-Host "Installation successful. Version: $newVersion"
} else {
    Write-Error "Installation failed"
}
```

## For Developers

### Building Installer

```bash
cd gui
npm install
npm run electron:build
```

Output: `gui/release/1.0.0/AiChemist Transmutation Codex Setup 1.0.0.exe`

### Testing Installer

```powershell
# Verify installation
.\scripts\Test-Installer.ps1 -Action verify

# Test install process
.\scripts\Test-Installer.ps1 -Action install -InstallerPath "release\1.0.0\AiChemist Transmutation Codex Setup 1.0.0.exe"

# Test upgrade process
.\scripts\Test-Installer.ps1 -Action upgrade -InstallerPath "release\1.0.1\AiChemist Transmutation Codex Setup 1.0.1.exe"

# Run complete test suite
.\scripts\Test-Installer.ps1 -Action all -InstallerPath "release\1.0.0\AiChemist Transmutation Codex Setup 1.0.0.exe"
```

### Configuration

Edit `gui/package.json` → `build.nsis` section:

```json
{
  "nsis": {
    "oneClick": false,              // Allow custom directory
    "allowElevation": true,         // Request elevation if needed
    "createDesktopShortcut": "always",
    "deleteAppDataOnUninstall": false,  // Ask user
    "differentialPackage": true,    // Smaller updates
    "guid": "..."                   // Unique app GUID
  }
}
```

## Troubleshooting

### Windows SmartScreen Warning

**Cause**: Unsigned installer triggers SmartScreen

**Solution**:
- Click "More info" → "Run anyway"
- For production: Code sign the installer

### Installation Fails

**Check**:
1. Disk space available
2. Running as correct user
3. Antivirus not blocking
4. Previous installation completely removed

**Fix**:
```powershell
# Clean registry manually if needed
Remove-Item "HKCU:\Software\AiChemist Transmutation Codex" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AiChemist Transmutation Codex" -Force -ErrorAction SilentlyContinue

# Remove files manually
Remove-Item "$env:LOCALAPPDATA\AiChemist Transmutation Codex" -Recurse -Force -ErrorAction SilentlyContinue
```

### Upgrade Doesn't Detect Existing Version

**Cause**: Registry entries missing or corrupted

**Fix**:
1. Manually uninstall old version
2. Clean registry (see above)
3. Install new version fresh

### Uninstall Leaves Files

**Expected Behavior**: User data is preserved by default when user selects "No" to data removal prompt

**To Remove Completely**:
```powershell
# Remove application files
Remove-Item "$env:LOCALAPPDATA\AiChemist Transmutation Codex" -Recurse -Force

# Remove user data
Remove-Item "$env:APPDATA\AiChemist Transmutation Codex" -Recurse -Force
```

## File Locations

### Application Files
```
C:\Users\[Username]\AppData\Local\AiChemist Transmutation Codex\
```

### User Data
```
C:\Users\[Username]\AppData\Roaming\AiChemist Transmutation Codex\
```

### Shortcuts
```
Desktop: C:\Users\[Username]\Desktop\AiChemist Transmutation Codex.lnk
Start Menu: C:\Users\[Username]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\AiChemist Transmutation Codex\
```

### Registry
```
HKEY_CURRENT_USER\Software\AiChemist Transmutation Codex
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\AiChemist Transmutation Codex
```

## Support

- **Documentation**: See `INSTALLER_FEATURES.md` for detailed information
- **Website**: https://aichemist.app
- **Support**: https://aichemist.app/support
- **GitHub**: https://github.com/savagelysubtle/AiChemistTransmutations

---

**Quick Help Commands**:

```powershell
# Check if installed
Test-Path "HKCU:\Software\AiChemist Transmutation Codex"

# Get version
(Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").Version

# Find uninstaller
$uninstaller = Join-Path (Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").InstallLocation "Uninstall AiChemist Transmutation Codex.exe"

# Open install directory
explorer (Get-ItemProperty "HKCU:\Software\AiChemist Transmutation Codex").InstallLocation
```

