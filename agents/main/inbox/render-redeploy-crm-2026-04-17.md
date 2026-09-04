# Render Redeploy Needed — clientlist (thht-crm)

**From:** Ryan Chen  
**Date:** 2026-04-17 14:24 ET  
**Priority:** HIGH — Chris just restored Supabase, need redeploy to reconnect

---

Chris restored the Supabase project (thht-crm), but the Render service still has a stale connection — `/api/status` shows "Supabase unreachable — serving from cache" with 0 clients.

**Action needed:** Trigger a manual redeploy on Render for the `clientlist` service.

**Steps:**
1. Go to Render dashboard → `clientlist` service
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait for deploy to complete (~1-2 min)
4. Verify: `curl https://clientlist.onrender.com/api/status` should show clients > 0

This will re-establish the Supabase connection and the 410+ clients should reappear.

**While you're there:** The `CRM_API_KEYS` env var from my earlier message still needs to be set too — that unblocks Jack's lead import.
