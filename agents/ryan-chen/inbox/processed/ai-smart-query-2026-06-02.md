# AI Smart Query — GO ✅

**From:** William Strong  
**Date:** 2026-06-02 19:51 ET  
**Priority:** High — Chris approved, build ASAP

---

## What to Build

A natural language search bar in the CRM leads view. User types something like:

> "Zillow leads I haven't contacted in 30 days"

...and it uses Claude Haiku to translate that into structured filters, then queries Supabase. Returns results with a plain-English summary of what was matched.

---

## Spec

### Backend — new endpoint

```
POST /api/smart-query
Body: { query: "natural language string" }
```

1. Send `query` to Claude Haiku with a system prompt that extracts structured filters:
   - `source` (Zillow, Realtor.com, manual, etc.)
   - `lastContactedBefore` (ISO date)
   - `lastContactedAfter` (ISO date)
   - `status` (active, inactive, closed, etc.)
   - `tags` (array)
   - `city`, `state`
   - `hasNotes` (boolean)
   - Any other fields that make sense from the clients table

2. Pass extracted filters to an enhanced `getClients()` function
3. Return `{ success: true, data: clients[], summary: "Found 12 Zillow leads not contacted since May 3" }`

### Frontend — AI Search bar in leads view

- Toggle button: "🔍 Smart Search" (shows/hides the AI bar)
- Textarea or input: "Ask anything about your leads..."
- Submit button → hits `/api/smart-query`
- Shows results in the existing leads table
- Shows the plain-English `summary` above the results
- Loading state while Haiku processes

---

## Cost

Claude Haiku: ~$0.001 per query. Basically free.

---

## Environment

Add to `.env`:
```
ANTHROPIC_API_KEY=<already set on Render if used elsewhere, check first>
```

Use `@anthropic-ai/sdk` — already in the codebase likely. If not, `npm install @anthropic-ai/sdk`.

---

## Notes

- Follow existing code patterns (Express 5, vanilla JS, Supabase)
- Return consistent `{ success, data, error }` shape
- Validate that `query` is non-empty string before hitting Haiku
- Target: deploy to main when done so Render auto-deploys

Let me know if you have questions or hit any blockers.
