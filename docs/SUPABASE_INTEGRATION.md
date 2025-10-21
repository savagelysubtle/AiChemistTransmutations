# Supabase Integration for AiChemist Licensing System

This document describes the Supabase integration for cloud-based license validation, activation tracking, and usage analytics.

## Overview

The AiChemist Transmutation Codex licensing system supports two modes:

1. **Offline Mode** (default): RSA-based license validation with local storage
2. **Online Mode** (optional): Cloud-based validation via Supabase with analytics

The system uses a **hybrid approach**: it tries online validation first, then falls back to offline validation if Supabase is unavailable.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    License Manager                           │
│  (Coordinates all licensing operations)                      │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
    ┌───────────▼──────────┐      ┌──────────▼──────────┐
    │  Offline Validation  │      │  Online Validation  │
    │  (Always Available)  │      │  (If Configured)    │
    └──────────────────────┘      └─────────────────────┘
    │                             │
    │ - RSA Signature             │ - Supabase Database
    │ - Local Storage             │ - Remote Activation
    │ - Machine Binding           │ - Usage Analytics
    │                             │ - Revocation Support
    └─────────────────────────────┴─────────────────────┘
                         │
              ┌──────────▼───────────┐
              │   Cached Results     │
              │ (24-hour TTL cache)  │
              └──────────────────────┘
```

## Database Schema

The Supabase database contains three main tables:

### `licenses` Table

Stores license key records with type and status.

```sql
CREATE TABLE licenses (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    license_key TEXT NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('trial', 'basic', 'professional', 'enterprise')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'revoked', 'expired')),
    max_activations INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**Columns:**
- `id`: Unique identifier
- `email`: License holder email
- `license_key`: Signed RSA license key
- `type`: License tier (trial, basic, professional, enterprise)
- `status`: Current status (active, suspended, revoked, expired)
- `max_activations`: Maximum number of machines
- `expires_at`: Expiration date (NULL for perpetual)

### `activations` Table

Tracks machine activations for each license.

```sql
CREATE TABLE activations (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    machine_id VARCHAR(255) NOT NULL,
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT unique_activation UNIQUE(license_id, machine_id)
);
```

**Columns:**
- `machine_id`: SHA256 hash of machine fingerprint
- `activated_at`: Initial activation timestamp
- `last_seen_at`: Last validation check

### `usage_logs` Table

Records conversion usage for analytics.

```sql
CREATE TABLE usage_logs (
    id BIGSERIAL PRIMARY KEY,
    license_id BIGINT NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    converter_name VARCHAR(100) NOT NULL,
    input_file_size BIGINT NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);
```

## Setup Instructions

### 1. Create Supabase Project

1. Go to https://supabase.com
2. Create a new project
3. Note your project URL and API keys

### 2. Setup Database Schema

Run the schema setup script:

```bash
python scripts/setup_supabase_schema.py
```

This will print SQL statements. Copy and execute them in your Supabase SQL Editor:
- Supabase Dashboard → SQL Editor → New Query → Paste SQL → Run

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**Find your credentials:**
- Supabase Dashboard → Settings → API
- Project URL: Copy from "Project URL"
- Anon Key: Copy from "Project API keys" → `anon` `public`

### 4. Install Dependencies

```bash
pip install supabase python-dotenv
```

Or using the project:

```bash
pip install -e ".[dev]"
```

### 5. Generate Developer License

Create a lifetime developer license:

```bash
python scripts/generate_dev_license.py
```

This creates:
- A perpetual enterprise license for `dev@aichemist.local`
- 999 max activations
- All features unlocked
- RSA key pair (if not exists) in `.keys/`
- License details saved to `.licenses/dev_license.txt`

**Important:** The license key will be printed to console AND inserted into Supabase.

### 6. Verify Setup

Test that everything works:

```python
from transmutation_codex.core.licensing import get_license_manager

manager = get_license_manager()

# Check if online mode is available
if manager.supabase_backend:
    print("✓ Online mode active")
    print(f"  Backend available: {manager.supabase_backend.is_online_available()}")
else:
    print("✓ Offline mode (Supabase not configured)")

# Get license status
status = manager.get_license_status()
print(f"License type: {status['license_type']}")
```

## Usage

### Activating a License

```python
from transmutation_codex.core.licensing import get_license_manager

manager = get_license_manager()

# Activate license (tries online first, falls back to offline)
license_key = "AICHEMIST:BASE64_SIGNATURE:BASE64_DATA"
status = manager.activate_license(license_key)

print(f"Activated: {status['activated']}")
print(f"Mode: {status.get('validation_mode', 'unknown')}")
```

### Recording Conversions

```python
# Record a conversion
manager.record_conversion(
    converter_name="md2pdf",
    input_file="/path/to/input.md",
    output_file="/path/to/output.pdf",
    file_size_bytes=1024000,
    success=True
)
```

