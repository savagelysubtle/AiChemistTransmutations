# Tesseract OCR Configuration

This document explains how the AiChemist Transmutation Codex handles Tesseract OCR configuration for production deployments.

## Overview

The application uses Tesseract OCR for:

- **PDF to Editable PDF** (`pdf2editable`) - Adding searchable text layers to scanned PDFs via OCRmyPDF
- **PDF to Markdown** (`pdf2md`) - Extracting text from non-text PDFs with OCR

## Automatic Tesseract Detection

The application automatically searches for Tesseract in the following order:

### 1. System PATH (Preferred)

If Tesseract is in your system PATH, it will be detected automatically. No configuration needed.

**Verification:**

```bash
# Windows
where tesseract

# Linux/macOS
which tesseract
```

### 2. User Configuration

Users can specify a custom Tesseract path in `config/default_config.yaml`:

```yaml
environment:
  tesseract_path: "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Windows
  # tesseract_path: "/usr/local/bin/tesseract"  # macOS
  # tesseract_path: "/usr/bin/tesseract"  # Linux
```

### 3. Common Installation Locations (Windows)

On Windows, the application automatically searches:

- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe`

### 4. Fallback

If Tesseract is not found by any method above, OCRmyPDF will attempt its own search. If this fails, conversions requiring OCR will return a helpful error message.

## Installation Instructions

### Windows

**Option 1: Chocolatey (Recommended for System PATH)**

```bash
choco install tesseract
```

**Option 2: Manual Installation**

1. Download from: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Application will auto-detect it

**Option 3: Add to PATH Manually**

1. Install Tesseract anywhere
2. Add `<install-dir>` to system PATH
3. Restart the application

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install tesseract-ocr
```

### macOS

```bash
brew install tesseract
```

## Language Packs

Tesseract supports multiple languages. Install language packs as needed:

**Windows (Chocolatey):**

```bash
choco install tesseract-languagepack-eng  # English
choco install tesseract-languagepack-fra  # French
choco install tesseract-languagepack-deu  # German
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr-eng
sudo apt-get install tesseract-ocr-fra
```

**macOS:**

```bash
brew install tesseract-lang
```

## Configuration for Production

### For End Users (Installer-based Distribution)

1. **Bundle Tesseract** (if licensing permits):
   - Include Tesseract in your installer
   - Install to a known location
   - Update `default_config.yaml` to point to bundled Tesseract

2. **Prompt User During Installation**:
   - Check if Tesseract is installed
   - If not, provide download link or auto-install
   - Update configuration with detected/installed path

3. **Runtime Detection**:
   - The current implementation will automatically detect Tesseract
   - No user intervention required if installed correctly

### For Enterprise Deployments

Use centralized configuration:

```yaml
# config/default_config.yaml (or environment-specific config)
environment:
  tesseract_path: "\\\\shared-server\\tools\\tesseract\\tesseract.exe"
```

Or use environment variables:

```bash
# Set before launching application
export TESSERACT_PATH="/opt/tesseract/bin/tesseract"
```

Then update `_configure_tesseract_path()` to check `os.environ.get("TESSERACT_PATH")`.

## Troubleshooting

### "Could not find program 'tesseract' on the PATH"

**Solution 1: Verify Installation**

```bash
tesseract --version
```

If this fails, Tesseract is not installed correctly.

**Solution 2: Add to Configuration**
Edit `config/default_config.yaml`:

```yaml
environment:
  tesseract_path: "/path/to/tesseract"  # Full path to tesseract executable
```

**Solution 3: Check Logs**
The application logs Tesseract detection at startup:

- `logs/python/app_session_*.log`
- Look for: "Found and added Tesseract to PATH" or warnings

### Missing Language Packs

**Error:** `Missing dependency for OCRmyPDF (likely Tesseract or language packs)`

**Solution:** Install required language pack (e.g., for English):

```bash
# Windows
choco install tesseract-languagepack-eng

# Linux
sudo apt-get install tesseract-ocr-eng

# macOS
brew install tesseract-lang
```

## Developer Notes

### Code Location

The Tesseract PATH configuration logic is in:

- `src/transmutation_codex/plugins/pdf/to_editable_pdf.py` - Function `_configure_tesseract_path()`

### Extending Detection

To add more search locations, modify the `common_locations` list in `_configure_tesseract_path()`:

```python
common_locations = [
    Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
    # Add custom location here:
    Path("D:\\CustomTools\\Tesseract\\tesseract.exe"),
]
```

### Platform-Specific Detection

Add platform checks for Linux/macOS:

```python
elif os.name == "posix":  # Linux/macOS
    common_locations = [
        Path("/usr/local/bin/tesseract"),
        Path("/usr/bin/tesseract"),
        Path("/opt/tesseract/bin/tesseract"),
    ]
```

## Best Practices

1. **Do NOT hard-code paths** - Always use dynamic detection
2. **Respect user configuration** - Check `ConfigManager` first
3. **Use environment variables** - For system-level PATH configuration
4. **Log detection results** - Help users troubleshoot issues
5. **Provide clear error messages** - Include installation instructions
6. **Document requirements** - In README and user documentation

## Related Configuration

See also:

- `config/default_config.yaml` - Application configuration
- `docs/INSTALLATION.md` - Installation instructions
- `README.md` - Quick start guide
