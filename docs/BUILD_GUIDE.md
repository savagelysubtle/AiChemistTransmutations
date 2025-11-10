# Build Full Application - Complete Guide

## Overview

Building the AiChemist Transmutation Codex application involves two main
components:

1. **Python Backend** - Built with `uv`
2. **Electron GUI** - Built with `electron-builder`

## Quick Start

### Using VS Code Tasks (Recommended)

1. Press `Ctrl+Shift+P`
2. Type "Run Task"
3. Select **"Build: Full Application"**

This runs both backend and frontend builds in sequence.

### Using Command Line

```powershell
# From project root

# 1. Build Python backend
uv build --wheel --out-dir dist

# 2. Build Electron installer (from gui directory)
cd gui
.\scripts\build-robust.ps1
```

## Build Tasks Reference

| Task                                 | Description              | Time     | Output             |
| ------------------------------------ | ------------------------ | -------- | ------------------ |
| **Build: Full Application**          | Builds Python + Electron | ~2-3 min | Complete installer |
| **Build: Python Backend**            | Builds wheel only        | ~30 sec  | `dist/*.whl`       |
| **Build: Electron Installer**        | Standard electron build  | ~2 min   | `gui/release/`     |
| **Build: Electron Installer (Safe)** | Uses robust script       | ~2 min   | `gui/release/`     |

## Prerequisites

### Required Software

- **Python 3.13+** with `uv` package manager
- **Node.js 18+** with `npm` or `bun`
- **Windows SDK** (for building Windows installers)

### External Dependencies (Bundled in Installer)

- **Tesseract OCR** (for PDF OCR)
- **Ghostscript** (for PDF processing)
- **Pandoc** (for document conversion)
- **MiKTeX** (optional, for advanced LaTeX support)

These are automatically bundled by the main build script at
`scripts/build/build_installer.ps1`.

## Build Scripts

### Python Backend

```powershell
# Standard build
uv build --wheel --out-dir dist

# Build with specific version
uv build --wheel --out-dir dist --project aichemist-transmutation-codex==1.0.3
```

**Output:** `dist/aichemist_transmutation_codex-*.whl`

### Electron GUI

#### Option 1: Standard Build (May have file locks)

```powershell
cd gui
npm run electron:build
# or
bun run electron:build
```

#### Option 2: Robust Build (Handles file locks)

```powershell
cd gui
.\scripts\build-robust.ps1
```

#### Option 3: Safe Build (Basic cleanup)

```powershell
cd gui
.\scripts\build-safe.ps1
```

**Output:** `gui/release/1.0.3/`

- `AiChemist Transmutation Codex Setup 1.0.3.exe` (NSIS installer)
- `AiChemist Transmutation Codex 1.0.3.exe` (Portable)
- `win-unpacked/` (Unpacked application)

## Common Build Issues

### Issue: "The process cannot access the file because it is being used by another process"

**Cause:** Windows Defender, VS Code/Cursor, or other processes locking files in
the `release` directory.

**✅ CONFIRMED FIX:** **Close Cursor/VS Code completely before building**

This is the most reliable solution. Cursor's file watcher locks files in the
release directory even with exclusions configured.

**Quick Solution:**

1. Close Cursor/VS Code
2. Open PowerShell
3. Build:
   ```powershell
   cd D:\Coding\AiChemistCodex\AiChemistTransmutations\gui
   npm run electron:build
   ```

**Alternative Solutions:** See [BUILD_ISSUES.md](./BUILD_ISSUES.md) for
comprehensive solutions including Windows Defender exclusions and retry scripts.

### Issue: Missing or incorrect icons in built application

**Symptoms:** Default Electron icon appears, or browser console shows 404 errors
for favicon files.

**Solution:**

1. Generate all required icon files:
   ```powershell
   npm run generate-all-icons
   ```
2. Rebuild application:
   ```powershell
   npm run electron:build
   ```

**What this creates:**

- `icon.ico` - Windows application icon
- `favicon-16x16.png` - Small browser favicon
- `favicon-32x32.png` - Standard browser favicon
- `icon-256x256.png` - Apple Touch icon
- `icon-512x512.png` - High-resolution icon

See [ICON_FIX_COMPLETE.md](./ICON_FIX_COMPLETE.md) for details.

### Issue: Build succeeds but installer doesn't work

**Symptoms:** Installer launches but app doesn't run, or missing dependencies.

**Solutions:**

1. **Check Python backend is built:**

   ```powershell
   # From project root
   ls dist/*.whl
   ```

   Should see: `aichemist_transmutation_codex-1.0.3-py3-none-any.whl`

2. **Verify external dependencies are bundled:** The full installer script
   bundles Tesseract, Ghostscript, and Pandoc. Use:

   ```powershell
   cd scripts\build
   .\build_installer.ps1
   ```

3. **Test on clean machine:** Copy installer to a machine without dev tools and
   test.

### Issue: Build is very slow

**Cause:** Antivirus scanning, file watchers, or large node_modules.

