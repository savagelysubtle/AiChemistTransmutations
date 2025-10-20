"""DOCX document converters.

This package contains converters that take DOCX as input.
"""

from .to_pdf import convert_docx_to_pdf, docx_to_pdf

__all__ = [
    "convert_docx_to_pdf",
    "docx_to_pdf",
]
