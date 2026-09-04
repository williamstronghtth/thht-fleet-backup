# Task: Prospect Intelligence Engine — Phase 1 (Lead Enrichment)

**From:** William Strong  
**Date:** 2026-06-02  
**Priority:** HIGH — Chris has greenlit this, start now

---

## The Big Picture

We're building a Prospect Intelligence Engine directly into the CRM. When a lead is added, we automatically enrich their profile with social/public data. Then a background system monitors that data and fires Telegram alerts to Chris the moment there's a meaningful reason to reach out — with a suggested message already drafted.

This is the feature that makes every outreach feel personal and timely instead of cold.

**Build in phases. Phase 1 is your mission today.**

---

## Phase 1: Lead Enrichment (on lead creation)

### Goal
When a new lead is created in the CRM, automatically kick off an enrichment job that populates their profile with social links, property data, and public record info.

### New Fields to Add to the `clients` Table (Supabase)

Run a Supabase migration to add these columns (all nullable):

```sql
ALTER TABLE clients ADD COLUMN IF NOT EXISTS linkedin_url TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS instagram_url TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS facebook_url TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS birthday DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS home_address TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS home_purchase_date DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS estimated_home_value INTEGER;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS enrichment_status TEXT DEFAULT 'pending'; -- pending | complete | failed
ALTER TABLE clients ADD COLUMN IF NOT EXISTS enriched_at TIMESTAMPTZ;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS enrichment_notes TEXT; -- any notes/failures
```

### Enrichment Service

Create a new file: `services/enrichment-service.js`

**What it does:**
1. Takes a client object `{ id, name, email, phone, city, state }`
2. Performs a series of lookups (see below)
3. Updates the client record in Supabase with whatever it finds
4. Sets `enrichment_status = 'complete'` and `enriched_at = now()`

**Lookups to implement (Phase 1 — keep it simple):**

#### A. LinkedIn URL Search
- Use Google Custom Search API or a simple web search to find their LinkedIn profile
- Query: `site:linkedin.com/in "[First Name] [Last Name]" "[City]"`
- Store the first result URL in `linkedin_url`
- API: Google Custom Search JSON API (free tier: 100 queries/day — plenty for now)
- Key goes in `.env` as `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX`

#### B. Property Lookup (NH Assessor)
- For NH leads, use the town's public assessor data
- Start simple: query the Hillsborough County GIS or use Zillow's informal search
- Fetch: property address, estimated value, purchase/sale date
- Store in `home_address`, `estimated_home_value`, `home_purchase_date`
- If nothing found, leave null and note in `enrichment_notes`

#### C. Birthday / DOB (Stretch — skip if complex)
- Skip for now unless People Data Labs API is already available
- Leave `birthday` null — we'll populate manually or via Phase 3

### Trigger: Auto-Enrich on Lead Creation

In the existing `POST /api/clients` route, after successfully inserting the client:
- Fire the enrichment service **asynchronously** (don't await it — don't block the API response)
- Log that enrichment was kicked off
- The client is created instantly; enrichment runs in the background

```js
// After successful insert:
enrichClient(newClient).catch(err => 
  console.error(`Enrichment failed for ${newClient.id}:`, err)
);
```

### UI: Show Enrichment Status in Client Detail View

In the client detail page (`/client/:id`), add a small "Intelligence" section:
- Show enrichment status badge: `🔄 Pending` / `✅ Enriched` / `⚠️ Failed`
- If enriched: show LinkedIn link (clickable), home address, estimated value, purchase date
- If any fields are null: show "—" (not an error, just unknown)
- Keep it clean — this doesn't need to be fancy yet

---

## Telegram Alert Format (for Phase 2 — just build the template now)

When we build Phase 2, alerts will look like this. Build a `formatTouchpointAlert(prospect, signal, suggestedMessage)` utility function now so Phase 2 can just call it:

```
🔔 TOUCHPOINT ALERT — [Prospect Name]

📍 Signal: [What was detected]
📅 Detected: [Today's date]
💬 Suggested message:
"Hey [Name], [personalized opener based on trigger]..."

📎 CRM: https://clientlist.onrender.com/client/[id]
```

Put this in `services/telegram-alerts.js` (create new file).

---

## Env Vars Needed

Add to `.env` (and document in README or a SETUP note):
```
GOOGLE_SEARCH_API_KEY=
<REDACTED:CREDENTIAL>=
```

Let William know if you need help getting these API keys set up.

---

## Deliverables for Phase 1

- [ ] Supabase migration: new enrichment columns on `clients` table
- [ ] `services/enrichment-service.js` — LinkedIn + property lookup
- [ ] `services/telegram-alerts.js` — alert formatter utility
- [ ] `POST /api/clients` updated to fire async enrichment
- [ ] Client detail UI updated with Intelligence section
- [ ] Push to main → Render auto-deploy

When done, message William Strong (run-agent.sh main) with a summary of what was built and any API keys or setup steps Chris needs to take.

---

## Phase 2 Preview (next task, not now)

Phase 2 is a weekly cron job that scans all enriched clients and fires alerts:
- Birthday in X days → touchpoint alert
- Home anniversary → touchpoint alert  
- LinkedIn job change → touchpoint alert
- Equity milestone (Zillow AVM vs. purchase price >20% gain) → touchpoint alert

Full spec in `/root/agents/william-strong/workspace/FEATURE-IDEAS.md`

Focus on Phase 1 first. Ship it, then we'll hand you Phase 2.
