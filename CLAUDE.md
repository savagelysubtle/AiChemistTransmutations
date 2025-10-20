# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiChemist Transmutation Codex is a document conversion toolkit with a Python backend and Electron/React GUI. The system is modular and plugin-based, where each format converter is encapsulated in its own module.

**Key Architecture Pattern**: Converters are organized by **source format**, not by conversion direction. Each converter file is named `to_<target>.py` within its source format directory.

## Development Commands

### Python Backend

```bash
# Install dependencies (Python 3.13+ with UV)
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m file_operations

# Run single test file
pytest tests/unit/test_converters/test_md2pdf.py

# Linting
ruff check

# CLI tool execution
python -m transmutation_codex.adapters.cli.main --help
codex --help  # After installation

# Example conversions
python -m transmutation_codex.adapters.cli.main --type md2pdf --input file.md --output file.pdf
python -m transmutation_codex.adapters.cli.main --type pdf2md --input file.pdf --output file.md --ocr
```

### GUI Application

```bash
cd gui/

# Install Node dependencies
npm install

# Development mode
npm run dev

# Run Electron in development
npm run electron:dev

# Build for production
npm run build
npm run electron:build

# Linting
npm run lint
```

## Architecture

### Directory Structure

```
src/transmutation_codex/
├── adapters/          # All inbound interfaces
│   ├── bridges/       # Electron bridge (electron_bridge.py)
│   └── cli/           # CLI entry points (main.py)
├── core/              # Shared infrastructure
│   ├── logger.py      # LogManager singleton
│   ├── config_manager.py
│   ├── events.py      # Event bus system
│   ├── progress.py    # Progress tracking
│   ├── registry.py    # Plugin registry
│   └── exceptions.py  # Custom exceptions
├── plugins/           # Format converters (organized by SOURCE format)
│   ├── markdown/      # Converters FROM markdown
│   │   ├── to_pdf.py
│   │   └── to_docx.py
│   ├── pdf/           # Converters FROM pdf
│   │   ├── to_markdown.py
│   │   └── to_html.py
│   ├── html/          # Converters FROM html
│   │   └── to_pdf.py
│   └── txt/           # Converters FROM txt
│       └── to_pdf.py
├── services/          # Business logic orchestration
│   ├── batcher.py     # Batch processing
│   └── merger.py      # PDF merging
└── utils/             # Generic helpers (use sparingly)

gui/
├── src/
│   ├── main/          # Electron main process
│   ├── renderer/      # React frontend
│   │   ├── components/
│   │   ├── pages/
│   │   ├── contexts/
│   │   └── utils/
│   └── converters/    # Node.js converters (only if Python not sufficient)
```

### Core Systems

**Logging System**: All backend modules MUST use the centralized `LogManager` from `core/`:

```python
from transmutation_codex.core import get_log_manager

logger = get_log_manager().get_converter_logger("md2pdf")
logger.info("Converting markdown to PDF")
```

- Never use stdlib `logging` directly
- Never reimplement logging logic
- LogManager is a singleton with session-based tracking
- Outputs JSON-formatted logs to stdout for Electron bridge (prefixed with `LOG_MESSAGE:`)
- Also writes to `logs/python/app_session_{session_id}.log`

**Configuration Management**: Use `ConfigManager` from `core/`:

```python
from transmutation_codex.core import get_config_manager

config = get_config_manager().get_converter_config("md2pdf")
```

**Event System**: Event bus for decoupled communication:

```python
from transmutation_codex.core import subscribe, publish, ConversionEvent

subscribe(EventTypes.CONVERSION_STARTED, my_handler)
publish(ConversionEvent(...))
```

**Progress Tracking**: Unified progress reporting:

```python
from transmutation_codex.core import start_operation, update_progress, complete_operation

operation = start_operation("conversion", "Converting file.md")
update_progress(operation.id, 50, "Processing pages")
complete_operation(operation.id)
```

### Python ↔ Electron Communication

The Electron main process communicates with Python backend via stdout/stderr, parsing JSON messages with prefixes:

- `PROGRESS:` - Progress updates
- `RESULT:` - Conversion results
- `ERROR:` - Error messages
- `LOG_MESSAGE:` - Structured log entries

The bridge is located at [adapters/bridges/electron_bridge.py](src/transmutation_codex/adapters/bridges/electron_bridge.py). Always use async functions when communicating between languages.

