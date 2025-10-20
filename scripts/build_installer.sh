#!/bin/bash
# Build Installer Script for AiChemist Transmutation Codex (Linux/macOS)
# This script automates the process of building a production installer with bundled Tesseract and Ghostscript

set -e  # Exit on error

VERSION="${1:-1.0.0}"
OUTPUT_DIR="dist"
SKIP_TESTS="${2:-false}"

echo "====================================================="
echo "  AiChemist Transmutation Codex Installer Builder"
echo "  Version: $VERSION"
echo "  Platform: $(uname -s)"
echo "====================================================="
echo ""

# Step 1: Clean previous builds
echo "[1/7] Cleaning previous builds..."
rm -rf build dist
mkdir -p build/resources/tesseract
mkdir -p build/resources/ghostscript
echo "  ✓ Created build directories"

# Step 2: Run tests (optional)
if [ "$SKIP_TESTS" != "true" ]; then
    echo ""
    echo "[2/7] Running tests..."
    if uv run pytest tests/unit/ -v --tb=short; then
        echo "  ✓ Tests passed"
    else
        echo "  ✗ Tests failed"
        read -p "  Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo ""
    echo "[2/7] Skipping tests..."
fi

# Step 3: Copy Tesseract files
echo ""
echo "[3/7] Copying Tesseract files..."

# Detect Tesseract installation location
if [ -f "/usr/bin/tesseract" ]; then
    TESSERACT_SOURCE="/usr"
elif [ -f "/usr/local/bin/tesseract" ]; then
    TESSERACT_SOURCE="/usr/local"
elif [ -f "/opt/homebrew/bin/tesseract" ]; then
    TESSERACT_SOURCE="/opt/homebrew"  # macOS Apple Silicon
