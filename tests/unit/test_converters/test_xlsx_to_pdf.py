"""Tests for XLSX to PDF conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.xlsx.to_pdf import convert_xlsx_to_pdf


class TestXLSXToPDFConverter:
    """Test the XLSX to PDF converter."""

    @pytest.fixture
    def test_xlsx_path(self):
        """Path to test XLSX file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.xlsx"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_openpyxl(self):
        """Mock openpyxl for testing."""
        with patch(
            "transmutation_codex.plugins.xlsx.to_pdf.openpyxl.load_workbook"
        ) as mock_load:
            mock_wb = Mock()
            mock_load.return_value = mock_wb
            mock_ws = Mock()
            mock_wb.active = mock_ws
            mock_wb.sheetnames = ["Sheet1"]  # Add sheetnames attribute

            # Make workbook subscriptable to access worksheets by name
            mock_wb.__getitem__ = Mock(return_value=mock_ws)

            # Add worksheet properties
            mock_ws.max_row = 3
            mock_ws.max_column = 3

            mock_ws.iter_rows.return_value = [
                ["Header1", "Header2", "Header3"],
                ["Value1", "Value2", "Value3"],
                ["Value4", "Value5", "Value6"],
            ]
            yield mock_load

    @pytest.fixture
    def mock_reportlab(self):
        """Mock ReportLab for testing."""
        with patch(
            "transmutation_codex.plugins.xlsx.to_pdf.SimpleDocTemplate"
        ) as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance

            # Mock the build method to create the output file
            def mock_build(story):
                # Create the output file to simulate successful PDF generation
                output_path = mock_doc.call_args[0][
                    0
                ]  # First argument is the output path
                Path(output_path).touch()

            mock_doc_instance.build = mock_build
            yield mock_doc

    def test_convert_xlsx_to_pdf_basic(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl, mock_reportlab
    ):
        """Test basic XLSX to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_xlsx_to_pdf(test_xlsx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

        # Verify ReportLab was called
        mock_reportlab.assert_called()

    def test_convert_xlsx_to_pdf_auto_output(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl, mock_reportlab
    ):
        """Test XLSX to PDF conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_xlsx_to_pdf(test_xlsx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path.name == "electron_test.pdf"

    def test_convert_xlsx_to_pdf_custom_options(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl, mock_reportlab
    ):
        """Test XLSX to PDF conversion with custom options."""
        output_path = temp_output_dir / "test_output.pdf"

        custom_options = {
            "page_size": "A4",
            "margin": "1in",
            "css_styles": "table { border-collapse: collapse; }",
            "sheet_name": "Sheet1",
            "include_headers": True,
        }

        result_path = convert_xlsx_to_pdf(test_xlsx_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify custom options were applied
        mock_reportlab.assert_called()

    def test_convert_xlsx_to_pdf_invalid_file(self, temp_output_dir):
        """Test XLSX to PDF conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.xlsx"
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ValidationError):
            convert_xlsx_to_pdf(invalid_path, output_path)

    def test_convert_xlsx_to_pdf_non_xlsx_file(self, temp_output_dir):
        """Test XLSX to PDF conversion with non-XLSX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an XLSX")
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ConversionError, match="Failed to load Excel file"):
            convert_xlsx_to_pdf(text_file, output_path)

    def test_progress_tracking(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl, mock_reportlab
    ):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.xlsx.to_pdf.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.xlsx.to_pdf.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.xlsx.to_pdf.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_xlsx_to_pdf(test_xlsx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl, mock_reportlab
    ):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.pdf"

        with patch("transmutation_codex.plugins.xlsx.to_pdf.publish") as mock_publish:
            result_path = convert_xlsx_to_pdf(test_xlsx_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "xlsx2pdf"

    def test_error_handling(self, test_xlsx_path, temp_output_dir, mock_openpyxl):
        """Test error handling during conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock WeasyPrint to raise an error
        with patch(
            "transmutation_codex.plugins.xlsx.to_pdf.SimpleDocTemplate"
        ) as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            mock_doc_instance.build.side_effect = Exception("ReportLab error")

            with pytest.raises(ConversionError, match="Excel to PDF conversion failed"):
                convert_xlsx_to_pdf(test_xlsx_path, output_path)

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        xlsx_to_pdf_converters = registry.get_plugins_for_conversion("xlsx", "pdf")
        assert len(xlsx_to_pdf_converters) >= 1
