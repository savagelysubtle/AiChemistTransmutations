"""Tests for XLSX to HTML conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.xlsx.to_html import convert_xlsx_to_html


class TestXLSXToHTMLConverter:
    """Test the XLSX to HTML converter."""

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
    def mock_pandas(self):
        """Mock pandas for testing."""
        with (
            patch(
                "transmutation_codex.plugins.xlsx.to_html.pd.ExcelFile"
            ) as mock_excel_file,
            patch(
                "transmutation_codex.plugins.xlsx.to_html.pd.read_excel"
            ) as mock_read_excel,
        ):
            mock_file = Mock()
            mock_excel_file.return_value = mock_file
            mock_file.sheet_names = ["Sheet1"]

            # Mock DataFrame for each sheet
            mock_df = Mock()
            mock_df.empty = False
            mock_df.to_html.return_value = "<table><tr><td>Test</td></tr></table>"
            mock_read_excel.return_value = mock_df

            yield mock_excel_file, mock_read_excel

    def test_convert_xlsx_to_html_basic(
        self, test_xlsx_path, temp_output_dir, mock_pandas
    ):
        """Test basic XLSX to HTML conversion."""
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_xlsx_to_html(test_xlsx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path == output_path

        # Verify HTML content
        content = result_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html lang='en'>" in content
        assert "<table>" in content
        assert "Test" in content

    def test_convert_xlsx_to_html_auto_output(
        self, test_xlsx_path, temp_output_dir, mock_pandas
    ):
        """Test XLSX to HTML conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_xlsx_to_html(test_xlsx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path.name == "electron_test.html"

    def test_convert_xlsx_to_html_custom_options(
        self, test_xlsx_path, temp_output_dir, mock_pandas
    ):
        """Test XLSX to HTML conversion with custom options."""
        output_path = temp_output_dir / "test_output.html"

        custom_options = {
            "include_styling": True,
            "include_navigation": True,
            "table_class": "excel-table",
            "max_rows": 1000,
            "include_index": False,
        }

        result_path = convert_xlsx_to_html(
            test_xlsx_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert "border-collapse: collapse" in content
        assert (
            "Excel Export: electron_test" in content
        )  # Default title based on filename

    def test_convert_xlsx_to_html_invalid_file(self, temp_output_dir):
        """Test XLSX to HTML conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.xlsx"
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ValidationError):
            convert_xlsx_to_html(invalid_path, output_path)

    def test_convert_xlsx_to_html_non_xlsx_file(self, temp_output_dir):
        """Test XLSX to HTML conversion with non-XLSX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an XLSX")
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ConversionError, match="Failed to load Excel file"):
            convert_xlsx_to_html(text_file, output_path)

    def test_progress_tracking(self, test_xlsx_path, temp_output_dir, mock_pandas):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.html"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.xlsx.to_html.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.xlsx.to_html.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.xlsx.to_html.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_xlsx_to_html(test_xlsx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_xlsx_path, temp_output_dir, mock_pandas):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.html"

        with patch("transmutation_codex.plugins.xlsx.to_html.publish") as mock_publish:
            result_path = convert_xlsx_to_html(test_xlsx_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "xlsx2html"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        xlsx_to_html_converters = registry.get_plugins_for_conversion("xlsx", "html")
        assert len(xlsx_to_html_converters) >= 1
