"""
Markdown to HTML converter.

This module converts Markdown documents to HTML format with basic styling.
"""

from pathlib import Path
from typing import Any

import markdown

from aichemist_transmutation_codex.config import ConfigManager, LogManager

# Setup logger
log_manager = LogManager()
logger = log_manager.get_converter_logger("md2html")

DEFAULT_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    padding: 2em;
    max-width: 50em;
    margin: 0 auto;
}
code {
    background-color: #f4f4f4;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
}
pre {
    background-color: #f4f4f4;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
}
img { max-width: 100%; }
table {
    border-collapse: collapse;
    width: 100%;
}
table, th, td { border: 1px solid #ddd; }
th, td { padding: 10px; text-align: left; }
th { background-color: #f4f4f4; }
blockquote {
    border-left: 4px solid #ddd;
    padding-left: 1em;
    color: #666;
    margin-left: 0;
}
"""


def md_to_html(markdown_content: str, custom_css: str | None = None) -> str:
    """
    Convert markdown content to HTML with styling.

    Args:
        markdown_content: Markdown content to convert
        custom_css: Optional custom CSS content to replace default

    Returns:
        HTML content with styling
    """
    try:
        html_body = markdown.markdown(
            markdown_content, extensions=["tables", "fenced_code", "codehilite"]
        )
        css = custom_css if custom_css else DEFAULT_CSS
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css}</style>
</head>
<body>
    {html_body}
</body>
</html>
"""
    except Exception as e:
        logger.exception(f"Error during markdown processing: {e}")
        return f"<html><body><h1>Error converting Markdown</h1><pre>{e}</pre></body></html>"


def convert_md_to_html(
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,  # Accept additional options
) -> Path:
    """Converts a Markdown file to a complete HTML document with styling.

    This function reads a Markdown file, converts its content to HTML using
    the `md_to_html` helper function (which applies default or custom CSS),
    and saves the result to an output HTML file.

    Args:
        input_path (str | Path): The path to the input Markdown file.
        output_path (str | Path | None): The path where the output HTML file
            will be saved. If None, it defaults to the same name as the input
            file but with an ".html" extension, in the same directory.
            Defaults to None.
        **kwargs (Any): Additional options. Currently supports:
            - `custom_css` (str | Path | None): Path to a custom CSS file to
              be used instead of the default styling. If the path is invalid
              or the file cannot be read, a warning is logged and default
              CSS is used.

    Returns:
        Path: The absolute path to the generated HTML file.

    Raises:
        FileNotFoundError: If `input_path` does not exist.
        ValueError: If `input_path` is not a Markdown file (based on extension).
        RuntimeError: For any other errors encountered during file operations or
            Markdown conversion.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input Markdown file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in [".md", ".markdown"]:
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError("Input file must be a Markdown file.")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".html")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get config and options
    config = ConfigManager()
    settings = config.get_converter_config(
        "md2html"
    )  # Though few settings specific to md2html
    custom_css_path = kwargs.get("custom_css", settings.get("custom_css"))
    custom_css_content = None
    if custom_css_path:
        css_path = Path(custom_css_path)
        if css_path.exists():
            try:
                with open(css_path, encoding="utf-8") as css_file:
                    custom_css_content = css_file.read()
                logger.info(f"Using custom CSS from: {css_path}")
            except Exception as css_err:
                logger.warning(f"Could not read custom CSS file {css_path}: {css_err}")
        else:
            logger.warning(f"Custom CSS file not found: {css_path}")

    logger.info(f"Converting {input_path} to HTML")

    try:
        with open(input_path, encoding="utf-8") as md_file:
            markdown_content = md_file.read()

        html_content = md_to_html(markdown_content, custom_css=custom_css_content)
        with open(output_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        logger.info(f"Markdown converted to HTML: {output_path}")
        return output_path
    except Exception as e:
        logger.exception(f"Error converting Markdown to HTML: {e}")
        raise RuntimeError(f"Error converting Markdown to HTML: {e}") from e
