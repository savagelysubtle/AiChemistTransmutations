# Icons and Assets

This directory contains the logo, icons, and favicons for the AiChemist
Transmutation Codex application.

## Files

### Source Files (SVG)

- **`logo.svg`** - Full logo with document transformation theme (512x512)
- **`icon.svg`** - App icon optimized for application icons (256x256)
- **`favicon.svg`** - Simplified favicon for browser tabs (64x64)

### Generated Files (Run `generate-icons.js` to create)

- **`icon.ico`** - Windows application icon (multi-size: 16, 32, 48, 256)
- **`icon.icns`** - macOS application icon (multi-size: 16-1024 with @2x
  variants)
- **`icon.png`** - Linux/fallback application icon (256x256, 512x512)
- **`favicon.ico`** - Browser favicon (multi-size: 16, 32, 48, 64)
- **`favicon-16x16.png`** - 16x16 PNG favicon
- **`favicon-32x32.png`** - 32x32 PNG favicon
- **`favicon-48x48.png`** - 48x48 PNG favicon
- **`favicon-64x64.png`** - 64x64 PNG favicon

## Design

The logo design represents:

- **Document Conversion**: Two documents (input → output) with transformation
  arrows
- **Transmutation Theme**: Alchemy/chemistry symbol (atom/molecule) representing
  transformation
- **Brand Colors**: Uses the app's gradient colors:
  - Light mode: `#0969DA` (blue) → `#E94560` (pink/red)
  - Dark mode: `#58A6FF` (light blue) → `#E94560` (pink/red)

## Generating Icons

To generate all required icon formats from the SVG sources:

```bash
cd gui
node scripts/generate-icons.js
```

### Requirements

- **ImageMagick** (for PNG and ICO generation)

  - Windows: Download from https://imagemagick.org/script/download.php
  - macOS: `brew install imagemagick`
  - Linux: `sudo apt-get install imagemagick`

- **iconutil** (macOS only, for ICNS generation)
  - Built-in macOS tool, no installation needed

### Manual Generation (if script fails)

#### Windows ICO

```bash
magick convert -background none icon.svg -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

#### macOS ICNS

1. Create `icon.iconset` directory
2. Generate PNGs at required sizes (see script for sizes)
3. Run: `iconutil -c icns icon.iconset -o icon.icns`

#### PNG Files

```bash
magick convert -background none -resize 256x256 icon.svg icon-256x256.png
magick convert -background none -resize 512x512 icon.svg icon-512x512.png
```

## Usage in Application

### Electron Builder (package.json)

- Windows: `"icon": "assets/icon.ico"`
- macOS: `"icon": "assets/icon.icns"`
- Linux: `"icon": "assets/icon.png"`

### HTML Favicon (index.html)

```html
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
<link
  rel="icon"
  type="image/png"
  sizes="32x32"
  href="/assets/favicon-32x32.png"
/>
<link
  rel="icon"
  type="image/png"
  sizes="16x16"
  href="/assets/favicon-16x16.png"
/>
```

## Color Reference

The icons use the application's gradient colors defined in `tailwind.config.js`:

**Light Mode:**

- Gradient Start: `#0969DA` (GitHub blue)
- Gradient End: `#E94560` (Coral red)

**Dark Mode:**

- Gradient Start: `#58A6FF` (Light blue)
- Gradient End: `#E94560` (Coral red)

## License

Icons are part of the AiChemist Transmutation Codex project and follow the same
license as the main application.
