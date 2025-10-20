"""Utility modules for the Transmutation Codex.

This package contains pure, stateless utility functions such as file operations,
format detection, validation, security helpers, metadata extraction, performance
measurement, and caching utilities that have minimal dependencies and no business logic.
"""

# Import validation utilities
# Import cache utilities
from .cache import (
    CacheEntry,
    ConversionCache,
    cache_conversion,
    cache_result,
    clear_cache,
    configure_cache,
    get_cache,
    get_cache_stats,
    get_cached_result,
    invalidate_cache,
)

# Import file utilities
from .file_utils import (
    FILE_SIGNATURES,
    MIME_TYPE_MAPPINGS,
    backup_file,
    clean_directory,
    create_temp_directory,
    create_temp_file,
    detect_file_format,
    ensure_directory_exists,
    find_files_by_extension,
    get_directory_size,
    get_file_info,
    get_unique_filename,
    read_file_chunks,
    safe_copy_file,
    safe_delete_file,
    safe_move_file,
)

# Import metadata utilities
from .metadata import (
    add_conversion_metadata,
    extract_document_metadata,
    extract_file_metadata,
    extract_html_metadata,
    extract_markdown_metadata,
    extract_pdf_metadata,
    extract_text_metadata,
    load_preserved_metadata,
    preserve_metadata,
)

# Import performance utilities
from .performance import (
    PerformanceMetrics,
    PerformanceMonitor,
    benchmark_system,
    get_performance_monitor,
    get_system_info,
    measure_performance,
    time_operation,
)

# Import security utilities
from .security import (
    DANGEROUS_EXTENSIONS,
    MAX_FILENAME_LENGTH,
    RESTRICTED_NAMES,
    calculate_file_hash,
    clean_user_input,
    create_secure_temp_path,
    is_path_within_directory,
    is_safe_file_extension,
    is_safe_path,
    sanitize_filename,
    sanitize_url_component,
    secure_file_copy_validation,
    validate_directory_permissions,
    validate_file_content_basic,
)
from .validators import (
    DEFAULT_MAX_FILE_SIZE_MB,
    OCR_MAX_FILE_SIZE_MB,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OCR_LANGUAGES,
    SUPPORTED_OUTPUT_FORMATS,
    get_file_extension,
    is_supported_input_format,
    is_supported_output_format,
    validate_batch_inputs,
    validate_conversion_type,
    validate_file_format,
    validate_file_path,
    validate_file_size,
    validate_ocr_dpi,
    validate_ocr_language,
    validate_output_path,
)

# Utils module exports
__all__ = [
    # Validation utilities
    "validate_file_path",
    "validate_output_path",
    "validate_file_format",
    "validate_file_size",
    "validate_ocr_language",
    "validate_ocr_dpi",
    "validate_conversion_type",
    "validate_batch_inputs",
    "get_file_extension",
    "is_supported_input_format",
    "is_supported_output_format",
    "SUPPORTED_INPUT_FORMATS",
    "SUPPORTED_OUTPUT_FORMATS",
    "SUPPORTED_OCR_LANGUAGES",
    "DEFAULT_MAX_FILE_SIZE_MB",
    "OCR_MAX_FILE_SIZE_MB",
    # Security utilities
    "is_safe_path",
    "sanitize_filename",
    "is_safe_file_extension",
    "validate_file_content_basic",
    "create_secure_temp_path",
    "calculate_file_hash",
    "is_path_within_directory",
    "sanitize_url_component",
    "validate_directory_permissions",
    "secure_file_copy_validation",
    "clean_user_input",
    "DANGEROUS_EXTENSIONS",
    "MAX_FILENAME_LENGTH",
    "RESTRICTED_NAMES",
    # File utilities
    "detect_file_format",
    "get_file_info",
    "create_temp_file",
    "create_temp_directory",
    "safe_copy_file",
    "safe_move_file",
    "safe_delete_file",
    "clean_directory",
    "ensure_directory_exists",
    "get_directory_size",
    "find_files_by_extension",
    "get_unique_filename",
    "read_file_chunks",
    "backup_file",
    "MIME_TYPE_MAPPINGS",
    "FILE_SIGNATURES",
    # Metadata utilities
    "extract_file_metadata",
    "extract_pdf_metadata",
    "extract_markdown_metadata",
    "extract_html_metadata",
    "extract_text_metadata",
    "extract_document_metadata",
    "add_conversion_metadata",
    "preserve_metadata",
    "load_preserved_metadata",
    # Performance utilities
    "PerformanceMonitor",
    "PerformanceMetrics",
    "get_performance_monitor",
    "measure_performance",
    "time_operation",
    "get_system_info",
    "benchmark_system",
    # Cache utilities
    "ConversionCache",
    "CacheEntry",
    "get_cache",
    "configure_cache",
    "get_cached_result",
    "cache_result",
    "invalidate_cache",
    "clear_cache",
    "get_cache_stats",
    "cache_conversion",
]


