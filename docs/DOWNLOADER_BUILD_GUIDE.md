# Downloader/Launcher Build Guide

**Purpose:** Create a lightweight launcher that downloads the full application

---

## Overview

Instead of distributing a 176 MB installer, you can distribute a small launcher (~5-10 MB) that:

1. Downloads the latest full installer
2. Runs the installer automatically
3. Always ensures users get the latest version

## Benefits

✅ **Smaller Initial Download** - 5-10 MB vs 176 MB
✅ **Always Latest Version** - Downloads current release
✅ **Lower Bandwidth Costs** - On Gumroad/hosting
✅ **Professional** - Many commercial apps use this pattern
✅ **Update Checking** - Built-in version checking

---

## Build the Launcher

### Step 1: Build Downloader Executable

```powershell
# Navigate to project root
cd D:\Coding\AiChemistCodex\AiChemistTransmutations

# Build the downloader
uv run pyinstaller scripts/build/downloader.spec --clean --noconfirm

# Output: dist/AiChemist-Launcher.exe (~5-10 MB)
```

### Step 2: Upload Full Installer to Hosting

You need to host the full installer somewhere accessible:

**Option A: GitHub Releases (Free)**

```bash
# Create a release on GitHub
# Upload: AiChemist Transmutation Codex Setup 1.0.0.exe
# Get download URL: https://github.com/user/repo/releases/latest/download/AiChemist-Setup.exe
```

**Option B: Your Own Server**

```bash
# Upload to your server
scp gui/release/1.0.0/AiChemist-Setup.exe user@server:/var/www/releases/latest/

# URL: https://your-domain.com/releases/latest/AiChemist-Setup.exe
```

**Option C: Cloud Storage (S3, DigitalOcean Spaces)**

```bash
# Upload to S3 bucket (public read)
aws s3 cp AiChemist-Setup.exe s3://your-bucket/releases/latest/ --acl public-read

# URL: https://your-bucket.s3.amazonaws.com/releases/latest/AiChemist-Setup.exe
```

### Step 3: Create Version JSON

Create a version file that the launcher checks:

```json
{
  "version": "1.0.0",
  "release_date": "2025-10-22",
  "url": "https://your-hosting.com/releases/latest/AiChemist-Setup.exe",
  "size_mb": 176,
  "sha256": "abc123...",
  "changelog": [
    "Initial release",
    "PDF to Markdown conversion",
    "Batch processing",
    "License system"
  ],
  "min_windows_version": "10.0.0"
}
```

Upload this as `version.json` to the same location.

### Step 4: Update Downloader Configuration

Edit `scripts/build/downloader.py`:

```python
# Configuration
DOWNLOAD_URL = "https://github.com/user/repo/releases/latest/download/AiChemist-Setup.exe"
VERSION_CHECK_URL = "https://github.com/user/repo/releases/latest/download/version.json"
```

Then rebuild:

```powershell
uv run pyinstaller scripts/build/downloader.spec --clean --noconfirm
```

---

## Distribution Strategy

### For Gumroad

**Distribute the Launcher:**

1. Upload: `AiChemist-Launcher.exe` (5-10 MB)
2. Users download the small launcher
3. Launcher downloads full installer (176 MB)
4. License key works the same way

**Benefits:**

- Faster downloads for users
- Lower Gumroad bandwidth usage
- Can update installer without re-uploading to Gumroad
- Users always get latest version

### For Your Website

**Direct Download:**

- Offer both options:
  - **Quick Download**: Launcher (5-10 MB)
  - **Full Download**: Complete installer (176 MB)

**Recommended:**

- Feature the launcher as primary download
- Provide full installer as backup

---

## Testing

### Test the Launcher

```powershell
# Run the built launcher
.\dist\AiChemist-Launcher.exe

# It should:
1. Open a GUI window
2. Check for latest version
3. Download the full installer
4. Ask to run the installer
5. Launch the full installation
```

### Test Offline Behavior

1. Disconnect internet
2. Run launcher
3. Should show appropriate error message
4. Should allow retry

---

## Advanced Features

### Add to Launcher

Edit `scripts/build/downloader.py` to add:

1. **SHA256 Verification**

   ```python
   def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
       """Verify downloaded file integrity."""
       sha256_hash = hashlib.sha256()
       with open(file_path, "rb") as f:
           for chunk in iter(lambda: f.read(4096), b""):
               sha256_hash.update(chunk)
       return sha256_hash.hexdigest() == expected_sha256
   ```

2. **Resume Downloads**

   ```python
   # Support resuming interrupted downloads
   # Use HTTP Range headers
   ```

