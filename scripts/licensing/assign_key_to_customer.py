"""Assign an unused license key from Supabase to a customer.

This script finds an unused license key of the specified tier and assigns it
to the customer's email address. Use this for manual fulfillment after Gumroad purchases.

Usage:
    python scripts/licensing/assign_key_to_customer.py --email customer@example.com --tier basic
    python scripts/licensing/assign_key_to_customer.py --email customer@example.com --tier pro --send-email

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (has admin access)
    SMTP_HOST: (Optional) SMTP server for sending emails
    SMTP_PORT: (Optional) SMTP port (default: 587)
    SMTP_USER: (Optional) SMTP username
    SMTP_PASSWORD: (Optional) SMTP password
    SMTP_FROM: (Optional) From email address

Example:
    # Assign key and display it (manual email)
    python scripts/licensing/assign_key_to_customer.py --email john@example.com --tier basic

    # Assign key and send email automatically
    python scripts/licensing/assign_key_to_customer.py --email john@example.com --tier basic --send-email
"""

from __future__ import annotations

import argparse
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from supabase import Client, create_client
except ImportError:
    print("❌ Error: supabase-py not installed")
    print("Run: pip install supabase")
    sys.exit(1)


def get_supabase_client() -> Client:
    """Get Supabase client with service role key."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    return create_client(url, key)


def get_unused_key(client: Client, tier: str) -> dict[str, Any] | None:
    """Find an unused license key for the specified tier.

    Args:
        client: Supabase client
        tier: License tier (basic, pro, enterprise)

    Returns:
        License record dict, or None if no unused keys found
    """
    # Map tier names
    tier_map = {"basic": "basic", "pro": "professional", "enterprise": "enterprise"}
    db_tier = tier_map.get(tier.lower())

    if not db_tier:
        print(f"❌ Invalid tier: {tier}. Must be: basic, pro, enterprise")
        return None

    try:
        # Query for active keys with no email (unused)
        response = (
            client.table("licenses")
            .select("*")
            .eq("type", db_tier)
            .eq("status", "active")
            .is_("email", "null")
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    except Exception as e:
        print(f"❌ Database error: {e}")
        return None


def assign_key_to_customer(
    client: Client, license_id: int, customer_email: str
) -> bool:
    """Assign a license key to a customer.

    Args:
        client: Supabase client
        license_id: License ID to assign
        customer_email: Customer's email address

    Returns:
        True if assignment successful
    """
    try:
        response = (
            client.table("licenses")
            .update({"email": customer_email, "metadata": {"assigned_at": datetime.now().isoformat(), "source": "gumroad_manual"}})
            .eq("id", license_id)
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:
        print(f"❌ Error assigning key: {e}")
        return False


def send_license_email(
    customer_email: str, license_key: str, tier: str, customer_name: str | None = None
) -> bool:
    """Send license key email to customer via SMTP.

    Args:
        customer_email: Customer's email address
        license_key: License key to send
        tier: License tier (basic, pro, enterprise)
        customer_name: Optional customer name

    Returns:
        True if email sent successfully
    """
    # Get SMTP configuration
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not all([smtp_host, smtp_user, smtp_password]):
        print("⚠️  SMTP not configured. Set SMTP_* environment variables to send emails.")
        return False

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AIChemist Transmutation Codex License Key"
    msg["From"] = smtp_from
    msg["To"] = customer_email

    # Email body
    greeting = f"Hi {customer_name}" if customer_name else "Hello"
    tier_name = tier.capitalize() if tier != "pro" else "Professional"

    text_body = f"""{greeting}!

Thank you for purchasing AIChemist Transmutation Codex - {tier_name} Edition!

Your License Key: {license_key}

🚀 Getting Started:

1. Download the installer: https://github.com/your-repo/releases/latest
2. Install the application
3. Open the app and click "Enter License"
4. Paste your license key above
5. Start converting documents!

📋 Your License Details:
• Tier: {tier_name}
• License Key: {license_key}
• Activations: {'2 devices' if tier == 'basic' else '5 devices' if tier == 'pro' else '25 devices'}

