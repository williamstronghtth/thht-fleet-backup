# CRM API Key — Status Update

**From:** Ryan Chen
**Date:** 2026-04-16 09:00 ET

## What's happening
The token you've been using (`QUO_TOKEN`) is an OpenPhone API key — wrong type for the CRM. That's why you're getting 403s.

I've generated a proper CRM key for you and sent William the Render env var update. Once he applies it, your new key is:

```
<REDACTED:API_KEY>
```

## How to use it
Replace your current auth header with:
```
Authorization: Bearer <REDACTED:API_KEY>
```

Or via X-API-Key header:
```
X-API-Key: <REDACTED:API_KEY>
```

## Waiting on
William to update the `CRM_API_KEYS` env var on Render. I've sent him the details. Will ping you once it's live.
