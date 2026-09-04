# CRM API Key — Morning Check

From: William Strong
To: Ryan Chen
Time: 9:00 AM ET

---

Ryan — quick heads up.

Jack's cadence-engine.py uses this token to authenticate with clientlist.onrender.com:

```
QUO_TOKEN = "<REDACTED:CREDENTIAL>"
```

As of this morning it returns **HTTP 403** (Forbidden). Yesterday evening it was 401. The CRM frontend and Supabase are healthy (you confirmed that last night), but the application-level API key is being rejected.

**What I need:**
- Can you check what API key is configured on the Render backend? Either in env vars or in the CRM auth logic?
- If the key changed (or was never set), Jack needs the correct one so his cadence scripts can run.

Jack has 214 fly-in absentee leads + 159 cold-calling leads sitting in CSV — all blocked until the API auth is resolved.

Also worth noting: SMTP password is still hardcoded in `send_newsletter.js` — flag for next deploy (not urgent but a security hygiene item).

Thanks
— William
