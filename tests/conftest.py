"""Pytest configuration for Transmutation Codex tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def test_files_dir():
    """Path to test files directory."""
    return Path(__file__).parent / "test_files"


@pytest.fixture
def test_pdf_path(test_files_dir):
    """Path to test PDF file."""
    return test_files_dir / "electron_test.pdf"


@pytest.fixture
def test_md_path(test_files_dir):
    """Path to test Markdown file."""
    return test_files_dir / "electron_test.md"


@pytest.fixture
def test_pagebreak_pdf_path(test_files_dir):
    """Path to test PDF with page breaks."""
    return test_files_dir / "test_pagebreak.pdf"


@pytest.fixture
def test_pagebreak_md_path(test_files_dir):
    """Path to test Markdown with page breaks."""
    return test_files_dir / "test_pagebreak.md"


@pytest.fixture
def output_pdf_path(temp_dir):
    """Path to a temporary output PDF file."""
    return temp_dir / "output.pdf"


@pytest.fixture
def output_html_path(temp_dir):
    """Path to a temporary output HTML file."""
    return temp_dir / "output.html"


@pytest.fixture
def output_md_path(temp_dir):
    """Path to a temporary output Markdown file."""
    return temp_dir / "output.md"


@pytest.fixture
def mock_fitz():
    """Mock PyMuPDF for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.plugins.pdf.to_markdown.fitz") as mock_fitz:
        # Mock document
        mock_doc = Mock()
        mock_doc.page_count = 2
        mock_doc.is_encrypted = False
        mock_doc.close = Mock()

        # Mock pages
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Test content from page 1"
        mock_page1.get_pixmap.return_value = Mock(width=100, height=100, samples=b"fake")

        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Test content from page 2"
        mock_page2.get_pixmap.return_value = Mock(width=100, height=100, samples=b"fake")

        mock_doc.load_page.side_effect = [mock_page1, mock_page2]
        mock_fitz.open.return_value = mock_doc

        yield mock_fitz


@pytest.fixture
def mock_tesseract():
    """Mock Tesseract OCR for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.plugins.pdf.to_markdown.pytesseract") as mock_tesseract:
        mock_tesseract.image_to_string.return_value = "OCR extracted text"
        yield mock_tesseract


@pytest.fixture
def mock_pymupdf4llm():
    """Mock PyMuPDF4LLM for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.plugins.pdf.to_markdown.parse_pdf_to_markdown") as mock_parse:
        mock_parse.return_value = "# Test Document\n\nThis is test content from PyMuPDF4LLM."
        yield mock_parse


@pytest.fixture
def mock_weasyprint():
    """Mock markdown_pdf library for testing."""
    from unittest.mock import Mock, patch

    # Mock both the availability flag and the MarkdownPdf class
    with (
        patch("transmutation_codex.plugins.markdown.to_pdf.MARKDOWN_PDF_AVAILABLE", True),
        patch("transmutation_codex.plugins.markdown.to_pdf.MarkdownPdf") as mock_md_pdf,
    ):
        mock_instance = Mock()
        mock_md_pdf.return_value = mock_instance
        mock_instance.save = Mock()
        yield mock_md_pdf


@pytest.fixture
def mock_progress_tracking():
    """Mock progress tracking for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.core.start_operation") as mock_start, \
         patch("transmutation_codex.core.update_progress") as mock_update, \
         patch("transmutation_codex.core.complete_operation") as mock_complete:
        
        mock_start.return_value = "test_operation_id"
        
        yield {
            "start": mock_start,
            "update": mock_update,
            "complete": mock_complete
        }


@pytest.fixture
def mock_event_system():
    """Mock event system for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.core.publish") as mock_publish:
        yield mock_publish


@pytest.fixture
def mock_log_manager():
    """Mock log manager for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.core.get_log_manager") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value.get_converter_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def mock_config_manager():
    """Mock config manager for testing."""
    from unittest.mock import Mock, patch
    
    with patch("transmutation_codex.core.ConfigManager") as mock_config:
        mock_config.return_value.get_environment_config.return_value = {
            "ocr_enabled": True,
            "ocr_languages": "eng",
            "ocr_dpi": 300,
            "ocr_psm": 1,
            "ocr_oem": 3,
            "force_ocr": False
        }
        yield mock_config


@pytest.fixture
def sample_markdown_content():
    """Sample Markdown content for testing."""
    return """# Test Document

This is a **bold** text and *italic* text.

## Section 2

- List item 1
- List item 2

```python
print("Hello, World!")
```

> This is a blockquote.

---

## Page Break Test

This content should be on a new page.
"""


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing (simulated)."""
    return {
        "pages": [
            {
                "text": "Test content from page 1",
                "page_number": 1
            },
            {
                "text": "Test content from page 2",
                "page_number": 2
            }
        ],
        "metadata": {
            "title": "Test Document",
            "author": "Test Author",
            "pages": 2
        }
    }


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the plugin registry cache before each test (keep registered plugins)."""
    from transmutation_codex.core import get_registry

    # Only clear the cache, not the registered plugins
    registry = get_registry()
    registry._cache.clear()
    
    yield
    
    # Clear cache after each test
    registry._cache.clear()


@pytest.fixture(autouse=True)
def reset_progress_tracker():
    """Reset the progress tracker before each test."""
    from transmutation_codex.core import get_progress_tracker
    
    # Clear tracker before each test
    tracker = get_progress_tracker()
    tracker._operations.clear()
    
    yield
    
    # Clear tracker after each test
    tracker._operations.clear()


@pytest.fixture(autouse=True)
def reset_event_bus():
    """Reset the event bus before each test."""
    from transmutation_codex.core import get_event_bus
    
    # Clear bus before each test
    bus = get_event_bus()
    bus._handlers.clear()
    
    yield
    
    # Clear bus after each test
    bus._handlers.clear()