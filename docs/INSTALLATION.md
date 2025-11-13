# Installation Requirements

## System Requirements

### Windows

- **Operating System**: Windows 10 or 11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for application + space for conversions

### **CRITICAL: Python 3.13+ Required**

⚠️ **This application requires Python 3.13 or later to be installed on your system.**

#### **Installing Python**

1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Download Python 3.13 or later

2. **During Installation**:
   - ✅ **CHECK "Add Python to PATH"** (very important!)
   - Choose "Install Now" or customize installation location

3. **Verify Installation**:
   ```powershell
   python --version
   # Should show: Python 3.13.x
   ```

#### **Common Python Locations**

The app will automatically search for Python in:
- System PATH (`python` or `python3`)
- `C:\Python313\`
- `C:\Python312\`
- `C:\Python311\`
- `C:\Program Files\Python313\`

If Python is not found, you'll see an error message asking you to install it.

---

## Installation Steps

### 1. **Install Python** (if not already installed)
See instructions above

### 2. **Download AiChemist Transmutation Codex**
- Get the latest installer from: https://github.com/savagelysubtle/AiChemistTransmutations/releases
- Download: `AiChemist Transmutation Codex Setup 1.1.0.exe`

### 3. **Run the Installer**
- Double-click the installer
- Accept the license agreements
- Choose installation location
- Wait for installation to complete

### 4. **Launch the Application**
- Start Menu: Search for "AiChemist Transmutation Codex"
- Desktop: Double-click the shortcut (if created)

### 5. **Activate Your License** (Optional)
- Try 50 free conversions with the trial
- Purchase a license from: https://aichemist.gumroad.com
- Activate in-app: Settings → License → Enter Key

---

## Python Dependencies

The application will automatically install required Python packages on first run:

- PyPDF2
- requests
- supabase
- python-dotenv
- And others (see `requirements.txt`)

If you experience issues, manually install dependencies:

```powershell
# Navigate to installation directory
cd "C:\Program Files\AiChemist Transmutation Codex\resources\python-backend"

# Install dependencies
python -m pip install PyPDF2 requests supabase python-dotenv pyyaml cryptography
```

---

## Optional External Tools

For advanced features, you can install these tools separately:

### **Tesseract OCR** (for OCR features)
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Required for: Extracting text from scanned PDFs and images

### **Ghostscript** (for advanced PDF operations)
- Download: https://www.ghostscript.com/releases/gsdnld.html
- Required for: Advanced PDF processing

### **Pandoc** (for universal document conversion)
- Download: https://pandoc.org/installing.html
- Required for: Additional conversion formats

### **LibreOffice** (for Office document conversions)
- Download: https://www.libreoffice.org/download/
- Required for: DOCX, XLSX, PPTX conversions

**Note**: These tools are bundled with the installer, but you can install them separately for system-wide use.

---

## Troubleshooting

### **Error: "Python backend not found"**

**Solution**:
1. Verify Python is installed: `python --version`
2. Ensure Python is in PATH
3. Reinstall Python with "Add to PATH" checked
4. Restart your computer after installing Python

### **Error: "Python 3.13+ is required"**

**Solution**:
1. Check Python version: `python --version`
2. If older than 3.13, download and install Python 3.13+
3. Uninstall older Python versions if needed

### **Error: "Module not found"**

**Solution**:
```powershell
# Install missing dependencies
python -m pip install --upgrade pip
python -m pip install PyPDF2 requests supabase python-dotenv
```

### **License Activation Fails**

**Solution**:
1. Check your internet connection
2. Verify license key is correct (copy-paste recommended)
3. Contact support@aichemist.app for assistance

### **App Won't Start**

**Solution**:
1. Check Python installation: `python --version`
2. Run as Administrator (right-click → Run as administrator)
3. Check Windows Event Viewer for errors
4. Reinstall the application

---

## Uninstallation

### **Windows**

1. **Uninstall via Settings**:
   - Settings → Apps → AiChemist Transmutation Codex → Uninstall

2. **Uninstall via Control Panel**:
   - Control Panel → Programs → Uninstall a program
   - Select "AiChemist Transmutation Codex" → Uninstall

3. **Manual Cleanup** (optional):
   ```powershell
   # Remove AppData
   Remove-Item -Recurse -Force "$env:APPDATA\AiChemist Transmutation Codex"
   Remove-Item -Recurse -Force "$env:LOCALAPPDATA\AiChemist Transmutation Codex"
   ```

---

## System Integration

### **File Associations**

The installer does NOT change file associations. To open files with AiChemist:
- Right-click file → Open with → Choose AiChemist Transmutation Codex
- Or drag-and-drop files onto the application window

### **Start Menu**

The installer creates Start Menu shortcuts:
- Start Menu → AiChemist Transmutation Codex

### **Desktop Shortcut**

Desktop shortcut is created automatically (can be removed manually if not needed)

---

## Support

- **Email**: support@aichemist.app
- **GitHub Issues**: https://github.com/savagelysubtle/AiChemistTransmutations/issues
- **Documentation**: https://github.com/savagelysubtle/AiChemistTransmutations/wiki

---

## License

- **Software**: Apache 2.0 License
- **Third-Party Components**: See `THIRD-PARTY-LICENSES.md`

---

**Last Updated**: November 13, 2025
**Version**: 1.1.0


