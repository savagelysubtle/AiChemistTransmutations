# Tests Directory Organization

This directory contains all tests for the AiChemist Transmutation Codex project, organized by test type and purpose.

## Directory Structure

```
tests/
├── unit/                          # Unit tests for individual components
│   ├── converters/                # Converter unit tests
│   │   ├── test_docx_to_markdown.py
│   │   ├── test_epub_to_docx.py
│   │   ├── test_markdown_to_pdf_new.py
│   │   ├── test_pdf_to_markdown_new.py
│   │   └── test_txt_to_pdf.py
│   ├── core/                      # ✨ NEW - Core system tests
│   │   ├── test_event_system.py
│   │   ├── test_log_manager.py
│   │   ├── test_config_manager.py
│   │   └── test_progress_tracking.py
│   ├── services/                  # ✨ NEW - Service layer tests
│   │   └── test_batch_processor.py
│   ├── adapters/                  # ✨ NEW - Adapter layer tests
│   │   └── test_electron_bridge.py
│   └── licensing/                 # Licensing system tests
│       └── test_licensing_system.py
│
├── integration/                   # Integration tests
│   ├── test_electron_bridge_integration.py
│   └── test_end_to_end_conversion.py
│
├── system/                        # System & bundled dependency tests
│   ├── test_bundled_tesseract.py
│   └── test_docx2pdf_engine_detection.py
│
├── smoke/                         # Quick smoke tests for rapid validation
│   ├── quick_test.py
│   └── quick_test_docx2md.py
│
├── helpers/                       # Test utilities and environment checks
│   ├── check_env.py               # Environment validation
│   ├── check_deps.py              # Dependency checker
│   ├── check_pdf_engines.py       # PDF engine detection
│   ├── run_tests.py               # Test runner utility
│   ├── test_modular_bridge.py     # Bridge test script
│   └── test_plugin_registry.py    # Registry test script
│
├── test_files/                    # Test fixtures and sample files
│   ├── *.md, *.pdf, *.docx, etc.
│   └── README.md
│
├── conftest.py                    # Pytest configuration & fixtures
├── pytest.ini                     # Pytest settings
└── __init__.py
```

## Test Categories

### Unit Tests (`unit/`)

**Purpose**: Test individual components in isolation

The unit directory is further organized by architectural layer:

- **`converters/`**: Test each converter's core functionality (md2pdf, pdf2md, etc.)
- **`core/`**: Test core infrastructure components
  - Event system (`test_event_system.py`)
  - Progress tracking (`test_progress_tracking.py`)
  - Logging system (`test_log_manager.py`)
  - Configuration management (`test_config_manager.py`)
- **`services/`**: Test service layer components
  - Batch processor (`test_batch_processor.py`)
  - PDF merger and other services
- **`adapters/`**: Test adapter layer components
  - Electron bridge (`test_electron_bridge.py`)
  - CLI adapters
- **`licensing/`**: Test license validation, trials, and feature gates

**When to add**: When implementing new features or components that can be tested independently

**Structure Benefits**:

- Mirrors the source code architecture (`src/transmutation_codex/`)
- Easy to find tests for specific components
- Clear separation between layers
- Supports architectural testing patterns

### Integration Tests (`integration/`)

**Purpose**: Test how components work together

- **Bridge Integration**: Test Electron ↔ Python communication
- **End-to-End**: Test complete conversion workflows

**When to add**: When testing multi-component interactions or full workflows

### System Tests (`system/`)

**Purpose**: Test system dependencies and bundled tools

- **Bundled Tools**: Verify Tesseract, Ghostscript, etc. are properly bundled
- **Engine Detection**: Test detection of external tools

**When to add**: When adding new external dependencies or bundled tools

### Smoke Tests (`smoke/`)

**Purpose**: Quick validation tests for rapid feedback

- Fast-running tests (<5 seconds)
- High-level functionality checks
- Used for quick validation during development

**When to add**: For quick sanity checks before running full test suite

### Test Helpers (`helpers/`)

**Purpose**: Utilities for testing and environment validation

- **Environment checkers**: `check_env.py` - Validate Python environment
- **Dependency validators**: `check_deps.py` - Check external dependencies
- **Diagnostic tools**: `check_pdf_engines.py` - Verify PDF engine availability
- **Test runners**: `run_tests.py` - Custom test execution utility
- **Manual test scripts**:
  - `test_modular_bridge.py` - Bridge architecture validation
  - `test_plugin_registry.py` - Plugin system verification

**Note**: These are not pytest tests. They are standalone scripts for diagnostics and validation.

**When to add**: When creating reusable test utilities or diagnostic scripts

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# System tests
pytest tests/system/ -v

# Smoke tests (fast)
pytest tests/smoke/ -v
```

### Run by Architectural Layer

```bash
# Core system tests
pytest tests/unit/core/ -v

# Service layer tests
pytest tests/unit/services/ -v

# Adapter layer tests
pytest tests/unit/adapters/ -v

# Converter tests
pytest tests/unit/converters/ -v

# Licensing tests
pytest tests/unit/licensing/ -v
```

### Run by Test Markers

```bash
# Run unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Test specific converter
pytest tests/unit/converters/test_pdf_to_markdown_new.py -v