## Critical Conventions

### Plugin Organization Rules

1. **Group by source format**: All converters that take Markdown as input → `plugins/markdown/`
2. **Name by target format**: Markdown to PDF converter → `plugins/markdown/to_pdf.py`
3. **No cross-imports between plugins**: Plugin modules cannot import from other plugin folders. Use `core/` or `services/` for shared code.
4. **Function-based API**: Converters use function-based API (not class-based) for simplicity

### Naming Conventions

- Avoid redundant naming: `adapters/cli/main.py` not `adapters/cli/cli.py`
- Fixed core locations:
  - Logger: `core/logger.py`
  - Settings: `core/settings.py` and `core/config_manager.py`
  - Electron bridge: `adapters/bridges/electron_bridge.py`
  - CLI entry: `adapters/cli/main.py`

### Import Organization

```python
# Standard library imports
import os
import sys

# Third-party imports
import PyPDF2
import yaml

# Local application imports
from transmutation_codex.core import get_log_manager, ConfigManager
from transmutation_codex.plugins.pdf import to_markdown
```

## Adding a New Converter

Follow this workflow (strictly enforced):

1. **Create plugin**: `src/transmutation_codex/plugins/[source]/to_[target].py`
   - Implement conversion function following existing patterns
   - Use `get_log_manager().get_converter_logger("source2target")`
   - Use `get_config_manager()` for configuration

2. **Add tests**: `tests/plugins/[source]/test_to_[target].py`
   - Mirror the plugin folder structure

3. **Update services**: If batch/merge operations needed, update `services/`

4. **Expose via bridge**: Update `adapters/bridges/electron_bridge.py` (ALWAYS required)

5. **Update GUI**:
   - Add/update React components in `gui/src/renderer/components/`
   - Add/update pages in `gui/src/renderer/pages/`
   - Ensure actions display in `ConversionLog.tsx`
   - Only modify `gui/src/converters/` if Python implementation is insufficient (rare)

6. **Document**: Update README and plugin registry

7. **Test**: Run all tests before merging

## External Dependencies

**Tesseract OCR** (required for PDF OCR functionality):
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## Project-Specific Context

- **Platform**: Windows-focused document converter
- **Python version**: 3.13+
- **Package manager**: UV (configured in `pyproject.toml`)
- **GUI stack**: Electron + React + TypeScript + TailwindCSS
- **Styling**: TailwindCSS with Shadcn/UI components
- **State management**: React hooks (useState, useEffect)
- **Build system**: UV for Python, Vite for GUI

## Test Markers

Use pytest markers for targeted test runs:

```bash
pytest -m unit              # Unit tests
pytest -m integration       # Integration tests
pytest -m file_operations   # File operation tests
pytest -m asyncio           # Async tests
pytest -m metadata          # Metadata extraction tests
pytest -m slow              # Slow-running tests
```

## Common Patterns

### Converter Function Signature

```python
def convert_format_to_format(
    input_path: str,
    output_path: str,
    **options
) -> bool:
    """Convert from one format to another.

    Args:
        input_path: Path to input file
        output_path: Path for output file
        **options: Format-specific options

    Returns:
        bool: True if conversion successful

    Raises:
        ConversionError: If conversion fails
    """
```

### Error Handling

Use custom exceptions from `core/exceptions.py`:

```python
from transmutation_codex.core import (
    ConversionError,
    raise_conversion_error,
    raise_validation_error
)

try:
    validate_input(input_path)
except Exception as e:
    raise_validation_error(f"Invalid input: {e}")
```

### Progress Reporting

```python
from transmutation_codex.core import start_operation, update_progress, complete_operation

operation = start_operation("conversion", "Converting document")
try:
    # Do work
    update_progress(operation.id, 50, "Processing pages")
    # More work
    complete_operation(operation.id, {"output_path": output_path})
except Exception as e:
    # Progress system handles error state
    raise
```

## Important Notes

- **Session-based logging**: Every run gets a unique session ID visible in logs
- **No direct stdlib logging**: Always use `LogManager`
- **No direct config file parsing**: Always use `ConfigManager`
- **Plugin isolation**: Plugins must not import from other plugin directories
- **Test structure mirrors code**: Tests follow the same directory structure as source code
- **GUI prefers Python**: Only implement converters in Node.js if Python libraries are insufficient