**Solutions:**

1. Add Windows Defender exclusions (see above)
2. Close VS Code during build
3. Use `--no-cache` flag:
   ```powershell
   npm run electron:build -- --no-cache
   ```

### Issue: Out of memory during build

**Symptoms:** Build crashes with heap memory errors.

**Solutions:**

1. Increase Node.js memory:

   ```powershell
   $env:NODE_OPTIONS="--max-old-space-size=4096"
   npm run electron:build
   ```

2. Close other applications
3. Build on machine with 8GB+ RAM

## Build Configuration

### Python (pyproject.toml)

```toml
[project]
name = "aichemist-transmutation-codex"
version = "1.0.3"
requires-python = ">=3.13"

[build-system]
requires = ["uv_build>=0.9.4,<0.10.0"]
build-backend = "uv_build"
```

### Electron (package.json)

```json
{
  "name": "aichemist-transmutation-codex",
  "version": "1.0.3",
  "build": {
    "appId": "com.aichemist.transmutationcodex",
    "productName": "AiChemist Transmutation Codex",
    "win": {
      "target": ["nsis", "portable"]
    }
  }
}
```

## Build Artifacts

After successful build:

```
dist/                                           # Python backend
├── aichemist_transmutation_codex-1.0.3-py3-none-any.whl
└── aichemist_transmutation_codex-1.0.3.tar.gz

gui/release/1.0.3/                              # Electron GUI
├── AiChemist Transmutation Codex Setup 1.0.3.exe  # NSIS Installer (recommended)
├── AiChemist Transmutation Codex 1.0.3.exe         # Portable version
├── win-unpacked/                                   # Unpacked application
│   ├── AiChemist Transmutation Codex.exe
│   └── resources/
│       └── app.asar                                # Application bundle
├── builder-effective-config.yaml                   # Build configuration used
└── latest.yml                                      # Auto-update metadata
```

## Testing Builds

### Test Locally

```powershell
# Run unpacked version
cd gui\release\1.0.3\win-unpacked
."AiChemist Transmutation Codex.exe"
```

### Test Installer

1. Copy `AiChemist Transmutation Codex Setup 1.0.3.exe` to test location
2. Run installer
3. Install to default location or custom path
4. Launch from Start Menu or desktop shortcut
5. Test all converters:
   - PDF to Markdown
   - Markdown to PDF
   - HTML to PDF
   - DOCX to Markdown
   - etc.

### Test Portable

1. Copy `AiChemist Transmutation Codex 1.0.3.exe` to USB drive or folder
2. Run without installation
3. Verify all features work

## Distribution

### Release Checklist

- [ ] Version number updated in:
  - [ ] `pyproject.toml`
  - [ ] `gui/package.json`
  - [ ] README.md
- [ ] All tests passing:
  ```powershell
  pytest tests/
  ```
- [ ] Build completes without errors
- [ ] Installer tested on clean Windows machine
- [ ] Portable version tested
- [ ] All converters functional
- [ ] License validation working
- [ ] External dependencies bundled (Tesseract, etc.)
- [ ] Release notes prepared
- [ ] Git tag created:
  ```powershell
  git tag -a v1.0.3 -m "Release v1.0.3"
  git push origin v1.0.3
  ```

### Upload Locations

1. **GitHub Releases** (primary)

   - Upload both NSIS and portable versions
   - Include release notes
   - Attach `latest.yml` for auto-update

2. **Website** (if applicable)

   - Upload to download page
   - Update version number
   - Publish release announcement

3. **Internal Distribution**
   - Share via company file server
   - Update internal documentation

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Installer

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install uv
        run: pip install uv

      - name: Build Python Backend
        run: uv build --wheel --out-dir dist

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Build Electron
        run: |
          cd gui
          npm install
          npm run electron:build

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: installer
          path: gui/release/**/*.exe
```

## Performance Tips

1. **Use SSD** for faster builds
2. **Add Defender exclusions** to prevent scanning
3. **Close VS Code** during large builds
4. **Use bun instead of npm** for faster installs:
   ```powershell
   bun install
   bun run electron:build
   ```
5. **Enable incremental builds** (already configured)
6. **Build on dedicated machine** for production releases

## Troubleshooting

### Build fails immediately

1. Check prerequisites are installed
2. Run `uv sync` and `npm install`
3. Check for disk space (need ~2GB free)

### Build hangs

1. Check for locked files (see BUILD_ISSUES.md)
2. Restart PowerShell
3. Try safe mode build

### Installer corrupted

1. Check antivirus didn't quarantine files
2. Verify file size is reasonable (>50MB)
3. Re-download dependencies
4. Clean rebuild

## Support

For build issues:

1. Check [BUILD_ISSUES.md](./BUILD_ISSUES.md)
2. Check [AGENTS.md](../AGENTS.md) for development setup
3. Open GitHub issue with build logs
4. Contact: simpleflowworks@gmail.com

---

**Last Updated:** November 2025 **Author:** AiChemist Development Team
(@savagelysubtle)
