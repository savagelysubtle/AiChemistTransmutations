# Frequently Asked Questions (FAQ)

## AiChemist Transmutation Codex

**Version:** 1.0.0
**Last Updated:** October 2025

---

## General Questions

### What is AiChemist Transmutation Codex?

AiChemist Transmutation Codex is a professional document conversion tool that transforms documents between various formats including PDF, Markdown, HTML, DOCX, and more. It runs entirely on your computer, ensuring your documents stay private.

### What makes it different from online converters?

- **Privacy**: All conversions happen locally - no uploads
- **Offline**: Works without internet (after license activation)
- **Batch Processing**: Convert multiple files simultaneously
- **OCR Support**: Extract text from scanned documents
- **Professional Quality**: Better formatting preservation
- **No File Size Limits**: Convert files of any size (with paid license)

### What platforms are supported?

- Windows 10/11 (64-bit)
- macOS 10.15 (Catalina) and newer
- Linux (Ubuntu 20.04+, Fedora 33+, Debian 10+)

---

## Licensing & Pricing

### Do I need to pay to use it?

AiChemist has a **free trial** with limitations:

- 50 total conversions
- 5MB maximum file size
- 4 basic converters

For unlimited use, purchase a license starting at $29.

### What are the license tiers?

| Feature | Trial | Basic ($29) | Pro ($79) | Enterprise |
|---------|-------|-------------|-----------|------------|
| Conversions | 50 | Unlimited | Unlimited | Unlimited |
| File Size | 5MB | Unlimited | Unlimited | Unlimited |
| All Converters | 4 | All | All | All |
| Use | Personal | Personal | Commercial | Multi-user |
| Support | Community | Email | Priority | Dedicated |
| Updates | ✅ | ✅ | ✅ | ✅ |
| OCR | ❌ | ✅ | ✅ | ✅ |

### Can I try before buying?

Yes! The trial mode gives you 50 conversions to test the software. No credit card required.

### Is there a refund policy?

Yes, we offer a **30-day money-back guarantee**. If you're not satisfied, email <support@aichemist.app> for a full refund.

### Can I use one license on multiple computers?

- **Basic/Pro**: One computer at a time (can deactivate and move)
- **Enterprise**: Multiple activations included (contact us)

### Does the license expire?

No! It's a **one-time purchase** with lifetime access. You own the software version you purchased.

### Do I get free updates?

Yes! Minor updates (1.x) are free. Major version upgrades (2.0+) may require a paid upgrade, but you can continue using your current version.

---

## Installation & Setup

### Do I need administrator rights to install?

