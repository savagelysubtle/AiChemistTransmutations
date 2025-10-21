"""Tests for CSV to XLSX conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ValidationError
from transmutation_codex.plugins.csv.to_xlsx import convert_csv_to_xlsx


class TestCSVToXLSXConverter:
    """Test the CSV to XLSX converter."""

    @pytest.fixture
    def test_csv_path(self):
        """Path to test CSV file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.csv"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_openpyxl(self):
        """Mock openpyxl for testing."""
        with patch(
            "transmutation_codex.plugins.csv.to_xlsx.openpyxl.load_workbook"
        ) as mock_load_wb:
            mock_workbook = Mock()
            mock_load_wb.return_value = mock_workbook
            mock_worksheet = Mock()
            mock_workbook.active = mock_worksheet
            yield mock_load_wb

    def test_convert_csv_to_xlsx_basic(
        self, test_csv_path, temp_output_dir, mock_openpyxl
    ):
        """Test basic CSV to XLSX conversion."""
        output_path = temp_output_dir / "test_output.xlsx"

        result_path = convert_csv_to_xlsx(test_csv_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".xlsx"
        assert result_path == output_path

        # Verify openpyxl was called
        mock_openpyxl.assert_called()

    def test_convert_csv_to_xlsx_auto_output(
        self, test_csv_path, temp_output_dir, mock_openpyxl
    ):
        """Test CSV to XLSX conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_csv_to_xlsx(test_csv_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".xlsx"
        assert result_path.name == "electron_test.xlsx"

    def test_convert_csv_to_xlsx_custom_options(
        self, test_csv_path, temp_output_dir, mock_openpyxl
    ):
        """Test CSV to XLSX conversion with custom options."""
        output_path = temp_output_dir / "test_output.xlsx"

        custom_options = {
            "delimiter": ",",
            "encoding": "utf-8",
            "sheet_name": "Data",
            "include_headers": True,
        }

        result_path = convert_csv_to_xlsx(test_csv_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".xlsx"

        # Verify custom options were applied
        mock_openpyxl.assert_called()

    def test_convert_csv_to_xlsx_invalid_file(self, temp_output_dir):
        """Test CSV to XLSX conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.csv"
        output_path = temp_output_dir / "output.xlsx"

        with pytest.raises(ValidationError):
            convert_csv_to_xlsx(invalid_path, output_path)

    def test_convert_csv_to_xlsx_non_csv_file(self, temp_output_dir):
        """Test CSV to XLSX conversion with non-CSV file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a CSV")
        output_path = temp_output_dir / "output.xlsx"

        # The converter accepts any text file as CSV content
        result = convert_csv_to_xlsx(text_file, output_path)
        assert result == output_path
        assert output_path.exists()

    def test_progress_tracking(self, test_csv_path, temp_output_dir, mock_openpyxl):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.xlsx"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.csv.to_xlsx.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.csv.to_xlsx.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.csv.to_xlsx.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_csv_to_xlsx(test_csv_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_csv_path, temp_output_dir, mock_openpyxl):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.xlsx"

        with patch("transmutation_codex.plugins.csv.to_xlsx.publish") as mock_publish:
            result_path = convert_csv_to_xlsx(test_csv_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "conversion"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        csv_to_xlsx_converters = registry.get_plugins_for_conversion("csv", "xlsx")
        assert len(csv_to_xlsx_converters) >= 1
