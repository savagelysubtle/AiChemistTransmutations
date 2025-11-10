# Quick Start: Generating Icons

## Windows (PowerShell)

1. **Install ImageMagick** (if not already installed):
   ```powershell
   winget install ImageMagick.ImageMagick
   ```

2. **Generate icons**:
   ```powershell
   cd gui
   npm run generate-icons:win
   ```

   Or run directly:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/generate-icons.ps1
   ```

## macOS / Linux

1. **Install ImageMagick** (if not already installed):
   ```bash
   # macOS
   brew install imagemagick

   # Linux (Debian/Ubuntu)
   sudo apt-get install imagemagick
   ```

2. **Generate icons**:
   ```bash
   cd gui
   npm run generate-icons
   ```

## What Gets Generated

After running the script, you'll have:

- ✅ `icon.ico` - Windows app icon
- ✅ `icon.png` - Linux/fallback icon (256x256, 512x512)
- ✅ `icon.icns` - macOS app icon (macOS only)
- ✅ `favicon.ico` - Browser favicon
- ✅ `favicon-*.png` - PNG favicons (16x16, 32x32, 48x48, 64x64)

## Troubleshooting

### ImageMagick not found
- **Windows**: Install via `winget install ImageMagick.ImageMagick`
- **macOS**: Install via `brew install imagemagick`
- **Linux**: Install via your package manager

### Icons not showing in app
1. Make sure icons are generated in `gui/assets/`
2. Rebuild the Electron app: `npm run build`
3. Check that `package.json` references correct icon paths

### SVG files look good but generated icons don't
- Ensure ImageMagick is up to date
- Try regenerating with: `npm run generate-icons` (or `generate-icons:win` on Windows)

## Manual Generation

If the script fails, you can generate icons manually:

### Windows ICO
```powershell
magick convert -background none icon.svg -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

### PNG Files
```powershell
magick convert -background none -resize 256x256 icon.svg icon-256x256.png
magick convert -background none -resize 512x512 icon.svg icon-512x512.png
```

### macOS ICNS (macOS only)
```bash
# Create iconset directory
mkdir icon.iconset

# Generate PNGs at required sizes (see generate-icons.js for sizes)
# Then run:
iconutil -c icns icon.iconset -o icon.icns
```


















