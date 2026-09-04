# Tech Scout — 2026-07-19 (from Ryan)

Weekly scout done. Two finds this week actually map to standing THHT pain, not just "interesting tools":

**1. Coolify (High priority — recommend pilot)**
Self-hosted Vercel/Render/Heroku alternative. Free/open-source, runs on a ~$5-20/mo Hetzner VPS. Docker-based, git-push CI/CD, auto SSL, 280+ one-click services (Postgres, Redis, n8n), per-branch preview deploys *with* backend + db.
- **Why it matters:** directly addresses our Render dependency — thht-hq has been suspended for weeks now. Coolify = we control uptime + no surprise suspensions.
- Supersedes DeployWise (already on radar, less mature).
- Trade-off: we own the uptime, no managed SLA. Setup ~4-8h.
- **Ask:** green light to pilot on a cheap VPS to de-risk Render? Low $, reversible.

**2. Uptime Kuma (High)**
Self-hosted uptime monitor (sites/APIs/DNS/Docker) with Telegram alerting + shareable status page. Single Docker container.
- **Why it matters:** replaces the manual keep-alive curls I've been logging on heartbeats (you & I both flagged those as low-value). It'd just auto-alert us on Telegram if thht-hq/clientlist go down.

Also added Dify + OpusClip (Medium) for Fiona's content pipeline. Full details in research-lab/tech-radar.md + scouting.jsonl.

— Ryan
