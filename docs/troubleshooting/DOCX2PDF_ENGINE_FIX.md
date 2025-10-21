# DOCX to PDF Engine Auto-Detection Fix

## Issue Summary

**Date**: 2025-10-18
**Log Session**: `app_session_20251018_183810_a1c42a67.log`
**Error**: DOCX to PDF conversion failed with exit code 47

### Root Cause

The DOCX to PDF converter was hardcoded to use `pdflatex` as the default PDF engine. However, `pdflatex` requires a LaTeX distribution (MiKTeX on Windows) to be installed, which was not available on the system.

```
RuntimeError: Pandoc died with exitcode "47" during conversion:
pdflatex not found. Please select a different --pdf-engine or install pdflatex
```

### Error Details

- **File**: `src/transmutation_codex/plugins/docx/to_pdf.py`
- **Function**: `convert_docx_to_pdf()`
- **Line**: 115 (original)
- **Issue**: Default parameter `pdf_engine: str = "pdflatex"` assumed LaTeX is installed

## Solution Implemented

### 1. Auto-Detection Mechanism

Added intelligent PDF engine detection with fallback logic:

```python
def _check_pdf_engine_available(engine: str) -> bool:
    """Check if a specific PDF engine is available on the system."""
    # Uses 'where' on Windows, 'which' on Linux/macOS
    # Returns True if engine found in PATH
```

```python
def _get_available_pdf_engine() -> str:
    """Detect and return the first available PDF engine.

    Tries engines in order of preference:
    1. wkhtmltopdf (most compatible, no LaTeX needed)
    2. pdflatex (best quality, requires MiKTeX)
    3. xelatex (Unicode support, requires MiKTeX)
    4. lualatex (Lua scripting, requires MiKTeX)
    """
```

### 2. Default Changed from "pdflatex" to "auto"

**Before**:

```python
def convert_docx_to_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    pdf_engine: str = "pdflatex",  # ❌ Assumes LaTeX installed
    **options: Any,
) -> Path:
```

**After**:

```python
def convert_docx_to_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    pdf_engine: str = "auto",  # ✅ Auto-detects available engine
    **options: Any,
) -> Path:
```

### 3. Runtime Detection During Conversion

Added logic to detect PDF engine during conversion if set to "auto":

```python
# Auto-detect PDF engine if set to "auto"
if pdf_engine == "auto":
    try:
        pdf_engine = _get_available_pdf_engine()
        logger.info(f"Auto-detected PDF engine: {pdf_engine}")
    except RuntimeError as e:
        logger.error(f"PDF engine detection failed: {e}")
        raise
```

### 4. Updated CLI Arguments

```python
parser.add_argument(
    "--pdf-engine",
    default="auto",  # Changed from "pdflatex"
    choices=["auto", "pdflatex", "xelatex", "lualatex", "wkhtmltopdf"],
    help="PDF engine to use (default: auto)",
)
```

## Benefits

### ✅ Better User Experience

- **No manual configuration required**: Works out of the box with any available engine
- **Clear error messages**: If no engines available, provides installation links
- **Graceful degradation**: Tries wkhtmltopdf first (no LaTeX needed)

### ✅ Flexibility

- Users can still specify a specific engine if desired
- Maintains backward compatibility (explicit engine selection still works)
- Supports all Pandoc-compatible engines

### ✅ Improved Error Handling

- Early detection prevents cryptic Pandoc errors
- Helpful installation instructions in error messages:

  ```
  No PDF engines available. Please install one of the following:
    - wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
    - MiKTeX (provides pdflatex/xelatex/lualatex): https://miktex.org/download
  ```

## Testing

### Test File Created

- **Location**: `tests/test_docx2pdf_engine_detection.py`
- **Tests**:
  1. `test_check_pdf_engine_available()` - Checks which engines are available
  2. `test_get_available_pdf_engine()` - Tests auto-detection logic
  3. `test_convert_docx_to_pdf_auto_engine()` - End-to-end conversion test

### Running the Tests

```bash
# Run specific test file
pytest tests/test_docx2pdf_engine_detection.py -v

# Run with output capture disabled to see print statements
pytest tests/test_docx2pdf_engine_detection.py -v -s

# Run just the detection test
pytest tests/test_docx2pdf_engine_detection.py::test_get_available_pdf_engine -v
```

## Installation Recommendations

### For Users Without Any PDF Engine

**Option 1: wkhtmltopdf (Recommended for simplicity)**

```powershell
# Windows (using Chocolatey)
choco install wkhtmltopdf

# Or download from: https://wkhtmltopdf.org/downloads.html
```

**Option 2: MiKTeX (Recommended for quality)**

```powershell
# Windows (using Chocolatey)
choco install miktex

# Or download from: https://miktex.org/download
```

### Verification

After installing, verify the engine is available:

```powershell
# Check wkhtmltopdf
where wkhtmltopdf

# Check pdflatex (if MiKTeX installed)
where pdflatex
```

## Files Modified

1. **`src/transmutation_codex/plugins/docx/to_pdf.py`**
   - Added `_check_pdf_engine_available()` function
   - Added `_get_available_pdf_engine()` function
   - Changed default `pdf_engine` parameter from `"pdflatex"` to `"auto"`
   - Added runtime detection logic in `convert_docx_to_pdf()`
   - Updated docstring to reflect new behavior
   - Updated CLI argument parser

2. **`tests/test_docx2pdf_engine_detection.py`** (NEW)
   - Comprehensive test suite for engine detection
   - End-to-end conversion test
   - Gracefully skips tests if no engines available

3. **`docs/DOCX2PDF_ENGINE_FIX.md`** (THIS FILE)
   - Documentation of the issue and solution

## Follow-Up Recommendations

### 1. Update GUI

Consider adding PDF engine selection in the GUI:

- Display detected engine to user
- Allow manual override in settings
- Show warning if no engines detected

### 2. Configuration File

Add PDF engine preference to config:

```yaml
# config/default_config.yaml
docx2pdf:
  preferred_engine: "auto"  # or "pdflatex", "wkhtmltopdf", etc.
```

### 3. Documentation Update

Update user-facing docs to mention PDF engine requirements:

- README.md installation section
- GUI help/about dialog
- Error message handling in Electron bridge

### 4. Bundling Consideration

For production deployment, consider bundling wkhtmltopdf:

- Small footprint (~40MB)
- No dependencies (unlike LaTeX distributions)
- Cross-platform support
- Similar approach to bundled Tesseract/Ghostscript

## Conclusion

This fix transforms the DOCX to PDF converter from a brittle, LaTeX-dependent implementation to a robust, auto-detecting solution that gracefully handles various system configurations. The minimal code changes (< 100 lines added) provide significant UX improvements while maintaining full backward compatibility.

**Status**: ✅ FIXED - Ready for testing
