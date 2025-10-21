#!/usr/bin/env python3
"""Check premium converter dependencies."""

import shutil
import subprocess
import sys
from pathlib import Path


def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        return True, f"✅ {package_name}"
    except ImportError:
        return False, f"❌ {package_name}"


def check_system_command(command, description):
    """Check if a system command is available."""
    if shutil.which(command):
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, timeout=5
            )
            version = (
                result.stdout.split("\n")[0] if result.stdout else "Unknown version"
            )
            return True, f"✅ {description}: {version}"
        except:
            return True, f"✅ {description}: Available"
    else:
        return False, f"❌ {description}: Not found"


def check_tesseract():
    """Check Tesseract OCR installation."""
    # Check common installation paths
    tesseract_paths = [
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
    ]

    for path in tesseract_paths:
        if Path(path).exists():
            try:
                result = subprocess.run(
                    [path, "--version"], capture_output=True, text=True, timeout=5
                )
                version = (
                    result.stdout.split("\n")[0] if result.stdout else "Unknown version"
                )
                return True, f"✅ Tesseract OCR: {version} (at {path})"
            except:
                return True, f"✅ Tesseract OCR: Available (at {path})"

    # Check PATH
    if shutil.which("tesseract"):
        try:
            result = subprocess.run(
                ["tesseract", "--version"], capture_output=True, text=True, timeout=5
            )
            version = (
                result.stdout.split("\n")[0] if result.stdout else "Unknown version"
            )
            return True, f"✅ Tesseract OCR: {version} (in PATH)"
        except:
            return True, "✅ Tesseract OCR: Available (in PATH)"

    return False, "❌ Tesseract OCR: Not found"


