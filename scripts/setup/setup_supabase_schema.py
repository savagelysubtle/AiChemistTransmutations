"""Setup Supabase database schema for license management.

This script creates the necessary tables and indexes for the
AiChemist Transmutation Codex licensing system in Supabase.

Run this script once when setting up a new Supabase project.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase-py is not installed.")
    print("Install with: pip install supabase")
    sys.exit(1)


# SQL Schema Definitions
SCHEMA_SQL = """
-- Licenses table
CREATE TABLE IF NOT EXISTS licenses (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    license_key TEXT NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('trial', 'basic', 'professional', 'enterprise')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'revoked', 'expired')),
    max_activations INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT valid_max_activations CHECK (max_activations > 0)
);

-- Activations table
CREATE TABLE IF NOT EXISTS activations (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    machine_id VARCHAR(255) NOT NULL,
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT unique_activation UNIQUE(license_id, machine_id)
);

-- Usage logs table
CREATE TABLE IF NOT EXISTS usage_logs (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    converter_name VARCHAR(100) NOT NULL,
    input_file_size BIGINT NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_licenses_email ON licenses(email);
CREATE INDEX IF NOT EXISTS idx_licenses_license_key ON licenses(license_key);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_activations_license_id ON activations(license_id);
CREATE INDEX IF NOT EXISTS idx_activations_machine_id ON activations(machine_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_license_id ON usage_logs(license_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);

-- Comments for documentation
COMMENT ON TABLE licenses IS 'License key records with type and status';
COMMENT ON TABLE activations IS 'Machine activations for each license';
COMMENT ON TABLE usage_logs IS 'Conversion usage tracking for analytics';

COMMENT ON COLUMN licenses.type IS 'License tier: trial, basic, professional, enterprise';
COMMENT ON COLUMN licenses.status IS 'License status: active, suspended, revoked, expired';
COMMENT ON COLUMN licenses.max_activations IS 'Maximum number of machines that can activate this license';
COMMENT ON COLUMN licenses.expires_at IS 'License expiration date (NULL for perpetual licenses)';

COMMENT ON COLUMN activations.machine_id IS 'SHA256 hash of machine fingerprint';
COMMENT ON COLUMN activations.last_seen_at IS 'Last time this activation was verified';

COMMENT ON COLUMN usage_logs.converter_name IS 'Name of converter used (e.g., md2pdf, pdf2md)';
COMMENT ON COLUMN usage_logs.input_file_size IS 'Size of input file in bytes';
"""


def print_sql_schema():
    """Print the SQL schema for manual execution."""
    print("=" * 80)
    print("SUPABASE DATABASE SCHEMA")
    print("=" * 80)
    print("\nCopy and execute this SQL in your Supabase SQL Editor:\n")
    print(SCHEMA_SQL)
    print("\n" + "=" * 80)
    print("Schema includes:")
    print("  - licenses table: License key records")
    print("  - activations table: Machine activation tracking")
    print("  - usage_logs table: Conversion usage analytics")
    print("  - Indexes for optimal query performance")
    print("=" * 80)


def setup_schema_via_api():
    """Setup schema using Supabase API (requires proper permissions)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")  # Note: SERVICE_KEY, not ANON_KEY

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        print("\nFor schema setup, you need the SERVICE ROLE KEY, not the anon key.")
        print("Find it in: Supabase Dashboard > Settings > API > service_role key")
        print("\nAlternatively, use the --print-only flag to get SQL for manual execution.")
        sys.exit(1)

    client = create_client(url, key)

    print("Setting up schema via Supabase API...")
    print("NOTE: This requires service_role permissions.")
    print("\nExecuting SQL schema...")

    try:
        # Execute schema SQL
        # Note: Supabase Python client doesn't have direct SQL execution
        # This is a placeholder - user should use SQL Editor or REST API
        print("\nWARNING: Python client doesn't support direct SQL execution.")
        print("Please use one of these methods instead:")
        print("\n1. Copy SQL from --print-only and execute in Supabase SQL Editor")
        print("2. Use Supabase CLI: supabase db push")
        print("3. Use REST API with service_role key")

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Supabase database schema for AiChemist licensing"
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Only print SQL schema (for manual execution)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Attempt to execute schema via API (requires SERVICE_KEY)",
    )

    args = parser.parse_args()

    if args.execute:
        setup_schema_via_api()
    else:
        # Default: print schema for manual execution
        print_sql_schema()


if __name__ == "__main__":
    main()
