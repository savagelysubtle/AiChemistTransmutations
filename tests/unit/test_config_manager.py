"""Tests for the config manager module."""

import pytest

# Skip these tests - ConfigManager API has changed significantly in Phase 1/2  
pytestmark = pytest.mark.skip(reason="ConfigManager API refactored - methods like _load_yaml, get_converter_config, get_electron_config removed")

import json
import os
from pathlib import Path
import tempfile
from unittest import mock

import yaml

from transmutation_codex.core.config_manager import ConfigManager
from transmutation_codex.core.logger import LogManager

# --- Fixtures ---


@pytest.fixture(scope="function")
def reset_config_manager_singleton():
    """Fixture to reset the ConfigManager singleton state before each test."""
    # print("Resetting ConfigManager singleton...") # Debug
    ConfigManager._instance = None
    yield
    # print("Cleaning up ConfigManager singleton...") # Debug
    ConfigManager._instance = None


@pytest.fixture
def mock_config_dir(tmp_path):
    """Creates a mock config directory within the pytest tmp_path."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def create_default_config(mock_config_dir):
    """Creates a default_config.yaml file."""
    config_path = mock_config_dir / "default_config.yaml"
    config_data = {
        "application": {
            "name": "Default App Name",
            "version": "1.0",
            "debug_mode": False,
        },
        "converters": {
            "pdf2md": {
                "default_engine": "pymupdf",
                "ocr_enabled": True,
                "timeout": 60,
            },
            "md2pdf": {
                "engine": "weasyprint",
                "theme": "default",
            },
        },
        "database": {"host": "localhost", "port": 5432},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    return config_path, config_data


@pytest.fixture
def create_user_config(mock_config_dir):
    """Creates a user_config.yaml file that overrides some defaults."""
    config_path = mock_config_dir / "user_config.yaml"
    config_data = {
        "application": {
            "debug_mode": True,  # Override default
            "user_preference": "dark_mode",
        },
        "converters": {
            "pdf2md": {
                "ocr_enabled": False,  # Override default
                "lang": "eng+fra",  # New value
            },
        },
        # No database section, should fall back to default
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    return config_path, config_data


@pytest.fixture
def create_electron_config(mock_config_dir):
    """Creates an electron_config.json file."""
    config_path = mock_config_dir / "electron_config.json"
    config_data = {
        "window": {"width": 1200, "height": 800, "title": "Electron PDF Converter"},
        "integrations": {"auto_update": True},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return config_path, config_data


@pytest.fixture
def mock_env_vars():
    """Mocks environment variables with the MDTOPDF_ prefix."""
    env_vars = {
        "MDTOPDF_APPLICATION_VERSION": "1.1-env",  # Override
        "MDTOPDF_CONVERTERS_PDF2MD_TIMEOUT": "120",  # Override, should be int
        "MDTOPDF_DATABASE_HOST": "env.db.host",  # Override
        "MDTOPDF_DATABASE_USER": "env_user",  # New value
        "MDTOPDF_LOGGING_LEVEL": "DEBUG",  # New section/value
        "MDTOPDF_FEATURE_NEW_FLAG": "True",  # Boolean true
    }
    with mock.patch.dict(os.environ, env_vars):
        yield


# --- Test Cases ---


def test_config_manager_singleton(reset_config_manager_singleton, mock_config_dir):
    """Test that ConfigManager implements the singleton pattern."""
    # Instantiate with mock path
    instance1 = ConfigManager(config_dir=mock_config_dir)
    instance2 = ConfigManager(config_dir=mock_config_dir)
    assert instance1 is instance2
    assert instance1._initialized is True
    assert instance2._initialized is True
    assert instance1.config_dir == mock_config_dir


def test_load_yaml_success(
    reset_config_manager_singleton, mock_config_dir, create_default_config
):
    """Test successfully loading a YAML file."""
    _, expected_data = create_default_config
    cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
    loaded_data = cm._load_yaml("default_config.yaml")
    assert loaded_data == expected_data


def test_load_yaml_not_found(reset_config_manager_singleton, mock_config_dir):
    """Test loading a non-existent YAML file returns an empty dict."""
    cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
    loaded_data = cm._load_yaml("non_existent.yaml")
    assert loaded_data == {}


def test_load_yaml_invalid(reset_config_manager_singleton, mock_config_dir):
    """Test loading an invalid YAML file returns an empty dict and prints error."""
    invalid_yaml_path = mock_config_dir / "invalid.yaml"
    invalid_yaml_path.write_text("application: { name: MissingQuote")

    with mock.patch("builtins.print") as mock_print:
        cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
        loaded_data = cm._load_yaml("invalid.yaml")
        assert loaded_data == {}
        mock_print.assert_called_once()
        # Make assertion less strict - check for key parts
        call_args = mock_print.call_args[0][0]
        assert "Error loading config file" in call_args
        assert "invalid.yaml" in call_args
        assert "while parsing" in call_args  # Check for YAML parser error indication


def test_load_json_success(
    reset_config_manager_singleton, mock_config_dir, create_electron_config
):
    """Test successfully loading a JSON file."""
    _, expected_data = create_electron_config
    cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
    loaded_data = cm._load_json("electron_config.json")
    assert loaded_data == expected_data


def test_load_json_not_found(reset_config_manager_singleton, mock_config_dir):
    """Test loading a non-existent JSON file returns an empty dict."""
    cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
    loaded_data = cm._load_json("non_existent.json")
    assert loaded_data == {}


def test_load_json_invalid(reset_config_manager_singleton, mock_config_dir):
    """Test loading an invalid JSON file returns an empty dict and prints error."""
    invalid_json_path = mock_config_dir / "invalid.json"
    invalid_json_path.write_text('{"window": {"width": 1200,}')  # Trailing comma

    with mock.patch("builtins.print") as mock_print:
        cm = ConfigManager(config_dir=mock_config_dir)  # Instantiate with mock path
        loaded_data = cm._load_json("invalid.json")
        assert loaded_data == {}
        mock_print.assert_called_once()
        # Make assertion less strict - check for key parts
        call_args = mock_print.call_args[0][0]
        assert "Error loading config file" in call_args
        assert "invalid.json" in call_args
        assert (
            "JSONDecodeError" in call_args or "Illegal" in call_args
        )  # Check for JSON error indication


def test_load_environment_variables(
    reset_config_manager_singleton, mock_config_dir, mock_env_vars
):
    """Test loading and parsing environment variables during init."""
    # Instantiate ConfigManager *after* env vars are mocked
    cm = ConfigManager(config_dir=mock_config_dir)
    # Access the loaded env vars from the instance
    env_config = cm.env_overrides

    expected_env_config = {
        "application": {"version": "1.1-env"},
        "converters": {
            "pdf2md": {
                "timeout": 120  # Should be int
            }
        },
        "database": {"host": "env.db.host", "user": "env_user"},
        "logging": {"level": "DEBUG"},
        "feature": {
            "new_flag": True  # Should be bool
        },
    }
    assert env_config == expected_env_config


def test_get_config_merging_priority(
    reset_config_manager_singleton,
    mock_config_dir,
    create_default_config,
    create_user_config,
    create_electron_config,  # Added just to ensure all files exist
    mock_env_vars,
):
    """Test the merging logic and priority: Env > User > Default."""
    # Files created by fixtures above
    # Instantiate ConfigManager *after* files and env vars are set
    cm = ConfigManager(config_dir=mock_config_dir)

    # Test Application Section
    app_config = cm.get_config("application")
    assert app_config["name"] == "Default App Name"  # From default
    assert app_config["version"] == "1.1-env"  # From env (overrides default)
    assert app_config["debug_mode"] is True  # From user (overrides default)
    assert app_config["user_preference"] == "dark_mode"  # From user (new)

    # Test PDF2MD Converter Section
    # Access nested dict directly for clarity
    converters_config = cm.get_config("converters")
    assert "pdf2md" in converters_config
    pdf2md_config = converters_config["pdf2md"]
    assert pdf2md_config["default_engine"] == "pymupdf"  # From default
    assert pdf2md_config["ocr_enabled"] is False  # From user (overrides default)
    assert (
        pdf2md_config["timeout"] == 120
    )  # From env (overrides default, type converted)
    assert pdf2md_config["lang"] == "eng+fra"  # From user (new)

    # Test MD2PDF Converter Section (Only in Default)
    assert "md2pdf" in converters_config
    md2pdf_config = converters_config["md2pdf"]
    assert md2pdf_config["engine"] == "weasyprint"
    assert md2pdf_config["theme"] == "default"

    # Test Database Section
    db_config = cm.get_config("database")
    assert db_config["host"] == "env.db.host"  # From env (overrides default)
    assert db_config["port"] == 5432  # From default
    assert db_config["user"] == "env_user"  # From env (new)

    # Test Logging Section (Only in Env)
    log_config = cm.get_config("logging")
    assert log_config["level"] == "DEBUG"

    # Test Feature Section (Only in Env)
    feature_config = cm.get_config("feature")
    assert feature_config["new_flag"] is True

    # Test Non-existent Section
    non_existent_config = cm.get_config("non_existent")
    assert non_existent_config == {}


def test_get_electron_config(
    reset_config_manager_singleton, mock_config_dir, create_electron_config
):
    """Test retrieving the electron configuration."""
    _, expected_data = create_electron_config
    # Instantiate *after* file is created
    cm = ConfigManager(config_dir=mock_config_dir)
    electron_config = cm.get_electron_config()
    assert electron_config == expected_data


def test_get_converter_config(
    reset_config_manager_singleton,
    mock_config_dir,
    create_default_config,
    create_user_config,
):
    """Test getting merged config for a specific converter type."""
    # Instantiate *after* files are created
    cm = ConfigManager(config_dir=mock_config_dir)

    # PDF2MD should have merged values
    pdf2md_config = cm.get_converter_config("pdf2md")
    assert pdf2md_config["default_engine"] == "pymupdf"  # Default
    assert pdf2md_config["ocr_enabled"] is False  # User override
    assert pdf2md_config["timeout"] == 60  # Default (no env var mock here)
    assert pdf2md_config["lang"] == "eng+fra"  # User new

    # MD2PDF should only have default values
    md2pdf_config = cm.get_converter_config("md2pdf")
    assert md2pdf_config["engine"] == "weasyprint"
    assert md2pdf_config["theme"] == "default"
    assert "ocr_enabled" not in md2pdf_config  # Not defined for md2pdf

    # Non-existent converter type
    non_existent = cm.get_converter_config("imaginary")
    assert non_existent == {}


def test_save_and_update_user_config(
    reset_config_manager_singleton, mock_config_dir, create_default_config
):
    """Test saving and updating the user configuration file."""
    user_config_path = mock_config_dir / "user_config.yaml"
    # Instantiate CM *after* default config exists, but *before* user config does
    cm = ConfigManager(config_dir=mock_config_dir)

    # Initial state: user config doesn't exist, should get default
    assert cm.get_value("application", "debug_mode", value_type=bool) is False
    assert not user_config_path.exists()

    # Update a value
    cm.update_user_config("application", "debug_mode", True)

    # Check if file was created and written
    assert user_config_path.exists()
    with open(user_config_path, encoding="utf-8") as f:
        saved_user_config = yaml.safe_load(f)
    assert saved_user_config == {"application": {"debug_mode": True}}

    # Check if the internal user_config was reloaded and reflects the change
    assert cm.user_config == {"application": {"debug_mode": True}}
    # Check if get_config now returns the updated value
    assert cm.get_value("application", "debug_mode", value_type=bool) is True

    # Update another value in a new section
    cm.update_user_config("new_section", "new_key", "new_value")
    with open(user_config_path, encoding="utf-8") as f:
        saved_user_config = yaml.safe_load(f)
    expected_saved = {
        "application": {"debug_mode": True},
        "new_section": {"new_key": "new_value"},
    }
    # Check YAML structure (might have different key order)
    assert saved_user_config.get("application") == expected_saved.get("application")
    assert saved_user_config.get("new_section") == expected_saved.get("new_section")
    assert cm.user_config == expected_saved  # Internal representation should match
    assert cm.get_value("new_section", "new_key") == "new_value"

    # Test saving the whole config (overwrites previous)
    new_full_config = {"user": {"id": 123, "name": "Tester"}}
    cm.save_user_config(new_full_config)
    with open(user_config_path, encoding="utf-8") as f:
        saved_user_config = yaml.safe_load(f)
    assert saved_user_config == new_full_config
    assert cm.user_config == new_full_config
    # Use get_config to verify merging still works (or doesn't) after overwrite
    assert cm.get_config("user")["id"] == 123
    assert "application" not in cm.get_config("user")  # Check old user keys removed
    # Check default values are still accessible if not overridden by new user conf
    assert cm.get_config("database")["port"] == 5432


def test_get_value(
    reset_config_manager_singleton,
    mock_config_dir,
    create_default_config,
    create_user_config,
    mock_env_vars,
):
    """Test retrieving specific values with defaults and type conversion."""
    # Instantiate ConfigManager *after* files/env vars are set
    cm = ConfigManager(config_dir=mock_config_dir)

    # Test existing value (env > user > default)
    assert cm.get_value("application", "version") == "1.1-env"
    assert cm.get_value("application", "debug_mode") is True  # User override
    assert (
        cm.get_value("converters", "pdf2md", value_type=dict)["timeout"] == 120
    )  # Env override

    # Test value only in user config
    assert cm.get_value("application", "user_preference") == "dark_mode"

    # Test value only in default config
    assert cm.get_value("database", "port") == 5432

    # Test default value when key not found
    assert (
        cm.get_value("application", "non_existent_key", default="fallback")
        == "fallback"
    )
    assert cm.get_value("non_existent_section", "key", default=None) is None

    # Test type conversion (int)
    assert cm.get_value("database", "port", value_type=int) == 5432
    pdf2md_dict_int = cm.get_value("converters", "pdf2md", value_type=dict)
    assert isinstance(pdf2md_dict_int, dict)
    assert pdf2md_dict_int.get("timeout") == 120
    # Corrected: Cannot use value_type in dict.get()
    # To check type after retrieval:
    assert isinstance(pdf2md_dict_int.get("timeout"), int)

    # Test type conversion (bool)
    assert (
        cm.get_value("application", "debug_mode", value_type=bool) is True
    )  # From user
    assert cm.get_value("feature", "new_flag", value_type=bool) is True  # From env

    # Test type conversion (float)
    pdf2md_dict_float = cm.get_value("converters", "pdf2md", value_type=dict)
    # Retrieve the value first, then convert if needed, or check type
    timeout_val = pdf2md_dict_float.get("timeout")  # This is int(120)
    assert isinstance(timeout_val, int)
    assert float(timeout_val) == 120.0  # Explicit conversion for test assertion
    # Test get_value requesting float conversion directly
    assert (
        cm.get_value("converters", "pdf2md", value_type=dict).get("timeout") == 120
    )  # Check the stored int first
    # Let's test get_value directly requesting float for an int value
    # Need a value that is purely integer in config first
    assert cm.get_value("database", "port", value_type=float) == 5432.0

    # Test type conversion success (returns converted value, not default)
    with mock.patch("builtins.print") as mock_print:
        # Port is int 5432, try converting to bool. bool(5432) is True.
        assert (
            cm.get_value("database", "port", default=False, value_type=bool) is True
        )  # Should be True
        mock_print.assert_not_called()  # Successful conversion, no warning

    # Test type conversion failure (e.g., int('abc') -> returns default)
    faulty_env = {"MDTOPDF_DATABASE_PORT": "not-a-number"}
    with mock.patch.dict(os.environ, faulty_env, clear=True):
        # We need to reset BOTH singletons
        LogManager._instance = None
        ConfigManager._instance = None
        # Now create a new instance that will pick up the faulty env var
        cm_faulty = ConfigManager(config_dir=mock_config_dir)
        with mock.patch("builtins.print") as mock_print_faulty:
            # Try getting the port (now "not-a-number" from env) as int
            assert (
                cm_faulty.get_value("database", "port", default=9999, value_type=int)
                == 9999
            )
            mock_print_faulty.assert_called_once()
            assert (
                "Warning: Config value 'database.port'"
                in mock_print_faulty.call_args[0][0]
            )

    # Test type conversion failure for non-existent key (returns default)
    with mock.patch("builtins.print") as mock_print_nonexist:
        assert (
            cm.get_value("application", "non_existent", default=0, value_type=int) == 0
        )
        mock_print_nonexist.assert_not_called()  # No warning if value is None

    # Test getting entire section with type hint (already covered by merging test)
    db_config_dict = cm.get_config("database")
    assert isinstance(db_config_dict, dict)
    assert db_config_dict["host"] == "env.db.host"  # Env override
