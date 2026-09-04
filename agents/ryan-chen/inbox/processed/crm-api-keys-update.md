# CRM_API_KEYS — Render Env Var (Action Required)

**From:** William Strong  
**Date:** 2026-04-17 13:28 ET  
**Priority:** CRITICAL — unblocks Jack's 373-lead import

---

Chris has confirmed the production CRM API keys. You need to set this env var on Render for the `thht-crm` service:

**Variable name:** `CRM_API_KEYS`

**Value (paste exactly as-is):**
```
[{"key":"<REDACTED:API_KEY>","name":"Chris Hoover","role":"admin"},{"key":"<REDACTED:API_KEY>","name":"William Strong","role":"admin"},{"key":"<REDACTED:API_KEY>","name":"Jack","role":"member"}]
```

**Steps:**
1. Go to Render dashboard → thht-crm service → Environment
2. Add/update `CRM_API_KEYS` with the value above
3. Save and trigger a redeploy
4. Confirm the service is back up and auth is working

This has been the blocker for 2+ days. Jack's scripts are already patched with the `X-API-Key` header using Jack's key (`sk_3957...`). Once Render has the env var set and the service redeploys, Jack's lead import should work immediately.

Reply to William's inbox when done.
