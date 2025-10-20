"""TXT to PDF converter module.

This module provides functionality to convert plain text files to PDF documents.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from transmutation_codex.core import (
    ConfigManager,
    get_log_manager,
    raise_conversion_error,
)
from transmutation_codex.core.decorators import converter


@converter(
    source_format='txt',
    target_format='pdf',
    description="Convert plain text files to PDF with configurable font and styling",
    input_formats=['txt'],
    max_file_size_mb=10,
    required_dependencies=['reportlab'],
    priority=10,
    version="1.0.0",
)
def convert_txt_to_pdf(
    input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
) -> Path:
    """Converts a plain text file to a PDF document.

    Args:
        input_path: Path to the input TXT file.
        output_path: Path for the output PDF file. If None, defaults to
                     the input filename with a .pdf extension.
        **kwargs: Additional keyword arguments. Currently supports:
            - font_name (str): Name of the font to use (e.g., "Helvetica").
            - font_size (int): Font size for the text.

    Returns:
        Path: The absolute path to the generated PDF file.

    Raises:
        FileNotFoundError: If the input_path does not exist.
        Exception: For errors encountered during PDF generation.
    """
    # Obtain logger at runtime from the centralized LogManager
    logger = get_log_manager().get_converter_logger("txt2pdf")

    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input TXT file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".txt":
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError(f"Input file must be a TXT file: {input_path}")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".pdf")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get config and options
    config = ConfigManager()
    settings = config.get_environment_config()
    font_name = kwargs.get("font_name", settings.get("font_name", "Helvetica"))
    font_size = kwargs.get("font_size", settings.get("font_size", 10))

    logger.info(
        f"Converting {input_path.name} to PDF. Output: {output_path.name}, Font: {font_name}, Size: {font_size}"
    )

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text_content = f.read()

        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = font_name
        style.fontSize = font_size
        style.leading = font_size * 1.2  # Line spacing

        story = []
        # Replace multiple newlines with a single paragraph break equivalent
        # Preserve single newlines by converting them to <br/> tags,
        # which ReportLab Paragraphs can interpret.
        processed_text = text_content.replace("\\r\\n", "\\n").replace("\\n", "<br/>\\n")

        # Split into paragraphs based on what would visually be a paragraph break (multiple newlines)
        # However, a simpler approach for plain text is often to treat each line as a potential start
        # of a new paragraph if it's separated by blank lines, or just wrap the whole content.
        # For now, let's create paragraphs by splitting by double newlines (or more)
        # and then rejoining with single <br/> for lines within those.

        # A simpler initial approach: treat the whole text as a single block,
        # and let ReportLab handle line wrapping.
        # We will replace newlines with <br/> for explicit line breaks.
        paragraphs = processed_text.split("<br/>\\n<br/>\\n") # Split by what were double newlines

        for para_text in paragraphs:
            if para_text.strip():
                story.append(Paragraph(para_text, style))
                story.append(Spacer(1, 0.2 * style.fontSize)) # Add some space between paragraphs

        if not story: # Handle empty or whitespace-only files
            story.append(Paragraph("<i>(Empty Document)</i>", style))

        doc.build(story)
        logger.info(f"Successfully converted {input_path.name} to {output_path.name}")
        return output_path

    except FileNotFoundError:
        logger.error(f"Input file not found during conversion: {input_path}")
        raise
    except Exception as e:
        logger.exception(
            f"An error occurred during TXT to PDF conversion for {input_path.name}: {e}"
        )
        raise_conversion_error(
            f"TXT to PDF conversion failed: {e}",
            input_path=str(input_path),
            output_path=str(output_path)
        )

if __name__ == "__main__":
    # Example usage for direct script execution (testing)
    if len(sys.argv) < 2:
        print("Usage: python to_pdf.py <input_txt_file> [output_pdf_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Basic logging for testing
    logging.basicConfig(level=logging.INFO)

    try:
        result_path = convert_txt_to_pdf(input_file, output_file)
        print(f"Successfully converted to: {result_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
