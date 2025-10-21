"""End-to-end integration tests for document conversion."""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core import get_registry
from transmutation_codex.plugins.pdf.to_markdown import convert_pdf_to_md
from transmutation_codex.plugins.markdown.to_pdf import convert_md_to_pdf


class TestEndToEndConversion:
    """Test end-to-end document conversion workflows."""

    @pytest.fixture
    def test_pdf_path(self):
        """Path to test PDF file."""
        return Path(__file__).parent.parent / "test_files" / "electron_test.pdf"

    @pytest.fixture
    def test_md_path(self):
        """Path to test Markdown file."""
        return Path(__file__).parent.parent / "test_files" / "electron_test.md"

    @pytest.fixture
    def test_pagebreak_pdf_path(self):
        """Path to test PDF with page breaks."""
        return Path(__file__).parent.parent / "test_files" / "test_pagebreak.pdf"

    @pytest.fixture
    def test_pagebreak_md_path(self):
        """Path to test Markdown with page breaks."""
        return Path(__file__).parent.parent / "test_files" / "test_pagebreak.md"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    def test_pdf_to_markdown_roundtrip(self, test_pdf_path, temp_output_dir):
        """Test PDF to Markdown conversion."""
        output_path = temp_output_dir / "test_output.md"
        
        # Convert PDF to Markdown
        result_path = convert_pdf_to_md(test_pdf_path, output_path)
        
        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path == output_path
        
        # Verify content
        content = result_path.read_text(encoding="utf-8")
        assert len(content) > 0
        assert "# electron_test" in content

    def test_markdown_to_pdf_roundtrip(self, test_md_path, temp_output_dir):
        """Test Markdown to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"
        
        # Convert Markdown to PDF
        result_path = convert_md_to_pdf(test_md_path, output_path)
        
        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

    def test_pdf_to_markdown_with_page_breaks(self, test_pagebreak_pdf_path, temp_output_dir):
        """Test PDF to Markdown conversion with page breaks."""
        output_path = temp_output_dir / "test_output.md"
        
        # Convert PDF to Markdown
        result_path = convert_pdf_to_md(test_pagebreak_pdf_path, output_path)
        
        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        
        # Verify page breaks are handled
        content = result_path.read_text(encoding="utf-8")
        assert "---" in content  # Page separator

    def test_markdown_to_pdf_with_page_breaks(self, test_pagebreak_md_path, temp_output_dir):
        """Test Markdown to PDF conversion with page breaks."""
        output_path = temp_output_dir / "test_output.pdf"
        
        # Convert Markdown to PDF
        result_path = convert_md_to_pdf(test_pagebreak_md_path, output_path)
        
        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

    def test_converter_registry_integration(self):
        """Test converter registry integration."""
        registry = get_registry()
        
        # Test PDF to MD converters
        pdf_to_md_converters = registry.get_converters("pdf", "md")
        assert len(pdf_to_md_converters) >= 1
        
        # Test MD to PDF converters
        md_to_pdf_converters = registry.get_converters("md", "pdf")
        assert len(md_to_pdf_converters) >= 1
        
        # Test converter priorities
        best_pdf_to_md = registry.get_best_converter("pdf", "md")
        assert best_pdf_to_md is not None
        assert best_pdf_to_md.priority == 10  # Basic converter should have highest priority
        
        best_md_to_pdf = registry.get_best_converter("md", "pdf")
        assert best_md_to_pdf is not None

    def test_converter_execution_through_registry(self, test_pdf_path, temp_output_dir):
        """Test converter execution through registry."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        output_path = temp_output_dir / "test_output.md"
        
        # Execute converter through registry
        result_path = converter_info.callable_func(str(test_pdf_path), str(output_path))
        
        # Verify output
        assert Path(result_path).exists()
        assert Path(result_path).suffix == ".md"

    def test_converter_options_passing(self, test_pdf_path, temp_output_dir):
        """Test passing options to converters."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        output_path = temp_output_dir / "test_output.md"
        
        # Execute converter with options
        options = {
            "auto_ocr": True,
            "lang": "eng",
            "dpi": 300
        }
        
        result_path = converter_info.callable_func(
            str(test_pdf_path), 
            str(output_path), 
            **options
        )
        
        # Verify output
        assert Path(result_path).exists()
        assert Path(result_path).suffix == ".md"

    def test_converter_error_handling(self, temp_output_dir):
        """Test converter error handling."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "test_output.md"
        
        # Execute converter with invalid input
        with pytest.raises(FileNotFoundError):
            converter_info.callable_func(str(invalid_path), str(output_path))

    def test_converter_validation(self, temp_output_dir):
        """Test converter input validation."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        # Create non-PDF file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a PDF")
        output_path = temp_output_dir / "test_output.md"
        
        # Execute converter with invalid file type
        with pytest.raises(ValueError, match="Input file must be a PDF"):
            converter_info.callable_func(str(text_file), str(output_path))

    def test_converter_priority_fallback(self, test_pdf_path, temp_output_dir):
        """Test converter priority fallback."""
        registry = get_registry()
        converters = registry.get_converters("pdf", "md")
        
        # Should have multiple converters with different priorities
        assert len(converters) >= 2
        
        # Basic converter should have highest priority
        basic_converter = next(
            (c for c in converters if c.priority == 10),
            None
        )
        assert basic_converter is not None
        
        # Should be selected as best converter
        best_converter = registry.get_best_converter("pdf", "md")
        assert best_converter.priority == 10

    def test_converter_metadata(self):
        """Test converter metadata."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        # Verify metadata
        assert converter_info.name is not None
        assert converter_info.description is not None
        assert converter_info.input_formats is not None
        assert len(converter_info.input_formats) > 0
        assert converter_info.max_file_size_mb > 0
        assert converter_info.version is not None
        assert converter_info.source_format == "pdf"
        assert converter_info.target_format == "md"

    def test_converter_performance(self, test_pdf_path, temp_output_dir):
        """Test converter performance."""
        import time
        
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        output_path = temp_output_dir / "test_output.md"
        
        # Measure conversion time
        start_time = time.time()
        result_path = converter_info.callable_func(str(test_pdf_path), str(output_path))
        end_time = time.time()
        
        # Verify output
        assert Path(result_path).exists()
        
        # Verify reasonable performance (should complete within 30 seconds)
        conversion_time = end_time - start_time
        assert conversion_time < 30.0

    def test_converter_memory_usage(self, test_pdf_path, temp_output_dir):
        """Test converter memory usage."""
        import psutil
        import os
        
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        output_path = temp_output_dir / "test_output.md"
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Execute converter
        result_path = converter_info.callable_func(str(test_pdf_path), str(output_path))
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verify output
        assert Path(result_path).exists()
        
        # Verify reasonable memory usage (should not increase by more than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_converter_concurrent_execution(self, test_pdf_path, temp_output_dir):
        """Test concurrent converter execution."""
        import threading
        import time
        
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        results = []
        errors = []
        
        def convert_file(thread_id):
            try:
                output_path = temp_output_dir / f"test_output_{thread_id}.md"
                result_path = converter_info.callable_func(str(test_pdf_path), str(output_path))
                results.append(result_path)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=convert_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all conversions succeeded
        assert len(errors) == 0
        assert len(results) == 3
        
        # Verify all output files exist
        for result_path in results:
            assert Path(result_path).exists()

    def test_converter_file_size_limits(self, test_pdf_path, temp_output_dir):
        """Test converter file size limits."""
        registry = get_registry()
        converter_info = registry.get_best_converter("pdf", "md")
        
        # Check file size limit
        file_size_mb = test_pdf_path.stat().st_size / (1024 * 1024)
        assert file_size_mb <= converter_info.max_file_size_mb
        
        output_path = temp_output_dir / "test_output.md"
        
        # Execute converter
        result_path = converter_info.callable_func(str(test_pdf_path), str(output_path))
        
        # Verify output
        assert Path(result_path).exists()

    def test_converter_version_compatibility(self):
        """Test converter version compatibility."""
        registry = get_registry()
        converters = registry.get_converters("pdf", "md")
        
        # All converters should have valid versions
        for converter_info in converters:
            assert converter_info.version is not None
            assert len(converter_info.version) > 0
            
            # Version should be in semantic versioning format
            version_parts = converter_info.version.split(".")
            assert len(version_parts) >= 2
            assert version_parts[0].isdigit()
            assert version_parts[1].isdigit()