💡 Need Help?
• Documentation: https://docs.your-site.com
• Support: support@your-site.com
• Reply to this email

Enjoy your new document conversion superpowers!

-The AIChemist Team
"""

    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2563eb;">{greeting}!</h2>

        <p>Thank you for purchasing <strong>AIChemist Transmutation Codex - {tier_name} Edition</strong>!</p>

        <div style="background: #f3f4f6; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px; color: #666;">Your License Key:</p>
            <p style="margin: 5px 0; font-size: 18px; font-family: monospace; font-weight: bold; color: #1f2937;">
                {license_key}
            </p>
        </div>

        <h3 style="color: #2563eb;">🚀 Getting Started:</h3>
        <ol>
            <li>Download the installer: <a href="https://github.com/your-repo/releases/latest">Latest Release</a></li>
            <li>Install the application</li>
            <li>Open the app and click "Enter License"</li>
            <li>Paste your license key above</li>
            <li>Start converting documents!</li>
        </ol>

        <h3 style="color: #2563eb;">📋 Your License Details:</h3>
        <ul style="list-style: none; padding: 0;">
            <li>✓ Tier: <strong>{tier_name}</strong></li>
            <li>✓ License Key: <code style="background: #f3f4f6; padding: 2px 6px;">{license_key}</code></li>
            <li>✓ Activations: <strong>{'2 devices' if tier == 'basic' else '5 devices' if tier == 'pro' else '25 devices'}</strong></li>
        </ul>

        <h3 style="color: #2563eb;">💡 Need Help?</h3>
        <ul style="list-style: none; padding: 0;">
            <li>📚 <a href="https://docs.your-site.com">Documentation</a></li>
            <li>📧 <a href="mailto:support@your-site.com">support@your-site.com</a></li>
            <li>💬 Reply to this email</li>
        </ul>

        <p style="margin-top: 30px; color: #666; font-size: 14px;">
            Enjoy your new document conversion superpowers!<br>
            <strong>-The AIChemist Team</strong>
        </p>
    </div>
</body>
</html>
"""

    # Attach both plain text and HTML versions
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"✅ Email sent to {customer_email}")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Assign unused license key to customer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--email", required=True, help="Customer email address"
    )
    parser.add_argument(
        "--tier",
        required=True,
        choices=["basic", "pro", "enterprise"],
        help="License tier",
    )
    parser.add_argument(
        "--name", help="Customer name (optional, for email personalization)"
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send license key via email (requires SMTP configuration)",
    )

    args = parser.parse_args()

    print("🔍 Finding unused license key...")
    print(f"   Email: {args.email}")
    print(f"   Tier: {args.tier}")

    # Get Supabase client
    client = get_supabase_client()

    # Find unused key
    license_record = get_unused_key(client, args.tier)

    if not license_record:
        print(f"\n❌ No unused {args.tier} keys available!")
        print("   Generate more keys with:")
        print(
            f"   python scripts/licensing/generate_gumroad_keys.py --count 100 --tier {args.tier}"
        )
        sys.exit(1)

    license_key = license_record["license_key"]
    license_id = license_record["id"]

    print(f"\n✅ Found unused key: {license_key}")
    print(f"   Assigning to: {args.email}...")

    # Assign key to customer
    if assign_key_to_customer(client, license_id, args.email):
        print(f"✅ Key assigned successfully!")
        print(f"\n{'=' * 70}")
        print(f"📧 EMAIL TO CUSTOMER: {args.email}")
        print(f"{'=' * 70}")
        print(f"\nLicense Key: {license_key}")
        print(f"Tier: {args.tier.capitalize()}")
        print(f"\n{'=' * 70}")

        # Send email if requested
        if args.send_email:
            print("\n📨 Sending email to customer...")
            if send_license_email(args.email, license_key, args.tier, args.name):
                print("✅ Email sent!")
            else:
                print("⚠️  Email not sent. Send manually using the key above.")
        else:
            print("\nℹ️  Email not sent (use --send-email to send automatically)")
            print("   Send this key to the customer manually.")

    else:
        print("❌ Failed to assign key")
        sys.exit(1)


if __name__ == "__main__":
    main()

