# Comprehensive Logging Update Guide

This document outlines the pattern for adding comprehensive logging with error codes to all converters in the plugins directory.

## Pattern Overview

All converters should follow this pattern:

1. **Import ErrorCode** from core
2. **Add logging at key points**:
   - Start of conversion (info level)
   - Validation checks (debug/error with error codes)
   - File operations (debug for success, error with codes for failures)
   - Conversion steps (debug for progress)
   - Error handling (error with codes and exc_info=True)
   - Success completion (info level)

3. **Use error codes** in all exception raises
4. **Complete operations** on both success and failure

## Standard Pattern

```python
from transmutation_codex.core import (
    ErrorCode,
    get_log_manager,
    raise_conversion_error,
    # ... other imports
)

# Setup logger
logger = get_log_manager().get_converter_logger("converter_name")

@converter(...)
def convert_function(input_path, output_path, **kwargs):
    operation = start_operation("converter_name", ...)

    try:
        logger.info(f"Starting conversion: {input_path}")

        # Validation with logging
        try:
            check_feature_access("converter_name")
            logger.debug("Feature access check passed")
        except Exception as e:
            logger.error(f"Feature access denied: {e}", exc_info=True)
            complete_operation(operation, success=False)
            raise

        # File validation
        if not input_path.exists():
            error_code = ErrorCode.VALIDATION_FILE_NOT_FOUND
            logger.error(f"[{error_code}] File not found: {input_path}")
            complete_operation(operation, success=False)
            raise FileNotFoundError(...)

        # File operations with error codes
        try:
            # Read/write operation
            logger.debug("Reading file...")
            # ... operation ...
            logger.debug("Successfully read file")
        except Exception as e:
            error_code = ErrorCode.CONVERSION_XXX_READ_FAILED
            logger.error(f"[{error_code}] Failed to read file: {e}", exc_info=True)
            raise_conversion_error(
                f"Failed to read file: {e}",
                source_format="xxx",
                target_format="yyy",
                source_file=str(input_path),
                error_code=error_code,
            )

        # Success
        complete_operation(operation, success=True)
        logger.info(f"Successfully completed conversion: {output_path}")
        return output_path

    except Exception as e:
        error_code = ErrorCode.CONVERSION_XXX_GENERATION_FAILED
        logger.error(f"[{error_code}] Conversion failed: {e}", exc_info=True)
        complete_operation(operation, success=False)
        raise_conversion_error(
            f"Conversion failed: {e}",
            source_format="xxx",
            target_format="yyy",
            source_file=str(input_path),
            error_code=error_code,
        )
```

## Error Code Mapping

### Validation Errors
- `VALIDATION_FILE_NOT_FOUND` - File doesn't exist
- `VALIDATION_INVALID_FORMAT` - Wrong file format
- `VALIDATION_FILE_TOO_LARGE` - File exceeds size limit

### Dependency Errors
- `DEPENDENCY_MISSING_LIBRARY` - Required Python library missing
- `DEPENDENCY_MISSING_EXECUTABLE` - Required executable missing (e.g., Tesseract, wkhtmltopdf)

### Conversion Errors
- `CONVERSION_XXX2YYY_READ_FAILED` - Failed to read input file
- `CONVERSION_XXX2YYY_GENERATION_FAILED` - Failed to generate output
- `CONVERSION_XXX2YYY_SAVE_FAILED` - Failed to save output file

## Remaining Converters to Update

### Markdown Converters
- [x] `markdown/to_pdf.py` - DONE
- [ ] `markdown/to_html.py`
- [ ] `markdown/to_docx.py`
- [ ] `markdown/to_epub.py`

### PDF Converters
- [ ] `pdf/to_markdown.py` (multiple functions)
- [ ] `pdf/to_html.py`
- [ ] `pdf/to_xlsx.py`
- [ ] `pdf/to_images.py`
- [ ] `pdf/to_compress.py`
- [ ] `pdf/to_encrypt.py`
- [ ] `pdf/to_split.py`
- [ ] `pdf/to_watermark.py`
- [ ] `pdf/to_ocr_layer.py`
- [ ] `pdf/to_pages.py`
- [ ] `pdf/to_editable_pdf.py`

### DOCX Converters
- [ ] `docx/to_markdown.py`
- [ ] `docx/to_pdf.py`
- [ ] `docx/to_pdf_libreoffice.py`
- [ ] `docx/to_epub.py`

### HTML Converters
- [x] `html/to_pdf.py` - DONE
- [ ] `html/to_epub.py`

### Excel/CSV Converters
- [x] `csv/to_pdf.py` - DONE
- [ ] `csv/to_xlsx.py`
- [ ] `xlsx/to_pdf.py`
- [ ] `xlsx/to_csv.py`
- [ ] `xlsx/to_html.py`
- [ ] `xlsx/to_markdown.py`

### PowerPoint Converters
- [ ] `pptx/to_pdf.py`
- [ ] `pptx/to_html.py`
- [ ] `pptx/to_markdown.py`
- [ ] `pptx/to_images.py`

### Image Converters
- [ ] `image/to_pdf.py`
- [ ] `image/to_text.py`
- [ ] `image/to_image.py`

### EPUB Converters
- [ ] `epub/to_pdf.py`
- [ ] `epub/to_markdown.py`
- [ ] `epub/to_html.py`
- [ ] `epub/to_docx.py`

### TXT Converters
- [ ] `txt/to_pdf.py`

## Key Points

1. **Always use error codes** - Every error log should include `[{error_code}]`
2. **Use exc_info=True** - For exception logging to capture stack traces
3. **Complete operations** - Always call `complete_operation()` on both success and failure
4. **Log at appropriate levels**:
   - `DEBUG` - Detailed progress information
   - `INFO` - Important milestones (start, completion)
   - `ERROR` - Failures with error codes
5. **Include context** - Log file paths, sizes, counts, etc. for debugging

