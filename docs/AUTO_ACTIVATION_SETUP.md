# Auto-Activation of Developer License

## Overview

The application is now configured to automatically retrieve and activate the developer license from Supabase when running in development mode. This eliminates the need to manually activate the license on each fresh setup.

## How It Works

### 1. Development Mode Detection

The system automatically detects development mode by checking:
- `DEV_MODE=true` in `.env` file
- `NODE_ENV=development` environment variable
- Presence of `SUPABASE_URL` in `.env` (indicates Supabase integration)

### 2. License Retrieval from Supabase

When running in development mode, the application:
1. Connects to Supabase using credentials from `.env`
2. Queries the `licenses` table for `dev@aichemist.local`
3. Retrieves the license key

### 3. Automatic Activation

The license is automatically activated if:
- Not already activated for this machine
- Supabase connection is available
- Developer license exists in database

## Usage

### Running the GUI with Auto-Activation

**Option 1: Using batch file**
```batch
run-gui.bat
```

**Option 2: Using Python startup script**
```batch
start_app.bat
```

**Option 3: Using VS Code task**
- Press `Ctrl+Shift+P`
- Select `Tasks: Run Task`
- Choose `Run GUI (Bun)`

### Standalone Auto-Activation

To manually test auto-activation:
```bash
python scripts/auto_activate_dev_license.py
```

## Configuration

### .env File

The `.env` file is pre-configured with:
```env
# Development Mode - Set to true to auto-activate developer license on startup
DEV_MODE=true

# Supabase Project URL
SUPABASE_URL=https://qixmfuwhlvipslxfxhrk.supabase.co

# Supabase Anonymous Key (Public Key)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Developer License in Supabase

The developer license is stored in Supabase:
- **Email**: `dev@aichemist.local`
- **Type**: Perpetual
- **Status**: Active
- **Features**: Full access to all premium features

## What Happens on Startup

When you run `run-gui.bat` or `start_app.bat`:

```
🚀 AiChemist Transmutation Codex
========================================

🔑 Auto-activating developer license...
✅ Developer license already active    (or)
✅ Developer license activated
   Email: dev@aichemist.local
   Type: Perpetual

🔍 Checking dependencies...
✅ All dependencies available

🚀 Launching GUI...
```

## Files Modified

### Batch Files
- **`run-gui.bat`**: Calls auto-activation before starting GUI
- **`start_app.bat`**: Includes auto-activation in startup flow

### Python Scripts
- **`scripts/auto_activate_dev_license.py`**: Standalone auto-activation script
- **`scripts/start_app.py`**: Integrated auto-activation into main startup

### Configuration
- **`.env`**: Added `DEV_MODE=true` flag

### GUI Integration
The GUI already has license status checking via `TrialStatus.tsx`:
- Automatically checks license status on startup
- Displays license information in the header
- Refreshes every 30 seconds
- Shows perpetual license status

## Benefits

1. **Zero Manual Setup**: License activates automatically
2. **Fresh Installs**: Works immediately after cloning and configuring `.env`
3. **Team Development**: All team members get dev license automatically
4. **CI/CD Ready**: Can be integrated into automated testing pipelines
5. **Supabase Integration**: Always uses the latest license from cloud

## Troubleshooting

### License Not Activating

Check the following:
1. **Supabase connection**: Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
2. **Dev mode**: Ensure `DEV_MODE=true` in `.env`
3. **License exists**: Check Supabase dashboard that `dev@aichemist.local` license exists
4. **Network**: Ensure internet connection for Supabase access

### Manual Activation

If auto-activation fails, you can still manually activate:
```bash
python -c "from transmutation_codex.core.licensing import activate_license_key; status = activate_license_key('YOUR-LICENSE-KEY'); print(status)"
```

### Check Current License Status

```bash
python -c "from transmutation_codex.core.licensing import get_full_license_status; import json; print(json.dumps(get_full_license_status(), indent=2))"
```

## Security Notes

- **Development Only**: Auto-activation is only enabled in development mode
- **Production Safe**: Production builds will not auto-activate
- **Secure Keys**: The `ANON_KEY` is public and safe to commit (protected by RLS)
- **Service Key**: Never commit `SUPABASE_SERVICE_KEY` (only needed for admin operations)

## Next Steps

The application is now fully integrated with Supabase for:
- ✅ License management
- ✅ Auto-activation in dev mode
- ✅ Online validation
- ✅ Usage tracking
- ✅ Activation management

Ready to start development with full premium features!

