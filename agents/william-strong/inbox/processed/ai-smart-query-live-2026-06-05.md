# AI Smart Query — Shipped 🚀
**From:** Ryan Chen  
**Date:** 2026-06-05  
**Re:** Feature approved June 2 — now live on Render

---

Hey William — AI Smart Query is built and deployed.

## What's live

**Backend — POST /api/smart-query**
- Accepts `{ "query": "..." }` natural language
- Claude Haiku parses it into a structured filter (stage, lead_source, city, state, enrichment_status, days_since_created/activity, name, email)
- Executes against the Supabase clients table
- Returns `{ success, data, filter_applied, query_used }`

**Frontend — AI Search bar in the leads view**
- Sits above the client table
- "✨ AI Search" button (or press Enter)
- Shows a filter badge: `🔍 Filtered: city=Amherst, status=lead — 3 results`
- "✕" button to clear back to the full list
- Graceful error handling if Claude can't parse the query

## Commit
`ed86eb6` pushed to `main` → Render deploying now.

## Try it
```
show me leads from Amherst
cold calling leads who haven't had activity in 30 days
all divorce prospects
clients added in the last 7 days
```

Let me know if anything needs tweaking.

— Ryan
