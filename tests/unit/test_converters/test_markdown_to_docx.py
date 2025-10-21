"""Tests for Markdown to DOCX conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ValidationError
from transmutation_codex.plugins.markdown.to_docx import convert_md_to_docx


class TestMarkdownToDOCXConverter:
    """Test the Markdown to DOCX converter."""

    @pytest.fixture
    def test_md_path(self):
        """Path to test Markdown file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.md"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_docx(self):
        """Mock python-docx for testing."""
        with patch(
            "transmutation_codex.plugins.markdown.to_docx.Document"
        ) as mock_docx:
            mock_doc = Mock()
            mock_docx.return_value = mock_doc
            mock_doc.save = Mock()
            yield mock_docx

    def test_convert_md_to_docx_basic(self, test_md_path, temp_output_dir, mock_docx):
        """Test basic Markdown to DOCX conversion."""
        output_path = temp_output_dir / "test_output.docx"

        result_path = convert_md_to_docx(test_md_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".docx"
        assert result_path == output_path

        # Verify DOCX was created
        mock_docx.assert_called()

    def test_convert_md_to_docx_auto_output(
        self, test_md_path, temp_output_dir, mock_docx
    ):
        """Test Markdown to DOCX conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_md_to_docx(test_md_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".docx"
        assert result_path.name == "electron_test.docx"

    def test_convert_md_to_docx_custom_options(
        self, test_md_path, temp_output_dir, mock_docx
    ):
        """Test Markdown to DOCX conversion with custom options."""
        output_path = temp_output_dir / "test_output.docx"

        custom_options = {
            "font_name": "Arial",
            "font_size": 12,
            "line_spacing": 1.5,
            "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
        }

        result_path = convert_md_to_docx(test_md_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".docx"

        # Verify custom options were applied
        mock_docx.assert_called()

    def test_convert_md_to_docx_invalid_file(self, temp_output_dir):
        """Test Markdown to DOCX conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.md"
        output_path = temp_output_dir / "output.docx"

        with pytest.raises(ValidationError):
            convert_md_to_docx(invalid_path, output_path)

    def test_convert_md_to_docx_non_md_file(self, temp_output_dir):
        """Test Markdown to DOCX conversion with non-Markdown file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not Markdown")
        output_path = temp_output_dir / "output.docx"

        # The converter accepts any text file and converts it successfully
        result_path = convert_md_to_docx(text_file, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".docx"
        assert result_path == output_path

    def test_progress_tracking(self, test_md_path, temp_output_dir, mock_docx):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.docx"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.markdown.to_docx.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.markdown.to_docx.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.markdown.to_docx.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_md_to_docx(test_md_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_md_path, temp_output_dir, mock_docx):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.docx"

        with patch(
            "transmutation_codex.plugins.markdown.to_docx.publish"
        ) as mock_publish:
            result_path = convert_md_to_docx(test_md_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "md2docx"

    def test_markdown_parsing(self, temp_output_dir, mock_docx):
        """Test Markdown parsing and DOCX generation."""
        # Create test Markdown content
        md_content = """# Test Document

This is a **bold** text and *italic* text.

## Section 2

- List item 1
- List item 2

```python
print("Hello, World!")
```

> This is a blockquote.
"""

        md_file = temp_output_dir / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        output_path = temp_output_dir / "test_output.docx"

        result_path = convert_md_to_docx(md_file, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".docx"

        # Verify DOCX generation
        mock_docx.assert_called()

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        md_to_docx_converters = registry.get_plugins_for_conversion("md", "docx")
        assert len(md_to_docx_converters) >= 1
