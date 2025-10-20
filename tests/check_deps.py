#!/usr/bin/env python3
"""Check dependencies."""

import sys
from pathlib import Path

# Ensure the project root is in the path for imports
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check required dependencies."""
    print("🔍 Checking Dependencies")
    print("=" * 50)
    
    dependencies = [
        ("pymupdf", "fitz"),
        ("markdown_pdf", "markdown_pdf"),
        ("pytesseract", "pytesseract"),
        ("PIL", "PIL"),
        ("cv2", "cv2"),
        ("numpy", "numpy"),
        ("pymupdf4llm", "pymupdf4llm"),
    ]
    
    available = []
    missing = []
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
            available.append(package_name)
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    print(f"\n📊 Summary:")
    print(f"Available: {len(available)}")
    print(f"Missing: {len(missing)}")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: uv add " + " ".join(missing))
    
    return len(missing) == 0

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)