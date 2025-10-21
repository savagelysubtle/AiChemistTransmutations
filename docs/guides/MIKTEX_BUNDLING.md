# MiKTeX Bundling and Installation

This document describes how MiKTeX is optionally bundled with the production installer for AiChemist Transmutation Codex.

## Overview

MiKTeX is a TeX/LaTeX distribution that enhances Pandoc's PDF generation capabilities. It's **optional** but recommended for:

- Advanced PDF formatting
- Professional typesetting
- Mathematical equations in PDFs
- Custom templates with LaTeX

The production installer optionally:

1. Downloads the MiKTeX installer (~10 MB bootstrapper)
2. Bundles it with the application installer
3. Can install MiKTeX during application installation (commented out by default due to size)
4. MiKTeX automatically downloads packages on first use

## For Development

### Quick Install

Run the automated installation script:

```powershell
.\scripts\install_miktex.ps1
```

This will:

- Try to install via `winget` (Windows Package Manager)
- Fall back to Chocolatey if available
- Provide manual download instructions if both fail

### Manual Installation

**Windows:**

- Download from <https://miktex.org/download>
- Run the installer
- Choose "Basic MiKTeX" for ~200 MB or "Complete MiKTeX" for ~4 GB
- Restart your development environment

**macOS:**

```bash
brew install --cask miktex-console
```

**Linux:**

```bash
# Full TeX Live distribution (recommended)
sudo apt-get install texlive-full

# Or minimal install
sudo apt-get install texlive-latex-base
```

## Why MiKTeX is Optional

MiKTeX is a large installation (~500 MB+ for basic, ~4 GB for complete), so we:

1. **Bundle the installer** but don't auto-install by default
2. **Let Pandoc work without it** for basic conversions
3. **Enable it for advanced features** when needed

## For Production Builds

### Build Script Integration

The `scripts/build_installer.ps1` automatically:

1. **Downloads MiKTeX Installer** (if not present):
   - Version: 5.9
   - URL: <https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/miktexsetup-5.9-x64.exe>
   - Saved to: `build/installers/miktexsetup-x64.exe`
   - **Note:** Download failures are non-fatal (optional dependency)

2. **Bundles with installer** (if present):
   - Installer is included in the application setup
   - Installation is commented out by default in `installer.iss`

### Installer Behavior

The Inno Setup installer (`installer.iss`):

1. **Checks if MiKTeX is installed**:
   - `C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe`
   - `C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe`
   - `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe`
   - Registry: `HKLM\SOFTWARE\MiKTeX.org\MiKTeX`

2. **Optional Installation** (commented out by default):

   ```pascal
   ; Uncomment to enable automatic MiKTeX installation:
   ; Filename: "{tmp}\miktexsetup-x64.exe";
   ; Parameters: "--shared=yes --package-set=basic --quiet";
   ; StatusMsg: "Installing MiKTeX (optional)...";
   ; Flags: waituntilterminated skipifdoesntexist;
   ; Check: not MiktexInstalled
   ```

3. **Why Commented Out:**
   - Large download (~500 MB+ additional data during install)
   - Long installation time (5-10 minutes)
   - Not required for core functionality
   - Users can install manually if needed

## When MiKTeX is Useful

### With MiKTeX

- Professional PDF layouts
- Mathematical equations (LaTeX math)
- Custom templates
- Advanced typography
- Bibliography management
- Cross-references

### Without MiKTeX

- Basic PDF generation (Pandoc's built-in PDF engine)
- HTML to PDF (via other engines)
- Simple documents
- Standard formatting

## Pandoc Integration

Pandoc automatically uses MiKTeX (if available) via:

```bash
# Pandoc will use pdflatex if available
pandoc input.md -o output.pdf --pdf-engine=pdflatex

# Or xelatex for better Unicode support
pandoc input.md -o output.pdf --pdf-engine=xelatex

# Falls back to built-in engine if MiKTeX not found
pandoc input.md -o output.pdf
```

## File Size Considerations

**MiKTeX Installer:**

- Bootstrapper: ~10 MB (bundled)
- Basic install: ~200-300 MB (downloaded on install)
- Complete install: ~4 GB (downloaded on install)

**Our Approach:**

- Bundle the 10 MB bootstrapper
- Let users decide if they want the full install
- Provide manual installation option

## Testing

### Development Testing

```powershell
# Install MiKTeX (optional)
.\scripts\install_miktex.ps1

# Verify installation
where pdflatex
pdflatex --version

# Test with Pandoc
pandoc test.md -o test.pdf --pdf-engine=pdflatex
```

### Production Testing

After building with `scripts/build_installer.ps1`:

1. Installer will include MiKTeX bootstrapper
2. Users can run MiKTeX installer manually from program folder if needed
3. Or install via `choco install miktex` or `winget install MiKTeX.MiKTeX`

## Troubleshooting

### MiKTeX Not Found

**Symptom:** Pandoc reports "pdflatex not found"

**Solution:**

```powershell
# Install MiKTeX
.\scripts\install_miktex.ps1

# Or use Pandoc's built-in engine
# (no MiKTeX required)
pandoc input.md -o output.pdf
```

### Package Installation Prompts

**Symptom:** MiKTeX asks to install packages during first use

**Solution:** This is normal! MiKTeX auto-installs packages on demand:

- Click "Install" when prompted
- Or configure MiKTeX Console to auto-install:

  ```
  MiKTeX Console → Settings → Package installation → Always install
  ```

### Build Script Can't Download MiKTeX

**Symptom:** Build script reports "Failed to download MiKTeX installer"

**Solution:** This is OK! MiKTeX is optional:

```powershell
# Download manually if you want to include it:
Invoke-WebRequest -Uri "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/miktexsetup-5.9-x64.exe" -OutFile "build\installers\miktexsetup-x64.exe"

# Or skip it - the build will continue without it
```

## Enabling Automatic Installation

To enable automatic MiKTeX installation in the production installer:

1. Edit `installer.iss`
2. Find the commented MiKTeX installation line:

   ```pascal
   ; Filename: "{tmp}\miktexsetup-x64.exe"; Parameters: "--shared=yes --package-set=basic --quiet"; StatusMsg: "Installing MiKTeX (optional)..."; Flags: waituntilterminated skipifdoesntexist; Check: not MiktexInstalled
   ```

3. Uncomment it (remove the `;` at the start)
4. Rebuild the installer

**Warning:** This will add 5-10 minutes to installation time and download ~300 MB.

## License

MiKTeX is free software under the MIT License.

- See: <https://miktex.org/copying>
- Includes various LaTeX packages with their own licenses

## Benefits

1. **Optional**: Not required, reducing installer size
2. **Flexible**: Users install only if they need advanced PDF features
3. **Auto-Updating**: MiKTeX auto-downloads packages as needed
4. **Professional**: Enables LaTeX typesetting quality
5. **Standard**: Industry-standard TeX distribution

## See Also

- [MiKTeX Official Website](https://miktex.org/)
- [MiKTeX Documentation](https://docs.miktex.org/)
- [Pandoc PDF Generation](https://pandoc.org/MANUAL.html#creating-a-pdf)
- [PANDOC_BUNDLING.md](./PANDOC_BUNDLING.md) - Pandoc setup (requires MiKTeX for advanced features)




