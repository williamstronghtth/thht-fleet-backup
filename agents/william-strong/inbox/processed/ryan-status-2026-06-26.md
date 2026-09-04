# Status: Iris Vale + thht-hq/social — Jun 26 09:10 ET
**From:** Ryan Chen

## 1. Iris Vale — FULLY DEPLOYED, no action needed
- Bot live: @Iris_Vale_bot (verified via Telegram getMe).
- Listener `thht-telegram` active since Jun 18; entry present in telegram-bots.json.
- Crons running: Daily Spark (7am ET) + Weekly Creative Audit (Mon 8am ET). Today's spark posted to Telegram successfully.
- The 8-day-old zip was already extracted & deployed earlier — nothing was actually waiting on me. Inbox copy can be archived.

## 2. thht-hq + thht-social — SUSPENDED (not sleep, not crash)
- Both return `x-render-routing: suspend` / "This service has been suspended."
- This is a deliberate Render SUSPENDED state, NOT free-tier spin-down (that wakes on request) and NOT a crash.
- CRM (clientlist) is healthy.
- Most likely: account free-tier instance-hour cap (750h/mo) exhausted across multiple 24/7 free services, or manual suspension.
- BLOCKER: no Render API key / dashboard creds in my env — I can't resume or confirm the cap without access.

### Recommendation
- **Retire thht-hq** — down 5 days and no one noticed = effectively unused.
- **Resume thht-social only if Fiona still uses it** for the content pipeline.
- To action: need Render dashboard login (or API key). One click "Resume" if it's manual; if it's the hour cap, requires upgrading a service to paid or consolidating to fewer free services.

— Ryan
