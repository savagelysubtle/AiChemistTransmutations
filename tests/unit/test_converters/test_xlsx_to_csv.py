"""Tests for XLSX to CSV conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.xlsx.to_csv import convert_xlsx_to_csv


class TestXLSXToCSVConverter:
    """Test the XLSX to CSV converter."""

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
            "transmutation_codex.plugins.xlsx.to_csv.load_workbook"
        ) as mock_load:
            mock_wb = Mock()
            mock_load.return_value = mock_wb
            mock_ws = Mock()
            mock_wb.active = mock_ws
            mock_ws.iter_rows.return_value = [
                ["Header1", "Header2", "Header3"],
                ["Value1", "Value2", "Value3"],
                ["Value4", "Value5", "Value6"],
            ]
            yield mock_load

    def test_convert_xlsx_to_csv_basic(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test basic XLSX to CSV conversion."""
        output_path = temp_output_dir / "test_output.csv"

        result_path = convert_xlsx_to_csv(test_xlsx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".csv"
        assert result_path == output_path

        # Verify CSV content
        content = result_path.read_text(encoding="utf-8")
        assert "Header1,Header2,Header3" in content
        assert "Value1,Value2,Value3" in content

    def test_convert_xlsx_to_csv_auto_output(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test XLSX to CSV conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_xlsx_to_csv(test_xlsx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".csv"
        assert result_path.name == "electron_test.csv"

    def test_convert_xlsx_to_csv_custom_options(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test XLSX to CSV conversion with custom options."""
        output_path = temp_output_dir / "test_output.csv"

        custom_options = {
            "delimiter": ";",
            "sheet_name": "Sheet1",
            "encoding": "utf-8",
            "include_headers": True,
        }

        result_path = convert_xlsx_to_csv(test_xlsx_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".csv"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert ";" in content  # Custom delimiter

    def test_convert_xlsx_to_csv_invalid_file(self, temp_output_dir):
        """Test XLSX to CSV conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.xlsx"
        output_path = temp_output_dir / "output.csv"

        with pytest.raises(ValidationError):
            convert_xlsx_to_csv(invalid_path, output_path)

    def test_convert_xlsx_to_csv_non_xlsx_file(self, temp_output_dir):
        """Test XLSX to CSV conversion with non-XLSX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an XLSX")
        output_path = temp_output_dir / "output.csv"

        with pytest.raises(ConversionError, match="Failed to load Excel file"):
            convert_xlsx_to_csv(text_file, output_path)

    def test_progress_tracking(self, test_xlsx_path, temp_output_dir, mock_openpyxl):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.csv"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.xlsx.to_csv.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.xlsx.to_csv.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.xlsx.to_csv.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_xlsx_to_csv(test_xlsx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_xlsx_path, temp_output_dir, mock_openpyxl):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.csv"

        with patch("transmutation_codex.plugins.xlsx.to_csv.publish") as mock_publish:
            result_path = convert_xlsx_to_csv(test_xlsx_path, output_path)

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
        xlsx_to_csv_converters = registry.get_plugins_for_conversion("xlsx", "csv")
        assert len(xlsx_to_csv_converters) >= 1
