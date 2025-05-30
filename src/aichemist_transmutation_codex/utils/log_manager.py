import json
import logging
import logging.config
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionIdFilter(logging.Filter):
    """A logging filter to add a session ID to log records."""

    def __init__(self, session_id: str, name: str = "") -> None:
        """Initializes the SessionIdFilter.

        Args:
            session_id (str): The session ID to add to log records.
            name (str): The name of the filter. Defaults to "".
        """
        super().__init__(name)
        self.session_id = session_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Adds the session ID to the log record.

        Args:
            record (logging.LogRecord): The log record to process.

        Returns:
            bool: Always True to indicate the record should be processed.
        """
        record.session_id = self.session_id
        return True


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON strings, prefixed for Electron bridge."""

    def __init__(
        self, session_id: str, fmt: str | None = None, datefmt: str | None = None
    ) -> None:
        """Initializes the JsonFormatter.

        Args:
            session_id (str): The active session ID.
            fmt (Optional[str]): The log record format. Not directly used for JSON
                structure but kept for compatibility. Defaults to None.
            datefmt (Optional[str]): The date format string. Defaults to None.
        """
        super().__init__(fmt, datefmt)
        self.session_id = session_id  # Store session_id if needed directly, though filter is preferred

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record as a JSON string prefixed with 'LOG_MESSAGE:'.

        Includes standard log fields as well as the session_id.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The JSON formatted log message with prefix.
        """
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "session_id": getattr(
                record, "session_id", self.session_id
            ),  # Fallback if filter not used
            "level": record.levelname,
            "name": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.getMessage(),
        }
        # Handle exc_info if present
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)

        return f"LOG_MESSAGE:{json.dumps(log_entry)}"


class LogManager:
    """Manages logging configuration and provides logging utilities.

    This class implements the singleton pattern and configures logging
    programmatically for both file output and structured JSON output to stdout
    for integration with an Electron GUI.
    """

    _instance = None
    _initialized = False  # Class attribute for initialization flag

    def __new__(cls, *args: Any, **kwargs: Any) -> "LogManager":
        """Creates a new LogManager instance if one doesn't exist (Singleton pattern).

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            LogManager: The singleton instance of the LogManager.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # _initialized flag is instance-specific, set in __init__
        return cls._instance

    def __init__(self, logs_dir: Path | None = None) -> None:
        """Initializes the LogManager. Called only once for the singleton.

        Sets up paths, generates a session ID, creates log directories, and
        applies programmatic logging configurations.

        Args:
            logs_dir (Optional[Path]): The base directory where log files will be
                stored. If None, defaults to "logs" in the current working
                directory (`Path.cwd() / "logs"`).
        """
        if self._initialized:
            return

        self.logs_dir = logs_dir if logs_dir is not None else Path.cwd() / "logs"
        self.session_id = self.generate_session_id()

        self._create_log_directories()
        self._configure_programmatic_logging()

        self.root_logger = logging.getLogger()  # Get the root logger
        LogManager._initialized = True  # Use class attribute for singleton init state

    def _create_log_directories(self) -> None:
        """Creates the necessary directory structure for log files.

        Ensures that the main log directory `logs/python` exists.
        Other component-specific directories can be created by `add_file_handler`
        if needed.
        """
        python_logs_dir = self.logs_dir / "python"
        python_logs_dir.mkdir(parents=True, exist_ok=True)
        # Example: Create other specific directories if always needed
        # (python_logs_dir / "converters").mkdir(exist_ok=True)
        # (python_logs_dir / "batch_processor").mkdir(exist_ok=True)

    def _configure_programmatic_logging(self) -> None:
        """Configures logging programmatically.

        Sets up a root logger with two handlers:
        1. A StreamHandler outputting JSON to stdout for the Electron bridge.
        2. A FileHandler for general application logging to a session-specific file.
        """
        root_logger = logging.getLogger()  # Configure the root logger
        root_logger.setLevel(logging.DEBUG)  # Set root logger level

        # Prevent multiple handlers if re-initializing (though singleton should prevent)
        if root_logger.hasHandlers():
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

        # Add session ID filter to the root logger
        session_filter = SessionIdFilter(self.session_id)
        root_logger.addFilter(session_filter)

        # 1. JSON Formatter and StreamHandler for stdout (Electron bridge)
        json_formatter = JsonFormatter(
            session_id=self.session_id, datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
        )
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(json_formatter)
        stdout_handler.setLevel(logging.INFO)  # Example: INFO level for GUI
        root_logger.addHandler(stdout_handler)

        # 2. Standard Formatter and FileHandler for persistent logs
        log_file_path = self.logs_dir / "python" / f"app_session_{self.session_id}.log"
        file_formatter = logging.Formatter(
            "%(asctime)s - %(session_id)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Example: DEBUG level for file logs
        root_logger.addHandler(file_handler)

        logging.info(
            f"Logging configured programmatically. Session ID: {self.session_id}. "
            f"File log: {log_file_path}"
        )

    def get_logger(self, name: str) -> logging.Logger:
        """Gets a logger instance with the specified name, prefixed.

        The logger name will be prefixed with 'aichemist_codex.' to ensure
        all application logs are under a common namespace.

        Args:
            name (str): The specific name for the logger (e.g., `__name__` from
                the calling module).

        Returns:
            logging.Logger: A configured logger instance.
        """
        logger_name = f"aichemist_codex.{name}"
        return logging.getLogger(logger_name)

    def generate_session_id(self) -> str:
        """Creates a unique session ID.

        Combines a timestamp with a short UUID for uniqueness.

        Returns:
            str: A string representing the unique session ID (e.g.,
                 "20231027_153000_a1b2c3d4").
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def get_converter_logger(self, converter_type: str) -> logging.Logger:
        """Gets a logger specifically for a converter.

        Args:
            converter_type (str): Type of converter (e.g., 'pdf2md', 'md2pdf').

        Returns:
            logging.Logger: A configured logger for the specified converter,
                            e.g., `aichemist_codex.converters.pdf2md`.
        """
        return self.get_logger(f"converters.{converter_type}")

    def get_batch_logger(self) -> logging.Logger:
        """Gets a logger specifically for batch processing operations.

        Returns:
            logging.Logger: A configured logger instance named
                            `aichemist_codex.batch_processor`.
        """
        return self.get_logger("batch_processor")

    def get_bridge_logger(self) -> logging.Logger:
        """Gets a logger specifically for the Electron bridge operations.

        Returns:
            logging.Logger: A configured logger instance named
                            `aichemist_codex.electron_bridge`.
        """
        return self.get_logger("electron_bridge")

    def add_file_handler(
        self,
        logger: logging.Logger,
        filepath: str | Path,
        level: int = logging.DEBUG,
        formatter: logging.Formatter | None = None,
    ) -> None:
        """Adds a file handler to a given logger instance.

        Ensures the directory for the log file exists.

        Args:
            logger (logging.Logger): The logger instance to add the handler to.
            filepath (str | Path): Absolute or relative path for the log file.
                If relative, it's based on the current working directory.
                It's recommended to use paths generated via
                `create_session_file_path` or absolute paths.
            level (int): Logging level for this handler. Defaults to `logging.DEBUG`.
            formatter (Optional[logging.Formatter]): Custom formatter. If None,
                a default formatter including session_id is used.
        """
        try:
            log_path = Path(filepath)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            handler = logging.FileHandler(log_path, encoding="utf-8")
            handler.setLevel(level)

            if formatter is None:
                formatter = logging.Formatter(
                    "%(asctime)s - %(session_id)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            handler.setFormatter(formatter)
            # Add session filter if this handler is for a logger not descending from root
            # or if finer control per handler is needed.
            # For now, relying on root logger's filter.
            # session_filter = SessionIdFilter(self.session_id)
            # handler.addFilter(session_filter)

            logger.addHandler(handler)
            # Use a general logger for LogManager's own messages if needed,
            # or print for setup diagnostics.
            # print(f"Added file handler for {log_path} to logger {logger.name}")
        except Exception as e:
            # Log this error using a basic configuration or print,
            # as the main logging might not be fully set up or could be the source of error.
            print(
                f"CRITICAL: Failed to add file handler for {filepath} "
                f"to logger {logger.name}: {e}"
            )

    def create_session_file_path(
        self, component_path: str, filename_base: str, extension: str = "log"
    ) -> Path:
        """Creates an absolute log file path with session ID for a component.

        The path will be structured under `logs_dir/python/component_path/`.

        Args:
            component_path (str): The sub-path for the component relative to
                `logs_dir/python/` (e.g., "converters/pdf2md", "utils").
            filename_base (str): The base name for the log file (e.g., "conversion_details").
            extension (str): The file extension without a leading dot. Defaults to "log".

        Returns:
            Path: The absolute `Path` object for the log file.
        """
        target_dir = self.logs_dir / "python" / component_path
        target_dir.mkdir(parents=True, exist_ok=True)

        session_filename = f"{filename_base}_{self.session_id}.{extension}"
        return target_dir / session_filename


# Example of how LogManager might be used (typically not in this file):
# if __name__ == "__main__":
#     # Initialize LogManager (usually done at application startup)
#     # The first call to LogManager() or LogManager(logs_dir=Path("my_app_logs"))
#     # will initialize the singleton.
#     log_manager = LogManager()

#     # Get a logger for the current module or a specific component
#     module_logger = log_manager.get_logger(__name__)
#     module_logger.info("LogManager example: Info message from module.")
#     module_logger.debug("LogManager example: Debug message, check file log.")

#     converter_logger = log_manager.get_converter_logger("test_converter")
#     converter_logger.warning("LogManager example: Warning from test_converter.")

#     try:
#         x = 1 / 0
#     except ZeroDivisionError:
#         module_logger.error("LogManager example: An error occurred!", exc_info=True)

#     # Example of adding a specific handler
#     # custom_log_path = log_manager.create_session_file_path("custom_component", "special_ops")
#     # special_logger = log_manager.get_logger("custom_component.special_ops")
#     # log_manager.add_file_handler(special_logger, custom_log_path, level=logging.INFO)
#     # special_logger.info("This goes to the special_ops session log and stdout.")
#     # module_logger.info("This info still goes to general logs and stdout.")

#     print(f"Logs are being managed. Session ID: {log_manager.session_id}")
#     print(f"Main session log likely at: {log_manager.logs_dir / 'python' / f'app_session_{log_manager.session_id}.log'}")
