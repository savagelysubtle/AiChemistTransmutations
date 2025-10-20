"""Base classes and protocols for document conversion plugins.

This module defines the standard interface that all conversion plugins must follow,
providing a consistent API and shared functionality.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from transmutation_codex.core import (
    ConfigManager,
    complete_operation,
    get_log_manager,
    raise_conversion_error,
    raise_validation_error,
    start_operation,
)
from transmutation_codex.utils.validators import (
    validate_file_path,
    validate_output_path,
)


@runtime_checkable
class Converter(Protocol):
    """Protocol defining the standard converter interface.

    All converter implementations should follow this protocol to ensure
    consistency across the codebase.
    """

    def convert(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        **options: Any,
    ) -> Path:
        """Convert input file to output format.

        Args:
            input_path: Path to the input file
            output_path: Path for the output file (auto-generated if None)
            **options: Format-specific conversion options

        Returns:
            Path: Absolute path to the converted output file

        Raises:
            ConversionError: If conversion fails
            ValidationError: If input validation fails
        """
        ...


class BaseConverter:
    """Base class providing common functionality for converters.

    This class handles logging, configuration, progress tracking, and validation,
    allowing converter implementations to focus on conversion logic.

    Attributes:
        source_format: Source file format (e.g., 'pdf', 'md')
        target_format: Target file format (e.g., 'md', 'pdf')
        converter_name: Unique name for this converter
    """

    def __init__(
        self,
        source_format: str,
        target_format: str,
        converter_name: str | None = None,
    ):
        """Initialize the base converter.

        Args:
            source_format: Source file format
            target_format: Target file format
            converter_name: Custom name (auto-generated if None)
        """
        self.source_format = source_format.lower()
        self.target_format = target_format.lower()
        self.converter_name = converter_name or f"{source_format}2{target_format}"

        # Initialize logger and config
        self._logger = get_log_manager().get_converter_logger(self.converter_name)
        self._config = ConfigManager()
        self._settings = self._config.get_converter_config(self.converter_name)

    def get_logger(self):
        """Get the logger for this converter."""
        return self._logger

    def get_settings(self) -> dict[str, Any]:
        """Get configuration settings for this converter."""
        return self._settings.copy()

    def validate_input(self, input_path: Path) -> None:
        """Validate input file path and format.

        Args:
            input_path: Path to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate file exists and is readable
        is_valid, error = validate_file_path(str(input_path))
        if not is_valid:
            raise_validation_error(error or "Invalid input file")

        # Validate file format matches expected source format
        if input_path.suffix.lower().lstrip(".") not in [
            self.source_format,
            f"{self.source_format}x",
        ]:
            expected = self.source_format
            actual = input_path.suffix.lower().lstrip(".")
            raise_validation_error(
                f"Input file format mismatch. Expected '.{expected}', got '.{actual}'"
            )

    def validate_output(self, output_path: Path) -> None:
        """Validate output file path.

        Args:
            output_path: Path to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate parent directory is writable
        is_valid, error = validate_output_path(str(output_path))
        if not is_valid:
            raise_validation_error(error or "Invalid output path")

    def prepare_output_path(
        self,
        input_path: Path,
        output_path: Path | None = None,
    ) -> Path:
        """Prepare and validate output path.

        Args:
            input_path: Input file path
            output_path: Desired output path (None for auto-generation)

        Returns:
            Resolved output path
        """
        if output_path is None:
            # Auto-generate output path next to input with target extension
            output_path = input_path.with_suffix(f".{self.target_format}")
        else:
            output_path = Path(output_path).resolve()

            # If output_path is a directory, create filename
            if output_path.is_dir():
                filename = input_path.stem + f".{self.target_format}"
                output_path = output_path / filename

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def convert(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        **options: Any,
    ) -> Path:
        """Convert input file to output format with progress tracking.

        This method handles validation, progress tracking, and error handling,
        delegating the actual conversion to _convert_impl().

        Args:
            input_path: Path to input file
            output_path: Path for output file (auto-generated if None)
            **options: Converter-specific options

        Returns:
            Path to converted output file

        Raises:
            ConversionError: If conversion fails
            ValidationError: If validation fails
        """
        # Normalize paths
        input_path = Path(input_path).resolve()

        # Validate input
        self.validate_input(input_path)

        # Prepare output path
        output_path_obj = self.prepare_output_path(input_path, output_path)

        # Validate output
        self.validate_output(output_path_obj)

        # Merge options with settings
        merged_options = {**self._settings, **options}

        # Start operation tracking
        operation = start_operation(
            self.converter_name,
            f"Converting {input_path.name} to {self.target_format.upper()}",
        )

        try:
            self._logger.info(
                f"Starting {self.converter_name} conversion: {input_path.name} -> {output_path_obj.name}"
            )

            # Delegate to implementation
            result = self._convert_impl(
                input_path, output_path_obj, operation, **merged_options
            )

            # Complete operation
            complete_operation(operation, {"output_path": str(result)})

            self._logger.info(f"Conversion successful: {result}")
            return result

        except Exception as e:
            self._logger.exception(f"Conversion failed: {e}")
            raise_conversion_error(
                f"{self.converter_name} conversion failed: {e}",
                input_path=str(input_path),
                output_path=str(output_path_obj),
            )

    @abstractmethod
    def _convert_impl(
        self,
        input_path: Path,
        output_path: Path,
        operation_id: str,
        **options: Any,
    ) -> Path:
        """Implement the actual conversion logic.

        Subclasses must implement this method to perform the conversion.
        Use update_progress(operation_id, percent, message) to report progress.

        Args:
            input_path: Validated input file path
            output_path: Prepared output file path
            operation_id: Operation ID for progress tracking
            **options: Merged conversion options

        Returns:
            Path to the converted output file

        Raises:
            ConversionError: If conversion fails
        """
        raise NotImplementedError("Subclasses must implement _convert_impl()")


def function_converter(
    source_format: str,
    target_format: str,
    converter_name: str | None = None,
):
    """Decorator to wrap a function-based converter with BaseConverter functionality.

    This allows function-based converters to benefit from validation, progress tracking,
    and error handling without requiring class-based implementation.

    Args:
        source_format: Source file format
        target_format: Target file format
        converter_name: Custom converter name (optional)

    Example:
        @function_converter('md', 'pdf')
        def convert_md_to_pdf(
            input_path: Path,
            output_path: Path,
            operation_id: str,
            **options
        ) -> Path:
            # Implementation here
            update_progress(operation_id, 50, "Processing")
            return output_path
    """

    def decorator(func):
        class FunctionConverter(BaseConverter):
            def __init__(self):
                super().__init__(source_format, target_format, converter_name)
                self._wrapped_func = func

            def _convert_impl(
                self,
                input_path: Path,
                output_path: Path,
                operation_id: str,
                **options: Any,
            ) -> Path:
                return self._wrapped_func(
                    input_path, output_path, operation_id, **options
                )

        # Create instance and return its convert method
        instance = FunctionConverter()
        return instance.convert

    return decorator