**Behavior:**
- **Trial users**: Recorded locally in SQLite for trial tracking
- **Paid users (online)**: Logged to Supabase for analytics
- **Paid users (offline)**: No logging (unlimited local use)

### Checking License Status

```python
status = manager.get_license_status()

if status['license_type'] == 'paid':
    print(f"Licensed to: {status['email']}")
    print(f"Validation mode: {status.get('validation_mode')}")
elif status['license_type'] == 'trial':
    trial = status['trial_status']
    print(f"Trial: {trial['remaining']}/{trial['limit']} conversions left")
```

### Deactivating a License

```python
# Deactivate on current machine
manager.deactivate_license()

# Deactivate remotely (online mode only)
if manager.supabase_backend:
    license_id = 123  # From database
    success, msg = manager.supabase_backend.deactivate_machine(license_id)
    print(msg)
```

## API Reference

### `SupabaseBackend` Class

#### `validate_license_online(license_key: str) -> tuple[bool, dict | None, str]`

Validate license against Supabase database.

**Returns:**
- `bool`: Whether license is valid
- `dict | None`: License data if valid
- `str`: Reason/message

**Example:**
```python
valid, data, reason = backend.validate_license_online("AICHEMIST-...")
if valid:
    print(f"Valid license for {data['email']}")
```

#### `record_activation(license_id: int, machine_id: str | None) -> tuple[bool, str]`

Record a license activation.

**Returns:**
- `bool`: Success status
- `str`: Message

#### `log_usage(license_id: int, converter_name: str, input_file_size: int, success: bool) -> bool`

Log a conversion usage event.

#### `check_license_status(license_key: str) -> dict`

Get comprehensive license status including activation count and usage stats.

#### `get_activation_list(license_id: int) -> list[dict]`

Get list of all machines with this license activated.

## License Types

| Type         | Max Activations | Converters | File Size | Expiry    |
|--------------|-----------------|------------|-----------|-----------|
| trial        | 1               | md2pdf only| 5 MB      | 10 conversions |
| basic        | 1               | All        | Unlimited | 1 year    |
| professional | 3               | All        | Unlimited | 1 year    |
| enterprise   | 999             | All        | Unlimited | Perpetual |

## Developer License

The generated dev license has these properties:

```json
{
  "email": "dev@aichemist.local",
  "type": "enterprise",
  "max_activations": 999,
  "expires_at": null,
  "status": "active",
  "features": ["all"]
}
```

**Use this for:**
- Development and testing
- Internal team usage
- CI/CD pipelines
- Demo environments

**Do not:**
- Share publicly
- Use in production for customers
- Distribute with releases

## Offline vs Online Mode Comparison

| Feature              | Offline Mode      | Online Mode       |
|----------------------|-------------------|-------------------|
| License Validation   | RSA signature     | Supabase DB       |
| Activation Limit     | Local check       | Remote enforcement|
| Usage Analytics      | None (paid users) | Full tracking     |
| License Revocation   | Not supported     | Instant           |
| Multi-device Sync    | No                | Yes               |
| Requires Internet    | No                | Yes (with cache)  |
| Offline Grace Period | N/A               | 24 hours (cached) |

## Troubleshooting

### "Supabase credentials not configured"

**Solution:**
1. Ensure `.env` file exists in project root
2. Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set
3. Verify `.env` is not in `.gitignore` (it should be!)

### "supabase-py is not installed"

**Solution:**
```bash
pip install supabase
```

### Online validation fails, offline works

**Expected behavior** - the system is designed to fall back to offline mode.

**To debug:**
```python
backend = SupabaseBackend()
print(f"Online available: {backend.is_online_available()}")
```

### License activates but usage not logged

**Check:**
1. License includes `id` field (from Supabase)
2. `license_key` is stored in activated license
3. Supabase backend is initialized

## Security Notes

1. **ANON_KEY is safe** for client use (protected by Row Level Security)
2. **SERVICE_KEY must never** be exposed in client code
3. **Private RSA key** (`.keys/private_key.pem`) must be kept secret
4. **License keys** are cryptographically signed and cannot be forged
5. **Machine IDs** are one-way hashed (SHA256)

## Migration from Offline-Only

If you have existing offline licenses:

1. Generate RSA keys (if not exists)
2. Set up Supabase database
3. Import existing licenses into `licenses` table
4. Users re-activate with same license key
5. System auto-detects online mode

No code changes needed - the hybrid system handles both modes transparently.

## Future Enhancements

- [ ] Automatic license renewal via Stripe integration
- [ ] License transfer between machines
- [ ] Usage-based billing
- [ ] Multi-tenant organization support
- [ ] License analytics dashboard
- [ ] Automated trial-to-paid upgrade

## Support

For issues or questions:
- Check logs in `~/.aichemist/` or `%APPDATA%/AiChemist/`
- Enable debug logging in LicenseManager
- Review Supabase logs in dashboard
