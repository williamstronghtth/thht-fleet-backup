# AI Smart Query — Build Reminder

**From:** William Strong  
**Date:** 2026-06-03 09:00 ET  
**Priority:** High

You received the AI Smart Query spec yesterday (ai-smart-query-2026-06-02.md in your processed folder). The prospect intelligence enrichment service is done — great work.

AI Smart Query is the next build:

## What to Build

**Backend:** `POST /api/smart-query`
- Accepts `{ q: "buyers in Amherst over 600k" }`
- Calls Claude Haiku with the query + a system prompt that maps natural language to filter params
- Returns the same shape as `GET /api/clients` (filtered list)

**Frontend:** Smart Search bar in the leads view
- Input field above the leads table
- Calls `/api/smart-query` on submit
- Shows results in the same table

## Claude Haiku integration
Use `@anthropic-ai/sdk`. System prompt should instruct Haiku to return a JSON object with filter keys matching your existing `GET /api/clients` params:
- `stage`, `source`, `leadType`, `search`
- Plus new ones you add: `minPrice`, `maxPrice`, `city`, `state`

## Env var needed
`ANTHROPIC_API_KEY` — already set on Render (it's what we use for enrichment).

## Important
GitHub token is still expired — code will sit uncommitted until Chris fixes that (likely today). Write the code anyway and note it in your daily memory.

