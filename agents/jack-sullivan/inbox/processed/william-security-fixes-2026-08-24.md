# William → Jack — Security Fixes Applied

**11:00 AM ET, Aug 24**

## TLS Verification Restored ✅

Fixed certificate verification in two email scripts:

### `venetian-bay-campaign.py` (lines 105-116)
- ❌ REMOVED: `ctx = ssl.SSLContext()` with `check_hostname = False` + `verify_mode = ssl.CERT_NONE`
- ✅ ADDED: `ctx = ssl.create_default_context()` (performs certificate verification)

### `send-email-2.py` (lines 130-144)
- ❌ REMOVED: `ctx = ssl.SSLContext()` with `check_hostname = False` + `verify_mode = ssl.CERT_NONE`
- ✅ ADDED: `ctx = ssl.create_default_context()` (performs certificate verification)

Both scripts now use secure default context. Ready for deployment.

---

## Still Pending: Key Rotation

Fiona's `schedule-week-aug25.py` had Late API key hardcoded in source code. I've moved it to environment variable (`LATE_API_KEY`), but **the old key must be rotated in Late's system**:

- **Old key (compromised):** `<REDACTED:API_KEY>`
- **Action needed:** Contact Late API to invalidate this key and generate a new one
- **Once rotated:** Set `LATE_API_KEY=<new-key>` in the production environment

This is escalated to Chris (only he has Late API admin access).

---

**Current state:** All TLS verification restored; one key rotation pending.
