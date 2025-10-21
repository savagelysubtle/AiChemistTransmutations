"""Test bundled Tesseract functionality.

This test script verifies that:
1. Bundled Tesseract can be detected
2. Tesseract executable exists and runs
3. Required language packs are present
4. OCR conversion works with bundled Tesseract

Usage:
    python tests/test_bundled_tesseract.py
    uv run pytest tests/test_bundled_tesseract.py -v
"""

import os
import subprocess
import sys

import pytest


def test_bundled_tesseract_detection():
    """Test that bundled Tesseract can be detected."""
    from transmutation_codex.plugins.pdf.to_editable_pdf import (
        _get_bundled_tesseract_path,
    )

    bundled_path = _get_bundled_tesseract_path()

    if bundled_path:
        print(f"✓ Bundled Tesseract found at: {bundled_path}")
        assert bundled_path.exists(), "Bundled Tesseract path exists"
        assert bundled_path.name == "tesseract.exe", "Correct executable name"
    else:
        print("⚠ No bundled Tesseract found (expected in development)")
        print("  This is normal if you haven't run the build script yet")
        pytest.skip("Bundled Tesseract not found (development environment)")


def test_bundled_tesseract_structure():
    """Test that bundled Tesseract has the required structure."""
    from transmutation_codex.plugins.pdf.to_editable_pdf import (
        _get_bundled_tesseract_path,
    )

    bundled_path = _get_bundled_tesseract_path()

    if not bundled_path:
        pytest.skip("Bundled Tesseract not found")

    tesseract_dir = bundled_path.parent

    # Check for tessdata directory
    tessdata_dir = tesseract_dir / "tessdata"
    assert tessdata_dir.exists(), "tessdata directory exists"

    # Check for English language pack (minimum requirement)
    eng_traineddata = tessdata_dir / "eng.traineddata"
    assert eng_traineddata.exists(), "English language pack exists"

    # Check for orientation detection data
    osd_traineddata = tessdata_dir / "osd.traineddata"
    if osd_traineddata.exists():
        print("✓ Orientation detection data present")
    else:
        print("⚠ Orientation detection data not found (optional)")

    print(f"✓ Bundled Tesseract structure valid: {tesseract_dir}")


def test_bundled_tesseract_runs():
    """Test that bundled Tesseract executable runs correctly."""
    from transmutation_codex.plugins.pdf.to_editable_pdf import (
        _get_bundled_tesseract_path,
    )

    bundled_path = _get_bundled_tesseract_path()

    if not bundled_path:
        pytest.skip("Bundled Tesseract not found")

    # Try to run tesseract --version
    result = subprocess.run(
        [str(bundled_path), "--version"], capture_output=True, text=True, timeout=10
    )

    assert result.returncode == 0, "Tesseract runs successfully"
    assert "tesseract" in result.stdout.lower(), "Valid Tesseract output"

    # Parse version
    version_line = result.stdout.split("\n")[0]
    print(f"✓ Tesseract version: {version_line}")


def test_bundled_tesseract_path_configuration():
    """Test that bundled Tesseract is added to PATH correctly."""
    from transmutation_codex.plugins.pdf.to_editable_pdf import (
        _configure_tesseract_path,
        _get_bundled_tesseract_path,
    )

    bundled_path = _get_bundled_tesseract_path()

    if not bundled_path:
        pytest.skip("Bundled Tesseract not found")

    # Get current PATH
    original_path = os.environ.get("PATH", "")

    # Configure Tesseract (should add to PATH if not already present)
    _configure_tesseract_path()

    # Check if bundled directory is in PATH
    bundled_dir = str(bundled_path.parent)
    current_path = os.environ.get("PATH", "")

    assert bundled_dir in current_path, "Bundled Tesseract directory added to PATH"
    print(f"✓ Bundled Tesseract directory in PATH: {bundled_dir}")


@pytest.mark.slow
def test_bundled_tesseract_ocr_conversion():
    """Test actual OCR conversion using bundled Tesseract.

    This test requires a sample PDF file in tests/test_files/
    """
    pytest.skip("OCR conversion test requires sample PDF - implement when needed")

    # Example implementation:
    # from transmutation_codex.plugins.pdf.to_editable_pdf import convert_pdf_to_editable
    # from transmutation_codex.plugins.pdf.to_editable_pdf import _get_bundled_tesseract_path
    #
    # bundled_path = _get_bundled_tesseract_path()
    # if not bundled_path:
    #     pytest.skip("Bundled Tesseract not found")
    #
    # test_pdf = Path("tests/test_files/sample_scanned.pdf")
    # if not test_pdf.exists():
    #     pytest.skip("Sample PDF not found")
    #
    # output_pdf = Path("tests/test_files/output_editable.pdf")
    # result = convert_pdf_to_editable(test_pdf, output_pdf)
    #
    # assert result.exists(), "Conversion created output file"
    # assert result.stat().st_size > 0, "Output file has content"
    #
    # # Clean up
    # output_pdf.unlink()
    # print("✓ OCR conversion successful")


def test_production_deployment_checklist():
    """Verify production deployment checklist items."""
    from transmutation_codex.plugins.pdf.to_editable_pdf import (
        _get_bundled_tesseract_path,
    )

    bundled_path = _get_bundled_tesseract_path()

    if not bundled_path:
        print("\n📋 Production Deployment Checklist:")
        print("  ☐ Run build_installer.ps1 script")
        print("  ☐ Verify bundled Tesseract in build/resources/tesseract/")
        print("  ☐ Build with PyInstaller (transmutation_codex.spec)")
        print("  ☐ Create installer with Inno Setup (installer.iss)")
        print("  ☐ Test on clean Windows machine")
        print("  ☐ Sign installer (optional)")
        pytest.skip("Bundled Tesseract not found - run build script")
    else:
        print("\n✅ Production Deployment Checklist:")
        print("  ✓ Bundled Tesseract detected")

        tesseract_dir = bundled_path.parent

        # Check required files
        checklist = {
            "Tesseract executable": bundled_path,
            "tessdata directory": tesseract_dir / "tessdata",
            "English language pack": tesseract_dir / "tessdata" / "eng.traineddata",
            "LICENSE file": tesseract_dir / "LICENSE",
        }

        all_present = True
        for item, path in checklist.items():
            if path.exists():
                print(f"  ✓ {item}")
            else:
                print(f"  ☐ {item} - MISSING")
                all_present = False

        assert all_present, "All required bundled files present"


if __name__ == "__main__":
    """Run tests directly for quick verification."""
    print("====================================================")
    print("  Bundled Tesseract Test Suite")
    print("====================================================\n")

    tests = [
        ("Detection", test_bundled_tesseract_detection),
        ("Structure", test_bundled_tesseract_structure),
        ("Execution", test_bundled_tesseract_runs),
        ("PATH Configuration", test_bundled_tesseract_path_configuration),
        ("Deployment Checklist", test_production_deployment_checklist),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for name, test_func in tests:
        try:
            print(f"[TEST] {name}...")
            test_func()
            print("  ✓ PASSED\n")
            passed += 1
        except pytest.skip.Exception as e:
            print(f"  ⊘ SKIPPED: {e}\n")
            skipped += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            failed += 1

    print("====================================================")
    print(f"  Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("====================================================")

    sys.exit(0 if failed == 0 else 1)




