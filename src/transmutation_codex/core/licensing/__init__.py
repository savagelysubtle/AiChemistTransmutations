"""Licensing system for AiChemist Transmutation Codex.

This package provides license validation, trial management, and feature gating
for the document conversion application.

Public API:
    - check_feature_access(converter_name) - Verify feature access
    - check_file_size_limit(input_path) - Check file size limits
    - record_conversion_attempt(...) - Track conversions for trial
    - get_trial_status() - Get trial information
    - get_license_type() - Get current license type
    - activate_license_key(key) - Activate a license
    - deactivate_current_license() - Deactivate license
    - get_full_license_status() - Get complete license info
    - get_license_manager() - Get LicenseManager instance

Example usage in converters:
    >>> from transmutation_codex.core.licensing import (
    ...     check_feature_access,
    ...     check_file_size_limit,
    ...     record_conversion_attempt,
    ... )
    >>>
    >>> def convert_pdf_to_md(input_path, output_path):
    ...     check_feature_access("pdf2md")
    ...     check_file_size_limit(input_path)
    ...
    ...     # Perform conversion...
    ...
    ...     record_conversion_attempt("pdf2md", input_path, output_path, True)
"""

# Core licensing components
from .activation import ActivationManager, MachineFingerprint
from .crypto import LicenseCrypto
from .license_manager import LicenseManager
from .trial_manager import TrialManager

# Feature gating functions (primary API)
from .feature_gates import (
    activate_license_key,
    check_feature_access,
    check_file_size_limit,
    deactivate_current_license,
    get_full_license_status,
    get_license_manager,
    get_license_type,
    get_trial_status,
    is_trial_expired,
    record_conversion_attempt,
)

__all__ = [
    # Primary API functions (used by converters)
    "check_feature_access",
    "check_file_size_limit",
    "record_conversion_attempt",
    "get_trial_status",
    "is_trial_expired",
    "get_license_type",
    "activate_license_key",
    "deactivate_current_license",
    "get_full_license_status",
    "get_license_manager",
    # Core classes (advanced usage)
    "LicenseManager",
    "TrialManager",
    "ActivationManager",
    "MachineFingerprint",
    "LicenseCrypto",
]
