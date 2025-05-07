import logging
import logging as original_logging  # Keep for spec
import logging.config  # Import for patching target
import os
import time
from pathlib import Path
from unittest import mock

import pytest
import yaml

from mdtopdf.config.log_manager import LogManager


# Define mock dirs at a higher scope if needed by multiple fixtures
@pytest.fixture(scope="function")
def mock_dirs(tmp_path):
    """Provides mock logs and config directories for a test function."""
    logs_dir = tmp_path / f"logs_{time.time_ns()}"
    config_dir = tmp_path / f"config_{time.time_ns()}"
    config_dir.mkdir()  # Ensure config dir exists for placing test configs
    # logs_dir is created by LogManager if needed
    # print(f"Mock Dirs Fixture: logs={logs_dir}, config={config_dir}") # Debug
    return logs_dir, config_dir


@pytest.fixture(scope="function")
def reset_log_manager_singleton(mock_dirs):
    """
    Fixture to reset the LogManager singleton state and mock logging.config.dictConfig.
    Does NOT automatically instantiate LogManager.
    """
    # print("Resetting LogManager singleton (fixture setup)...") # Debug
    LogManager._instance = None
    # Get paths needed for potential cleanup or context, though not strictly needed now
    # logs_dir, config_dir = mock_dirs

    # Patch dictConfig for tests that expect configuration loading
    with mock.patch("logging.config.dictConfig") as mock_dict_config:
        yield mock_dict_config  # Provide the mock to the test

    # print("Cleaning up LogManager singleton (fixture teardown)...") # Debug
    # Reset singleton after test
    LogManager._instance = None


@pytest.fixture
def create_logging_config(mock_dirs):
    """Create a dummy logging_config.yaml in the mock config directory."""
    _, config_dir = mock_dirs
    log_config_path = config_dir / "logging_config.yaml"
    # Define relative paths as they would appear in a real config file
    # LogManager's _configure_logging will make them absolute using its logs_dir
    config_data = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
            "app_file": {  # General app log - SHOULD NOT get session ID based on name
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "level": "DEBUG",
                # Use relative paths here, LogManager makes them absolute
                "filename": "python/app.log",
                "mode": "a",
            },
            "converter_session_file": {  # Session specific log - SHOULD get session ID
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "level": "DEBUG",
                "filename": "python/converters/converter.log",  # Base name
                "mode": "a",
            },
            "batch_session_file": {  # Session specific log - SHOULD get session ID
                "class": "logging.FileHandler",
                "formatter": "standard",
                "level": "INFO",
                "filename": "python/batch_processor/batch.log",  # Base name
                "mode": "a",
            },
        },
        "loggers": {
            "mdtopdf": {  # Root logger for the app
                "handlers": ["console", "app_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "mdtopdf.converters": {
                "handlers": ["converter_session_file"],
                "level": "DEBUG",
                "propagate": True,
            },
            "mdtopdf.batch_processor": {
                "handlers": ["batch_session_file"],
                "level": "INFO",
                "propagate": True,
            },
            # Add other loggers if needed by tests
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }
    with open(log_config_path, "w") as f:
        yaml.dump(config_data, f)
    # print(f"Created logging config at: {log_config_path}") # Debug
    return log_config_path, config_data


# --- Test Cases ---


def test_log_manager_singleton(mock_dirs):
    """Test that LogManager implements the singleton pattern."""
    logs_dir, config_dir = mock_dirs
    # Explicitly reset before test (though fixture might do it too if requested)
    LogManager._instance = None

    # Instantiate instance 1
    instance1 = LogManager(logs_dir=logs_dir, config_dir=config_dir)
    # Instantiate instance 2
    instance2 = LogManager(logs_dir=logs_dir, config_dir=config_dir)

    assert instance1 is instance2
    assert instance1._initialized is True
    assert instance2._initialized is True

    assert instance1.logs_dir == logs_dir
    assert instance1.config_dir == config_dir
    assert "pytest-of-" in str(instance1.logs_dir)


def test_create_log_directories(mock_dirs):
    """Test that necessary log directories are created."""
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None  # Ensure clean state
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE

    assert lm.logs_dir == logs_dir

    expected_dirs = [
        logs_dir / "python",
        logs_dir / "python" / "converters",
        logs_dir / "python" / "batch_processor",
        logs_dir / "python" / "electron_bridge",
        logs_dir / "python" / "converters" / "pdf2md",
        logs_dir / "python" / "converters" / "md2pdf",
        logs_dir / "python" / "converters" / "html2pdf",
        logs_dir / "electron",
        logs_dir / "electron" / "main",
        logs_dir / "electron" / "renderer",
    ]

    missing_dirs = []
    for expected_path in expected_dirs:
        if not expected_path.exists():
            missing_dirs.append(str(expected_path))

    assert not missing_dirs, f"LogManager failed to create directories: {missing_dirs}"


def test_configure_logging_from_file(
    create_logging_config,
    reset_log_manager_singleton,
    mock_dirs,  # Order matters
):
    """Test loading and applying logging config from YAML with session IDs."""
    # Fixture setup order: mock_dirs -> create_logging_config -> reset_log_manager_singleton (setup)
    mock_dictConfig = reset_log_manager_singleton  # Get the mock from the fixture
    log_config_path, original_config_data = create_logging_config  # Get path and data
    logs_dir, config_dir = mock_dirs  # Get paths

    # Instantiate LogManager HERE, *after* the config file exists
    # reset_log_manager_singleton already reset the singleton state
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)

    # Check that dictConfig was called now because the file exists during init
    try:
        mock_dictConfig.assert_called_once()
    except AssertionError as e:
        pytest.fail(
            f"logging.config.dictConfig was not called. File existed, but init failed? {e}"
        )

    applied_config = mock_dictConfig.call_args[0][0]

    # --- Assertions on the applied_config (remain the same) ---
    assert applied_config["version"] == original_config_data["version"]
    assert "mdtopdf.converters" in applied_config["loggers"]
    assert "handlers" in applied_config
    handlers = applied_config["handlers"]
    assert "converter_session_file" in handlers
    converter_handler = handlers["converter_session_file"]
    assert "filename" in converter_handler
    converter_path = Path(converter_handler["filename"])
    assert converter_path.parent == logs_dir / "python" / "converters"
    assert converter_path.name.startswith("converter_")
    assert converter_path.name.endswith(f"_{lm.session_id}.log")
    assert converter_path.is_absolute()
    assert "batch_session_file" in handlers
    batch_handler = handlers["batch_session_file"]
    assert "filename" in batch_handler
    batch_path = Path(batch_handler["filename"])
    assert batch_path.parent == logs_dir / "python" / "batch_processor"
    assert batch_path.name.startswith("batch_")
    assert batch_path.name.endswith(f"_{lm.session_id}.log")
    assert batch_path.is_absolute()
    assert "app_file" in handlers
    app_handler = handlers["app_file"]
    assert "filename" in app_handler
    app_path = Path(app_handler["filename"])
    assert app_path.parent == logs_dir / "python"
    assert app_path.name == "app.log"
    assert app_path.is_absolute()