def validate_file_path(file_path: str) -> tuple[bool, str | None]:
    """Validate that a file path is safe and accessible.

    Args:
        file_path: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not isinstance(file_path, str):
        return False, "File path must be a non-empty string"

    if len(file_path.strip()) == 0:
        return False, "File path cannot be empty or whitespace"

    try:
        path = Path(file_path)

        # Check for path traversal attempts
        if ".." in path.parts:
            return False, "Path traversal detected in file path"

        # Check if path exists
        if not path.exists():
            return False, f"File does not exist: {file_path}"

        # Check if it's a file (not directory)
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        # Check if file is readable
        if not os.access(path, os.R_OK):
            return False, f"File is not readable: {file_path}"

        return True, None

    except (OSError, ValueError) as e:
        return False, f"Invalid file path: {e!s}"


def validate_output_path(output_path: str) -> tuple[bool, str | None]:
    """Validate that an output path is safe and writable.

    Args:
        output_path: Output path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not output_path or not isinstance(output_path, str):
        return False, "Output path must be a non-empty string"

    if len(output_path.strip()) == 0:
        return False, "Output path cannot be empty or whitespace"

    try:
        path = Path(output_path)

        # Check for path traversal attempts
        if ".." in path.parts:
            return False, "Path traversal detected in output path"

        # Check if parent directory exists and is writable
        parent_dir = path.parent
        if not parent_dir.exists():
            return False, f"Output directory does not exist: {parent_dir}"

        if not os.access(parent_dir, os.W_OK):
            return False, f"Output directory is not writable: {parent_dir}"

        # If file exists, check if it's writable
        if path.exists():
            if not path.is_file():
                return False, f"Output path exists but is not a file: {output_path}"
            if not os.access(path, os.W_OK):
                return False, f"Output file is not writable: {output_path}"

        return True, None

    except (OSError, ValueError) as e:
        return False, f"Invalid output path: {e!s}"


def validate_file_format(
    file_path: str, expected_formats: list[str]
) -> tuple[bool, str | None]:
    """Validate that a file has one of the expected formats.

    Args:
        file_path: Path to the file
        expected_formats: List of acceptable file extensions (without dots)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not isinstance(file_path, str):
        return False, "File path must be a non-empty string"

    if not expected_formats:
        return False, "Expected formats list cannot be empty"

    try:
        path = Path(file_path)
        file_extension = path.suffix.lower().lstrip(".")

        if not file_extension:
            return False, f"File has no extension: {file_path}"

        # Normalize expected formats
        normalized_formats = [fmt.lower().lstrip(".") for fmt in expected_formats]

        if file_extension not in normalized_formats:
            return (
                False,
                f"Unsupported file format '.{file_extension}'. Expected: {', '.join(normalized_formats)}",
            )

        return True, None

    except Exception as e:
        return False, f"Error validating file format: {e!s}"


def validate_file_size(
    file_path: str, max_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB
) -> tuple[bool, str | None]:
    """Validate that a file size is within acceptable limits.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in megabytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path or not isinstance(file_path, str):
        return False, "File path must be a non-empty string"

    if max_size_mb <= 0:
        return False, "Maximum file size must be positive"

    try:
        path = Path(file_path)

        if not path.exists():
            return False, f"File does not exist: {file_path}"

        file_size_bytes = path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        if file_size_mb > max_size_mb:
            return False, f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"

        return True, None

    except (OSError, ValueError) as e:
        return False, f"Error checking file size: {e!s}"


