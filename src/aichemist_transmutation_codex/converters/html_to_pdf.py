#!/usr/bin/env python
"""
HTML to PDF converter module.

This module provides functionality to convert HTML files to PDF.
"""

import sys
from pathlib import Path
from typing import Any

from mdtopdf.config import ConfigManager, LogManager

# Setup logger
log_manager = LogManager()
logger = log_manager.get_converter_logger("html2pdf")

try:
    import pdfkit  # type: ignore

    PDFKIT_AVAILABLE = True
except ImportError:
    logger.warning(
        "pdfkit not found or wkhtmltopdf missing. Install pdfkit and wkhtmltopdf."
    )
    PDFKIT_AVAILABLE = False


def _ensure_path(input_val: str | Path) -> Path:
    """Ensure the input is a Path object."""
    return Path(input_val)


def convert_html_to_pdf(
    input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
) -> Path:
    """
    Convert an HTML file to PDF using pdfkit.

    Args:
        input_path: Path to the input HTML file.
        output_path: Output file path; if not provided, defaults to same name with .pdf extension.
        **kwargs: Additional keyword arguments for the pdfkit converter.

    Returns:
        Path to the created PDF file.

    Raises:
        FileNotFoundError: If input file not found.
        ValueError: If input file is not HTML.
        ImportError: If pdfkit or wkhtmltopdf is not installed/found.
        RuntimeError: For other conversion errors.
    """
    if not PDFKIT_AVAILABLE:
        raise ImportError(
            "pdfkit library not found or wkhtmltopdf is not installed/configured."
        )

    input_path = _ensure_path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input HTML file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in [".html", ".htm"]:
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError(f"Input file must be an HTML file: {input_path}")

    output_path = (
        _ensure_path(output_path).resolve()
        if output_path
        else input_path.with_suffix(".pdf")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get config
    config = ConfigManager()
    settings = config.get_converter_config("html2pdf")
    # Engine is now always pdfkit
    engine = "pdfkit"

    logger.info(f"Converting {input_path} to PDF using engine: {engine}")

    try:
        # pdfkit options can be passed as a dictionary
        options = {
            "page-size": kwargs.get("page_size", settings.get("page_size", "A4")),
            "margin-top": kwargs.get("margin_top", settings.get("margin_top", "1cm")),
            "margin-right": kwargs.get(
                "margin_right", settings.get("margin_right", "1cm")
            ),
            "margin-bottom": kwargs.get(
                "margin_bottom", settings.get("margin_bottom", "1cm")
            ),
            "margin-left": kwargs.get(
                "margin_left", settings.get("margin_left", "1cm")
            ),
            "encoding": "UTF-8",
            "enable-local-file-access": None,  # Enable loading local files (CSS, images)
            "quiet": None,  # Suppress wkhtmltopdf output
        }
        # Add optional JS delay
        js_delay = kwargs.get("javascript_delay", settings.get("javascript_delay"))
        if js_delay:
            options["javascript-delay"] = js_delay

        # Check for wkhtmltopdf path in config or kwargs
        wkhtmltopdf_path = kwargs.get(
            "wkhtmltopdf_path", settings.get("wkhtmltopdf_path")
        )
        pdfkit_config = (
            pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            if wkhtmltopdf_path
            else None
        )
        logger.debug(f"pdfkit options: {options}, config: {pdfkit_config}")

        pdfkit.from_file(
            str(input_path),
            str(output_path),
            options=options,
            configuration=pdfkit_config,
        )

        logger.info(f"HTML converted to PDF: {output_path}")
        return output_path
    except FileNotFoundError as e:
        # Check if it's wkhtmltopdf not found
        if "wkhtmltopdf" in str(e):
            logger.error(
                "wkhtmltopdf executable not found. Please install it and ensure it's in PATH "
                "or specify the path in config (html2pdf.wkhtmltopdf_path)."
            )
            raise FileNotFoundError(
                "wkhtmltopdf not found. Install it or set path in config."
            ) from e
        else:
            logger.exception(f"File not found during conversion: {e}")
            raise  # Reraise other FileNotFoundError
    except Exception as e:
        logger.exception(f"Error during HTML to PDF conversion using pdfkit: {e}")
        raise RuntimeError(f"Error converting HTML to PDF with pdfkit: {e}") from e


# Alias for naming consistency
html_to_pdf = convert_html_to_pdf

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf.py <input_html_file> [output_pdf_file]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # LogManager initializes automatically via singleton in convert call
        # log_manager.configure_logging() # Incorrect - Removed
        result = convert_html_to_pdf(input_file, output_file)
        # Logger is already configured, so just log the success
        # logger.info(f"Conversion successful: {result}") # Redundant if convert logs
        sys.exit(0)
    except Exception as e:
        # Logger should already be configured to handle this via root or specific loggers
        # logger.error(f"Error: {e}") # Redundant if convert logs exception
        print(f"Error: {e}", file=sys.stderr)  # Print to stderr for CLI feedback
        sys.exit(1)
