"""
Module containing various document conversion implementations.

This package contains different converter modules for converting
between different formats such as Markdown, PDF, HTML, etc.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn, Optional, Union, cast

from .markdown_to_html import convert_md_to_html, md_to_html
from .markdown_to_pdf import convert_md_to_pdf
from .pdf_to_markdown import (
    convert_pdf_to_md,
    convert_pdf_to_md_with_enhanced_ocr,
    convert_pdf_to_md_with_ocr,
    convert_pdf_to_md_with_pymupdf4llm,
)

# Import for Markdown to DOCX
try:
    from .markdown_to_docx import markdown_to_docx as _imported_markdown_to_docx

    markdown_to_docx = cast(Callable[..., Path], _imported_markdown_to_docx)
except ImportError:

    def markdown_to_docx(
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> Path:
        """Placeholder for Markdown to DOCX conversion if dependencies are missing.

        This function is a stand-in if 'pypandoc' or the underlying Pandoc
        executable is not available. Calling it will raise an ImportError.

        Args:
            input_path (Union[str, Path]): Path to the input Markdown file.
            output_path (Union[str, Path, None]): Desired path for the output DOCX file.
            **kwargs (Any): Additional keyword arguments, ignored.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to indicate missing dependencies.
        """
        raise ImportError(
            "Markdown to DOCX converter is not available. "
            "Please ensure 'pypandoc' is installed and Pandoc executable is in PATH."
        )


# Import for DOCX to PDF
try:
    from .doc_to_pdf import convert_docx_to_pdf as _imported_convert_docx_to_pdf

    convert_docx_to_pdf = cast(Callable[..., Path], _imported_convert_docx_to_pdf)
except ImportError:

    def convert_docx_to_pdf(
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> Path:
        """Placeholder for DOCX to PDF conversion if dependencies are missing.

        This function is a stand-in if 'docx2pdf' is not installed or if its
        underlying dependencies (like Microsoft Word or LibreOffice) are not available.
        Calling it will raise an ImportError.

        Args:
            input_path (Union[str, Path]): Path to the input DOCX file.
            output_path (Union[str, Path, None]): Desired path for the output PDF file.
            **kwargs (Any): Additional keyword arguments, ignored.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to indicate missing dependencies.
        """
        raise ImportError(
            "DOCX to PDF converter (docx2pdf) is not available or its dependencies (e.g., MS Word, LibreOffice) are missing. "
            "Please ensure 'docx2pdf' is installed and system dependencies are met."
        )


# Import new converters if available
try:
    from .html_to_pdf import convert_html_to_pdf as _imported_convert_html_to_pdf
    from .html_to_pdf import html_to_pdf as _imported_html_to_pdf

    convert_html_to_pdf = cast(Callable[..., Path], _imported_convert_html_to_pdf)
    html_to_pdf = cast(Callable[..., Path], _imported_html_to_pdf)
except ImportError:

    def convert_html_to_pdf(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder for HTML to PDF conversion when dependencies are missing.

        This function is a stand-in for the actual `convert_html_to_pdf` that
        would be imported from `.html_to_pdf`. It is defined when the necessary
        libraries (e.g., WeasyPrint or pdfkit) cannot be imported, indicating
        they are not installed.

        Args:
            input_path (str | Path): The path to the input HTML file.
            output_path (str | Path | None): The desired path for the output PDF file.
            **kwargs (Any): Additional keyword arguments, ignored by this placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to indicate that the required converter
                dependencies are not available.
        """
        raise ImportError(
            "HTML to PDF converter is not available. Install WeasyPrint or pdfkit."
        )

    def html_to_pdf(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for the `convert_html_to_pdf` placeholder function.

        This ensures that `html_to_pdf` is always available, even if the underlying
        dependencies for HTML to PDF conversion are missing. It will call the
        placeholder which raises an ImportError.

        Args:
            input_path (str | Path): The path to the input HTML file.
            output_path (str | Path | None): The desired path for the output PDF file.
            **kwargs (Any): Additional keyword arguments, passed to the placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Propagated from the placeholder function.
        """
        return convert_html_to_pdf(input_path, output_path, **kwargs)


try:
    from .pdf_to_html import convert_pdf_to_html as _imported_convert_pdf_to_html
    from .pdf_to_html import pdf_to_html as _imported_pdf_to_html

    convert_pdf_to_html = cast(Callable[..., Path], _imported_convert_pdf_to_html)
    pdf_to_html = cast(Callable[..., Path], _imported_pdf_to_html)
except ImportError:

    def convert_pdf_to_html(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder for PDF to HTML conversion when dependencies are missing.

        This function serves as a fallback if libraries like PyMuPDF or pdfminer.six,
        required for PDF to HTML conversion, are not installed. Calling this function
        will always result in an ImportError.

        Args:
            input_path (str | Path): The path to the input PDF file.
            output_path (str | Path | None): The desired path for the output HTML file.
            **kwargs (Any): Additional keyword arguments, ignored by this placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to signal that the necessary PDF to HTML
                converter dependencies are unavailable.
        """
        raise ImportError(
            "PDF to HTML converter is not available. Install PyMuPDF or pdfminer.six."
        )

    def pdf_to_html(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for the `convert_pdf_to_html` placeholder function.

        Provides a consistent API point even when PDF to HTML conversion
        dependencies are not met. Calls the placeholder which raises an ImportError.

        Args:
            input_path (str | Path): The path to the input PDF file.
            output_path (str | Path | None): The desired path for the output HTML file.
            **kwargs (Any): Additional keyword arguments, passed to the placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Propagated from the placeholder function.
        """
        return convert_pdf_to_html(input_path, output_path, **kwargs)


try:
    from .doc_to_markdown import convert_docx_to_md as _imported_convert_docx_to_md
    from .doc_to_markdown import docx_to_md as _imported_docx_to_md

    convert_docx_to_md = cast(Callable[..., Path], _imported_convert_docx_to_md)
    docx_to_md = cast(Callable[..., Path], _imported_docx_to_md)
except ImportError:

    def convert_docx_to_md(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Placeholder for DOCX to Markdown conversion when dependencies are missing.

        This function acts as a substitute if `python-docx` or `mammoth` (libraries
        for DOCX processing) are not installed. It raises an ImportError upon being called.

        Args:
            input_path (str | Path): The path to the input DOCX file.
            output_path (str | Path | None): The desired path for the output Markdown file.
            **kwargs (Any): Additional keyword arguments, ignored by this placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to indicate that the required DOCX to Markdown
                converter dependencies are not installed.
        """
        raise ImportError(
            "DOCX to Markdown converter is not available. Install python-docx or mammoth."
        )

    def docx_to_md(
        input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
    ) -> Path:
        """Alias for the `convert_docx_to_md` placeholder function.

        Ensures `docx_to_md` is available in the API even if the necessary
        dependencies for DOCX conversion are absent. Calls the placeholder,
        which will raise an ImportError.

        Args:
            input_path (str | Path): The path to the input DOCX file.
            output_path (str | Path | None): The desired path for the output Markdown file.
            **kwargs (Any): Additional keyword arguments, passed to the placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Propagated from the placeholder function.
        """
        return convert_docx_to_md(input_path, output_path, **kwargs)


# PDF to Editable PDF converter
try:
    from .pdf_to_editable_pdf import (
        convert_pdf_to_editable as _imported_convert_pdf_to_editable,
    )

    convert_pdf_to_editable = cast(
        Callable[..., Path], _imported_convert_pdf_to_editable
    )
except ImportError:
    # This block will be executed if `ocrmypdf` is not installed or another import error occurs.
    def convert_pdf_to_editable(
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> Path:
        """Placeholder for PDF to Editable PDF conversion when dependencies are missing.

        This function is defined if `ocrmypdf` or its dependencies (like Tesseract OCR)
        are not available. Calling it will always raise an ImportError, guiding the user
        to install the necessary components.

        Args:
            input_path (str | Path): The path to the input PDF file.
            output_path (str | Path | None): The desired path for the output editable PDF file.
            **kwargs (Any): Additional keyword arguments, ignored by this placeholder.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to signal that OCRmyPDF or its dependencies
                are missing, preventing the conversion.
        """
        # It's helpful to inform the user about the missing dependency.
        raise ImportError(
            "PDF to Editable PDF converter is not available. "
            "Please ensure 'ocrmypdf' and its dependency Tesseract OCR are installed."
        )


# Import for PDF Merging
try:
    from .pdf_merger import (
        merge_multiple_pdfs_to_single_pdf as _imported_merge_pdfs,
    )

    merge_multiple_pdfs_to_single_pdf = cast(Callable[..., Path], _imported_merge_pdfs)
except ImportError:

    def merge_multiple_pdfs_to_single_pdf(
        input_paths: list[str | Path],  # Note: list of paths
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Placeholder for PDF merging if dependencies (PyPDF2) are missing.

        Args:
            input_paths (list[Union[str, Path]]): List of input PDF file paths.
            output_path (Union[str, Path]): Path for the merged output PDF file.
            **kwargs (Any): Additional keyword arguments, ignored.

        Returns:
            Path: This function does not return normally.

        Raises:
            ImportError: Always raised to indicate missing PyPDF2.
        """
        raise ImportError(
            "PDF Merging functionality (PyPDF2) is not available. "
            "Please ensure 'PyPDF2' is installed."
        )


__all__ = [
    "convert_docx_to_md",
    "convert_docx_to_pdf",
    "convert_html_to_pdf",
    "convert_md_to_html",
    "convert_md_to_pdf",
    "convert_pdf_to_editable",
    "convert_pdf_to_html",
    "convert_pdf_to_md",
    "convert_pdf_to_md_with_enhanced_ocr",
    "convert_pdf_to_md_with_ocr",
    "convert_pdf_to_md_with_pymupdf4llm",
    "docx_to_md",
    "html_to_pdf",
    "markdown_to_docx",
    "md_to_html",
    "merge_multiple_pdfs_to_single_pdf",
    "pdf_to_html",
]