def check_ghostscript():
    """Check Ghostscript installation."""
    # Check common installation paths
    gs_paths = [
        "C:\\Program Files\\gs",
        "C:\\Program Files (x86)\\gs",
        "/usr/bin/gs",
        "/usr/local/bin/gs",
        "/opt/homebrew/bin/gs",
    ]

    for path in gs_paths:
        if Path(path).exists():
            # Find the latest version
            if sys.platform == "win32":
                version_dirs = list(Path(path).glob("gs*"))
                if version_dirs:
                    latest_dir = max(version_dirs, key=lambda x: x.name)
                    gs_exe = latest_dir / "bin" / "gswin64c.exe"
                    if gs_exe.exists():
                        try:
                            result = subprocess.run(
                                [str(gs_exe), "--version"],
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            version = (
                                result.stdout.split("\n")[0]
                                if result.stdout
                                else "Unknown version"
                            )
                            return True, f"✅ Ghostscript: {version} (at {gs_exe})"
                        except:
                            return True, f"✅ Ghostscript: Available (at {gs_exe})"
            else:
                gs_exe = Path(path) / "bin" / "gs"
                if gs_exe.exists():
                    try:
                        result = subprocess.run(
                            [str(gs_exe), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        version = (
                            result.stdout.split("\n")[0]
                            if result.stdout
                            else "Unknown version"
                        )
                        return True, f"✅ Ghostscript: {version} (at {gs_exe})"
                    except:
                        return True, f"✅ Ghostscript: Available (at {gs_exe})"

    # Check PATH
    if shutil.which("gswin64c") or shutil.which("gs"):
        command = "gswin64c" if shutil.which("gswin64c") else "gs"
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, timeout=5
            )
            version = (
                result.stdout.split("\n")[0] if result.stdout else "Unknown version"
            )
            return True, f"✅ Ghostscript: {version} (in PATH)"
        except:
            return True, "✅ Ghostscript: Available (in PATH)"

    return False, "❌ Ghostscript: Not found"


def check_libreoffice():
    """Check LibreOffice installation."""
    # Check common installation paths
    lo_paths = [
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
        "/usr/bin/libreoffice",
        "/usr/local/bin/libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]

    for path in lo_paths:
        if Path(path).exists():
            try:
                result = subprocess.run(
                    [path, "--version"], capture_output=True, text=True, timeout=5
                )
                version = (
                    result.stdout.split("\n")[0] if result.stdout else "Unknown version"
                )
                return True, f"✅ LibreOffice: {version} (at {path})"
            except:
                return True, f"✅ LibreOffice: Available (at {path})"

    # Check PATH
    if shutil.which("soffice") or shutil.which("libreoffice"):
        command = "soffice" if shutil.which("soffice") else "libreoffice"
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, timeout=5
            )
            version = (
                result.stdout.split("\n")[0] if result.stdout else "Unknown version"
            )
            return True, f"✅ LibreOffice: {version} (in PATH)"
        except:
            return True, "✅ LibreOffice: Available (in PATH)"

    return False, "❌ LibreOffice: Not found"


def main():
    """Check all premium converter dependencies."""
    print("🔍 Checking Premium Converter Dependencies")
    print("=" * 60)
    print()

    # Python packages
    print("Python Packages:")
    print("-" * 20)

    python_packages = [
        ("openpyxl", "openpyxl"),
        ("pandas", "pandas"),
        ("tabula-py", "tabula"),
        ("python-pptx", "pptx"),
        ("ebooklib", "ebooklib"),
        ("beautifulsoup4", "bs4"),
        ("docutils", "docutils"),
        ("pygments", "pygments"),
        ("pikepdf", "pikepdf"),
        ("pdf2image", "pdf2image"),
        ("Pillow", "PIL"),
        ("pytesseract", "pytesseract"),
        ("reportlab", "reportlab"),
        ("PyPDF2", "PyPDF2"),
        ("python-docx", "docx"),
        ("mammoth", "mammoth"),
        ("markdown", "markdown"),
        ("ocrmypdf", "ocrmypdf"),
        ("PyMuPDF", "fitz"),
        ("pdfminer.six", "pdfminer"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("cryptography", "cryptography"),
        ("supabase", "supabase"),
        ("python-dotenv", "dotenv"),
    ]

    python_results = []
    for package_name, import_name in python_packages:
        success, message = check_python_package(package_name, import_name)
        python_results.append((success, message))
        print(f"  {message}")

    print()

    # System commands
    print("System Commands:")
    print("-" * 20)

    system_commands = [
        ("node", "Node.js"),
        ("npm", "npm"),
        ("python", "Python"),
        ("pip", "pip"),
        ("uv", "UV Package Manager"),
    ]

    system_results = []
    for command, description in system_commands:
        success, message = check_system_command(command, description)
        system_results.append((success, message))
        print(f"  {message}")

    print()

    # Specialized tools
    print("Specialized Tools:")
    print("-" * 20)

    # Tesseract
    success, message = check_tesseract()
    print(f"  {message}")
    tesseract_ok = success

    # Ghostscript
    success, message = check_ghostscript()
    print(f"  {message}")
    ghostscript_ok = success

    # LibreOffice
    success, message = check_libreoffice()
    print(f"  {message}")
    libreoffice_ok = success

    # Pandoc
    success, message = check_system_command("pandoc", "Pandoc")
    print(f"  {message}")
    pandoc_ok = success

    # MiKTeX/LaTeX
    success, message = check_system_command("pdflatex", "MiKTeX/LaTeX")
    print(f"  {message}")
    latex_ok = success

    print()

    # Summary
    print("Summary:")
    print("-" * 20)

    python_ok = sum(1 for success, _ in python_results if success)
    python_total = len(python_results)
    system_ok = sum(1 for success, _ in system_results if success)
    system_total = len(system_results)

    print(f"Python packages: {python_ok}/{python_total} ✅")
    print(f"System commands: {system_ok}/{system_total} ✅")
    print(f"Tesseract OCR: {'✅' if tesseract_ok else '❌'}")
    print(f"Ghostscript: {'✅' if ghostscript_ok else '❌'}")
    print(f"LibreOffice: {'✅' if libreoffice_ok else '❌'}")
    print(f"Pandoc: {'✅' if pandoc_ok else '❌'}")
    print(f"LaTeX: {'✅' if latex_ok else '❌'}")

    print()

    # Recommendations
    if not tesseract_ok:
        print("⚠️  Tesseract OCR is required for image-to-text and PDF OCR operations")
        print("   Install: https://github.com/UB-Mannheim/tesseract/wiki")

    if not ghostscript_ok:
        print("⚠️  Ghostscript is required for advanced PDF operations")
        print("   Install: https://ghostscript.com/releases/gsdnld.html")

    if not libreoffice_ok:
        print(
            "ℹ️  LibreOffice is optional but recommended for advanced document conversions"
        )
        print("   Install: https://www.libreoffice.org/download/")

    if not pandoc_ok:
        print("ℹ️  Pandoc is optional but recommended for universal document conversion")
        print("   Install: https://pandoc.org/installing.html")

    if not latex_ok:
        print("ℹ️  LaTeX is optional but recommended for high-quality PDF generation")
        print("   Install: https://miktex.org/download")

    # Overall status
    critical_missing = []
    if not tesseract_ok:
        critical_missing.append("Tesseract OCR")
    if not ghostscript_ok:
        critical_missing.append("Ghostscript")

    if critical_missing:
        print()
        print("❌ Critical dependencies missing:")
        for dep in critical_missing:
            print(f"   - {dep}")
        print()
        print("Run the setup script to install missing dependencies:")
        print("   .\\scripts\\setup_external_dependencies.ps1")
        return False
    else:
        print()
        print("🎉 All critical dependencies are available!")
        print("   Premium converters should work correctly.")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
