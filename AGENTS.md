# AGENTS.md

This file provides guidance for AI coding agents working on the AiChemist Transmutation Codex project.

## Project Overview

AiChemist Transmutation Codex is a Python library for converting between different document formats with a focus on Markdown and PDF conversions. The project includes:

- **Core Python Library**: Document conversion plugins and services
- **CLI Interface**: Command-line tool for document conversion
- **GUI Application**: Electron-based desktop application with React frontend
- **Electron Bridge**: Integration layer between Python backend and Electron frontend

## Architecture & Structure

### Core Components
- `src/transmutation_codex/` - Main Python package
  - `core/` - Core utilities (settings, logging)
  - `plugins/` - Format-specific conversion plugins (markdown, pdf, html, txt)
  - `services/` - Business logic (batcher, merger)
  - `adapters/` - Interface adapters (CLI, Electron bridge)

### Frontend (GUI)
- `gui/` - Electron application
  - `src/renderer/` - React TypeScript frontend
  - `src/main/` - Electron main process
  - `src/converters/` - Frontend conversion utilities

### Configuration
- `config/` - Configuration files
- `pyproject.toml` - Python project configuration
- `gui/package.json` - Node.js dependencies for GUI

## Development Environment Setup

### Python Environment
```bash
# Install Python dependencies (requires Python >=3.13.0)
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check
```

### GUI Development
```bash
# Navigate to GUI directory
cd gui/

# Install Node.js dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### External Dependencies
- **Tesseract OCR**: Required for OCR functionality
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

## Testing Guidelines

### Test Structure
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - End-to-end integration tests
- `tests/test_files/` - Test data and sample files

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration

# Run tests with coverage
pytest --cov=transmutation_codex
```

### Test File Conventions
- Use `test_*.py` naming convention
- Place unit tests in `tests/unit/test_<module_name>/`
- Add integration tests for cross-component functionality
- Include test data in `tests/test_files/`

## Code Style & Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use Ruff for linting and formatting
- Type hints required for all function signatures
- Docstrings required for public methods and classes

### TypeScript/React Style
- Use TypeScript strict mode
- Follow React functional component patterns
- Use Tailwind CSS for styling
- ESLint configuration provided in `gui/.eslintrc.js`

### Import Organization
```python
# Standard library imports first
import os
import sys

# Third-party imports
import PyPDF2
import yaml

# Local application imports
from transmutation_codex.core import settings
from transmutation_codex.plugins.pdf import to_markdown
```

## Plugin Development

### Adding New Conversion Plugins
1. Create new module in `src/transmutation_codex/plugins/<format>/`
2. Implement conversion functions following existing patterns
3. Add error handling and logging
4. Write unit tests in `tests/unit/test_converters/`
5. Update CLI interface in `adapters/cli/main.py`

### Plugin Interface Pattern
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

## CLI Commands

### Development Commands
```bash
# Run the CLI tool
python -m transmutation_codex.adapters.cli.main --help

# Convert files
python -m transmutation_codex.adapters.cli.main --type md2pdf --input file.md --output file.pdf

# Launch GUI
python -m transmutation_codex.adapters.cli.main --gui
```

### GUI Commands
```bash
cd gui/
npm run dev              # Start development server
npm run build            # Build for production
npm run electron:dev     # Run Electron in development
npm run electron:build   # Build Electron app
```

## Error Handling

### Error Patterns
- Use custom exception classes defined in `core/`
- Log errors with appropriate severity levels
- Provide user-friendly error messages in GUI
- Include context information in error logs

### Logging
- Use the logger configured in `core/logger.py`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include module name and function context in logs

## File Handling Best Practices

### Input Validation
- Always validate file paths and formats before processing
- Check file permissions and accessibility
- Validate file size limits for memory-intensive operations

### OCR Integration
- Use OCR only when regular text extraction fails
- Support multiple languages via `--ocr-lang` parameter
- Configure DPI settings for optimal accuracy vs. performance

### Memory Management
- Process large files in chunks when possible
- Clean up temporary files after processing
- Monitor memory usage for batch operations

## GUI Development

### Component Structure
- Keep components small and focused
- Use TypeScript interfaces for props
- Implement proper error boundaries
- Follow React hooks patterns

### Electron Integration
- Use IPC (Inter-Process Communication) for Python bridge
- Handle file system operations through main process
- Implement proper security practices for file access

## Common Tasks

### Adding a New Format
1. Create plugin module in `plugins/<format>/`
2. Implement conversion functions
3. Add CLI support in `adapters/cli/main.py`
4. Add GUI support in `gui/src/renderer/components/`
5. Write comprehensive tests
6. Update documentation

### Debugging Conversion Issues
1. Check input file format and validity
2. Verify external dependencies (Tesseract, etc.)
3. Review conversion logs for specific errors
4. Test with minimal input files
5. Check memory and disk space availability

### Performance Optimization
1. Profile conversion operations with large files
2. Implement streaming for memory-efficient processing
3. Add progress indicators for long-running operations
4. Consider parallel processing for batch operations

## Security Considerations

- Validate all user inputs and file paths
- Sanitize filenames and prevent directory traversal
- Limit file size and processing time for uploaded files
- Use secure file handling practices in Electron

## Deployment

### Python Package
- Build with `python -m build`
- Deploy to PyPI with proper versioning
- Include all necessary dependencies in `pyproject.toml`

### GUI Application
- Build platform-specific installers with electron-builder
- Test on target platforms (Windows, macOS, Linux)
- Include Python runtime in distributed packages

## Contributing

- Follow the existing code patterns and conventions
- Add tests for all new functionality
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all tests pass before submitting changes