elif [ -d "/usr/local/Cellar/tesseract" ]; then
    # macOS Homebrew Intel
    TESSERACT_SOURCE=$(ls -d /usr/local/Cellar/tesseract/* | sort -V | tail -1)
else
    echo "  ✗ Tesseract not found"
    echo "  Install Tesseract:"
    echo "    Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "    macOS: brew install tesseract"
    echo "    Fedora/RHEL: sudo dnf install tesseract"
    exit 1
fi

echo "  Found Tesseract at: $TESSERACT_SOURCE"

# Copy Tesseract executable
if [ -f "$TESSERACT_SOURCE/bin/tesseract" ]; then
    cp "$TESSERACT_SOURCE/bin/tesseract" build/resources/tesseract/
    chmod +x build/resources/tesseract/tesseract
    echo "  ✓ Copied tesseract executable"
else
    echo "  ✗ Tesseract executable not found"
    exit 1
fi

# Copy Tesseract data files
if [ -d "$TESSERACT_SOURCE/share/tessdata" ]; then
    cp -r "$TESSERACT_SOURCE/share/tessdata" build/resources/tesseract/
    echo "  ✓ Copied tessdata directory"
elif [ -d "$TESSERACT_SOURCE/share/tesseract-ocr/*/tessdata" ]; then
    cp -r $TESSERACT_SOURCE/share/tesseract-ocr/*/tessdata build/resources/tesseract/
    echo "  ✓ Copied tessdata directory"
fi

# Copy shared libraries (Linux)
if [ "$(uname -s)" = "Linux" ]; then
    if [ -d "$TESSERACT_SOURCE/lib" ]; then
        mkdir -p build/resources/tesseract/lib
        find "$TESSERACT_SOURCE/lib" -name "*tesseract*.so*" -exec cp {} build/resources/tesseract/lib/ \;
        find "$TESSERACT_SOURCE/lib" -name "*lept*.so*" -exec cp {} build/resources/tesseract/lib/ \;
        echo "  ✓ Copied Tesseract libraries"
    fi
fi

# Calculate Tesseract bundle size
TESSERACT_SIZE=$(du -sh build/resources/tesseract | cut -f1)
echo "  ℹ Tesseract bundle size: $TESSERACT_SIZE"

# Step 3b: Copy Ghostscript files
echo ""
echo "  Copying Ghostscript files..."

# Detect Ghostscript installation
if [ -f "/usr/bin/gs" ]; then
    GS_SOURCE="/usr"
elif [ -f "/usr/local/bin/gs" ]; then
    GS_SOURCE="/usr/local"
elif [ -f "/opt/homebrew/bin/gs" ]; then
    GS_SOURCE="/opt/homebrew"  # macOS Apple Silicon
elif [ -d "/usr/local/Cellar/ghostscript" ]; then
    # macOS Homebrew Intel
    GS_SOURCE=$(ls -d /usr/local/Cellar/ghostscript/* | sort -V | tail -1)
else
    echo "  ✗ Ghostscript not found"
    echo "  Install Ghostscript:"
    echo "    Ubuntu/Debian: sudo apt-get install ghostscript"
    echo "    macOS: brew install ghostscript"
    echo "    Fedora/RHEL: sudo dnf install ghostscript"
    exit 1
fi

echo "  Found Ghostscript at: $GS_SOURCE"

# Copy Ghostscript executable
if [ -f "$GS_SOURCE/bin/gs" ]; then
    cp "$GS_SOURCE/bin/gs" build/resources/ghostscript/
    chmod +x build/resources/ghostscript/gs
    echo "  ✓ Copied gs executable"
else
    echo "  ✗ Ghostscript executable not found"
    exit 1
fi

# Copy Ghostscript libraries (Linux)
if [ "$(uname -s)" = "Linux" ]; then
    if [ -d "$GS_SOURCE/lib" ]; then
        mkdir -p build/resources/ghostscript/lib
        find "$GS_SOURCE/lib" -name "*gs*.so*" -exec cp {} build/resources/ghostscript/lib/ \;
        echo "  ✓ Copied Ghostscript libraries"
    fi
fi

# Copy Ghostscript data files if they exist
if [ -d "$GS_SOURCE/share/ghostscript" ]; then
    cp -r "$GS_SOURCE/share/ghostscript" build/resources/ghostscript/share
    echo "  ✓ Copied Ghostscript data files"
fi

# Calculate Ghostscript bundle size
GS_SIZE=$(du -sh build/resources/ghostscript | cut -f1)
echo "  ℹ Ghostscript bundle size: $GS_SIZE"

# Step 4: Build Python application with PyInstaller
echo ""
echo "[4/7] Building Python application with PyInstaller..."
if [ -f "transmutation_codex.spec" ]; then
    uv run pyinstaller transmutation_codex.spec --clean
    echo "  ✓ PyInstaller build complete"
else
    echo "  ✗ transmutation_codex.spec not found"
    echo "  Skipping PyInstaller build"
fi

# Step 5: Package for distribution (platform-specific)
echo ""
echo "[5/7] Creating distribution package..."

if [ "$(uname -s)" = "Darwin" ]; then
    # macOS: Create .app bundle or .dmg
    echo "  Creating macOS application bundle..."
    # TODO: Implement macOS packaging
    echo "  ℹ macOS packaging not yet implemented"

elif [ "$(uname -s)" = "Linux" ]; then
    # Linux: Create .tar.gz or AppImage
    echo "  Creating Linux archive..."
    cd dist
    tar -czf "aichemist-transmutation-codex-${VERSION}-linux.tar.gz" aichemist_transmutation_codex/
    cd ..
    echo "  ✓ Created: dist/aichemist-transmutation-codex-${VERSION}-linux.tar.gz"
fi

# Step 6: Create installer (platform-specific)
echo ""
echo "[6/7] Creating installer..."

if [ "$(uname -s)" = "Darwin" ]; then
    echo "  ℹ macOS installer creation not yet implemented"
    echo "  Use 'create-dmg' or 'electron-builder' for .dmg creation"

elif [ "$(uname -s)" = "Linux" ]; then
    echo "  ℹ Linux installer creation not yet implemented"
    echo "  Use 'electron-builder' for .deb/.rpm/.AppImage creation"
fi

# Step 7: Calculate total bundle size
echo ""
echo "[7/7] Build summary..."
TOTAL_SIZE=$(du -sh build/resources | cut -f1)
echo "  Total bundle size: $TOTAL_SIZE"
echo "  Tesseract: $TESSERACT_SIZE"
echo "  Ghostscript: $GS_SIZE"

echo ""
echo "====================================================="
echo "  ✓ Build complete!"
echo "====================================================="
echo ""
echo "Next steps:"
echo "  1. Test the executable: ./dist/aichemist_transmutation_codex/aichemist_transmutation_codex"
echo "  2. Verify bundled executables work"
echo "  3. Create platform-specific installer"
echo ""




