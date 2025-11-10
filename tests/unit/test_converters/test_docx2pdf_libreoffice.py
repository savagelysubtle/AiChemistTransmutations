"""Tests for DOCX to PDF conversion using LibreOffice."""

import shutil
from pathlib import Path

import pytest

from transmutation_codex.plugins.docx.to_pdf_libreoffice import (
    _find_libreoffice,
    convert_docx_to_pdf_libreoffice,
)


@pytest.fixture
def sample_docx(tmp_path):
    """Create a sample DOCX file for testing."""
    # Copy from test files
    test_file = Path("tests/test_files/sample.docx")
    if test_file.exists():
        dest = tmp_path / "test.docx"
        shutil.copy(test_file, dest)
        return dest
    return None


class TestLibreOfficeFinder:
    """Tests for LibreOffice detection."""

    def test_find_libreoffice(self):
        """Test that LibreOffice can be found (or not)."""
        result = _find_libreoffice()
        # Should return either a valid path or None
        if result:
            assert Path(result).exists()
            assert isinstance(result, str)


class TestLibreOfficeConversion:
    """Tests for LibreOffice DOCX to PDF conversion."""

    @pytest.mark.skipif(
        not _find_libreoffice(), reason="LibreOffice not installed"
    )
    def test_convert_docx_to_pdf_basic(self, sample_docx, tmp_path):
        """Test basic DOCX to PDF conversion with LibreOffice."""
        if sample_docx is None:
            pytest.skip("Sample DOCX file not found")

        output_pdf = tmp_path / "output.pdf"

        result = convert_docx_to_pdf_libreoffice(sample_docx, output_pdf)

        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    @pytest.mark.skipif(
        not _find_libreoffice(), reason="LibreOffice not installed"
    )
    def test_convert_docx_to_pdf_default_output(self, sample_docx):
        """Test conversion with default output path."""
        if sample_docx is None:
            pytest.skip("Sample DOCX file not found")

        result = convert_docx_to_pdf_libreoffice(sample_docx)

        assert result.exists()
        assert result.stem == sample_docx.stem
        assert result.suffix == ".pdf"

        # Clean up
        result.unlink()

    def test_convert_missing_input_file(self, tmp_path):
        """Test that missing input file raises FileNotFoundError."""
        fake_input = tmp_path / "nonexistent.docx"
        output = tmp_path / "output.pdf"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            convert_docx_to_pdf_libreoffice(fake_input, output)

    def test_convert_invalid_file_extension(self, tmp_path):
        """Test that invalid file extension raises ValueError."""
        fake_input = tmp_path / "test.txt"
        fake_input.touch()
        output = tmp_path / "output.pdf"

        with pytest.raises(ValueError, match="must be .docx or .doc"):
            convert_docx_to_pdf_libreoffice(fake_input, output)

    @pytest.mark.skipif(
        _find_libreoffice() is not None,
        reason="LibreOffice is installed (test for missing LibreOffice)",
    )
    def test_convert_without_libreoffice(self, tmp_path):
        """Test that conversion fails gracefully when LibreOffice is not installed."""
        fake_input = tmp_path / "test.docx"
        fake_input.touch()
        output = tmp_path / "output.pdf"

        with pytest.raises(
            FileNotFoundError, match="LibreOffice not found"
        ):
            convert_docx_to_pdf_libreoffice(fake_input, output)


class TestLibreOfficeQuality:
    """Tests for conversion quality (requires LibreOffice and test files)."""

    @pytest.mark.skipif(
        not _find_libreoffice(), reason="LibreOffice not installed"
    )
    @pytest.mark.slow
    def test_preserve_formatting(self, tmp_path):
        """Test that formatting is preserved (tables, images, styles)."""
        # This would require a reference DOCX with complex formatting
        # For now, just check that conversion completes
        test_file = Path("tests/test_files/formatted_document.docx")
        if not test_file.exists():
            pytest.skip("Formatted test document not found")

        output = tmp_path / "formatted_output.pdf"
        result = convert_docx_to_pdf_libreoffice(test_file, output)

        assert result.exists()
        # Additional quality checks would go here
        # (e.g., checking PDF structure, embedded fonts, etc.)

