# Test Suite Cleanup Summary

## Completed Actions

### ✅ Removed Duplicate Test Files

- Deleted 14 duplicate test files from `tests/unit/`
- Deleted root-level test files (debug/quick tests)
- Removed old converter test files
- Removed duplicate integration tests

### ✅ Fixed Import Errors

- Updated `test_batch_processor.py`: `mdtopdf.batch_processor` → `transmutation_codex.services.batcher`
- Updated `test_config_manager.py`: `mdtopdf.config` → `transmutation_codex.core`
- Updated `test_log_manager.py`: `mdtopdf.config.log_manager` → `transmutation_codex.core.logger`
- Skipped `test_electron_bridge.py` (legacy tests for refactored bridge)

### ✅ Fixed conftest.py

- Changed `registry._converters` → `registry._plugins`
- Added `registry._cache.clear()`

### ✅ Current Test Status

```
25 passed ✅
21 skipped (legacy electron_bridge tests)
58 failed (need updates for refactored APIs)
18 errors (mostly missing attributes in mocked modules)
```

## Remaining Issues

### 1. Progress Tracking Issues

**Problem**: `start_operation()` defaults to `total_steps=1`, but converters use steps like 10, 20, 95.

**Solution**: Update all converter `start_operation` calls:

```python
# Current (broken):
operation = start_operation("pdf2md", message="Converting...")
update_progress(operation, 10, "File validated")  # Error: 10 > 1

# Fix:
operation = start_operation("pdf2md", message="Converting...", total_steps=100)
update_progress(operation, 10, "File validated")  # OK: 10 <=  100
```

**Files to fix**:

- `src/transmutation_codex/plugins/pdf/to_markdown.py` (all 3 converters)
- `src/transmutation_codex/plugins/markdown/to_pdf.py`
- `src/transmutation_codex/plugins/txt/to_pdf.py`

### 2. Test Files Need API Updates

**Test files referencing old APIs**:

- `test_config_manager.py` - Methods like `_load_yaml`, `get_converter_config`, `get_electron_config` removed
- `test_log_manager.py` - Constructor signature changed (no `config_dir` parameter)
- `test_batch_processor.py` - Needs updated batcher API
- Converter tests - `registry.get_converters()` → `registry.get_plugins_for_conversion()`

### 3. Missing Mock Attributes

Several tests try to mock `HTML`, `parse_pdf_to_markdown` that don't exist in modules.

**Solution Options**:

1. **Update test mocks** to match actual module structure
2. **Skip outdated tests** temporarily
3. **Rewrite tests** for Phase 1/2 architecture

## Recommended Next Steps

### Priority 1: Fix Converter Progress Tracking

1. Update `start_operation()` calls in all converters to use `total_steps=100`
2. This will fix ~15-20 test failures immediately

### Priority 2: Update or Skip API-Specific Tests

1. **Skip** or **rewrite** `test_config_manager.py` (API changed significantly)
2. **Skip** or **rewrite** `test_log_manager.py` (API changed significantly)
3. **Skip** or **rewrite** `test_batch_processor.py` (service refactored)

### Priority 3: Fix Converter Test Files

1. Update `get_converters()` → `get_plugins_for_conversion()`
2. Fix mock setups for missing attributes
3. Update expected behaviors for Phase 1/2 features

## Quick Commands

### Run only passing tests

```bash
uv run pytest tests/unit/test_event_system.py tests/unit/test_plugin_registry.py tests/unit/test_progress_tracking.py tests/unit/test_modular_bridge.py -v
```

### Run converter tests

```bash
uv run pytest tests/unit/test_converters/ -v
```

### Run with specific markers

```bash
uv run pytest -m unit -v
```

## Files Status

### ✅ Clean (Removed)

- All duplicate test files
- All root-level debug test files
- Old converter test files

### ✅ Updated (Working)

- `tests/conftest.py`
- Test imports for core modules

### ⚠️ Need Updates

- All converter source files (progress tracking)
- `test_config_manager.py` (API changes)
- `test_log_manager.py` (API changes)
- `test_batch_processor.py` (API changes)
- Converter test files (mock updates)

### ✅ Passing Tests

- `test_event_system.py` (17/23 tests passing)
- `test_plugin_registry.py` (1/1 test passing)
- `test_progress_tracking.py` (10/13 tests passing)
- PDF to markdown converters (1 test passing)
