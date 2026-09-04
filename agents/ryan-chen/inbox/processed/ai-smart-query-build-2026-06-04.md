# Task: Build AI Smart Query — CRM Natural Language Search
**From:** William Strong  
**Date:** 2026-06-04  
**Priority:** HIGH — Chris approved this on June 2, still not built

## Background
Chris approved the AI Smart Query feature on June 2. The spec was sent to your inbox (now in processed). This is a top-priority CRM build for today.

## What to Build
A natural language search bar in the CRM leads view that converts English queries into Supabase filters using Claude Haiku.

## Spec

### Backend: POST /api/smart-query
- Accept: `{ "query": "string" }` (natural language)
- Use Claude Haiku (claude-haiku-3-5 or latest haiku model) to parse intent
- Convert to a structured Supabase filter (status, source, city, state, enrichment_status, date range, etc.)
- Execute the filtered query against the clients table
- Return: `{ success: true, data: [...clients], filter_applied: {...}, query_used: "..." }`
- Cost: ~$0.001/query — negligible

### Frontend: Smart Search Bar in Leads View
- Add a text input above the client table with placeholder: "e.g. show me clients from Amherst who haven't been contacted in 30 days"
- On submit, POST to /api/smart-query
- Replace table results with filtered results
- Show the interpreted filter as a small tag/badge (e.g. "Filtered: city=Amherst, last_contact>30d")
- "Clear" button to reset to full list

### Claude Haiku Prompt (use this structure)
```
You are a CRM query interpreter. Convert the user's natural language into a JSON filter object.

Available fields:
- status: string (one of: lead, prospect, client, past_client, inactive)
- lead_source: string (e.g. "Browns Landing", "Zillow", "Referral")
- city: string
- state: string (2-letter code)
- enrichment_status: string (one of: pending, processing, complete, failed)
- days_since_created: number
- firstName, lastName: string (partial match)
- email: string

User query: "${query}"

Respond with ONLY a valid JSON object, no explanation. Example:
{"city": "Amherst", "state": "NH", "status": "lead"}
```

## Code Quality
- Keep the Claude call in its own helper function `parseQueryToFilter(query)`
- Use the ANTHROPIC_API_KEY env var (already set on Render from other usage or add it)
- Handle malformed Claude responses gracefully (fallback to empty filter + show error)
- Error returns: `{ success: false, error: "..." }`

## Deployment
- Commit to master → Render auto-deploys
- Notify William Strong when live

## Done Criteria
- POST /api/smart-query returns filtered client results given a plain-English query
- Smart search bar works in the CRM leads view
- Deployed to Render
