# Render Services — Escalation (from Ryan, Jun 21)

Flagging from this week's research lab review. Render instability is spreading, not resolving:

- ✅ **clientlist.onrender.com** (CRM) — healthy (302)
- ❌ **thht-hq.onrender.com** — 503, **down since June 11 (10 days)**
- ❌ **thht-social.onrender.com** (Fiona's dashboard) — 503, **newly down this week**

2 of 3 services are down; only the revenue-critical CRM is holding.

I've been health-monitoring these, but monitoring a service that's been confirmed down for 10 days adds no value. The next step is root cause in the Render dashboard — likely suspended free tier, failed build, or billing. I don't have dashboard access; can you or Chris check, or grant me access?

Also logged a related issue: Nolan's 7 cron entries silently vanished this week (no picks until Chris noticed) — the shared crontab.txt is a single point of failure across all agents. Want to discuss isolating per-agent schedules.

— Ryan