# Test licensing system
pytest tests/unit/licensing/test_licensing_system.py -v

# Quick smoke test
python tests/smoke/quick_test.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=transmutation_codex --cov-report=html

# View coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

## Test Utilities

### Environment Checker

```bash
python tests/helpers/check_env.py
```

### Dependency Checker

```bash
python tests/helpers/check_deps.py
```

### PDF Engine Checker

```bash
python tests/helpers/check_pdf_engines.py
```

## Writing New Tests

### Test File Naming

- **Unit tests**: `test_<component_name>.py`
- **Integration tests**: `test_<feature>_integration.py`
- **System tests**: `test_<tool>_<aspect>.py`
- **Smoke tests**: `quick_test_<feature>.py`

### Test Function Naming

- Use descriptive names: `test_convert_pdf_to_markdown_with_ocr()`
- Not: `test_conversion()` or `test1()`
- Follow pattern: `test_<what>_<condition>_<expected_result>()`

### Test Structure

```python
def test_feature_name():
    """Test description explaining what is being tested."""
    # Arrange: Set up test data and preconditions
    input_data = create_test_data()

    # Act: Execute the code being tested
    result = function_under_test(input_data)

    # Assert: Verify the results
    assert result == expected_output
    assert result.property == expected_value
```

### Using Fixtures

```python
@pytest.fixture
def sample_pdf_file(tmp_path):
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    # Create PDF...
    return pdf_path

def test_with_fixture(sample_pdf_file):
    """Test using the fixture."""
    result = convert_pdf(sample_pdf_file)
    assert result.exists()
```

### Test Markers

Add markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_unit_function():
    """Unit test."""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """Integration test."""
    pass

@pytest.mark.slow
def test_large_file_conversion():
    """Slow-running test."""
    pass

@pytest.mark.skipif(not has_tesseract(), reason="Tesseract not installed")
def test_ocr_conversion():
    """Test requiring Tesseract."""
    pass
```

## Test Files (`test_files/`)

Sample files for testing conversions:

- **Markdown**: `test.md`, `batch_test_4.md`
- **DOCX**: `batch_test_2.docx`, `electron_test.docx`
- **PDF**: Various test PDFs
- **EPUB**: `test_epub_*.epub` (5 files)
- **Images**: `test_image_*.*` (6 files)
- **CSV/Excel**: `test_csv_*.csv`, `test_excel_sample.xlsx`
- **PowerPoint**: `test_powerpoint_sample.pptx`

### Adding New Test Files

1. Place files in `test_files/`
2. Use descriptive names: `test_<format>_<description>.<ext>`
3. Keep file sizes small (< 1MB preferred)
4. Document special characteristics in `test_files/README.md`

## Continuous Integration

Tests are run automatically on:

- Every pull request
- Every commit to `main` branch
- Nightly builds

### CI Test Matrix

- Python 3.13 on Windows, macOS, Linux
- Multiple converter configurations
- With and without optional dependencies

## Test Coverage Goals

- **Unit Tests**: > 80% code coverage
- **Integration Tests**: All major workflows covered
- **System Tests**: All external dependencies validated
- **Overall**: > 75% code coverage

## Troubleshooting Tests

### Tests Fail Locally

1. Check Python version: `python --version` (should be 3.13+)
2. Verify dependencies: `python tests/helpers/check_deps.py`
3. Check environment: `python tests/helpers/check_env.py`
4. Run with verbose output: `pytest -vv`

### Skipped Tests

Some tests may be skipped if:

- External tools not installed (Tesseract, Ghostscript, etc.)
- Optional dependencies missing
- Running in CI environment

To see why tests are skipped:

```bash
pytest -v -rs
```

### Slow Tests

To identify slow tests:

```bash
pytest --durations=10
```

## Best Practices

1. **Keep tests independent**: Each test should be able to run alone
2. **Use fixtures**: Share setup code with pytest fixtures
3. **Clean up**: Always clean up temporary files
4. **Test edge cases**: Test boundary conditions, empty inputs, large files
5. **Descriptive names**: Test names should describe what they test
6. **One assertion concept per test**: Test one thing at a time
7. **Fast feedback**: Keep unit tests fast (< 1 second each)
8. **Use markers**: Tag tests appropriately (unit, integration, slow)

## Common Issues

### Import Errors

- Ensure `PYTHONPATH` includes project root
- Check `__init__.py` files exist in all directories
- Verify package structure is correct

### File Not Found

- Use `tmp_path` fixture for temporary files
- Use `test_files/` for static test files
- Always use `Path` objects for cross-platform compatibility

### Flaky Tests

- Avoid time-dependent tests
- Use mocking for external dependencies
- Ensure proper cleanup in teardown

---

**Last Updated**: October 21, 2025
**Maintainer**: @savagelysubtle

For more information, see:

- [TESTING_MAIN_BRANCH.md](../TESTING_MAIN_BRANCH.md) - Testing plan
- [TEST_RESULTS_SUMMARY.md](../TEST_RESULTS_SUMMARY.md) - Latest test results
- [pytest.ini](pytest.ini) - Pytest configuration
