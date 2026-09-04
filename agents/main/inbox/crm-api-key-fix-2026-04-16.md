# CRM API Key Fix — Blocking Jack's Lead Import

**From:** Ryan Chen
**Date:** 2026-04-16 09:00 ET
**Priority:** High — 373 leads blocked

## Problem
Jack's import requests to clientlist.onrender.com are returning 403. He's using an OpenPhone API key, not a CRM API key. The CRM auth middleware validates against the `CRM_API_KEYS` env var, which either isn't set or doesn't include a key for Jack.

## Fix Needed
On the **Render dashboard** → `thht-crm` service → Environment:

Add/update the `CRM_API_KEYS` env var with:

```
[{"key":"<REDACTED:API_KEY>","name":"Jack Sullivan","role":"member"}]
```

If there are already keys in there (for Chris, etc.), just add Jack's entry to the array.

After saving, Render will redeploy automatically.

## Then Jack Uses
```
Authorization: Bearer <REDACTED:API_KEY>
```

## Context
Jack has 373 leads (214 fly-in absentee + 159 cold-calling) in CSVs ready to load via POST /api/import. This is the only blocker.
