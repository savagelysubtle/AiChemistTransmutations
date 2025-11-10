"""Check how many unused license keys are available in Supabase.

This script queries Supabase to show how many keys are available for each tier
and their status distribution.

Usage:
    python scripts/licensing/get_unused_keys_count.py

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (has admin access)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

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


def get_key_counts(client: Client) -> dict:
    """Get counts of keys by tier and status.

    Returns:
        Dict with tier -> status -> count mapping
    """
    try:
        # Get all licenses
        response = client.table("licenses").select("type, status, email").execute()

        counts = {}
        for record in response.data:
            tier = record["type"]
            status = record["status"]
            has_email = bool(record.get("email"))

            if tier not in counts:
                counts[tier] = {
                    "total": 0,
                    "unused": 0,  # active with no email
                    "assigned": 0,  # active with email but not activated
                    "used": 0,  # activated by customer
                }

            counts[tier]["total"] += 1

            if status == "active" and not has_email:
                counts[tier]["unused"] += 1
            elif status == "active" and has_email:
                counts[tier]["assigned"] += 1
            elif status in ["used", "activated"]:
                counts[tier]["used"] += 1

        return counts

    except Exception as e:
        print(f"❌ Database error: {e}")
        return {}


def main():
    """Main function."""
    print("🔍 Checking license key availability...\n")

    # Get Supabase client
    client = get_supabase_client()

    # Get counts
    counts = get_key_counts(client)

    if not counts:
        print("❌ No license keys found in database")
        sys.exit(1)

    # Display results
    print("=" * 70)
    print("LICENSE KEY INVENTORY")
    print("=" * 70)

    tier_names = {
        "basic": "Basic",
        "professional": "Professional",
        "enterprise": "Enterprise",
    }

    for tier, stats in sorted(counts.items()):
        tier_display = tier_names.get(tier, tier.capitalize())
        print(f"\n{tier_display} Tier:")
        print(f"  Total Keys:       {stats['total']}")
        print(f"  ✅ Unused:        {stats['unused']} (available for new customers)")
        print(f"  📧 Assigned:      {stats['assigned']} (sent but not yet activated)")
        print(f"  🔒 Used:          {stats['used']} (activated by customers)")

    print("\n" + "=" * 70)
    print("\n💡 Tips:")
    print("  • 'Unused' keys can be assigned to new customers")
    print("  • 'Assigned' keys have been sent but customer hasn't activated yet")
    print("  • 'Used' keys are actively in use by customers")
    print("\n  Generate more keys:")
    print("    python scripts/licensing/generate_gumroad_keys.py --count 100 --tier basic")


if __name__ == "__main__":
    main()





