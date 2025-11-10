"""Gumroad setup validator and configuration helper.

This script helps validate your Gumroad setup and provides helpful guidance
for each step of the configuration process.

Usage:
    python scripts/gumroad/validate_setup.py
    python scripts/gumroad/validate_setup.py --check-webhook https://your-url.com
"""

import argparse
import os
import sys
from pathlib import Path

import requests
import yaml


def load_config() -> dict:
    """Load Gumroad configuration file."""
    config_path = Path(__file__).parent / "gumroad_config.yaml"
    if not config_path.exists():
        print("❌ Error: gumroad_config.yaml not found!")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def check_environment_variables() -> dict[str, bool]:
    """Check if required environment variables are set."""
    required_vars = [
        "GUMROAD_WEBHOOK_SECRET",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "PRIVATE_KEY_PATH",
    ]

    results = {}
    for var in required_vars:
        value = os.getenv(var)
        results[var] = bool(value and value != "your_value_here")

    return results


def check_private_key() -> bool:
    """Check if private key file exists."""
    key_path = Path(__file__).parent.parent / "licensing" / "keys" / "private_key.pem"
    return key_path.exists()


def check_webhook_health(webhook_url: str) -> dict:
    """Check if webhook server is responding."""
    try:
        health_url = f"{webhook_url.rstrip('/webhook/gumroad')}/health"
        response = requests.get(health_url, timeout=10)
        return {
            "reachable": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None,
            "error": None,
        }
    except requests.exceptions.RequestException as e:
        return {
            "reachable": False,
            "response": None,
            "error": str(e),
        }


def validate_product_mapping(config: dict) -> dict[str, dict]:
    """Validate product mapping configuration."""
    products = config.get("products", {})
    validation = {}

    for tier, product_info in products.items():
        validation[tier] = {
            "has_name": bool(product_info.get("name")),
            "has_permalink": bool(product_info.get("permalink")),
            "has_price": bool(product_info.get("price")),
            "has_license_type": bool(product_info.get("license_type")),
            "has_features": bool(product_info.get("features")),
        }

    return validation


def print_section(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def print_status(check_name: str, passed: bool, details: str = "") -> None:
    """Print a check status."""
    icon = "✅" if passed else "❌"
    print(f"{icon} {check_name}")
    if details:
        print(f"   {details}")


def main() -> None:
    """Run validation checks."""
    parser = argparse.ArgumentParser(description="Validate Gumroad setup configuration")
    parser.add_argument(
        "--check-webhook",
        help="Check if webhook server is responding (provide webhook URL)",
    )
    args = parser.parse_args()

    print("🔍 AiChemist Gumroad Setup Validator")
    print("=" * 70)

    # Load configuration
    try:
        config = load_config()
        print("✅ Configuration file loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)

    # Check 1: Product Configuration
    print_section("1. Product Configuration")
    product_validation = validate_product_mapping(config)

    all_products_valid = True
    for tier, checks in product_validation.items():
        tier_valid = all(checks.values())
        all_products_valid = all_products_valid and tier_valid

        print_status(
            f"{tier.capitalize()} Tier",
            tier_valid,
            f"Permalink: {config['products'][tier].get('permalink', 'MISSING')}",
        )

        if not tier_valid:
            for check_name, passed in checks.items():
                if not passed:
                    print(f"   ⚠️  Missing: {check_name}")

    # Check 2: Environment Variables
    print_section("2. Environment Variables (Server-side)")
    env_vars = check_environment_variables()

    print(
        "ℹ️  These are only needed on your webhook server, not locally for development"
    )
    print()

    for var, is_set in env_vars.items():
        print_status(var, is_set, "Set" if is_set else "Not set or using placeholder")

    # Check 3: Private Key
    print_section("3. RSA Private Key")
    key_exists = check_private_key()
    print_status(
        "Private key exists",
        key_exists,
        "Found at scripts/licensing/keys/private_key.pem"
        if key_exists
        else "Run: python scripts/licensing/generate_rsa_keys.py",
    )

    # Check 4: Webhook Health (optional)
    if args.check_webhook:
        print_section("4. Webhook Server Health")
        webhook_result = check_webhook_health(args.check_webhook)

        print_status(
            "Webhook server reachable",
            webhook_result["reachable"],
            (
                f"Response: {webhook_result['response']}"
                if webhook_result["reachable"]
                else f"Error: {webhook_result['error']}"
            ),
        )

    # Summary
    print_section("Summary")

    issues = []
    if not all_products_valid:
        issues.append("Product configuration incomplete")
    if not all(env_vars.values()):
        issues.append(
            "Environment variables not set (needed for webhook server deployment)"
        )
    if not key_exists:
        issues.append("Private key not generated")
    if args.check_webhook and not webhook_result["reachable"]:
        issues.append("Webhook server not reachable")

    if not issues:
        print("✅ All checks passed! Your Gumroad setup looks good.")
        print()
        print("Next steps:")
        print("1. Deploy webhook server (see docs/GUMROAD_SETUP_GUIDE.md)")
        print("2. Create products in Gumroad dashboard")
        print("3. Configure webhook in Gumroad settings")
        print("4. Test with a test purchase")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        print("📚 See docs/GUMROAD_SETUP_GUIDE.md for detailed setup instructions")

    # Product URLs
    print_section("Product URLs (after Gumroad setup)")
    for tier, product_info in config["products"].items():
        permalink = product_info.get("permalink", "NOT_SET")
        print(f"{tier.capitalize()}: https://aichemist.gumroad.com/l/{permalink}")

    # Configuration details
    print_section("Configuration Details")
    print(f"Store Name: {config['store']['name']}")
    print(f"Store URL: {config['store']['url']}")
    print(f"Support Email: {config['store']['support_email']}")
    print(f"Documentation: {config['store']['documentation_url']}")

    print()


if __name__ == "__main__":
    main()
