# User Guide

## AiChemist Transmutation Codex

**Version:** 1.0.0
**Last Updated:** October 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [License Activation](#license-activation)
4. [Using the Converter](#using-the-converter)
5. [Supported Formats](#supported-formats)
6. [Advanced Features](#advanced-features)
7. [Settings](#settings)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

AiChemist Transmutation Codex is a powerful document conversion tool that transforms documents between various formats including Markdown, PDF, HTML, DOCX, and more.

### What You Can Do

- Convert PDF documents to Markdown
- Convert Markdown to beautifully formatted PDFs
- Extract text from images using OCR (Optical Character Recognition)
- Batch convert multiple files at once
- Merge multiple PDFs into one document
- Preserve formatting and structure during conversions

---

## Installation

### Windows

1. **Download the Installer:**
   - Visit <https://aichemist.app/download>
   - Click "Download for Windows"
   - Save the `.exe` installer file

2. **Run the Installer:**
   - Double-click the downloaded installer
   - If Windows SmartScreen appears, click "More info" then "Run anyway"
   - Follow the installation wizard
   - Choose installation location (default recommended)
   - Click "Install"

3. **Launch the Application:**
   - Find "AiChemist Transmutation Codex" in your Start Menu
   - Double-click to launch

### macOS

1. **Download the DMG:**
   - Visit <https://aichemist.app/download>
   - Click "Download for macOS"
   - Save the `.dmg` file

2. **Install the Application:**
   - Open the downloaded DMG file
   - Drag AiChemist to your Applications folder
   - Eject the DMG

3. **First Launch:**
   - Open Applications and find AiChemist
   - Right-click and select "Open" (first time only)
   - Click "Open" in the security dialog

### Linux

1. **Download AppImage or .deb:**
   - Visit <https://aichemist.app/download>
   - Choose AppImage (universal) or .deb (Debian/Ubuntu)

2. **Install:**

   **AppImage:**

   ```bash
   chmod +x AiChemist-1.0.0.AppImage
   ./AiChemist-1.0.0.AppImage
   ```

   **.deb:**

   ```bash
   sudo dpkg -i aichemist-transmutation-codex_1.0.0_amd64.deb
   sudo apt-get install -f  # Install dependencies
   ```

3. **Launch:**
   - Find "AiChemist Transmutation Codex" in your applications menu

---

## License Activation

### Trial Mode

AiChemist starts in **trial mode** with the following limitations:

- 50 total conversions
- 5MB maximum file size
- 4 basic converters (PDF↔Markdown, Markdown→HTML, Text→PDF)

### Purchasing a License

1. **Click "Upgrade"** in the app or visit <https://aichemist.gumroad.com/l/transmutation-codex>

2. **Choose Your License:**
   - **Basic** ($29): Personal use, unlimited conversions
   - **Pro** ($79): Commercial use, priority support
   - **Enterprise** (Contact us): Multi-user, dedicated support

3. **Complete Purchase:**
   - Enter your email address
   - Complete payment through Gumroad
   - Receive license key via email (usually within 5 minutes)

### Activating Your License

1. **Open License Dialog:**
   - Click the key icon in the top-right corner
   - Or go to Settings → License

2. **Enter License Key:**
   - Paste your license key (format: `AICHEMIST-XXXXX-XXXXX-XXXXX`)
   - Click "Activate License"

3. **Activation Successful:**
   - You'll see a green success message
   - All features are now unlocked
   - File size limits removed

### Offline Activation

If you don't have internet access:

1. Click "Activate Offline" in the license dialog
2. Note your Machine ID
3. Email <support@aichemist.app> with:
   - Your license key
   - Machine ID
4. We'll send you an offline activation code
5. Enter the code in the "Offline Activation" field

---

## Using the Converter

### Basic Conversion

1. **Select Conversion Type:**
   - Click the dropdown at the top
   - Choose your conversion (e.g., "PDF to Markdown")

2. **Add Files:**
   - Click "Select Files" button
   - Or drag and drop files into the window
   - Multiple files can be selected for batch conversion

3. **Choose Output Location:**
   - Click "Output Folder" button
   - Select where converted files should be saved
   - Default: Same folder as input files

4. **Start Conversion:**
   - Click the "Convert" button
   - Watch progress in real-time
   - Converted files appear in output folder

### Conversion Options

Different converters have specific options:

**PDF to Markdown:**

- ☑️ **Enable OCR**: Extract text from images/scanned PDFs
- **OCR Language**: Choose language (English, Spanish, French, etc.)
- **Force OCR**: Always use OCR, even if text is extractable

**Markdown to PDF:**

- **Page Size**: A4, Letter, Legal, etc.
- **Margins**: Top, bottom, left, right spacing
- **Custom CSS**: Apply custom styling

**HTML to PDF:**

- **Page Size**: Document dimensions
- **Enable JavaScript**: Run JavaScript in HTML
- **Wait Time**: Seconds to wait for page load

### Batch Conversion

Convert multiple files at once:

1. Select multiple files (Ctrl+Click or Shift+Click)
2. All files will be converted with the same settings
3. Progress shown for each file individually
4. Failed conversions are logged (check Conversion Log)

### PDF Merging

Combine multiple PDFs into one:

1. Select "Merge PDFs" from conversion type
2. Add multiple PDF files
3. Drag to reorder files
4. Click "Merge"
5. Result saved as `merged_document.pdf`

---

## Supported Formats

### Input Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Portable Document Format |
| Markdown | `.md` | Plain text with formatting |
| HTML | `.html`, `.htm` | Web pages |
| DOCX | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| EPUB | `.epub` | E-book format |

### Output Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| PDF | `.pdf` | Sharing, printing, archiving |
| Markdown | `.md` | Documentation, editing, version control |
| HTML | `.html` | Web publishing |
| DOCX | `.docx` | Microsoft Word editing |
| Text | `.txt` | Simple text extraction |

### Conversion Matrix

| From ↓ / To → | PDF | Markdown | HTML | DOCX | Text |
|---------------|-----|----------|------|------|------|
| **PDF** | — | ✅ | ✅ | ⚠️ | ✅ |
| **Markdown** | ✅ | — | ✅ | ✅ | ✅ |
| **HTML** | ✅ | ⚠️ | — | ⚠️ | ✅ |
| **DOCX** | ✅ | ✅ | ✅ | — | ✅ |
| **Text** | ✅ | ✅ | ✅ | ✅ | — |

✅ Fully supported | ⚠️ Partial support (may lose formatting) | — Not applicable

---

## Advanced Features

### OCR (Optical Character Recognition)

Extract text from scanned PDFs or images:

1. Enable "OCR" checkbox in PDF to Markdown conversion
2. Select OCR language (matches document language)
3. Adjust DPI if needed (300 is good balance)
4. Higher DPI = better accuracy but slower

**Tips:**

- Use Force OCR for completely scanned documents
- Clean, high-contrast documents work best
- Multiple languages can be selected (e.g., "eng+spa")

### Custom CSS for PDF Generation

Style your PDF output:

1. Create a CSS file with your styles
2. In Markdown → PDF, click "Custom CSS"
3. Select your CSS file
4. PDF will use your custom formatting

**Example CSS:**

```css
body {
  font-family: 'Georgia', serif;
  font-size: 12pt;
  line-height: 1.6;
}
h1 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
}
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open files |
| `Ctrl+S` | Choose output folder |
| `Ctrl+Enter` | Start conversion |
| `Ctrl+L` | Open Conversion Log |
| `Ctrl+,` | Open Settings |
| `F1` | Open Help |

---

## Settings

### General Settings

- **Default Output Folder**: Where converted files are saved
- **Open Output Folder**: Automatically open after conversion
- **Remember Last Settings**: Save your conversion preferences

### Privacy Settings

- **Telemetry Consent**: Help improve AiChemist by sharing anonymous usage data
  - What's collected: Conversion success rates, feature usage
  - What's NOT collected: File contents, file names, personal information
  - Can be disabled anytime

### Advanced Settings

- **Conversion Quality**: Balance between speed and quality
- **Concurrent Conversions**: How many files to process simultaneously
- **Temporary File Location**: Where temporary files are stored

### External Dependencies

Some converters require external tools (automatically included with installation):

- **Tesseract OCR**: For text extraction from images
- **Ghostscript**: For PDF processing
- **Pandoc**: For document format conversions

Check status: Settings → Dependencies

---

## Troubleshooting

### Installation Issues

**Problem:** "Windows protected your PC" message

**Solution:**

- This is Windows SmartScreen
- Click "More info"
- Click "Run anyway"
- This happens because the app is new (will improve once signed)

**Problem:** macOS says "App can't be opened"

**Solution:**

- Right-click the app in Applications
- Select "Open"
- Click "Open" in the dialog
- This grants security permission

### Conversion Issues

**Problem:** "Conversion failed" error

**Solutions:**

1. Check file isn't corrupted (can you open it normally?)
2. Verify file format is supported
3. Try converting a smaller file first
4. Check conversion log for specific error
5. Update to latest version

**Problem:** PDF conversion produces garbled text

**Solutions:**

- Enable OCR in conversion options
- Use "Force OCR" for scanned documents
- Select correct OCR language
- Check if PDF is password-protected

**Problem:** Markdown to PDF loses formatting

**Solutions:**

- Verify Markdown syntax is correct
- Use custom CSS for specific styling
- Check if images are accessible
- Try different page size settings

### License Issues

**Problem:** "License validation failed"

**Solutions:**

1. Check internet connection
2. Verify license key format (AICHEMIST-XXXXX-XXXXX-XXXXX)
3. Copy-paste carefully (no extra spaces)
4. Try offline activation if no internet
5. Contact <support@aichemist.app>

**Problem:** "License already activated on another machine"

**Solutions:**

- Deactivate license on old machine first
- Or contact support for license transfer
- Enterprise licenses allow multiple activations

### Performance Issues

**Problem:** Conversion is very slow

**Solutions:**

1. Convert smaller files first
2. Disable OCR if not needed
3. Reduce concurrent conversions in Settings
4. Close other applications
5. Check available disk space

**Problem:** App crashes or freezes

**Solutions:**

1. Update to latest version
2. Check conversion log for errors
3. Restart the application
4. Clear temporary files (Settings → Advanced)
5. Report crash to support with log files

### Getting Help

**Check Logs:**

- Windows: `%APPDATA%\AiChemist\logs`
- macOS: `~/Library/Application Support/AiChemist/logs`
- Linux: `~/.local/share/aichemist/logs`

**Contact Support:**

- Email: <support@aichemist.app>
- Include:
  - Operating system and version
  - AiChemist version
  - Description of issue
  - Log files (if applicable)

**Community:**

- FAQ: <https://aichemist.app/faq>
- Documentation: <https://aichemist.app/docs>
- GitHub Issues: <https://github.com/savagelysubtle/AiChemistTransmutations/issues>

---

## Tips and Best Practices

### Getting the Best Results

1. **Use high-quality source files** - Better input = better output
2. **Choose appropriate settings** - OCR for scans, high DPI for images
3. **Test with small files first** - Verify settings before batch conversion
4. **Keep backups** - Original files are never modified
5. **Update regularly** - New versions improve conversion quality

### Common Workflows

**Academic Papers (PDF → Markdown):**

- Enable OCR for scanned papers
- Use high DPI (300+) for equations
- Review output for special characters

**Blog Posts (Markdown → PDF):**

- Use A4 or Letter page size
- Add custom CSS for branding
- Include cover page in Markdown

**Documentation (DOCX → PDF):**

- Preserve images and tables
- Use consistent formatting in source
- Check hyperlinks work in PDF

---

## Privacy and Data

**Your Documents Stay Private:**

- All conversions happen locally on your computer
- No files are uploaded to servers
- Document content never leaves your machine

**License Validation:**

- Only license keys are checked online
- No file information transmitted

**Anonymous Telemetry** (opt-in only):

- Helps improve features
- No personally identifiable information
- Can be disabled anytime in Settings

---

## Keyboard Reference Card

```
┌─────────────────────────────────────────────┐
│       AiChemist Quick Reference             │
├─────────────────────────────────────────────┤
│ Ctrl+O         Open Files                   │
│ Ctrl+S         Set Output Folder            │
│ Ctrl+Enter     Start Conversion             │
│ Ctrl+L         View Conversion Log          │
│ Ctrl+,         Open Settings                │
│ Ctrl+Q         Quit Application             │
│ F1             Open Help                    │
│ F5             Refresh File List            │
└─────────────────────────────────────────────┘
```

---

**Need More Help?**

📧 Email: <support@aichemist.app>
🌐 Website: <https://aichemist.app>
📖 Documentation: <https://aichemist.app/docs>

**Version:** 1.0.0
**Last Updated:** October 2025
**Copyright © 2025 AiChemist. All rights reserved.**
