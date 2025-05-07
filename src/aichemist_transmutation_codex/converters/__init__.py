"""
Module containing various document conversion implementations.

This package contains different converter modules for converting
between different formats such as Markdown, PDF, HTML, etc.
"""

from pathlib import Path
from typing import Any, NoReturn, Optional, Union

from .markdown_to_html import convert_md_to_html, md_to_html
from .markdown_to_pdf import convert_md_to_pdf
from .pdf_to_markdown import (
    convert_pdf_to_md,
    convert_pdf_to_md_with_enhanced_ocr,
    convert_pdf_to_md_with_ocr,
    convert_pdf_to_md_with_pymupdf4llm,
)

# Import new converters if available
try:
    from .html_to_pdf import convert_html_to_pdf, html_to_pdf
except ImportError:

    def convert_html_to_pdf(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder function that raises ImportError when called."""
        raise ImportError(
            "HTML to PDF converter is not available. Install WeasyPrint or pdfkit."
        )

    def html_to_pdf(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for convert_html_to_pdf placeholder."""
        return convert_html_to_pdf(input_path, output_path, **kwargs)


try:
    from .pdf_to_html import convert_pdf_to_html, pdf_to_html
except ImportError:

    def convert_pdf_to_html(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder function that raises ImportError when called."""
        raise ImportError(
            "PDF to HTML converter is not available. Install PyMuPDF or pdfminer.six."
        )

    def pdf_to_html(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for convert_pdf_to_html placeholder."""
        return convert_pdf_to_html(input_path, output_path, **kwargs)


try:
    from .doc_to_markdown import convert_docx_to_md, docx_to_md
except ImportError:

    def convert_docx_to_md(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder function that raises ImportError when called."""
        raise ImportError(
            "DOCX to Markdown converter is not available. Install python-docx or mammoth."
        )

    def docx_to_md(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for convert_docx_to_md placeholder."""
        return convert_docx_to_md(input_path, output_path, **kwargs)


# PDF to Editable PDF converter
try:
    from .pdf_to_editable_pdf import convert_pdf_to_editable
except ImportError:
    # This block will be executed if `ocrmypdf` is not installed or another import error occurs.
    def convert_pdf_to_editable(
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> Path:
        """Placeholder for PDF to Editable PDF if dependencies are missing."""
        # It's helpful to inform the user about the missing dependency.
        raise ImportError(
            "PDF to Editable PDF converter is not available. "
            "Please ensure 'ocrmypdf' and its dependency Tesseract OCR are installed."
        )


__all__ = [
    "convert_md_to_html",
    "md_to_html",
    "convert_md_to_pdf",
    "convert_pdf_to_md",
    "convert_pdf_to_md_with_ocr",
    "convert_pdf_to_md_with_enhanced_ocr",
    "convert_pdf_to_md_with_pymupdf4llm",
    "convert_html_to_pdf",
    "html_to_pdf",
    "convert_pdf_to_html",
    "pdf_to_html",
    "convert_docx_to_md",
    "docx_to_md",
    "convert_pdf_to_editable",
]
