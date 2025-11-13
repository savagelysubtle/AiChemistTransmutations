# Supabase Setup Guide

This guide explains how to set up Supabase integration for online license
tracking and analytics.

> **Note:** Supabase is **optional**. The application works perfectly fine in
> offline mode without it. Supabase adds online license tracking, usage
> analytics, and multi-device activation management.

## Table of Contents

- [Why Use Supabase?](#why-use-supabase)
- [Prerequisites](#prerequisites)
- [Step 1: Create Supabase Project](#step-1-create-supabase-project)
- [Step 2: Create Database Tables](#step-2-create-database-tables)
- [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
- [Step 4: Test Integration](#step-4-test-integration)
- [Troubleshooting](#troubleshooting)

## Why Use Supabase?

Supabase provides:

- **License Activation Tracking**: Track which devices have activated licenses
- **Usage Analytics**: Monitor conversion counts and feature usage
- **Multi-Device Management**: Enforce activation limits across devices
- **Purchase History**: Store Gumroad purchase data for reference
- **Real-time Sync**: Keep license status synchronized across installations

## Prerequisites

- Free Supabase account (https://supabase.com/dashboard)
- Your Gumroad product ID configured in the app

## Step 1: Create Supabase Project

1. **Sign up or log in** to Supabase: https://supabase.com/dashboard
2. **Create a new project**:
   - Project name: `aichemist-licenses` (or your choice)
   - Database password: Generate a strong password and save it securely
   - Region: Choose closest to your users
3. **Wait for project to finish provisioning** (2-3 minutes)

## Step 2: Create Database Tables

### Table 1: `gumroad_licenses`

This table stores activated Gumroad licenses.

```sql
-- Create gumroad_licenses table
CREATE TABLE gumroad_licenses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    license_key TEXT UNIQUE NOT NULL,
    gumroad_purchase_id TEXT,
    gumroad_product_id TEXT,
    tier TEXT NOT NULL CHECK (tier IN ('basic', 'pro', 'enterprise')),
    email TEXT,
    purchase_date TIMESTAMPTZ,
    activation_date TIMESTAMPTZ DEFAULT NOW(),
    machine_id TEXT NOT NULL,
    gumroad_data JSONB,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
    max_activations INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on license_key for fast lookups
CREATE INDEX idx_gumroad_licenses_license_key ON gumroad_licenses(license_key);

-- Create index on machine_id for activation tracking
CREATE INDEX idx_gumroad_licenses_machine_id ON gumroad_licenses(machine_id);

-- Enable Row Level Security (RLS)
ALTER TABLE gumroad_licenses ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role full access
CREATE POLICY "Service role has full access" ON gumroad_licenses
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
```

### Table 2: `license_usage`

This table tracks usage metrics for each license.

```sql
-- Create license_usage table
CREATE TABLE license_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    license_key TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    conversion_type TEXT NOT NULL,
    file_size_bytes BIGINT,
    success BOOLEAN DEFAULT true,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on license_key for analytics
CREATE INDEX idx_license_usage_license_key ON license_usage(license_key);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_license_usage_timestamp ON license_usage(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE license_usage ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role full access
CREATE POLICY "Service role has full access" ON license_usage
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
```

### Run the SQL

1. Go to **SQL Editor** in Supabase dashboard
2. Click **New Query**
3. Copy and paste the SQL above
4. Click **Run** to execute

## Step 3: Configure Environment Variables

### For Desktop Application

1. **Copy the template**:

   ```bash
   cp .env.template .env
   # Or for GUI:
   cp gui/.env.template gui/.env
   ```

2. **Get your Supabase credentials**:

   - Go to **Settings** → **API** in Supabase dashboard
   - Copy **Project URL**
   - Copy **anon public** key

3. **Edit `.env` file**:

   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```

4. **Restart the application** to load new environment variables

### For Webhook Server

If you're deploying the webhook server for automated license delivery:

1. **Get service role key** (more permissions than anon key):

   - Go to **Settings** → **API** in Supabase dashboard
   - Copy **service_role** key (⚠️ Keep this secret!)

2. **Configure webhook `.env`**:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key-here
   GUMROAD_WEBHOOK_SECRET=your-webhook-secret
   ```

## Step 4: Test Integration

### Test 1: Verify Connection

Run the test script to verify Supabase connection:

```bash
python scripts/licensing/test_gumroad_integration.py
```

Look for:

```
✓ Supabase backend initialized
✓ Connection successful
```

### Test 2: Activate a License

1. Launch the application
2. Enter your Gumroad license key
3. Click **Activate**
4. Check Supabase dashboard → **Table Editor** → `gumroad_licenses`
5. You should see a new row with your activation

### Test 3: Usage Tracking

1. Perform a file conversion in the app
2. Check Supabase dashboard → **Table Editor** → `license_usage`
3. You should see a new usage record

## Troubleshooting

### "Failed to connect to Supabase"

**Cause:** Network issues or incorrect credentials

**Solutions:**

- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check your internet connection
- Verify Supabase project is active (not paused)
- Try accessing the Supabase URL in your browser

### "Permission denied" errors

**Cause:** Row Level Security (RLS) policies blocking access

**Solutions:**

- Verify RLS policies are created correctly
- Use `service_role` key for server-side operations
- Use `anon` key for client-side operations
- Check policy SQL for typos

### License activates but doesn't appear in Supabase

**Cause:** Non-critical Supabase logging failure

**Solutions:**

- Check application logs for specific error
- Verify table structure matches schema above
- Ensure `gumroad_licenses` table exists
- Try manual INSERT to test permissions:
  ```sql
  INSERT INTO gumroad_licenses (license_key, tier, machine_id)
  VALUES ('TEST-KEY', 'basic', 'test-machine-123');
  ```

### "getaddrinfo failed" error

**Cause:** DNS resolution issue or network problem

**Solutions:**

- Check your internet connection
- Try different network (e.g., switch from WiFi to mobile hotspot)
- Verify firewall isn't blocking Supabase
- Wait a few minutes and try again

## Security Best Practices

### Environment Variables

✅ **DO:**

- Store credentials in `.env` files (already in `.gitignore`)
- Use `anon` key for client-side operations
- Use `service_role` key only in secure server environments
- Rotate keys if compromised

❌ **DON'T:**

- Commit `.env` files to version control
- Share `service_role` key publicly
- Hardcode credentials in source code
- Use `service_role` key in client applications

### Row Level Security (RLS)

- Always enable RLS on tables with sensitive data
- Create specific policies for different access patterns
- Test policies thoroughly before production
- Use `service_role` to bypass RLS for admin operations

### API Keys

- Store Supabase keys securely (environment variables, secrets manager)
- Never log or display full API keys
- Implement rate limiting on public endpoints
- Monitor API usage for suspicious activity

## Advanced Configuration

### Custom Tables

You can extend the schema with custom tables:

```sql
-- Example: License activation history
CREATE TABLE activation_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    license_key TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('activated', 'deactivated')),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
```

### Analytics Queries

Query usage statistics:

```sql
-- Total conversions per license
SELECT
    license_key,
    COUNT(*) as total_conversions,
    COUNT(DISTINCT conversion_type) as unique_types
FROM license_usage
GROUP BY license_key;

-- Usage over time
SELECT
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as conversions
FROM license_usage
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date;
```

## Monitoring

### Dashboard

Create a monitoring dashboard in Supabase:

1. Go to **Database** → **Extensions**
2. Enable `pg_stat_statements` for query monitoring
3. Set up alerts for:
   - Failed license activations
   - High usage rates
   - Suspicious activation patterns

### Logs

Check Supabase logs:

1. Go to **Logs** in Supabase dashboard
2. Filter by **Postgres Logs** for database errors
3. Check **API Logs** for request patterns

## Next Steps

- [Set up Gumroad webhook](./GUMROAD_SETUP_GUIDE.md) for automated license
  delivery
- [Configure email notifications](./EMAIL_NOTIFICATIONS.md) for license events
- [Deploy webhook server](../scripts/licensing/gumroad/README.md) for production
  use

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review Supabase documentation: https://supabase.com/docs
3. Check application logs: `logs/python/app_session_*.log`
4. Open an issue on GitHub with logs and error messages

---

**Last Updated:** November 2025 **Supabase Version:** Compatible with all
Supabase versions
