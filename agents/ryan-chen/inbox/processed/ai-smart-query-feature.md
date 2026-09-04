# Feature Brief: AI-Powered Smart Query for CRM
**From:** William Strong  
**To:** Ryan Chen  
**Date:** 2026-05-25  
**Priority:** Medium — Chris is interested, not urgent

---

## Background

Chris saw Supabase's AI-powered table filters feature and wants something similar in the CRM. The Supabase dashboard version is Studio-only (not an SDK feature), but we can build an equivalent "natural language → Supabase query" feature ourselves using Claude Haiku.

Current state: `getClients()` supports `stage`, `leadSource`, `leadType`, and basic text `search` (name/email/phone ilike). We need to add NL query support on top of that.

---

## What to Build

### 1. New API endpoint: `POST /api/smart-query`

Takes a plain English query, calls Claude Haiku to translate it into structured filter params, then runs `getClients()` with those params.

```javascript
// Request
POST /api/smart-query
{ "query": "show me Zillow leads that haven't been contacted in 30 days" }

// Response
{ "success": true, "data": [...clients], "parsedFilters": { leadSource: "Zillow", lastActivityBefore: "2026-04-25" } }
```

### 2. Enhance `getClients()` in `db.js`

Add these new filter params (currently missing):
- `lastActivityBefore` — filter by `last_activity < date` (ISO string)
- `followUpOverdue` — boolean, filter where `follow_up_date < today`
- `createdAfter` / `createdBefore` — date range on `created_at`
- `updatedAfter` — for "recently updated" queries

### 3. Claude Haiku prompt for NL → filters

Create `/services/smart-query.js`:

```javascript
const Anthropic = require('@anthropic-ai/sdk');

const SCHEMA_CONTEXT = `
CRM clients table schema:
- stage: "lead" | "active" | "contract" | "closed" | "past"
- lead_source: "Cold Calling" | "Letter" | "Sold.com" | "Close AI" | "OPCity" | "Qazzoo" | "KvCORE" | "CB Lead" | "Door Knocking" | "Buyers" | "Website Home Evaluation" | "EDDM" | "Renter" | "Open House" | "Other"
- lead_type: "warm" | "cold" | "divorce" | "probate" | "pre-foreclosure" | "expired" | "fsbo" | "investor" | "referral" | "sphere" | "other"
- client_type: "buyer" | "seller" | "both" | "investor" | "past"
- follow_up_date: ISO date string (YYYY-MM-DD)
- last_activity: ISO timestamp
- created_at: ISO timestamp
- Today's date: ${new Date().toISOString().split('T')[0]}
`;

const SYSTEM_PROMPT = `You translate natural language queries about a real estate CRM into structured JSON filter objects.
Return ONLY valid JSON with these possible keys: stage, leadSource, leadType, clientType, lastActivityBefore, followUpOverdue (bool), createdAfter, createdBefore, search.
If a filter doesn't apply, omit the key. Never include keys not in this list.`;

async function parseNaturalQuery(userQuery) {
  const client = new Anthropic();
  const msg = await client.messages.create({
    model: 'claude-haiku-4-5',
    max_tokens: 256,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: `${SCHEMA_CONTEXT}\nQuery: "${userQuery}"\nReturn JSON filters:` }]
  });
  return JSON.parse(msg.content[0].text);
}

module.exports = { parseNaturalQuery };
```

### 4. New route in `server.js`

```javascript
app.post('/api/smart-query', apiAuth, async (req, res) => {
  const { query } = req.body;
  if (!query) return res.status(400).json({ success: false, error: 'query is required' });
  
  try {
    const filters = await parseNaturalQuery(query);
    const clients = await db.getClients(filters);
    res.json({ success: true, data: clients, parsedFilters: filters, count: clients.length });
  } catch (err) {
    console.error('Smart query error:', err);
    res.status(500).json({ success: false, error: 'Failed to process query' });
  }
});
```

### 5. UI: Smart Search bar

Add an "AI Search" input to the main leads view (above the existing filter dropdowns). Simple toggle between normal search and AI search mode. On submit, hit `POST /api/smart-query` and render results. Show `parsedFilters` back to the user ("Showing: Zillow leads, last activity before Apr 25") so they can understand what was matched.

---

## Example Queries Chris Would Use

| Natural Language | Parsed Filters |
|---|---|
| "Zillow leads not contacted in 30 days" | `{ leadSource: "Zillow", lastActivityBefore: "2026-04-25" }` |
| "warm leads in active stage" | `{ leadType: "warm", stage: "active" }` |
| "closed deals this quarter" | `{ stage: "closed", createdAfter: "2026-04-01" }` |
| "overdue follow-ups" | `{ followUpOverdue: true }` |
| "cold calling leads from this month" | `{ leadSource: "Cold Calling", createdAfter: "2026-05-01" }` |
| "FSBO leads I haven't touched in 2 weeks" | `{ leadType: "fsbo", lastActivityBefore: "2026-05-11" }` |

---

## Env Var Required

`ANTHROPIC_API_KEY` — check if already set in Render env. If not, add it.

---

## Estimate

- `db.js` filter enhancements: ~1-2 hours
- `/services/smart-query.js`: ~1 hour  
- New route: 30 min
- UI search bar: ~2-3 hours
- Total: **~1 day of work**

Cost: Claude Haiku is ~$0.001 per query. Negligible.

---

## Not Doing (Scope Cuts)

- No pgvector / embeddings — overkill for 400 leads
- No streaming — simple request/response is fine
- No query history persistence (can add later)

---

Hold off on starting until Chris gives the green light. This is exploratory for now.
