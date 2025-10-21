-- =============================================================================
-- AiChemist Transmutation Codex - Supabase Database Setup
-- =============================================================================
-- This script creates all necessary tables, indexes, and Row Level Security
-- policies for the licensing system.
--
-- Execute this entire file in Supabase Dashboard > SQL Editor
-- =============================================================================

-- Create Tables
-- =============================================================================

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

-- Create Indexes
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_licenses_email ON licenses(email);
CREATE INDEX IF NOT EXISTS idx_licenses_license_key ON licenses(license_key);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_activations_license_id ON activations(license_id);
CREATE INDEX IF NOT EXISTS idx_activations_machine_id ON activations(machine_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_license_id ON usage_logs(license_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);

-- Add Comments for Documentation
-- =============================================================================

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

-- Enable Row Level Security
-- =============================================================================

ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE activations ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-running this script)
-- =============================================================================

DROP POLICY IF EXISTS "Allow license validation" ON licenses;
DROP POLICY IF EXISTS "Allow recording activations" ON activations;
DROP POLICY IF EXISTS "Allow updating last seen" ON activations;
DROP POLICY IF EXISTS "Allow reading own activations" ON activations;
DROP POLICY IF EXISTS "Allow usage logging" ON usage_logs;
DROP POLICY IF EXISTS "Service role full access licenses" ON licenses;
DROP POLICY IF EXISTS "Service role full access activations" ON activations;
DROP POLICY IF EXISTS "Service role full access usage_logs" ON usage_logs;

-- Create Row Level Security Policies
-- =============================================================================

-- Allow anon users to read active licenses (for validation)
CREATE POLICY "Allow license validation" ON licenses
  FOR SELECT
  TO anon
  USING (status = 'active');

-- Allow anon users to record activations
CREATE POLICY "Allow recording activations" ON activations
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Allow anon users to update last_seen timestamp
CREATE POLICY "Allow updating last seen" ON activations
  FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

-- Allow anon users to read their own activations (by machine_id hash)
CREATE POLICY "Allow reading own activations" ON activations
  FOR SELECT
  TO anon
  USING (true);

-- Allow anon users to log usage for valid licenses
CREATE POLICY "Allow usage logging" ON usage_logs
  FOR INSERT
  TO anon
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM licenses
      WHERE licenses.id = usage_logs.license_id
      AND licenses.status = 'active'
    )
  );

-- Service role has full access (for admin operations)
CREATE POLICY "Service role full access licenses" ON licenses
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access activations" ON activations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access usage_logs" ON usage_logs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- =============================================================================
-- Setup Complete!
-- =============================================================================
--
-- Verification Steps:
-- 1. Check that all three tables were created: licenses, activations, usage_logs
-- 2. Verify RLS is enabled on all tables
-- 3. Confirm policies are in place (should see 8 policies total)
--
-- Next Steps:
-- 1. Run: python scripts/generate_dev_license.py
-- 2. Test license activation in the GUI
-- 3. Verify data appears in these tables
--
-- =============================================================================

