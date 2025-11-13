# Supabase Quick Reference

## 🔗 Connection Details

```env
SUPABASE_URL=https://qixmfuwhlvipslxfxhrk.supabase.co
SUPABASE_ANON_KEY=<configured_in_env_files>
```

## 📊 Database Schema

### Table: `gumroad_licenses`

| Column                | Type        | Description                           |
| --------------------- | ----------- | ------------------------------------- |
| `id`                  | UUID        | Primary key                           |
| `license_key`         | TEXT        | Gumroad license key (unique)          |
| `gumroad_purchase_id` | TEXT        | Purchase ID from Gumroad              |
| `gumroad_product_id`  | TEXT        | Product ID (E7oYHqtGSVBBWcpbCFyF-A==) |
| `tier`                | TEXT        | basic / pro / enterprise              |
| `email`               | TEXT        | Customer email                        |
| `purchase_date`       | TIMESTAMPTZ | When purchased                        |
| `activation_date`     | TIMESTAMPTZ | When activated in app                 |
| `machine_id`          | TEXT        | Hashed machine fingerprint            |
| `gumroad_data`        | JSONB       | Full Gumroad API response             |
| `status`              | TEXT        | active / revoked / expired            |
| `max_activations`     | INTEGER     | Activation limit for tier             |

### Table: `license_usage`

| Column            | Type        | Description           |
| ----------------- | ----------- | --------------------- |
| `id`              | UUID        | Primary key           |
| `license_key`     | TEXT        | Reference to license  |
| `machine_id`      | TEXT        | Which machine         |
| `conversion_type` | TEXT        | md2pdf, pdf2md, etc.  |
| `file_size_bytes` | BIGINT      | Input file size       |
| `success`         | BOOLEAN     | Conversion succeeded? |
| `timestamp`       | TIMESTAMPTZ | When it happened      |

## 🔍 Useful Queries

### View All Activations

```sql
SELECT
  license_key,
  email,
  tier,
  status,
  machine_id,
  activation_date
FROM gumroad_licenses
ORDER BY activation_date DESC;
```

### Count Activations by Tier

```sql
SELECT
  tier,
  COUNT(*) as count,
  COUNT(DISTINCT machine_id) as unique_machines
FROM gumroad_licenses
GROUP BY tier;
```

### Today's Conversions

```sql
SELECT
  conversion_type,
  COUNT(*) as count,
  SUM(file_size_bytes) as total_bytes
FROM license_usage
WHERE DATE(timestamp) = CURRENT_DATE
GROUP BY conversion_type;
```

### Top Users by Usage

```sql
SELECT
  license_key,
  COUNT(*) as conversions,
  SUM(file_size_bytes) as total_data_processed
FROM license_usage
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY license_key
ORDER BY conversions DESC
LIMIT 10;
```

### Recent Errors

```sql
SELECT
  license_key,
  conversion_type,
  timestamp
FROM license_usage
WHERE success = false
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

## 🛠️ Management Tasks

### Check License Status

```sql
SELECT * FROM gumroad_licenses
WHERE license_key = 'YOUR-LICENSE-KEY';
```

### Revoke a License

```sql
UPDATE gumroad_licenses
SET status = 'revoked'
WHERE license_key = 'LICENSE-TO-REVOKE';
```

### View Machine Activations

```sql
SELECT
  license_key,
  COUNT(DISTINCT machine_id) as active_machines,
  max_activations
FROM gumroad_licenses
GROUP BY license_key, max_activations
HAVING COUNT(DISTINCT machine_id) >= max_activations;
```

## 🔐 Row Level Security

All tables have RLS enabled with service role access:

```sql
-- Policy allows full access for service role
CREATE POLICY "Service role has full access"
ON table_name
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
```

## 📍 Dashboard Links

- **Project:** https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk
- **Table Editor:**
  https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk/editor
- **SQL Editor:**
  https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk/sql
- **Logs:**
  https://supabase.com/dashboard/project/qixmfuwhlvipslxfxhrk/logs/explorer

## 🐍 Python Access

The app automatically uses Supabase when environment variables are set:

```python
from transmutation_codex.core.licensing import SupabaseBackend

# Initialized automatically in LicenseManager
backend = SupabaseBackend()

# Records activation
backend.record_gumroad_activation(
    license_key="ABC-123",
    gumroad_data={...},
    tier="basic"
)

# Logs usage
backend.log_gumroad_usage(
    license_key="ABC-123",
    conversion_type="md2pdf",
    file_size=1024,
    success=True
)
```

## ⚡ Quick Checks

### Is Supabase Working?

Check app console logs for:

```
[LICENSE_BRIDGE] INFO: SUPABASE_URL: ***set***
[LICENSE_BRIDGE] INFO: ✓ Supabase backend initialized
```

### View Recent Activity

```sql
-- Last 10 actions
(SELECT 'activation' as type, activation_date as timestamp, license_key, tier
 FROM gumroad_licenses
 ORDER BY activation_date DESC LIMIT 10)
UNION ALL
(SELECT 'usage' as type, timestamp, license_key, conversion_type
 FROM license_usage
 ORDER BY timestamp DESC LIMIT 10)
ORDER BY timestamp DESC;
```

---

**Quick Reference Version:** 1.0 **Last Updated:** November 13, 2025
