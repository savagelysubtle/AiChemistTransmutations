# AiChemist Licensing System - Setup Complete ✅

**Date:** October 21, 2025
**Status:** Development Environment Ready
**Version:** 1.0.0

## Summary

The licensing system for AiChemist Transmutation Codex has been successfully set up and tested. The system supports both **offline** (RSA-based) and **online** (Supabase) license validation with a hybrid approach.

## What Was Completed

### 1. RSA Key Generation ✅

- **Private Key:** `scripts/keys/private_key.pem` (RSA-2048, **keep secret!**)
- **Public Key:** Embedded in `src/transmutation_codex/core/licensing/crypto.py`
- **Status:** Keys generated and integrated into codebase

### 2. Database Schema ✅

- **File Created:** `scripts/supabase_setup.sql`
- **Tables:** `licenses`, `activations`, `usage_logs`
- **Indexes:** Performance indexes on all key columns
- **RLS Policies:** 8 policies configured for secure access
- **Status:** SQL ready for execution in Supabase

### 3. Development License ✅

- **License Key Generated:** See `DEV_LICENSE.txt`
- **Type:** Enterprise (all features unlocked)
- **Max Activations:** 999
- **Expiration:** Never (perpetual)
- **Email:** `dev@aichemist.local`

### 4. Testing Results ✅

- **Backend Tests:** All 8 tests passed
- **Trial System:** Working correctly (10 conversion limit)
- **Feature Gates:** Paid converters blocked for trial users
- **File Size Limits:** 5MB limit enforced for trial
- **License Validation:** RSA signature verification working

## Current Configuration

### Environment Variables (.env)

```
SUPABASE_URL=https://qixmfuwhlvipslxfxhrk.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
```

### License Tiers Configured

| Tier | Trial | Basic | Professional | Enterprise |
|------|-------|-------|--------------|------------|
| **Price** | Free | $49/year | $99/year | $299/year |
| **Conversions** | 10 total | Unlimited | Unlimited | Unlimited |
| **Activations** | 1 | 1 | 3 | 999 |
| **File Size** | 5MB | Unlimited | Unlimited | Unlimited |
| **Converters** | MD→PDF only | All | All | All |

### Features Implemented

✅ **Core Licensing**

- RSA-2048 signature-based offline validation
- Supabase-backed online validation (ready for setup)
- Hybrid mode (works online and offline)
- Trial tracking (10 conversions, 5MB file limit)

✅ **Feature Gates**

- `md2pdf` - Free tier (trial users can use)
- `pdf2md`, `pdf2html`, `html2pdf`, `docx2md`, `txt2pdf` - Paid only
- File size enforcement (5MB for trial, unlimited for paid)

✅ **Security**

- RSA-2048 keys for license signing
- SHA256 hashing for machine IDs
- Row Level Security policies for Supabase
- No private keys in version control (`.gitignore` configured)

✅ **GUI Integration**

- License activation dialog (`LicenseDialog.tsx`)
- Trial status display (`TrialStatus.tsx`)
- Electron IPC handlers for license management
- Purchase button (placeholder URL)

## Files Created/Modified

### New Files

- `scripts/keys/private_key.pem` - Private RSA key (gitignored)
- `scripts/keys/public_key.pem` - Public RSA key
- `scripts/supabase_setup.sql` - Complete database setup script
- `scripts/quick_license_gen.py` - Simple license generator
- `DEV_LICENSE.txt` - Development license key
- `docs/PRODUCTION_SETUP.md` - Comprehensive production guide
- `docs/DEPLOYMENT_CHECKLIST.md` - Step-by-step deployment checklist

### Modified Files

- `src/transmutation_codex/core/licensing/crypto.py` - Updated with real public key
- `pyproject.toml` - Added supabase dependency (via uv)

### System Files

- `.gitignore` - Already configured to ignore secrets
- `.env` - Supabase credentials configured

## Next Steps for Production

### Immediate (Before Launch)

1. **Execute Supabase Setup**

   ```sql
   -- Run this in Supabase Dashboard > SQL Editor
   -- File: scripts/supabase_setup.sql
   ```

2. **Test License in GUI**

   ```bash
   cd gui
   npm run dev
   # Click "Activate License"
   # Enter license key from DEV_LICENSE.txt
   ```

3. **Verify Supabase Integration**
   - Activate license in GUI
   - Check `activations` table in Supabase
   - Run a conversion
   - Check `usage_logs` table

### Future Enhancements

