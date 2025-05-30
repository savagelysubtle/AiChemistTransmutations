"""MDtoPDF package for converting between various document formats.

This package provides tools to convert between Markdown, HTML, PDF, and other formats.
"""

__version__ = "0.1.0"

# Re-export common conversion functions for easy access
# Export batch conversion functionality
from .converters import (
    convert_html_to_pdf,
    convert_md_to_html,
    convert_md_to_pdf,
    convert_pdf_to_html,
    convert_pdf_to_md,
    convert_pdf_to_md_with_enhanced_ocr,
    convert_pdf_to_md_with_ocr,
    convert_pdf_to_md_with_pymupdf4llm,
    html_to_pdf,
    md_to_html,
    pdf_to_html,
)

__all__ = [
    "convert_html_to_pdf",
    "convert_md_to_html",
    "convert_md_to_pdf",
    "convert_pdf_to_html",
    "convert_pdf_to_md",
    "convert_pdf_to_md_with_enhanced_ocr",
    "convert_pdf_to_md_with_ocr",
    "convert_pdf_to_md_with_pymupdf4llm",
    "html_to_pdf",
    "md_to_html",
    "pdf_to_html",
]
