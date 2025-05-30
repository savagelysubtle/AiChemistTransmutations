"""Path manipulation utilities for the Aichemist Transmutation Codex.

This module provides functions for working with file system paths, particularly
for modifying sys.path.
"""

import sys
from pathlib import Path

from .log_manager import LogManager

_module_logger = LogManager().get_logger("utils.path_utils")


def add_path_to_sys(path_to_add: Path | str, insert_at_front: bool = True) -> bool:
    """Adds a specified path to sys.path if it's not already present.

    This utility resolves the given path to an absolute path before adding.
    It's intended for general use within the application after initial
    bootstrap has made the 'aichemist_transmutation_codex' package importable.

    Args:
        path_to_add (Path | str): The path to add. Can be a string or
            Path object. An empty or None path will be ignored.
        insert_at_front (bool): If True (default), inserts the path at the
            beginning of sys.path (index 0). Otherwise, appends it to the end.

    Returns:
        bool: True if the path was successfully added, False if it was already
              present, invalid, or if path_to_add was empty/None.
    """
    if not path_to_add:
        _module_logger.warning("Attempted to add an empty or None path to sys.path.")
        return False

    try:
        resolved_path = Path(path_to_add).resolve()
        path_str = str(resolved_path)
    except Exception as e:
        _module_logger.error(f"Invalid path provided: '{path_to_add}'. Error: {e}")
        return False

    if path_str not in sys.path:
        if insert_at_front:
            sys.path.insert(0, path_str)
            _module_logger.info(f"Inserted path into sys.path[0]: {path_str}")
        else:
            sys.path.append(path_str)
            _module_logger.info(f"Appended path to sys.path: {path_str}")
        return True

    _module_logger.debug(f"Path already in sys.path: {path_str}")
    return False