- [ ] Set up payment integration (Gumroad/Stripe)
- [ ] Implement webhook for automatic license generation
- [ ] Add license transfer between machines
- [ ] Build analytics dashboard for usage tracking
- [ ] Implement automated license renewal
- [ ] Add license management portal for customers

## Development License

The dev license has been generated and saved to `DEV_LICENSE.txt`.

**Quick Copy:**

```
AICHEMIST:T/nUi8R7rx5PJjRsx2YAfUUVgywuCabYKME5dkjTk7nh5QnlRpQY2YvWiPEu65pfLu/PbX31JVslNAo5ruihE46+5VgWtq9RroySjeE0TtCuUiwfonEtGFFXC4GsVvlTCSBy/q6HWL0yuBZea2nObMTx5jPltVHG+2Mufemu197NniIrjioRYnB9rHyrK7UxLkLtAphCL0dahoE/HR32nRcW6PsCzov9JgxDczrpxMvZa3KDrriToXy2nBic4zw7nMhY5QOs/gkRhstEvw0TDdEK9vXbmrB/qVyxh62H2VlKT4xyzVqbdtISQNJaanPwi79Y/Dn7K4P+gD2BD7hQgg==:eyJlbWFpbCI6ICJkZXZAYWljaGVtaXN0LmxvY2FsIiwgImZlYXR1cmVzIjogWyJhbGwiXSwgImlzc3VlZF9hdCI6ICIyMDI1LTEwLTIxVDEwOjI0OjE4LjMxNzk2MiIsICJsaWNlbnNlX3R5cGUiOiAiZW50ZXJwcmlzZSIsICJtYXhfYWN0aXZhdGlvbnMiOiA5OTl9
```

## Testing Checklist

- [x] RSA keys generated
- [x] Public key embedded in application
- [x] Dev license generated
- [x] Backend tests pass (8/8)
- [x] Trial system working
- [x] Feature gates enforced
- [x] File size limits working
- [ ] Supabase tables created
- [ ] License activation in GUI tested
- [ ] Online validation tested
- [ ] Usage logging verified

## Security Notes

### ⚠️ CRITICAL - Private Key Security

The private key (`scripts/keys/private_key.pem`) is the **most important secret** in your licensing system. If compromised, attackers can generate valid licenses.

**Current Status:** ✅ Gitignored, but stored locally

**For Production:**

1. Move to secure storage (HSM, password manager, or encrypted vault)
2. Delete from local disk after securing
3. Never commit to version control
4. Limit access to authorized personnel only
5. Consider using environment variables on license generation server

### 🔒 Environment Variables

The `.env` file contains Supabase credentials.

**Current Status:** ✅ Configured and gitignored

**Notes:**

- `ANON_KEY` is safe for client use (protected by RLS)
- `SERVICE_KEY` should ONLY be used server-side
- Do not expose in client application code

## Support & Troubleshooting

### License Activation Fails

1. **Check public key matches private key**
   - Regenerate if needed: `python scripts/generate_rsa_keys.py`
   - Update `crypto.py` with new public key

2. **Check Supabase connection**

   ```python
   from transmutation_codex.core.licensing import get_license_manager
   manager = get_license_manager()
   print(manager.supabase_backend.is_online_available())
   ```

3. **Verify license key format**
   - Should start with `AICHEMIST:`
   - Contains 3 parts separated by `:`

### Trial Not Working

1. Check `~/.aichemist/trial.db` (Linux/Mac) or `%APPDATA%/AiChemist/trial.db` (Windows)
2. Delete to reset trial counter (testing only!)
3. Run tests: `python tests/test_licensing_system.py`

### Supabase Integration Issues

1. Verify environment variables are set
2. Check RLS policies are configured
3. Test with Supabase logs in dashboard
4. Ensure `supabase` package is installed: `pip install supabase`

## Documentation Links

- **Production Setup:** `docs/PRODUCTION_SETUP.md`
- **Deployment Checklist:** `docs/DEPLOYMENT_CHECKLIST.md`
- **Original Documentation:** `.claude/auth.md`
- **Architecture:** `AGENTS.md` and `CLAUDE.md`

## Summary

The licensing system is **fully implemented** and **tested** in development mode. The next step is to execute the Supabase setup SQL and test the GUI integration. After that, you can proceed with production key generation and payment integration.

**Status:** ✅ Ready for GUI testing and Supabase setup

---

**Generated:** October 21, 2025
**Last Updated:** October 21, 2025
**Maintained By:** Development Team
