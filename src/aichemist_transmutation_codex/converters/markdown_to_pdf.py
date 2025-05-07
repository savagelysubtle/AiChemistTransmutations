"""
Markdown to PDF converter.

This module converts Markdown documents to PDF format, preserving structure.
"""

import re
from pathlib import Path
from typing import Any

from markdown_pdf import MarkdownPdf, Section

from mdtopdf.config import ConfigManager, LogManager

# Setup logger
log_manager = LogManager()
logger = log_manager.get_converter_logger("md2pdf")

# HTML styling for tables to be injected
TABLE_STYLE = """
<style>
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1em;
}
th, td {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f9f9f9;
}
.pagebreak {
    page-break-after: always;
}
</style>
"""


def convert_md_to_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,  # Accept additional options
) -> Path:
    """
    Convert a markdown file to PDF.

    Args:
        input_path: Path to the Markdown file
        output_path: Path to save the PDF file.
        **kwargs: Additional options like page_break_marker, respect_html_breaks

    Returns:
        Path to the generated PDF file
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".pdf")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get config
    config = ConfigManager()
    settings = config.get_converter_config("md2pdf")

    # Get options from kwargs or config
    page_break_marker = kwargs.get(
        "page_break_marker", settings.get("page_break_marker", "<!-- pagebreak -->")
    )
    # respect_html_breaks is handled by the library by default

    logger.info(f"Converting {input_path} to PDF using marker: '{page_break_marker}'")

    with open(input_path, encoding="utf-8") as md_file:
        markdown_content = md_file.read()

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else input_path.name
    logger.debug(f"Using title: {title}")

    # Preprocess markdown for page breaks
    break_token = "<!-- pagebreak -->"
    if page_break_marker and page_break_marker != break_token:
        markdown_content = markdown_content.replace(page_break_marker, break_token)
        logger.info(
            f"Replaced custom marker '{page_break_marker}' with '{break_token}'"
        )

    markdown_content = markdown_content.replace("\\pagebreak", break_token)
    markdown_content = markdown_content.replace("\\newpage", break_token)

    # Inject table style if not present
    has_style_tag = "<style" in markdown_content
    if not has_style_tag:
        markdown_content = TABLE_STYLE + markdown_content
        logger.debug("Injected default table styles.")

    try:
        pdf = MarkdownPdf()
        pdf.meta["title"] = title
        pdf.meta["author"] = config.get_value(
            "application", "name", "MDtoPDF Converter"
        )

        if break_token in markdown_content:
            sections = markdown_content.split(break_token)
            logger.info(f"Document split into {len(sections)} sections by page breaks.")
            for i, section_content in enumerate(sections):
                if section_content.strip():
                    if i > 0 and not has_style_tag and "<style" not in section_content:
                        section_content = TABLE_STYLE + section_content
                    pdf.add_section(Section(section_content, toc=True))
        else:
            logger.info("No page breaks found.")
            pdf.add_section(Section(markdown_content, toc=True))

        pdf.save(str(output_path))
        logger.info(f"Markdown converted to PDF: {output_path}")
        return output_path
    except Exception as e:
        logger.exception(f"Error converting Markdown to PDF: {e}")
        raise RuntimeError(f"Error converting Markdown to PDF: {e}") from e
