# Bundling Ghostscript Installer with Production App

## Overview

This guide explains how the Ghostscript installer is bundled with your production installer, so users get a complete, zero-configuration installation experience.

## How It Works

### 1. **Ghostscript Installer is Downloaded**

The `build_installer.ps1` script automatically downloads the Ghostscript installer:

```powershell
# Downloads gs10.04.0-win64.exe (~40 MB) to build/installers/
.\scripts\build_installer.ps1 -Version "1.0.0"
```

### 2. **Inno Setup Bundles It**

The Inno Setup script (`installer.iss`) includes the Ghostscript installer:

```ini
[Files]
; Ghostscript installer (bundled for automatic installation)
Source: "build\installers\gs10.04.0-win64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
```

### 3. **Silent Installation During Setup**

When users install your app, Ghostscript is automatically installed:

```ini
[Run]
; Install Ghostscript silently (if not already installed)
Filename: "{tmp}\gs10.04.0-win64.exe";
Parameters: "/S /D=C:\Program Files\gs\gs10.04.0";
StatusMsg: "Installing Ghostscript...";
Flags: waituntilterminated;
Check: not GhostscriptInstalled
```

### 4. **PATH is Configured Automatically**

After installation, the Inno Setup script adds Ghostscript to the user's PATH:

```pascal
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    AddToPath('C:\Program Files\gs\gs10.04.0\bin');
    MsgBox('Ghostscript has been installed and added to your PATH.');
  end;
end;
```

## User Experience

### Without Bundling (Old Way)

```
1. User installs your app
2. User tries PDF to Editable ❌
3. Error: "Ghostscript not found"
4. User googles error
5. User downloads Ghostscript manually
6. User installs Ghostscript
7. User configures PATH manually (maybe)
8. User restarts app
9. Maybe it works now ❓
```

### With Bundling (New Way)

```
1. User installs your app
   ↓
   (Ghostscript installs automatically)
   (PATH configured automatically)
   ↓
2. User tries PDF to Editable ✅
3. It works immediately! 🎉
```

## Build Process

### Step 1: Run Build Script

```powershell
.\scripts\build_installer.ps1 -Version "1.0.0"
```

**What happens:**

- ✅ Downloads Ghostscript installer to `build/installers/`
- ✅ Copies Tesseract from system installation
- ✅ Prepares resources for PyInstaller

### Step 2: Build with PyInstaller

```powershell
pyinstaller transmutation_codex.spec --clean
```

**What happens:**

- ✅ Creates standalone executable
- ✅ Bundles Tesseract resources
- ✅ Includes runtime hook for PATH configuration

### Step 3: Create Installer

```powershell
iscc installer.iss
```

**What happens:**

- ✅ Creates Windows installer
- ✅ Bundles Ghostscript installer
- ✅ Configures silent installation
- ✅ Adds PATH configuration

### Output

```
dist/installer/AiChemistSetup_1.0.0.exe
```

**Installer includes:**

- Your application (~50 MB)
- Bundled Tesseract (~40 MB)
- Ghostscript installer (~40 MB)
- **Total: ~130 MB**

## Smart Installation Logic

### Ghostscript Already Installed

If the user already has Ghostscript, it won't reinstall:

```pascal
function GhostscriptInstalled(): Boolean;
begin
  Result := FileExists('C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe');
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\GPL Ghostscript\10.04', 'GS_DLL', GsPath);
end;
```

### Silent Installation

Ghostscript installs silently in the background:

- No user interaction required
- No separate installer windows
- Installs to standard location
- Configures PATH automatically

## Testing

### Test the Build Process

```powershell
# Build everything
.\scripts\build_installer.ps1 -Version "1.0.0"
pyinstaller transmutation_codex.spec --clean
iscc installer.iss

# Test the installer on a clean VM
.\dist\installer\AiChemistSetup_1.0.0.exe
```

### Verify Ghostscript Installation

