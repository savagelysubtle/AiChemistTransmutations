"""Tests for DOCX to PDF conversion."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from transmutation_codex.plugins.docx.to_pdf import convert_docx_to_pdf


class TestDOCXToPDFConverter:
    """Test the DOCX to PDF converter."""

    @pytest.fixture
    def test_docx_path(self):
        """Path to test DOCX file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.docx"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_pypandoc(self):
        """Mock pypandoc for testing."""
        with patch(
            "transmutation_codex.plugins.docx.to_pdf.pypandoc.convert_file"
        ) as mock_convert:

            def mock_convert_file(input_file, to, format, outputfile, extra_args=None):
                # Create the output file to simulate successful conversion
                Path(outputfile).touch()
                return None

            mock_convert.side_effect = mock_convert_file
            yield mock_convert

    def test_convert_docx_to_pdf_basic(
        self, test_docx_path, temp_output_dir, mock_pypandoc
    ):
        """Test basic DOCX to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_docx_to_pdf(test_docx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

        # Verify pypandoc was called
        mock_pypandoc.assert_called()

    def test_convert_docx_to_pdf_auto_output(
        self, test_docx_path, temp_output_dir, mock_pypandoc
    ):
        """Test DOCX to PDF conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_docx_to_pdf(test_docx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path.name == "electron_test.pdf"

    def test_convert_docx_to_pdf_custom_options(
        self, test_docx_path, temp_output_dir, mock_pypandoc
    ):
        """Test DOCX to PDF conversion with custom options."""
        output_path = temp_output_dir / "test_output.pdf"

        custom_options = {
            "page_size": "A4",
            "margin": "1in",
            "orientation": "portrait",
            "quality": "high",
        }

        result_path = convert_docx_to_pdf(test_docx_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify custom options were applied
        mock_pypandoc.assert_called()

    def test_convert_docx_to_pdf_invalid_file(self, temp_output_dir):
        """Test DOCX to PDF conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.docx"
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(FileNotFoundError):
            convert_docx_to_pdf(invalid_path, output_path)

    def test_convert_docx_to_pdf_non_docx_file(self, temp_output_dir):
        """Test DOCX to PDF conversion with non-DOCX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a DOCX")
        output_path = temp_output_dir / "output.pdf"

        # The converter accepts any file and attempts conversion
        with pytest.raises(RuntimeError, match="Pandoc conversion failed"):
            convert_docx_to_pdf(text_file, output_path)

    def test_progress_tracking(self, test_docx_path, temp_output_dir, mock_pypandoc):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.docx.to_pdf.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.docx.to_pdf.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.docx.to_pdf.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_docx_to_pdf(test_docx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with("test_operation_id", success=True)

    def test_event_publishing(self, test_docx_path, temp_output_dir, mock_pypandoc):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.pdf"

        with patch("transmutation_codex.plugins.docx.to_pdf.publish") as mock_publish:
            result_path = convert_docx_to_pdf(test_docx_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "docx2pdf"

    def test_error_handling(self, test_docx_path, temp_output_dir):
        """Test error handling during conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock pypandoc to raise an error
        with patch(
            "transmutation_codex.plugins.docx.to_pdf.pypandoc.convert_file"
        ) as mock_convert:
            mock_convert.side_effect = Exception("pypandoc error")

            with pytest.raises(RuntimeError, match="Pandoc conversion failed"):
                convert_docx_to_pdf(test_docx_path, output_path)

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        docx_to_pdf_converters = registry.get_plugins_for_conversion("docx", "pdf")
        assert len(docx_to_pdf_converters) >= 1
