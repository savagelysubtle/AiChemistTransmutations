"""Tests for XLSX to Markdown conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.xlsx.to_markdown import convert_xlsx_to_markdown


class TestXLSXToMarkdownConverter:
    """Test the XLSX to Markdown converter."""

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
            "transmutation_codex.plugins.xlsx.to_markdown.load_workbook"
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

    def test_convert_xlsx_to_markdown_basic(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test basic XLSX to Markdown conversion."""
        output_path = temp_output_dir / "test_output.md"

        result_path = convert_xlsx_to_markdown(test_xlsx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path == output_path

        # Verify Markdown content
        content = result_path.read_text(encoding="utf-8")
        assert "| Header1 | Header2 | Header3 |" in content
        assert "| Value1 | Value2 | Value3 |" in content
        assert "| --- | --- | --- |" in content

    def test_convert_xlsx_to_markdown_auto_output(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test XLSX to Markdown conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_xlsx_to_markdown(test_xlsx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path.name == "electron_test.md"

    def test_convert_xlsx_to_markdown_custom_options(
        self, test_xlsx_path, temp_output_dir, mock_openpyxl
    ):
        """Test XLSX to Markdown conversion with custom options."""
        output_path = temp_output_dir / "test_output.md"

        custom_options = {
            "sheet_name": "Sheet1",
            "include_headers": True,
            "title": "# Custom Title",
            "table_format": "pipe",
        }

        result_path = convert_xlsx_to_markdown(
            test_xlsx_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert "# Custom Title" in content

    def test_convert_xlsx_to_markdown_invalid_file(self, temp_output_dir):
        """Test XLSX to Markdown conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.xlsx"
        output_path = temp_output_dir / "output.md"

        with pytest.raises(ValidationError):
            convert_xlsx_to_markdown(invalid_path, output_path)

    def test_convert_xlsx_to_markdown_non_xlsx_file(self, temp_output_dir):
        """Test XLSX to Markdown conversion with non-XLSX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an XLSX")
        output_path = temp_output_dir / "output.md"

        with pytest.raises(ConversionError, match="Failed to load Excel file"):
            convert_xlsx_to_markdown(text_file, output_path)

    def test_progress_tracking(self, test_xlsx_path, temp_output_dir, mock_openpyxl):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.md"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.xlsx.to_markdown.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.xlsx.to_markdown.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.xlsx.to_markdown.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_xlsx_to_markdown(test_xlsx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_xlsx_path, temp_output_dir, mock_openpyxl):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.md"

        with patch(
            "transmutation_codex.plugins.xlsx.to_markdown.publish"
        ) as mock_publish:
            result_path = convert_xlsx_to_markdown(test_xlsx_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "xlsx2md"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        xlsx_to_md_converters = registry.get_plugins_for_conversion("xlsx", "md")
        assert len(xlsx_to_md_converters) >= 1
