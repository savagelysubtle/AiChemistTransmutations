"""Quick setup script for Gumroad license integration.

This script automates the process of:
1. Generating license keys for each tier
2. Inserting keys into Supabase
3. Creating ready-to-upload CSV files for Gumroad

Usage:
    python scripts/licensing/quick_gumroad_setup.py --basic 1000 --pro 500 --enterprise 100
    python scripts/licensing/quick_gumroad_setup.py --all 100  # Generate 100 of each

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (has admin access)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and handle errors.

    Args:
        cmd: Command and arguments to run.
        description: Human-readable description for logging.

    Returns:
        True if command succeeded, False otherwise.
    """
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        if e.stderr:
            print(e.stderr)
        return False


def generate_keys_for_tier(tier: str, count: int, output_dir: Path) -> Path | None:
    """Generate license keys for a specific tier.

    Args:
        tier: License tier (basic, pro, enterprise).
        count: Number of keys to generate.
        output_dir: Directory to save output files.

    Returns:
        Path to generated CSV file, or None if failed.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = output_dir / f"keys_{tier}_{timestamp}.csv"

    cmd = [
        sys.executable,
        "scripts/licensing/generate_gumroad_keys.py",
        "--count",
        str(count),
        "--tier",
        tier,
        "--output",
        str(csv_path),
    ]

    success = run_command(cmd, f"Generating {count} {tier.upper()} keys")

    return csv_path if success and csv_path.exists() else None


def insert_keys_to_supabase(csv_path: Path, tier: str) -> bool:
    """Insert generated keys into Supabase database.

    Args:
        csv_path: Path to CSV file with license keys.
        tier: License tier (basic, pro, enterprise).

    Returns:
        True if insertion succeeded, False otherwise.
    """
    cmd = [
        sys.executable,
        "scripts/licensing/insert_license_keys.py",
        "--csv",
        str(csv_path),
        "--tier",
        tier,
    ]

    return run_command(cmd, f"Inserting {tier.upper()} keys into Supabase")


def main() -> None:
    """CLI interface for quick Gumroad setup."""
    parser = argparse.ArgumentParser(
        description="Quick setup for Gumroad license integration"
    )

    parser.add_argument(
        "--basic", type=int, help="Number of Basic tier keys to generate"
    )
    parser.add_argument("--pro", type=int, help="Number of Pro tier keys to generate")
    parser.add_argument(
        "--enterprise", type=int, help="Number of Enterprise tier keys to generate"
    )
    parser.add_argument(
        "--all",
        type=int,
        help="Generate same number of keys for all tiers (shortcut)",
    )
    parser.add_argument(
        "--skip-supabase",
        action="store_true",
        help="Skip Supabase insertion (only generate CSVs)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated_keys"),
        help="Output directory for CSV files (default: generated_keys/)",
    )

    args = parser.parse_args()

    # Determine which tiers to generate
    tiers_to_generate = {}

    if args.all:
        tiers_to_generate = {
            "basic": args.all,
            "pro": args.all,
            "enterprise": args.all,
        }
    else:
        if args.basic:
            tiers_to_generate["basic"] = args.basic
        if args.pro:
            tiers_to_generate["pro"] = args.pro
        if args.enterprise:
            tiers_to_generate["enterprise"] = args.enterprise

    if not tiers_to_generate:
        print("❌ Error: No tiers specified!")
        print()
        print("Use --basic, --pro, --enterprise, or --all")
        print()
        print("Example: python quick_gumroad_setup.py --basic 1000 --pro 500")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("GUMROAD LICENSE KEY SETUP")
    print("=" * 70)
    print()
    print("Configuration:")
    for tier, count in tiers_to_generate.items():
        print(f"  {tier.upper()}: {count} keys")
    print(f"  Output Directory: {args.output_dir.resolve()}")
    print(f"  Supabase Insertion: {'Skipped' if args.skip_supabase else 'Enabled'}")
    print()

    # Generate keys for each tier
    generated_files = {}

    for tier, count in tiers_to_generate.items():
        print(f"\n{'='*70}")
        print(f"Processing {tier.upper()} Tier ({count} keys)")
        print(f"{'='*70}\n")

        # Generate keys
        csv_path = generate_keys_for_tier(tier, count, args.output_dir)

        if csv_path is None:
            print(f"❌ Failed to generate {tier} keys!")
            continue

        generated_files[tier] = csv_path

        # Insert into Supabase
        if not args.skip_supabase:
            success = insert_keys_to_supabase(csv_path, tier)
            if not success:
                print(f"⚠️  Warning: Failed to insert {tier} keys into Supabase")
                print("    Keys are still available in CSV file")

    # Print summary
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()

    if generated_files:
        print("✅ Generated Files:")
        for tier, csv_path in generated_files.items():
            print(f"  {tier.upper()}: {csv_path.resolve()}")
            json_path = csv_path.with_suffix(".json")
            if json_path.exists():
                print(f"    Records: {json_path.resolve()}")
        print()

        print("📋 Next Steps:")
        print()
        print("1. Upload CSV files to Gumroad:")
        print("   - Go to each product → Settings → License Keys")
        print("   - Click 'Upload license keys'")
        print("   - Upload the corresponding CSV file")
        print()
        print("2. Configure Gumroad email template:")
        print("   - Include download link to your app")
        print("   - Add clear activation instructions")
        print("   - Test with a test purchase")
        print()
        print("3. Test complete purchase flow:")
        print("   - Make a test purchase in Gumroad")
        print("   - Check email for license key")
        print("   - Activate key in your app")
        print("   - Verify Supabase records activation")
        print()

        if args.skip_supabase:
            print("⚠️  Note: Supabase insertion was skipped!")
            print("   Run this command to insert keys manually:")
            print()
            for tier, csv_path in generated_files.items():
                print(
                    f"   python scripts/licensing/insert_license_keys.py --csv {csv_path} --tier {tier}"
                )
            print()
    else:
        print("❌ No keys were generated successfully!")
        print("   Check error messages above.")


if __name__ == "__main__":
    main()