3. **Mirror Support**

   ```python
   # Try multiple download URLs if one fails
   DOWNLOAD_MIRRORS = [
       "https://primary-host.com/...",
       "https://backup-host.com/...",
   ]
   ```

4. **Update Checking**

   ```python
   # Check installed version vs latest
   # Offer to update if newer available
   ```

---

## File Sizes Comparison

| Distribution Method | Size | Pros | Cons |
|---------------------|------|------|------|
| **Full Installer** | 176 MB | One-click install | Large download |
| **Launcher + Download** | 5-10 MB initial | Smaller, always latest | Requires internet |
| **Portable** | 176 MB | No install needed | Large file |

---

## Hosting Costs

### GitHub Releases (FREE)

- ✅ Free hosting
- ✅ Unlimited bandwidth
- ✅ CDN included
- ✅ Version management
- ⚠️ 2 GB file size limit (we're under this)

### AWS S3

- ~$0.023 per GB storage
- ~$0.09 per GB transfer (first 10 TB)
- For 1000 downloads/month: ~$16/month

### DigitalOcean Spaces

- $5/month for 250 GB storage + 1 TB transfer
- Additional transfer: $0.01 per GB
- More predictable than AWS

---

## Gumroad Integration

### Option 1: Launcher Only

**On Gumroad:**

1. Upload: `AiChemist-Launcher.exe` (5-10 MB)
2. Description: "Launcher will download the full installer"

**After Purchase:**

1. Customer downloads launcher
2. Runs launcher → downloads full installer
3. Installs application
4. Activates with license key from Gumroad email

### Option 2: Both Options

**On Gumroad:**

- **File 1**: `AiChemist-Launcher.exe` (Recommended)
- **File 2**: `AiChemist-Setup-Full.exe` (Backup)

**Let customers choose:**

- Fast download (launcher)
- Full download (complete installer)

---

## Automation

### Auto-Update Version JSON

Create a script to update `version.json` on each release:

```python
# scripts/build/update_version.py
import json
import hashlib
from pathlib import Path
from datetime import datetime

def generate_version_json(installer_path: Path, version: str) -> dict:
    """Generate version.json for the installer."""
    # Calculate SHA256
    sha256_hash = hashlib.sha256()
    with open(installer_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    # Get file size
    size_mb = installer_path.stat().st_size / (1024 * 1024)

    return {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "url": f"https://your-hosting.com/releases/{version}/AiChemist-Setup.exe",
        "size_mb": round(size_mb, 2),
        "sha256": sha256_hash.hexdigest(),
        "changelog": [],
        "min_windows_version": "10.0.0"
    }

# Usage
installer = Path("gui/release/1.0.0/AiChemist Transmutation Codex Setup 1.0.0.exe")
version_data = generate_version_json(installer, "1.0.0")

with open("version.json", "w") as f:
    json.dump(version_data, f, indent=2)
```

---

## Complete Build & Deploy Process

### Build Everything

```powershell
# 1. Build Python backend
uv run pyinstaller transmutation_codex.spec --noconfirm

# 2. Build Electron GUI with Python bundled
cd gui
npm run build

# 3. Build the launcher
cd ..
uv run pyinstaller scripts/build/downloader.spec --noconfirm

# Results:
# - gui/release/1.0.0/AiChemist-Setup.exe (176 MB) ← Upload to hosting
# - dist/AiChemist-Launcher.exe (5-10 MB) ← Distribute this
```

### Deploy

```bash
# 1. Upload full installer to GitHub Releases
gh release create v1.0.0 \
  gui/release/1.0.0/"AiChemist Transmutation Codex Setup 1.0.0.exe"

# 2. Generate and upload version.json
python scripts/build/update_version.py
gh release upload v1.0.0 version.json

# 3. Distribute launcher on Gumroad
# Upload: dist/AiChemist-Launcher.exe
```

---

## Recommended Approach

**For Launch:**

1. ✅ Build both full installer and launcher
2. ✅ Host full installer on GitHub Releases (free)
3. ✅ Distribute launcher via Gumroad (small, fast)
4. ✅ Offer full installer as backup option

**This gives you:**

- Smallest Gumroad download
- Free hosting for large files
- Professional user experience
- Always latest version for users

---

## Testing Checklist

- [ ] Launcher builds successfully (~5-10 MB)
- [ ] Full installer uploaded to hosting
- [ ] version.json accessible
- [ ] Launcher downloads installer correctly
- [ ] Launcher runs installer after download
- [ ] License activation works same as before
- [ ] Offline error handling works
- [ ] Progress bar updates correctly

---

**Ready to build?** Run the commands above to create your launcher!
