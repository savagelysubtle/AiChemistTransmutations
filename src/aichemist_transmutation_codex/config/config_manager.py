import copy
import json
import os
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

import yaml


# Deep merge utility function
def deep_merge(
    source: MutableMapping[Any, Any], destination: MutableMapping[Any, Any]
) -> MutableMapping[Any, Any]:
    """
    Deeply merges source dictionary into destination dictionary.
    Modifies destination in place.
    """
    for key, value in source.items():
        if isinstance(value, MutableMapping):
            # Get node or create one
            node = destination.setdefault(key, {})
            if isinstance(node, MutableMapping):
                deep_merge(value, node)
            # If the destination node is not a dictionary, the source value replaces it
            # This handles cases where default might have a scalar but user/env has a dict
            else:
                destination[key] = copy.deepcopy(
                    value
                )  # Use deepcopy for nested structures
        else:
            destination[key] = value
    return destination


class ConfigManager:
    """
    Manages configuration settings from multiple sources.

    This class implements the singleton pattern to ensure only one
    configuration manager is active throughout the application.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern for ConfigManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_dir: Path | str | None = None):
        """Initialize the ConfigManager if not already initialized."""
        if getattr(self, "_initialized", False):
            return

        # Set up paths
        self.config_dir = Path(config_dir) if config_dir is not None else Path("config")

        # Load configurations
        self.default_config = self._load_yaml("default_config.yaml")
        self.user_config = self._load_yaml("user_config.yaml")
        self.electron_config = self._load_json("electron_config.json")

        # Environment overrides
        self.env_overrides = self._load_environment_variables()

        # Mark as initialized
        self._initialized = True

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        """
        Load a YAML configuration file. Handles FileNotFoundError.
        """
        config_path = self.config_dir / filename
        if not config_path.exists():
            return {}
        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config if config is not None else {}
        except FileNotFoundError:
            return {}
        except (yaml.YAMLError, Exception) as e:
            print(f"Error loading config file {config_path}: {e}")
            return {}

    def _load_json(self, filename: str) -> dict[str, Any]:
        """
        Load a JSON configuration file. Handles FileNotFoundError.
        """
        config_path = self.config_dir / filename
        if not config_path.exists():
            return {}
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading config file {config_path}: {e}")
            return {}

    def _load_environment_variables(self) -> dict[str, Any]:
        """
        Load configuration from environment variables.

        For variables like MDTOPDF_FEATURE_NEW_FLAG=True, creates:
        {'feature': {'new_flag': True}}

        For MDTOPDF_CONVERTERS_PDF2MD_TIMEOUT=120, creates:
        {'converters': {'pdf2md': {'timeout': 120}}}
        """
        prefix = "MDTOPDF_"
        config: dict[str, Any] = {}

        for env_key, value_str in os.environ.items():
            if not env_key.startswith(prefix):
                continue

            # For debugging purposes, print the environment variables being processed
            # print(f"Processing env var: {env_key}={value_str}")

            # Remove prefix and split by underscore
            parts = env_key[len(prefix) :].lower().split("_")
            if len(parts) < 2:
                continue  # Need at least a section and a key

            # First part is the top-level section
            section = parts[0]
            current = config.setdefault(section, {})

            # Special case for converters section with 3+ parts
            # MDTOPDF_CONVERTERS_PDF2MD_TIMEOUT → converters.pdf2md.timeout
            if section == "converters" and len(parts) >= 3:
                converter_type = parts[1]
                converter_dict = current.setdefault(converter_type, {})

                # Join remaining parts with underscore for the key
                key_name = "_".join(parts[2:])

                # Convert and store the value
                converter_dict[key_name] = self._convert_env_value(value_str)

            # Standard case for 2-part env vars
            # MDTOPDF_SECTION_KEY → section.key
            elif len(parts) == 2:
                current[parts[1]] = self._convert_env_value(value_str)

            # Handle 3+ part env vars (not converters)
            # MDTOPDF_FEATURE_NEW_FLAG → feature.new_flag
            else:
                # Join all parts after the section with underscore
                key_name = "_".join(parts[1:])
                current[key_name] = self._convert_env_value(value_str)

        return config

    def _convert_env_value(self, value_str: str) -> Any:
        """Convert environment variable string to appropriate type."""
        if value_str.lower() in ("true", "yes", "1"):
            return True
        elif value_str.lower() in ("false", "no", "0"):
            return False
        else:
            try:
                return int(value_str)
            except ValueError:
                try:
                    return float(value_str)
                except ValueError:
                    return value_str

    def get_config(self, section: str) -> dict[str, Any]:
        """
        Get configuration for a specific section, merging from all sources.

        Priority order (highest to lowest):
        1. Environment variables
        2. User configuration
        3. Default configuration

        Performs a deep merge.

        Args:
            section: Section name to retrieve

        Returns:
            Dictionary containing deeply merged configuration for the section
        """
        # Start with a deep copy of the default section to avoid modifying it
        merged_config = copy.deepcopy(self.default_config.get(section, {}))

        # Merge user config into the result
        user_section = self.user_config.get(section, {})
        if isinstance(
            user_section, MutableMapping
        ):  # Ensure it's a dict-like structure
            deep_merge(user_section, merged_config)

        # Merge environment overrides into the result
        env_section = self.env_overrides.get(section, {})
        if isinstance(env_section, MutableMapping):  # Ensure it's a dict-like structure
            deep_merge(env_section, merged_config)

        return merged_config

    def get_electron_config(self) -> dict[str, Any]:
        """
        Get Electron-specific configuration. (No merging applied here by default)

        Returns:
            Dictionary containing Electron configuration
        """
        # Electron config is typically standalone, no deep merge applied here
        # unless specific requirements arise.
        return self.electron_config

    def get_converter_config(self, converter_type: str) -> dict[str, Any]:
        """
        Get configuration for a specific converter, performing a deep merge.

        Args:
            converter_type: Type of converter (e.g., 'pdf2md', 'md2pdf')

        Returns:
            Dictionary containing merged configuration for the converter
        """
        # Get the top-level 'converters' section using the deep merge logic
        converters_config = self.get_config("converters")

        # Return the specific converter's config from the merged result
        return converters_config.get(converter_type, {})

    def save_user_config(self, config: dict[str, Any]) -> None:
        """
        Save user configuration to file. Ensures config dir exists.
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config_path = self.config_dir / "user_config.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            self.user_config = self._load_yaml("user_config.yaml")
        except Exception as e:
            print(f"Error saving user config to {config_path}: {e}")

    def update_user_config(self, section: str, key: str, value: Any) -> None:
        """
        Update a specific value in the user configuration.
        """
        if section not in self.user_config:
            self.user_config[section] = {}

        self.user_config[section][key] = value
        self.save_user_config(self.user_config)

    def get_value(
        self,
        section: str,
        key: str,
        default: Any = None,
        value_type: type | None = None,
    ) -> Any:
        """
        Get a specific configuration value with type checking from the merged config.
        """
        # Use get_config to ensure deep merge has happened
        section_config = self.get_config(section)
        value = section_config.get(key, default)

        if value is None:
            return default

        if value_type is not None:
            try:
                if isinstance(value, value_type):
                    return value
                return value_type(value)
            except (ValueError, TypeError):
                print(
                    f"Warning: Config value '{section}.{key}' ('{value}') is not convertible to type {value_type.__name__}. Returning default."
                )
                return default

        return value
