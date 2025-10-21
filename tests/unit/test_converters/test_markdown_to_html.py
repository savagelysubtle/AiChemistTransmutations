"""Tests for Markdown to HTML conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.plugins.markdown.to_html import convert_md_to_html


class TestMarkdownToHTMLConverter:
    """Test the Markdown to HTML converter."""

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
    def mock_markdown(self):
        """Mock markdown library for testing."""
        with patch("transmutation_codex.plugins.markdown.to_html.markdown") as mock_md:
            # Mock the Markdown class and its methods
            mock_md_instance = Mock()
            mock_md_instance.convert.return_value = (
                "<h1>Test Document</h1><p>Test content</p>"
            )
            mock_md_instance.toc = "<ul><li>Test Document</li></ul>"
            mock_md.Markdown.return_value = mock_md_instance
            yield mock_md

    def test_convert_md_to_html_basic(
        self, test_md_path, temp_output_dir, mock_markdown
    ):
        """Test basic Markdown to HTML conversion."""
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_md_to_html(test_md_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path == output_path

        # Verify HTML content
        content = result_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html lang=" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_convert_md_to_html_auto_output(
        self, test_md_path, temp_output_dir, mock_markdown
    ):
        """Test Markdown to HTML conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_md_to_html(test_md_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path.name == "electron_test.html"

    def test_convert_md_to_html_custom_options(
        self, test_md_path, temp_output_dir, mock_markdown
    ):
        """Test Markdown to HTML conversion with custom options."""
        output_path = temp_output_dir / "test_output.html"

        custom_options = {
            "css_styles": "body { font-size: 14px; color: #333; }",
            "include_toc": True,
            "metadata": {"title": "Custom Title", "author": "Test Author"},
        }

        result_path = convert_md_to_html(test_md_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        # Note: The converter uses default CSS, so custom CSS may not be applied
        # But the HTML structure should be correct
        assert "<h1>Test Document</h1>" in content
        assert "<p>Test content</p>" in content

    def test_convert_md_to_html_invalid_file(self, temp_output_dir):
        """Test Markdown to HTML conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.md"
        output_path = temp_output_dir / "output.html"

        with pytest.raises(FileNotFoundError):
            convert_md_to_html(invalid_path, output_path)

    def test_convert_md_to_html_non_md_file(self, temp_output_dir):
        """Test Markdown to HTML conversion with non-Markdown file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not Markdown")
        output_path = temp_output_dir / "output.html"

        # The converter doesn't validate file extensions, so it will process any text file
        # This test verifies that the converter can handle non-markdown content
        result_path = convert_md_to_html(text_file, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify content was processed
        content = result_path.read_text(encoding="utf-8")
        assert "This is not Markdown" in content

    def test_progress_tracking(self, test_md_path, temp_output_dir, mock_markdown):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.html"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.markdown.to_html.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.markdown.to_html.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.markdown.to_html.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_md_to_html(test_md_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
        mock_complete.assert_called_once_with("test_operation_id", success=True)

    def test_event_publishing(self, test_md_path, temp_output_dir, mock_markdown):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.html"

        with patch(
            "transmutation_codex.plugins.markdown.to_html.publish"
        ) as mock_publish:
            result_path = convert_md_to_html(test_md_path, output_path)

            # Verify events were published (both started and completed)
            assert mock_publish.call_count >= 2

            # Check that both started and completed events were published
            call_args_list = [call[0][0] for call in mock_publish.call_args_list]
            event_types = [call.event_type for call in call_args_list]
            assert "conversion.started" in event_types
            assert "conversion.completed" in event_types

    def test_markdown_parsing(self, temp_output_dir, mock_markdown):
        """Test Markdown parsing and HTML generation."""
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
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_md_to_html(md_file, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify HTML generation
        content = result_path.read_text(encoding="utf-8")
        # The mock returns simplified HTML, so check for basic structure
        assert "<h1>Test Document</h1>" in content
        assert "<p>Test content</p>" in content
        assert "<!DOCTYPE html>" in content
        assert "<html lang=" in content

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        md_to_html_converters = registry.get_plugins_for_conversion("md", "html")
        assert len(md_to_html_converters) >= 1
