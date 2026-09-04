# MEMORY.md - Long-Term Memory

## Team Structure
- **Chris Hoover** - Boss, owner of The Hoover Home Team, client-facing
- **William Strong** - Co-founder, my manager, external comms & quality gate
- **Ryan Chen (me)** - Software engineer, first agent hire

## Projects

### THHT CRM (Active)
- **Repo:** github.com/williamstronghtth/thht-crm
- **Status:** MVP pushed, waiting for Render deploy
- **Stack:** Express 5 + vanilla JS (matches thht-board pattern)
- **Features built:**
  - Client list with search
  - Pipeline stages (Lead → Active → Contract → Closed → Past)
  - 14 lead sources from Chris's data
  - Activity logging
  - Import API endpoint
- **Next:** CSV import script, follow-up reminders

### THHT Board (Reference)
- **Repo:** github.com/williamstronghtth/thht-board
- Kanban board, already deployed on Render
- Used as pattern reference for CRM

## Key Learnings
- William's mantra: "Quality over speed is our True North"
- Deployment: Push to GitHub main → auto-deploy on Render (thht-board uses master branch)
- ~150 existing contacts to import from Chris's Google Sheet
- **Config keys:** `tools.sessions.visibility` and `tools.agentToAgent` go at TOP LEVEL in openclaw.json, NOT under agents.defaults
- **Agent routing:** Use `openclaw agents bind --agent <id> --bind telegram:<account-key>` for Telegram
- **New agents need:** AGENTS.md in workspace or they inherit default (William's) identity
- **Session management:** `/reset`, `/new`, `/compact` built-in for Telegram context management

## Research Lab 🔬
Self-improvement loop for engineering — Sundays 6pm ET review
- `research-lab/experiments.jsonl` — task logs
- `research-lab/outcomes.jsonl` — results
- `research-lab/insights.md` — learnings
- `research-lab/current-config.json` — active settings

## Skills Installed
- 2026-02-09: skill-guard, claude-code-mastery, cellcog, kameleondb, google-search-console, seo-optimizer, seo-article-gen, web-perf, web-deploy, webhook-gen, internal-comms, relationship-skills, telegram-compose, prompt-engineering-expert, frontend-design
- 2026-02-13: canva (by @abgohel) - Canva Connect API integration

## Team Members
- **Chris Hoover** - Boss, Telegram: 8560812913
- **William Strong** - Co-founder, my manager, session: agent:main:main
- **Fiona Murphy** - Marketing Specialist (joined 2026-02-13)
- **Willow Hayes** - Nutritionist for Hoover family (NOT THHT), @willow_hayes_bot
- **Oliver Kensington** - Financial Analyst (NOT THHT), @OliverKensington_bot
- **Elliot Crane** - Prediction Market Trader (Kalshi), session: agent:elliot-crane:main
- **Nolan Price** - MLB Betting Analyst, @Nolan_Price_Bot, session: agent:nolan-price:main

### Nolan Price MLB Betting Agent (Active)
- **Repo:** github.com/williamstronghtth/Nolan-Price-BackUp
- **Status:** 7/11 books complete, 233 rules (R1-R233)
- **Workspace:** /root/.openclaw/workspace-nolan-price
- **Key files:** model/STRATEGY.md (master rules), model/books/ (110 chapter notes)
- **Next:** 4 more books, then live betting with calibration tracking

### Miles Redgrave — Premiere Pro Troubleshooter (Active, joined 2026-07-08)
- **Workspace:** /root/agents/miles-redgrave/workspace (run-agent.sh pattern, like Iris — NOT in openclaw.json, that's fine)
- **Role:** Post-Production Engineer, diagnoses Premiere Pro issues for Chris. 🎬, reports to Chris, Telegram channel.
- **Files:** SOUL, IDENTITY, USER, AGENTS, MEMORY, TOOLS, HEARTBEAT (empty) + 6 skills: premiere-diagnostics, export-delivery, color-grading, audio-troubleshooting, proxy-and-media, project-recovery
- **Persona:** diagnose-before-prescribe, ranks causes by likelihood, exact menu paths. Knows Chris's rig: Windows, Canon 70D (1080p H.264 MOV), DJI Mini 4 Pro (4K H.265, D-Log M), YouTube Rec.709 delivery.
- **Telegram:** registered in telegram-bots.json with PLACEHOLDER token — Chris must create bot via @BotFather, supply token, then `systemctl restart thht-telegram`.
- **Also:** added iris-vale + miles-redgrave to run-agent.sh "Available agent IDs" list (iris was missing). No cron (reactive troubleshooter).
- **Tested live:** responds fully in character. ✅

## Apps Deployed
| App | URL | Repo | Purpose |
|-----|-----|------|---------|
| Team HQ | thht-hq.onrender.com | thht-hq | Virtual office, live chat, takeaways |
| Social Dashboard | thht-social.onrender.com | thht-social | Fiona's content pipeline |
| CRM | clientlist.onrender.com | thht-crm | Client management (Supabase backend) |

## Supabase (CRM Database)
- **Project:** thht-crm
- **URL:** https://lkceqalryoyfxbdbmvvj.supabase.co
- **Status:** Live, 410+ leads
- **Render env vars:** SUPABASE_URL, SUPABASE_ANON_KEY configured

## Integrations
- **Late** (getlate.dev) - Social auto-posting, $33/mo, env: LATE_API_KEY
- **Canva** - OAuth connected, env: CANVA_CLIENT_ID, CANVA_CLIENT_SECRET

## Agent Scripts
- **Elliot News**: `workspace-elliot-crane/scripts/news-digest.mjs`, `breaking-news-monitor.mjs`
- **Oliver Trading Digest**: `workspace-oliver-kensington/scripts/trading-news-digest.mjs` (hourly 9am-4pm ET)
- **Oliver Morning Brief**: `workspace-oliver-kensington/scripts/morning-briefing.py` (7am ET weekdays)
- **OpenBB SDK**: `/root/.openclaw/shared/opentypebb/` - financial data via Yahoo Finance
- **Fiona Blog Publish Gate** (exp-070, 2026-08-16): `fiona-murphy/scripts/publish-gate.py`, cron `0 18 * * *` (2pm ET). Alerts Chris via Telegram if a draft dated today exists but nothing published. Detects the Aug 4/5/8 silent-publish-drop bug. WAF needs `curl/*` UA (see TOOLS.md).

## Open Items (as of 2026-08-16 weekly review)
- **issue-008 (process, root cause):** `inbox/processed/` used as a graveyard — William's blog-gate ticket + 3 nudges (Aug 11/12/13) sat "processed" but unbuilt for 6 days. Propose a shipped-vs-claimed reconciliation check to William.
- **opus-5 flip STILL inert (high, wk2):** `anthropic/claude-opus-5` not registered in `agents.defaults.models` in openclaw.json — 11 agents silently fall back. Needs William sign-off to register + verify.
- **Sonnet 5 pilot (fiona+derek):** intro pricing ends **Sep 1**. Sequenced after opus-5 fix.
- **Secrets cluster (medium, batch):** (1) `publish-aug-15.py` hardcodes WP pw + Late key [NEW exp-070], (2) CRM `sk_3957…` key in 19 files. Move to `secrets_loader` in one pass.
- **issue-003:** thht-hq + thht-social re-suspend monthly ~11th (free-tier cap). 3rd cycle confirmed. Chris kill/keep/pay.
