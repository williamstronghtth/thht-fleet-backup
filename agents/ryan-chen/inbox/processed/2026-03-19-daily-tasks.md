# Daily Tasks — 2026-03-19 (Wednesday)
**From:** William

Morning Ryan. Here's today's priorities:

## Priority 1: Jack Routing Fix Investigation
Jack's messages are still routing through Billy's bot even with `channel: "telegram"`. He also needs `accountId: "jack"` specified. Can you check the gateway config and confirm Jack's Telegram bot binding is set up correctly? If there's a config-level fix we can make so he doesn't have to specify accountId every time, that would be ideal.

## Priority 2: Cron Cleanup
We have way too many overlapping crons firing (Ryan check-in every 3 hours, growth mindset every 3 hours, backup checks every 3 hours). Can you audit the current cron list and flag which ones are redundant? I'll decide what to cut.

## Priority 3: Oliver Trading News Digest
How's the trading-news-digest.mjs working? Any issues since you built it on 3/16? Oliver should be getting hourly market digests during trading hours.

## If Time Permits
- OpenBB SDK integration status
- Property Alerts Phase 2 (RPR matcher)

No blockers on my end. Let me know if you need anything.

— William
