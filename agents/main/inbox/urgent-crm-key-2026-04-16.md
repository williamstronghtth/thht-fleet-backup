# URGENT: Jack's CRM Key — Action Needed

From: Ryan Chen
Time: 11:22 AM ET

---

William — Jack is still blocked. His 373 leads can't import until the CRM_API_KEYS env var is set on Render.

**One step needed:** Render dashboard → thht-crm → Environment → Add:

```
CRM_API_KEYS=[{"key":"<REDACTED:API_KEY>","name":"Jack Sullivan","role":"member"}]
```

Save → auto-redeploy → Jack's leads flow immediately.

This has been blocking since yesterday. Full details in `crm-api-key-fix-2026-04-16.md`.

— Ryan
