"""Feature access control and gating.

This module provides convenient functions for checking feature access
and enforcing license restrictions in converters.
"""

from pathlib import Path

from ..exceptions import LicenseError, raise_license_error
from .license_manager import LicenseManager


# Singleton instance
_license_manager_instance: LicenseManager | None = None


def get_license_manager() -> LicenseManager:
    """Get or create the singleton LicenseManager instance.

    Returns:
        LicenseManager instance

    Example:
        >>> manager = get_license_manager()
        >>> status = manager.get_license_status()
    """
    global _license_manager_instance
    if _license_manager_instance is None:
        _license_manager_instance = LicenseManager()
    return _license_manager_instance


def check_feature_access(converter_name: str):
    """Check if user has access to a converter feature.

    Args:
        converter_name: Name of converter (e.g., "pdf2md", "html2pdf")

    Raises:
        LicenseError: If feature access is denied
        TrialExpiredError: If trial has expired

    Example:
        >>> check_feature_access("pdf2md")  # Raises if not allowed
        >>> # Continue with conversion...
    """
    manager = get_license_manager()

    if not manager.has_feature_access(converter_name):
        status = manager.get_license_status()

        if status["license_type"] == "trial":
            raise_license_error(
                f"Converter '{converter_name}' requires a paid license. "
                f"Free trial only includes: {', '.join(manager.trial_manager.FREE_CONVERTERS)}. "
                "Please purchase a license at https://aichemist.gumroad.com to access all converters.",
                license_type="trial",
                feature=converter_name,
                reason="feature_not_in_trial",
            )
        else:
            raise_license_error(
                f"Converter '{converter_name}' is not included in your license.",
                license_type=status.get("license_type", "unknown"),
                feature=converter_name,
                reason="feature_not_licensed",
            )


def check_file_size_limit(input_path: str):
    """Check if file size is within license limits.

    Args:
        input_path: Path to input file

    Raises:
        LicenseError: If file exceeds size limit

    Example:
        >>> check_file_size_limit("/path/to/large/file.pdf")
        >>> # Raises LicenseError if file > 5MB in trial
    """
    manager = get_license_manager()
    manager.check_file_size_limit(input_path)


def record_conversion_attempt(
    converter_name: str,
    input_file: str,
    output_file: str | None = None,
    success: bool = True,
):
    """Record a conversion attempt for trial tracking.

    Args:
        converter_name: Name of converter used
        input_file: Input file path
        output_file: Output file path (if successful)
        success: Whether conversion succeeded

    Example:
        >>> record_conversion_attempt("md2pdf", "input.md", "output.pdf", True)
    """
    manager = get_license_manager()

    # Get file size
    try:
        file_size = Path(input_file).stat().st_size
    except FileNotFoundError:
        file_size = None

    manager.record_conversion(
        converter_name=converter_name,
        input_file=input_file,
        output_file=output_file,
        file_size_bytes=file_size,
        success=success,
    )


def get_trial_status() -> dict:
    """Get current trial status.

    Returns:
        Trial status dictionary

    Example:
        >>> status = get_trial_status()
        >>> print(f"{status['remaining']} conversions remaining")
    """
    manager = get_license_manager()
    license_status = manager.get_license_status()

    if license_status["license_type"] == "trial":
        return license_status["trial_status"]

    # Paid license - return unlimited status
    return {
        "status": "unlimited",
        "used": 0,
        "limit": -1,
        "remaining": -1,
    }


def is_trial_expired() -> bool:
    """Check if trial has expired.

    Returns:
        True if trial is expired

    Example:
        >>> if is_trial_expired():
        ...     show_upgrade_prompt()
    """
    status = get_trial_status()
    return status.get("status") == "expired"


def get_license_type() -> str:
    """Get current license type.

    Returns:
        License type: "trial" | "paid" | "none"

    Example:
        >>> if get_license_type() == "trial":
        ...     show_trial_badge()
    """
    manager = get_license_manager()
    status = manager.get_license_status()
    return status["license_type"]


def activate_license_key(license_key: str) -> dict:
    """Activate a license key.

    Args:
        license_key: License key to activate

    Returns:
        Activation status

    Raises:
        LicenseError: If activation fails

    Example:
        >>> status = activate_license_key("AICHEMIST-XXXXX-...")
        >>> print(f"Activated: {status['activated']}")
    """
    manager = get_license_manager()
    return manager.activate_license(license_key)


def deactivate_current_license() -> dict:
    """Deactivate current license.

    Returns:
        Deactivation status

    Example:
        >>> status = deactivate_current_license()
        >>> print(f"License deactivated")
    """
    manager = get_license_manager()
    return manager.deactivate_license()


def get_full_license_status() -> dict:
    """Get complete license status.

    Returns:
        Full license status dictionary

    Example:
        >>> status = get_full_license_status()
        >>> if status['license_type'] == 'paid':
        ...     print(f"Licensed to: {status['email']}")
    """
    manager = get_license_manager()
    return manager.get_license_status()