@mock.patch("logging.basicConfig")
def test_configure_logging_file_not_found(mock_basicConfig, mock_dirs):
    """Test fallback to basicConfig when config file is missing."""
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None  # Ensure clean state
    with mock.patch("logging.warning") as mock_log_warning:
        lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE

        mock_basicConfig.assert_called_once()
        mock_log_warning.assert_called_once()
        assert "Logging config file not found" in mock_log_warning.call_args[0][0]


@mock.patch("logging.basicConfig")
@mock.patch("logging.config.dictConfig")
def test_configure_logging_invalid_yaml(mock_dictConfig, mock_basicConfig, mock_dirs):
    """Test fallback to basicConfig when config file is invalid YAML."""
    logs_dir, config_dir = mock_dirs
    invalid_config_path = config_dir / "logging_config.yaml"
    invalid_config_path.write_text("version: 1\nhandlers: { console:")  # Invalid YAML

    LogManager._instance = None  # Ensure clean state
    with mock.patch("logging.error") as mock_log_error:
        lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE

        mock_basicConfig.assert_called_once()
        mock_dictConfig.assert_not_called()
        mock_log_error.assert_called_once()
        assert (
            "Error loading or parsing logging config" in mock_log_error.call_args[0][0]
        )


def test_get_logger(mock_dirs):
    """Test getting a logger instance with correct naming."""
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None  # Ensure clean state
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE
    logger1 = lm.get_logger("my_component")
    logger2 = lm.get_logger("mdtopdf.another.component")

    assert logger1.name == "mdtopdf.my_component"
    assert logger2.name == "mdtopdf.another.component"
    assert isinstance(logger1, logging.Logger)


def test_get_converter_logger(mock_dirs):
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)
    logger = lm.get_converter_logger("pdf2md")
    assert logger.name == "mdtopdf.converters.pdf2md"


def test_get_batch_logger(mock_dirs):
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)
    logger = lm.get_batch_logger()
    assert logger.name == "mdtopdf.batch_processor"


def test_get_bridge_logger(mock_dirs):
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)
    logger = lm.get_bridge_logger()
    assert logger.name == "mdtopdf.electron_bridge"


@mock.patch("logging.FileHandler")
def test_add_file_handler(mock_FileHandler_class, mock_dirs):
    """Test adding a file handler to a logger."""
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None  # Ensure clean state
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE
    test_logger = lm.get_logger("test_handler")
    log_filepath_obj = lm.logs_dir / "custom" / "test_log.log"
    log_filepath_str = str(log_filepath_obj)

    mock_handler_instance = mock_FileHandler_class.return_value
    lm.add_file_handler(test_logger, log_filepath_str, level=logging.WARNING)

    assert log_filepath_obj.parent.exists()
    mock_FileHandler_class.assert_called_once_with(log_filepath_str)
    mock_handler_instance.setLevel.assert_called_once_with(logging.WARNING)
    mock_handler_instance.setFormatter.assert_called_once()
    assert mock_handler_instance in test_logger.handlers


def test_create_session_file_path(mock_dirs):
    """Test creating an absolute log file path with session ID."""
    logs_dir, config_dir = mock_dirs
    LogManager._instance = None  # Ensure clean state
    lm = LogManager(logs_dir=logs_dir, config_dir=config_dir)  # Instantiate HERE

    session_id = lm.session_id
    component = "converters/pdf2md"
    filename = "conversion.log"

    expected_path = logs_dir / "python" / component / f"conversion_{session_id}.log"
    expected_dir = logs_dir / "python" / component

    result_path_str = lm.create_session_file_path(component, filename)
    result_path = Path(result_path_str)

    assert expected_dir.exists(), f"Directory {expected_dir} was not created"
    assert expected_dir.is_dir()
    assert result_path == expected_path
    assert result_path.is_absolute()