After running your installer, check:

```powershell
# Ghostscript should be installed
Test-Path "C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe"
# Should return: True

# Ghostscript should be in PATH
where.exe gswin64c
# Should show: C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe

# Ghostscript should work
gswin64c --version
# Should show: GPL Ghostscript 10.04.0
```

## Troubleshooting

### Issue: Ghostscript installer download fails

**Solution:** Download manually and place in `build/installers/`:

```powershell
# Download URL
https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10040/gs10.04.0-win64.exe

# Save to
build/installers/gs10.04.0-win64.exe
```

### Issue: Silent installation fails

**Cause:** User doesn't have admin rights

**Solution:** Modify `installer.iss`:

```ini
[Setup]
PrivilegesRequired=admin  ; Ensure admin rights
```

### Issue: PATH not updated

**Cause:** User needs to restart applications

**Solution:** Show message after installation:

```pascal
MsgBox('Installation complete!' + #13#10 +
       'Please restart any running applications to use Ghostscript.',
       mbInformation, MB_OK);
```

## Licensing

### Ghostscript License

**License:** AGPL 3.0 (GNU Affero General Public License)

**What this means:**

- ✅ Free to bundle and distribute
- ✅ Can include in commercial software IF:
  - You provide source code to users (AGPL requirement)
  - OR you purchase a commercial license from Artifex

**Options:**

1. **Open Source:** Make your app AGPL-compliant (provide source)
2. **Commercial:** Purchase Ghostscript commercial license (~$10K/year)
3. **Don't Bundle:** Let users install Ghostscript separately

**Recommended for closed-source commercial software:**

- Purchase commercial license from Artifex
- OR don't bundle (users install separately)

### License Files

Include Ghostscript license in your installer:

```ini
[Files]
Source: "build\resources\ghostscript\LICENSE";
DestDir: "{app}\licenses";
DestName: "GHOSTSCRIPT_LICENSE.txt";
Flags: ignoreversion
```

## Benefits

### For Users

- ✅ One-click installation
- ✅ Zero configuration
- ✅ Works immediately
- ✅ Professional experience

### For You

- ✅ Fewer support tickets
- ✅ Better reviews
- ✅ Higher user satisfaction
- ✅ Less troubleshooting

## Alternatives

### Option 1: Don't Bundle (Simpler Licensing)

**Pros:**

- No AGPL licensing concerns
- Smaller installer size

**Cons:**

- Users must install Ghostscript manually
- More support tickets
- Lower user satisfaction

**Implementation:**

- Remove Ghostscript installer from `installer.iss`
- Show helpful error when Ghostscript missing
- Provide installation instructions

### Option 2: Bundle with Commercial License

**Pros:**

- Fully compliant
- Best user experience
- No licensing concerns

**Cons:**

- Annual licensing cost
- Must maintain license agreement

**Implementation:**

- Purchase commercial license from Artifex
- Bundle as described in this document
- Include commercial license file

## Summary

**What you get:**

1. ✅ Automatic Ghostscript installation
2. ✅ Automatic PATH configuration
3. ✅ Zero user configuration
4. ✅ Professional installer experience

**Trade-offs:**

- Larger installer size (~130 MB vs ~90 MB)
- AGPL licensing considerations
- One-time setup complexity

**Result:** Users install your app and PDF to Editable conversion works immediately with zero configuration! 🚀

## Quick Commands Reference

```powershell
# Build production installer with bundled Ghostscript
.\scripts\build_installer.ps1 -Version "1.0.0"
pyinstaller transmutation_codex.spec --clean
iscc installer.iss

# Output
dist/installer/AiChemistSetup_1.0.0.exe

# Test on clean VM
.\dist\installer\AiChemistSetup_1.0.0.exe

# Verify Ghostscript
where.exe gswin64c
gswin64c --version
```

---

**Status:** ✅ Complete bundling solution ready for production!
