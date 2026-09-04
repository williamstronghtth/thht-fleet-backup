# Task: Debug + Fix Prospect Intelligence Enrichment (Phase 1)

**Priority:** HIGH  
**Date:** 2026-06-03

## Problem

The enrichment service is deployed (Phase 1 code is live) but **enrichment_status never changes from 'pending'** after triggering. The service endpoint responds, but Supabase writes are silently failing.

## What I've tested

1. Created test client `mpy81p8t4q29k` (Richard Keras, 17 Hillside Drive, Townsend MA 01469) via API
2. Called `POST /api/clients/mpy81p8t4q29k/enrich` → got `{ success: true, message: 'Enrichment started' }`
3. Polled `/api/clients/mpy81p8t4q29k/enrichment` for 2+ minutes → status stays `"pending"` (never moves to `"processing"`)

The enrichment service code is definitely deployed (the `/api/clients/:id/enrichment` endpoint is live). But the async writes to Supabase aren't happening.

## Most likely causes (check in this order)

### 1. Check Render logs for `[Enrichment]` lines
In Render dashboard → thht-crm service → Logs. Look for any of these:
- `[Enrichment] Starting enrichment for client mpy81p8t4q29k`
- `[Enrichment] No Supabase connection` ← this would be the smoking gun
- `[Enrichment] Status update failed`
- `[Enrichment] Unexpected failure`

### 2. The enrichment service uses a lazy-init Supabase client
In `services/enrichment-service.js`, the Supabase client is initialized separately from the main app's client. If `SUPABASE_URL` or `SUPABASE_ANON_KEY` aren't accessible at the time the enrichment fires, it silently returns without writing.

**Recommended fix:** Remove the lazy-init pattern and reuse the existing Supabase instance from `services/supabase.js` instead:

```js
// In enrichment-service.js, replace:
const { createClient } = require('@supabase/supabase-js');
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY;
let supabase = null;
function getSupabase() { ... }

// With:
const { supabase } = require('./supabase');
function getSupabase() { return supabase; }
```

### 3. RLS policy on UPDATE
The Supabase RLS policy we added allows all operations, but double-check:
- In Supabase dashboard → Authentication → Policies → `clients` table
- Verify there's a policy that covers UPDATE with `USING (true)` AND `WITH CHECK (true)` for both `anon` and `authenticated` roles

### 4. Column name mismatch
The enrichment service writes `estimated_home_value` but the old schema had `home_estimated_value`. Similarly `enriched_at` vs `enrichment_last_run`. Both columns now exist. Make sure enrichment is writing to the columns the API reads.

Current API reads (via `snakeToCamel`):
- `enrichment_status` → `enrichmentStatus` ✓
- `enrichment_notes` → `enrichmentNotes` ✓
- `enriched_at` → `enrichedAt` ✓ (new column from migration)
- `linkedin_url` → `linkedinUrl` ✓ (new column from migration)
- `estimated_home_value` → `estimatedHomeValue` ✓ (new column from migration)

These look aligned — but verify the columns exist in Supabase.

## Test client for debugging

Richard Keras (`mpy81p8t4q29k`) is in the CRM — reset his `enrichment_status` to `pending` before testing:

```bash
curl -s -X PUT "https://clientlist.onrender.com/api/clients/mpy81p8t4q29k" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <REDACTED:API_KEY>" \
  -d '{"enrichmentStatus": "pending", "enrichmentNotes": null}'
```

Then trigger enrichment:
```bash
curl -s -X POST "https://clientlist.onrender.com/api/clients/mpy81p8t4q29k/enrich" \
  -H "x-api-key: <REDACTED:API_KEY>"
```

Then watch Render logs in real time and verify the status changes.

## Success criteria

1. After triggering enrichment, `enrichmentStatus` changes to `"processing"` within 5 seconds
2. Within 30 seconds, `enrichmentStatus` changes to `"complete"` (or `"failed"` if Google API has issues)
3. `enrichmentNotes` shows what was found/not found
4. `linkedinUrl` may have a value if LinkedIn profile was found
5. `homeAddress` shows the normalized address

Once fixed, deploy and notify me (William). I'll do a final test with Richard Keras and report back to Chris.
