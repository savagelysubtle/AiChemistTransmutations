# Test Suite Overview

This document provides an overview of the test suite for the AiChemist Transmutation Codex project.

## Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                  # Pytest configuration
├── quick_test.py              # Quick smoke test for development
├── check_deps.py              # Dependency checker
├── check_env.py               # Environment checker
├── test_files/                # Test data files
│   ├── test_pdfs/
│   └── output_md/
├── unit/                      # Unit tests
│   ├── run_tests.py          # Test runner script
│   ├── test_batch_processor.py
│   ├── test_config_manager.py
│   ├── test_electron_bridge.py
│   ├── test_event_system.py
│   ├── test_log_manager.py
│   ├── test_modular_bridge.py
│   ├── test_plugin_registry.py
│   ├── test_progress_tracking.py
│   └── test_converters/      # Converter-specific tests
│       ├── test_markdown_to_pdf_new.py
│       ├── test_pdf_to_markdown_new.py
│       └── test_txt_to_pdf.py
└── integration/               # Integration tests
    ├── test_electron_bridge_integration.py
    └── test_end_to_end_conversion.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

**Core System Tests:**

- `test_config_manager.py` - Configuration management tests
- `test_log_manager.py` - Logging system tests
- `test_event_system.py` - Event bus tests
- `test_progress_tracking.py` - Progress tracking tests
- `test_plugin_registry.py` - Plugin registry tests

**Adapter Tests:**

- `test_electron_bridge.py` - Electron bridge tests (legacy)
- `test_modular_bridge.py` - Modular bridge tests

**Service Tests:**

- `test_batch_processor.py` - Batch processing tests

**Converter Tests (`test_converters/`):**

- `test_pdf_to_markdown_new.py` - PDF to Markdown conversion tests
- `test_markdown_to_pdf_new.py` - Markdown to PDF conversion tests
- `test_txt_to_pdf.py` - TXT to PDF conversion tests

### Integration Tests (`tests/integration/`)

- `test_electron_bridge_integration.py` - Bridge integration tests
- `test_end_to_end_conversion.py` - End-to-end conversion workflows

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_plugin_registry.py

# Specific test function
pytest tests/unit/test_plugin_registry.py::test_register_converter
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run file operation tests
pytest -m file_operations

# Run async tests
pytest -m asyncio
```

### Run with Coverage

```bash
pytest --cov=transmutation_codex --cov-report=html
```

### Quick Development Test

```bash
python tests/quick_test.py
```

## Test Markers

The following pytest markers are available:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.file_operations` - Tests involving file I/O
- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.metadata` - Metadata extraction tests
- `@pytest.mark.slow` - Slow-running tests

## Test Fixtures

Key fixtures available in `conftest.py`:

- `temp_output_dir` - Temporary directory for test outputs
- `test_pdf_path` - Path to test PDF file
- `test_md_path` - Path to test Markdown file
- `mock_registry` - Mocked plugin registry
- `mock_log_manager` - Mocked log manager
- `mock_progress_tracker` - Mocked progress tracker

## Test Files

Test data is located in `tests/test_files/`:

- `test_pdfs/` - Sample PDF files for testing
- `output_md/` - Expected Markdown outputs
- `*.md`, `*.pdf` - Various test files

## Notes

- Converter tests check both basic functionality and Phase 1/2 features (progress tracking, event system, registry integration)
- All new converters must have corresponding tests
- Tests should cover happy path, error cases, and edge cases
- Integration tests verify cross-component functionality
- Quick test (`quick_test.py`) provides fast smoke testing during development

## Test Coverage Goals

- **Core Systems**: 90%+ coverage
- **Converters**: 80%+ coverage
- **Adapters**: 70%+ coverage
- **Services**: 80%+ coverage

## Adding New Tests

When adding new functionality:

1. **Add unit tests** in `tests/unit/` for the specific component
2. **Add integration tests** in `tests/integration/` if the feature involves multiple components
3. **Add test data** to `tests/test_files/` if needed
4. **Update this document** if adding new test categories or markers
5. **Ensure tests pass** before committing

## CI/CD Integration

Tests are run automatically on:

- Pull requests
- Commits to main branch
- Pre-release tags

CI runs the full test suite with coverage reporting.
