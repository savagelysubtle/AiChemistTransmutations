# Pandoc Bundling and Installation

This document describes how Pandoc is bundled with the production installer for AiChemist Transmutation Codex.

## Overview

Pandoc is required for **Markdown to DOCX** conversion. The production installer automatically:

1. Downloads the Pandoc MSI installer (~30 MB)
2. Bundles it with the application installer
3. Silently installs Pandoc during application installation
4. Adds Pandoc to the system PATH
5. Verifies installation

## For Development

### Quick Install

Run the automated installation script:

```powershell
.\scripts\install_pandoc.ps1
```

This will:

- Try to install via `winget` (Windows Package Manager)
- Fall back to Chocolatey if available
- Provide manual download instructions if both fail

### Manual Installation

**Windows:**

- Download from <https://pandoc.org/installing.html>
- Run the MSI installer (accept defaults)
- Restart your development environment

**macOS:**

```bash
brew install pandoc
```

**Linux:**

```bash
sudo apt-get install pandoc
```

## For Production Builds

### Build Script Integration

The `scripts/build_installer.ps1` automatically:

1. **Downloads Pandoc MSI** (if not present):
   - Version: 3.1.11.1
   - URL: <https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.msi>
   - Saved to: `build/installers/pandoc-3.1.11.1-windows-x86_64.msi`

2. **Copies Pandoc files** from system installation:

   ```
   build/resources/pandoc/
   ├── pandoc.exe              (~100 MB)
   ├── *.dll                   (dependencies)
   ├── data/                   (templates and filters)
   └── COPYRIGHT*              (license files)
   ```

3. **Bundles with PyInstaller**:
   - Files copied to `resources/pandoc/` in the compiled application
   - Runtime hook adds to PATH automatically

### Installer Behavior

The Inno Setup installer (`installer.iss`):

1. **Checks if Pandoc is installed**:
   - `C:\Program Files\Pandoc\pandoc.exe`
   - `C:\Program Files (x86)\Pandoc\pandoc.exe`
   - `%LOCALAPPDATA%\Pandoc\pandoc.exe`
   - Registry: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Pandoc`

2. **Installs if not present**:

   ```
   msiexec.exe /i pandoc-3.1.11.1-windows-x86_64.msi /qn /norestart
   ```

3. **Adds to PATH**:
   - Automatically added by MSI installer
   - Verified and manually added if needed

4. **Shows installation message**:

   ```
   The following components have been installed:
     • Pandoc

   You may need to restart the application for changes to take effect.
   ```

## Runtime PATH Configuration

### Automatic Detection (Production)

The `scripts/runtime_hook_paths.py` automatically:

1. Detects if running as frozen executable
2. Looks for `resources/pandoc/` in `sys._MEIPASS`
3. Prepends to PATH if found
4. Verifies `pandoc.exe` is accessible

### Converter Logic (Development & Production)

The `plugins/markdown/to_docx.py` converter checks locations in this order:

1. **Bundled Pandoc** (production):
   - `sys._MEIPASS/resources/pandoc/pandoc.exe`

2. **System PATH** (both):
   - Uses `where pandoc` (Windows) or `which pandoc` (Unix)

3. **Common locations** (both):
   - `C:\Program Files\Pandoc\pandoc.exe`
   - `C:\Program Files (x86)\Pandoc\pandoc.exe`
   - `%LOCALAPPDATA%\Pandoc\pandoc.exe`
   - `/usr/bin/pandoc` (Linux)
   - `/usr/local/bin/pandoc` (macOS)
   - `/opt/homebrew/bin/pandoc` (macOS Apple Silicon)

## File Size Estimates

**Bundled Files:**

- Pandoc executable: ~100 MB
- Data directory: ~10-20 MB
- **Total bundled size: ~110-120 MB**

**Installer:**

- Pandoc MSI: ~30 MB
- Included in application installer

**Total installer increase: ~30 MB** (MSI only, bundled files are in the main app)

## Testing

### Development Testing

```powershell
# Install Pandoc
.\scripts\install_pandoc.ps1

# Verify installation
where pandoc
pandoc --version

# Test conversion
cd gui
npm run dev
# Try MD to DOCX conversion in GUI
```

### Production Testing

After building with `scripts/build_installer.ps1`:

1. Run the installer
2. Verify Pandoc is installed: `where pandoc`
3. Check PATH includes Pandoc directory
4. Test MD to DOCX conversion in the application

## Troubleshooting

### Pandoc Not Found in Development

**Symptom:** "Pandoc executable not found" error

**Solution:**

```powershell
# Install Pandoc
.\scripts\install_pandoc.ps1

# Verify
where pandoc

# Restart GUI
cd gui
npm run dev
```

### Pandoc Not Found in Production

**Symptom:** MD to DOCX conversion fails

**Solution:**

1. Check if Pandoc is installed: `where pandoc`
2. If not installed, run the installer again
3. Or install manually from <https://pandoc.org/installing.html>
4. Restart the application

### Build Script Fails to Download Pandoc

**Symptom:** Build fails with "Failed to download Pandoc installer"

**Solution:**

```powershell
# Download manually
Invoke-WebRequest -Uri "https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.msi" -OutFile "build\installers\pandoc-3.1.11.1-windows-x86_64.msi"

# Or use browser to download and save to:
# build/installers/pandoc-3.1.11.1-windows-x86_64.msi
```

### Pandoc Version Mismatch

**Symptom:** Different Pandoc version installed

**Solution:** The bundled version (3.1.11.1) and system version can coexist. The bundled version takes priority in production.

## License

Pandoc is licensed under the GPL (General Public License).

- License included in MSI installer
- See: <https://github.com/jgm/pandoc/blob/master/COPYRIGHT>

## Benefits

1. **Zero Configuration**: Pandoc works immediately after installation
2. **Version Control**: Bundled version ensures consistency
3. **Offline Support**: No internet required after initial installer download
4. **Cross-Platform**: Same approach works on Windows/Mac/Linux (with platform-specific installers)
5. **Automatic Updates**: Update Pandoc version by updating the build script URL

## See Also

- [Pandoc Official Website](https://pandoc.org/)
- [Pandoc GitHub Releases](https://github.com/jgm/pandoc/releases)
- [TESSERACT_CONFIGURATION.md](./TESSERACT_CONFIGURATION.md) - Similar setup for Tesseract
- [GHOSTSCRIPT_BUNDLING_INSTALLER.md](./GHOSTSCRIPT_BUNDLING_INSTALLER.md) - Similar setup for Ghostscript



