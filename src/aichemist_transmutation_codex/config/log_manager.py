import logging
import logging.config
import os
import uuid
from datetime import datetime
from pathlib import Path

import yaml


class LogManager:
    """
    Manages logging configuration and provides logging utilities.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Creates a new LogManager instance if one doesn't exist (Singleton pattern).

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            LogManager: The singleton instance of the LogManager.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, logs_dir: Path | None = None, config_dir: Path | None = None):
        """Initializes the LogManager, setting up paths and logging configurations.

        This constructor is called only once due to the singleton pattern.
        It defines log and configuration directories, generates a session ID,
        creates log directories, and applies logging configurations from a YAML file.

        Args:
            logs_dir (Path | None): The base directory where log files will be stored.
                If None, defaults to a directory named "logs" in the current working
                directory. Defaults to None.
            config_dir (Path | None): The directory where the `logging_config.yaml`
                file is located. If None, defaults to a directory named "config"
                in the current working directory. Defaults to None.
        """
        if self._initialized:
            # If already initialized, potentially update paths if provided?
            # For simplicity now, we assume paths are set on first init.
            # Re-initialization logic might be needed if paths can change runtime.
            return

        # Use provided paths or default
        self.logs_dir = logs_dir if logs_dir is not None else Path("logs")
        self.config_dir = config_dir if config_dir is not None else Path("config")
        self.session_id = self.generate_session_id()

        # Ensure log directories exist
        self._create_log_directories()

        # Load and apply logging configuration
        self._configure_logging()

        # Get root logger
        self.root_logger = logging.getLogger()

        # Mark as initialized
        self._initialized = True

    def _create_log_directories(self):
        """Creates the necessary directory structure for log files.

        Ensures that the main log directories (e.g., `logs/python`,
        `logs/electron`) and subdirectories for specific components
        (e.g., `logs/python/converters`) exist.
        """
        # Main log directories
        (self.logs_dir / "python").mkdir(parents=True, exist_ok=True)
        (self.logs_dir / "python" / "converters").mkdir(exist_ok=True)
        (self.logs_dir / "python" / "batch_processor").mkdir(exist_ok=True)
        (self.logs_dir / "python" / "electron_bridge").mkdir(exist_ok=True)

        # Converter-specific directories
        (self.logs_dir / "python" / "converters" / "pdf2md").mkdir(exist_ok=True)
        (self.logs_dir / "python" / "converters" / "md2pdf").mkdir(exist_ok=True)
        (self.logs_dir / "python" / "converters" / "html2pdf").mkdir(exist_ok=True)

        # Electron directories
        (self.logs_dir / "electron" / "main").mkdir(parents=True, exist_ok=True)
        (self.logs_dir / "electron" / "renderer").mkdir(exist_ok=True)

    def _configure_logging(self):
        """Loads and applies logging configuration from `logging_config.yaml`.

        This method reads the YAML configuration file, updates log file paths
        to be absolute and include the session ID where appropriate, and then
        applies the configuration using `logging.config.dictConfig`.
        If the configuration file is not found or is invalid, it falls back
        to basic logging.
        """
        config = None  # Initialize config to None
        config_path = self.config_dir / "logging_config.yaml"
        try:
            if not config_path.exists():
                self._setup_basic_logging()
                logging.warning(f"Logging config file not found: {config_path}")
                return

            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):  # Check if YAML load was successful
                raise ValueError(f"Invalid YAML content in {config_path}")

            # Update filenames with session ID and absolute paths
            if "handlers" in config:
                handlers_to_process = list(
                    config["handlers"].items()
                )  # Iterate over a copy
                for handler_name, handler_config in handlers_to_process:
                    if (
                        isinstance(handler_config, dict)
                        and "filename" in handler_config
                    ):
                        try:
                            original_relative_path = Path(handler_config["filename"])
                            absolute_parent_dir = (
                                self.logs_dir / original_relative_path.parent
                            )

                            # Ensure parent directory exists (important for logging setup)
                            absolute_parent_dir.mkdir(parents=True, exist_ok=True)

                            # Add session ID to the filename for specific session logs
                            if handler_name.endswith(
                                "_session_file"
                            ) and not original_relative_path.name.startswith("_"):
                                session_filename = f"{original_relative_path.stem}_{self.session_id}{original_relative_path.suffix}"
                                absolute_path = absolute_parent_dir / session_filename
                            else:
                                # Use original filename but ensure path is absolute
                                absolute_path = (
                                    absolute_parent_dir / original_relative_path.name
                                )

                            handler_config["filename"] = str(absolute_path)
                            # print(f"Updated handler '{handler_name}' filename to: {absolute_path}") # Debugging
                        except Exception as handler_ex:
                            # Log specific handler error and potentially remove/disable it
                            logging.error(
                                f"Error processing handler '{handler_name}': {handler_ex}. Skipping handler."
                            )
                            # Optionally remove the problematic handler: del config['handlers'][handler_name]
                            # For now, we log and continue, but dictConfig might still fail later if structure is bad

            # Apply configuration if loaded and processed
            if config:
                logging.config.dictConfig(config)
                logging.info(
                    f"Logging configured from {config_path} with session ID: {self.session_id}"
                )
            else:
                # This case should ideally be caught earlier (file not found, invalid YAML)
                self._setup_basic_logging()
                logging.warning(
                    "Logging config was not loaded or processed correctly. Using basic config."
                )

        except (
            FileNotFoundError
        ):  # Should be caught by exists() check, but just in case
            self._setup_basic_logging()
            logging.warning(f"Logging config file not found during open: {config_path}")
        except (
            yaml.YAMLError,
            ValueError,
        ) as e:  # Catch YAML parsing errors or value errors
            self._setup_basic_logging()
            logging.error(f"Error loading or parsing logging config {config_path}: {e}")
        except Exception as e:
            # Catch potential errors during dictConfig application or other issues
            self._setup_basic_logging()
            logging.error(
                f"Unexpected error configuring logging from {config_path}: {e}"
            )

    def _setup_basic_logging(self):
        """Sets up a basic logging configuration as a fallback.

        This is used if the `logging_config.yaml` file cannot be found or parsed.
        It configures a simple console logger with INFO level.
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with a specific name.

        Args:
            name: The name of the logger (will be prefixed with 'mdtopdf.')

        Returns:
            A configured logger instance
        """
        # Add mdtopdf prefix if not already present
        if not name.startswith("mdtopdf"):
            name = f"mdtopdf.{name}"

        return logging.getLogger(name)

    def generate_session_id(self) -> str:
        """
        Create a unique session ID.

        Returns:
            A string containing timestamp and unique identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def get_converter_logger(self, converter_type: str) -> logging.Logger:
        """
        Get a logger specifically for a converter.

        Args:
            converter_type: Type of converter (e.g., 'pdf2md', 'md2pdf')

        Returns:
            A configured logger for the specified converter
        """
        return self.get_logger(f"converters.{converter_type}")

    def get_batch_logger(self) -> logging.Logger:
        """Gets a logger specifically for batch processing operations.

        Returns:
            logging.Logger: A configured logger instance named "mdtopdf.batch_processor".
        """
        return self.get_logger("batch_processor")

    def get_bridge_logger(self) -> logging.Logger:
        """Gets a logger specifically for the Electron bridge operations.

        Returns:
            logging.Logger: A configured logger instance named "mdtopdf.electron_bridge".
        """
        return self.get_logger("electron_bridge")

    def add_file_handler(
        self,
        logger: logging.Logger,
        filepath: str,
        level: int = logging.DEBUG,
        formatter: logging.Formatter | None = None,
    ) -> None:
        """
        Add a file handler to a logger.

        Args:
            logger: The logger to add the handler to
            filepath: Absolute path where logs will be written
            level: Logging level for this handler
            formatter: Custom formatter (or None to use default)
        """
        try:
            # Ensure directory exists using pathlib for robustness
            log_path = Path(filepath)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Create handler
            handler = logging.FileHandler(filepath)
            handler.setLevel(level)

            # Set formatter
            if formatter is None:
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            handler.setFormatter(formatter)

            # Add to logger
            logger.addHandler(handler)
            # print(f"Added file handler for {filepath} to logger {logger.name}") # Debug
        except Exception as e:
            logging.error(
                f"Failed to add file handler for {filepath} to logger {logger.name}: {e}"
            )

    def create_session_file_path(self, component: str, filename: str) -> str:
        """
        Create an absolute log file path with session ID.

        Args:
            component: Component sub-path (e.g., 'converters/pdf2md')
            filename: Base filename

        Returns:
            Full absolute path to the log file as a string
        """
        # Construct the absolute base path using the instance's logs_dir
        base_path = self.logs_dir / "python" / component
        base_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        # Split filename into base and extension
        name, ext = os.path.splitext(filename)
        session_filename = f"{name}_{self.session_id}{ext}"

        # Return the absolute path as a string
        return str(base_path / session_filename)
