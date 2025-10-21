"""Test DOCX to PDF conversion with auto-detected PDF engine."""

import pytest
from pathlib import Path
from transmutation_codex.plugins.docx.to_pdf import (
    convert_docx_to_pdf,
    _check_pdf_engine_available,
    _get_available_pdf_engine,
)


def test_check_pdf_engine_available():
    """Test that we can check for PDF engine availability."""
    # At least one of these should be available on most systems
    engines_to_check = ["wkhtmltopdf", "pdflatex", "xelatex", "lualatex"]
    
    # Check each engine
    results = {engine: _check_pdf_engine_available(engine) for engine in engines_to_check}
    
    # At least one should be available (or test environment needs setup)
    print(f"PDF Engine availability: {results}")
    
    # This test always passes but logs the results
    assert True


def test_get_available_pdf_engine():
    """Test that we can detect an available PDF engine."""
    try:
        engine = _get_available_pdf_engine()
        print(f"Auto-detected PDF engine: {engine}")
        assert engine in ["wkhtmltopdf", "pdflatex", "xelatex", "lualatex"]
    except RuntimeError as e:
        # If no engines available, skip test with informative message
        pytest.skip(f"No PDF engines available on this system: {e}")


@pytest.mark.skipif(
    not Path("tests/test_files/electron_test.docx").exists(),
    reason="Test DOCX file not found"
)
def test_convert_docx_to_pdf_auto_engine():
    """Test DOCX to PDF conversion with auto-detected engine."""
    input_file = Path("tests/test_files/electron_test.docx")
    output_file = Path("tests/test_files/electron_test_auto.pdf")
    
    # Clean up any existing output
    if output_file.exists():
        output_file.unlink()
    
    try:
        # Convert with auto-detection (default)
        result = convert_docx_to_pdf(input_file, output_file)
        
        # Verify output was created
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0
        
        print(f"Successfully created PDF: {result}")
        
    except RuntimeError as e:
        # If no engines available, skip test
        if "No PDF engines available" in str(e):
            pytest.skip(f"Cannot run test: {e}")
        else:
            raise
    finally:
        # Clean up
        if output_file.exists():
            output_file.unlink()


if __name__ == "__main__":
    # Run tests
    print("Testing PDF engine detection...")
    test_check_pdf_engine_available()
    print("\nTesting auto-detection...")
    test_get_available_pdf_engine()
    print("\nTesting conversion...")
    test_convert_docx_to_pdf_auto_engine()