def validate_ocr_language(lang_code: str) -> tuple[bool, str | None]:
    """Validate OCR language code.

    Args:
        lang_code: Tesseract language code (e.g., 'eng', 'fra', 'eng+fra')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not lang_code or not isinstance(lang_code, str):
        return False, "Language code must be a non-empty string"

    # Handle multiple languages separated by '+'
    languages = [lang.strip() for lang in lang_code.split("+")]

    for lang in languages:
        if not lang:
            return False, "Empty language code detected"

        if lang not in SUPPORTED_OCR_LANGUAGES:
            supported = ", ".join(sorted(SUPPORTED_OCR_LANGUAGES))
            return False, f"Unsupported language '{lang}'. Supported: {supported}"

    return True, None


def validate_ocr_dpi(dpi: int) -> tuple[bool, str | None]:
    """Validate OCR DPI setting.

    Args:
        dpi: Dots per inch for OCR scanning

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(dpi, int):
        return False, "DPI must be an integer"

    if dpi < 72:
        return False, "DPI too low (minimum: 72)"

    if dpi > 1200:
        return False, "DPI too high (maximum: 1200)"

    return True, None


def validate_conversion_type(conversion_type: str) -> tuple[bool, str | None]:
    """Validate conversion type specification.

    Args:
        conversion_type: Conversion type in format 'source2target' (e.g., 'md2pdf')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not conversion_type or not isinstance(conversion_type, str):
        return False, "Conversion type must be a non-empty string"

    # Parse conversion type (e.g., 'md2pdf' -> 'md', 'pdf')
    pattern = r"^([a-zA-Z]+)2([a-zA-Z]+)$"
    match = re.match(pattern, conversion_type.lower())

    if not match:
        return (
            False,
            f"Invalid conversion type format: '{conversion_type}'. Expected format: 'source2target'",
        )

    source_format, target_format = match.groups()

    # Validate source format
    if source_format not in SUPPORTED_INPUT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_INPUT_FORMATS))
        return (
            False,
            f"Unsupported source format '{source_format}'. Supported: {supported}",
        )

    # Validate target format
    if target_format not in SUPPORTED_OUTPUT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_OUTPUT_FORMATS))
        return (
            False,
            f"Unsupported target format '{target_format}'. Supported: {supported}",
        )

    return True, None


def validate_batch_inputs(input_paths: list[str]) -> tuple[bool, str | None]:
    """Validate a list of input files for batch processing.

    Args:
        input_paths: List of file paths to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not input_paths:
        return False, "Input paths list cannot be empty"

    if not isinstance(input_paths, list):
        return False, "Input paths must be a list"

    if len(input_paths) > 100:
        return (
            False,
            f"Too many files for batch processing: {len(input_paths)} (max: 100)",
        )

    for i, path in enumerate(input_paths):
        is_valid, error = validate_file_path(path)
        if not is_valid:
            return False, f"File {i + 1}: {error}"

    return True, None


def get_file_extension(file_path: str) -> str | None:
    """Get the file extension from a file path.

    Args:
        file_path: Path to the file

    Returns:
        File extension without dot, or None if no extension
    """
    try:
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        return extension if extension else None
    except Exception:
        return None


def is_supported_input_format(file_path: str) -> bool:
    """Check if a file format is supported for input.

    Args:
        file_path: Path to the file

    Returns:
        True if format is supported, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in SUPPORTED_INPUT_FORMATS if extension else False


def is_supported_output_format(file_path: str) -> bool:
    """Check if a file format is supported for output.

    Args:
        file_path: Path to the file

    Returns:
        True if format is supported, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in SUPPORTED_OUTPUT_FORMATS if extension else False