**Windows**: Yes, for system-wide installation
**macOS**: Yes, to move to Applications folder
**Linux**: Depends on install method (AppImage doesn't require root)

### How much disk space does it need?

- Application: ~200MB
- External tools (Tesseract, Ghostscript): ~300MB
- **Total**: ~500MB plus space for temporary files

### Can I install it on a USB drive?

The Windows portable version (coming soon) will support USB installation. Currently, standard installation is recommended.

### Why does Windows show a security warning?

Our installer is new and not yet widely recognized by Windows SmartScreen. This warning will diminish as more users install the software. Click "More info" → "Run anyway" to proceed. (We're working on code signing to eliminate this warning.)

---

## Conversion Questions

### What file formats can I convert?

**Input formats**: PDF, Markdown (.md), HTML, DOCX, TXT, EPUB
**Output formats**: PDF, Markdown, HTML, DOCX, TXT

See the [Conversion Matrix](USER_GUIDE.md#conversion-matrix) for specific combinations.

### Can I convert scanned PDFs?

Yes! Enable **OCR** (Optical Character Recognition) when converting PDF to Markdown or text. This extracts text from images.

### Why is my PDF conversion producing garbled text?

This usually means the PDF is scanned or image-based. **Solution**: Enable OCR in the conversion options and select the appropriate language.

### Can I batch convert multiple files?

Yes! Select multiple files (Ctrl+Click or drag-and-drop multiple files), and they'll all be converted with the same settings.

### How long does conversion take?

**Typical times**:

- Small PDF (1-10 pages): 5-15 seconds
- Large PDF (100+ pages): 1-3 minutes
- With OCR enabled: 2-5x longer
- Batch conversions: Parallel processing speeds things up

### Can I convert password-protected PDFs?

Not directly. You'll need to remove the password first using Adobe Acrobat or similar tools, then convert with AiChemist.

### Will formatting be preserved?

**Good preservation**: Headings, paragraphs, lists, tables (in supported formats)
**May be lost**: Complex layouts, exact fonts, multi-column designs
**Best results**: Simple, well-structured documents

### Can I merge multiple PDFs?

Yes! Select "Merge PDFs" from the conversion type, add your files, reorder them as needed, and click "Merge".

---

## Technical Questions

### Does AiChemist need internet access?

**License activation**: Yes, one-time (offline activation available)
**Conversions**: No, everything runs locally
**Updates**: Optional (can check for updates)
**Telemetry**: Optional (opt-in only)

### Where are my converted files saved?

By default: **Same folder as input files**

You can change this in Settings or select a custom output folder before each conversion.

### Are my documents uploaded anywhere?

**No!** All conversions happen entirely on your computer. Your documents never leave your machine. Only license validation contacts our servers (and only sends the license key, not your files).

### Where are log files stored?

- **Windows**: `%APPDATA%\AiChemist\logs`
- **macOS**: `~/Library/Application Support/AiChemist/logs`
- **Linux**: `~/.local/share/aichemist/logs`

### What external tools does it use?

- **Tesseract OCR**: Text extraction from images
- **Ghostscript**: PDF processing
- **Pandoc**: Format conversions

These are bundled with the installer - no separate installation needed.

### Can I use AiChemist from the command line?

Yes! The CLI is included:

```bash
# Windows
aichemist-cli --type pdf2md --input document.pdf --output output.md

# macOS/Linux
aichemist --type pdf2md --input document.pdf --output output.md
```

See `aichemist --help` for all options.

---

## Privacy & Security

### What data does AiChemist collect?

**Without consent**: Nothing except license validation
**With telemetry consent** (opt-in only):

- Conversion success/failure rates
- Feature usage statistics
- Error types (no file contents)
- Performance metrics

**Never collected**:

- File contents or names
- Personal information
- Browsing history

See our [Privacy Policy](PRIVACY_POLICY.md) for complete details.

### Is my data encrypted?

- **License validation**: HTTPS encryption
- **Local storage**: Standard file system security
- **Documents**: Never transmitted, stay on your computer

### Can AiChemist access my files without permission?

No. The app only accesses files you explicitly select for conversion. It has no background file access.

---

## Troubleshooting

### The app won't start - what should I do?

1. **Restart your computer** (simple but often effective)
2. **Check system requirements** (OS version, disk space)
3. **Reinstall the application**
4. **Check antivirus** isn't blocking it
5. **Contact support** with error message

### Conversion failed - how do I fix it?

1. **Check the conversion log** (Ctrl+L) for specific error
2. **Try a smaller file** to test if it's file-size related
3. **Update to latest version**
4. **Enable OCR** if converting scanned documents
5. **Verify file isn't corrupted** (can you open it normally?)

### License activation isn't working

**Common causes**:

- **Typo in license key**: Copy-paste carefully
- **No internet**: Try offline activation
- **Already activated**: Deactivate on other machine first
- **Expired trial**: Need to purchase a license

**Solution**: Email <support@aichemist.app> with your license key

### App is running slow

**Quick fixes**:

1. **Disable OCR** if not needed (biggest speedup)
2. **Close other applications**
3. **Convert smaller batches**
4. **Check available disk space** (need space for temp files)
5. **Reduce concurrent conversions** in Settings

### Getting different results each time

This can happen with:

- **Complex PDFs**: Try Force OCR for consistency
- **Scanned documents**: Use higher DPI for stability
- **Web pages (HTML)**: Enable "Wait for load" option

---

## Feature Requests & Support

### How do I request a new feature?

1. **Check the roadmap**: <https://aichemist.app/roadmap>
2. **Email us**: <support@aichemist.app>
3. **GitHub Issues**: <https://github.com/savagelysubtle/AiChemistTransmutations/issues>

Popular requests get prioritized!

### Can I get help with a specific conversion?

Yes! Email <support@aichemist.app> with:

- Sample file (if possible)
- Desired output
- What's going wrong
- Your license tier

Pro and Enterprise customers get priority support.

### How do I report a bug?

Email <support@aichemist.app> with:

1. **Description** of the problem
2. **Steps to reproduce**
3. **Expected vs actual** behavior
4. **Log files** (see locations above)
5. **Screenshots** if relevant

### Is there a community forum?

Not yet, but planned! For now:

- **Email**: <support@aichemist.app>
- **GitHub Discussions**: Coming soon
- **Discord**: Launching with v1.1

---

## Advanced Usage

### Can I automate conversions?

Yes! Use the CLI with scripts:

```bash
# Batch convert all PDFs in a folder
for file in *.pdf; do
  aichemist --type pdf2md --input "$file" --output "${file%.pdf}.md"
done
```

### Can I customize PDF styling?

Yes! Create a custom CSS file and use it in Markdown → PDF conversions. See [User Guide - Custom CSS](USER_GUIDE.md#custom-css-for-pdf-generation).

### Can I use AiChemist in my commercial application?

**Pro or Enterprise license required**. Basic license is personal use only. Contact us for API access if you need programmatic integration.

### Does it support LaTeX?

Markdown with LaTeX math is supported in PDF output. Full LaTeX document conversion is planned for v1.2.

---

## Comparison Questions

### AiChemist vs Pandoc?

**AiChemist advantages**:

- Graphical interface (easier)
- OCR support
- Better PDF handling
- Batch processing GUI
- Professional formatting

**Pandoc advantages**:

- Free and open source
- More format support
- Highly customizable
- Command-line power users

(AiChemist actually uses Pandoc under the hood for some conversions!)

### AiChemist vs Adobe Acrobat?

**AiChemist advantages**:

- Much cheaper ($29 vs $180/year)
- Better Markdown support
- Batch conversion
- Privacy (local processing)

**Adobe advantages**:

- PDF editing (not just conversion)
- Form creation
- Digital signatures
- Industry standard

### AiChemist vs Online Converters?

**AiChemist advantages**:

- **Privacy**: Files stay on your computer
- **No file size limits** (with paid license)
- **Offline**: Works without internet
- **Batch**: Convert many files at once
- **Quality**: Better formatting preservation

**Online converters**:

- Usually free for small files
- No installation needed
- Accessible from any device

---

## Tips & Tricks

### Best Practices

1. **Test settings with small files first** before batch converting
2. **Keep original files** - AiChemist never modifies inputs
3. **Use OCR for scanned documents** - don't forget to enable it!
4. **Custom CSS** makes beautiful branded PDFs
5. **Keyboard shortcuts** speed up your workflow (see User Guide)

### Hidden Features

- **Drag files to reorder** before merging PDFs
- **Right-click files** for quick actions
- **Double-click** conversion log entries for details
- **Middle-click** output folder opens in file manager
- **Ctrl+Shift+D** toggles debug mode

### Pro Tips

**For academic papers:**

- Use high DPI (300-600) OCR for equations
- Enable "Preserve structure" in settings
- Export to Markdown for easy editing

**For e-books:**

- Convert EPUB → Markdown for editing
- Use custom CSS for branded PDFs
- Markdown → PDF with table of contents

**For documentation:**

- Keep Markdown source in version control
- Use consistent formatting
- Generate PDFs for distribution

---

## Still Have Questions?

📧 **Email Support**: <support@aichemist.app>
🌐 **Website**: <https://aichemist.app>
📖 **Documentation**: <https://aichemist.app/docs>
💬 **Live Chat** (Pro/Enterprise): Available in-app

**Average Response Times**:

- Basic: 24-48 hours
- Pro: 12-24 hours
- Enterprise: 4-8 hours (with SLA)

---

**Version:** 1.0.0
**Last Updated:** October 2025
**Copyright © 2025 AiChemist. All rights reserved.**
