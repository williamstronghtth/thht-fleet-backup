# Cron Inventory — The Hoover Home Team

**Last updated:** 2026-03-24  
**Total active crons:** 33

---

## Work Pulse & Check-ins

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 1 | Workday Start (8am) | `662a965c` | `0 13 * * 1-5` UTC | main | Morning kickoff |
| 2 | Work Pulse (10am) | `6a252eb4` | `0 15 * * 1-5` UTC | main | Mid-morning check-in |
| 3 | Work Pulse (2pm) | `31e8901e` | `0 19 * * 1-5` UTC | main | Afternoon check-in |
| 4 | Workday End (6pm) | `62b1593c` | `0 23 * * 1-5` UTC | main | End-of-day wrap-up |
| 5 | Morning Brief | `677326bc` | `30 6 * * 1-5` ET | main | Daily morning brief |
| 6 | Check in on Mikey | `a9ed0ae4` | `0 9 * * 1` ET | main | Weekly Monday check-in |

## Content & Marketing

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 7 | Daily Blog Post | `a5298081` | `0 10 * * *` ET | derek-marshall | Daily RE blog content |
| 8 | Daily Content Handoff | `8e0bfb11` | `0 7 * * *` ET | main | Morning content handoff |
| 9 | Weekly Newsletter Prep | `ca5d26c8` | `0 14 * * 2` UTC | main | Tuesday newsletter prep (9am EST) |
| 10 | Weekly Marketing Review | `0ee1a309` | `0 23 * * 0` UTC | fiona-murphy | Sunday marketing review |

## Prospecting & Outreach (Jack Sullivan)

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 11 | Check Email Replies | `d7aa8585` | `*/30 9-20 * * *` ET | jack-sullivan | Check email replies every 30 min |
| 12 | Email Outreach (Domain) | `c6367cab` | `0 8,10,12,14,16,18 * * *` ET | jack-sullivan | Scheduled email outreach |
| 13 | Lis Pendens Cadence | `42311a88` | `0 13 * * *` ET | jack-sullivan | Daily lis pendens cadence |
| 14 | Cold Calling Sequence (Daily) | `0d626ca0` | `0 14 * * *` ET | jack-sullivan | Daily cold calling sequence |
| 15 | Cold Calling Sequence (Friday) | `6f6275be` | `0 17 * * 5` ET | jack-sullivan | Friday cold calling block |
| 16 | Fly In 15-Touch Cadence | `b723ad40` | `0 13 * * *` UTC | jack-sullivan | Daily fly-in cadence drip |

## Finance & Trading (Oliver Kensington)

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 17 | 📊 Oliver's Morning Financials | `1cf8c91b` | `0 7 * * 1-5` ET | oliver-kensington | Morning financial brief |
| 18 | 📈 Trading News Digest | `dcc6f162` | `0 9-16 * * 1-5` ET | oliver-kensington | Hourly trading news (market hours) |
| 19 | Hourly Market Update | `6f7e65c9` | `0 14-20 * * 1-5` UTC | oliver-kensington | Hourly market update |
| 20 | Morning News Scan | `97f58082` | `0 10 * * 1-5` UTC | oliver-kensington | Daily morning news scan |
| 21 | 🔬 Oliver's Weekly Research | `fc4879ec` | `0 18 * * 0` ET | oliver-kensington | Sunday weekly research review |

## Prediction Markets (Elliot Crane)

*All 4 Elliot crons removed 2026-03-24 to save usage. Agent offline.*

## Sports (Calvin)

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 26 | 🏥 Injury Report (1:30pm) | `7659987b` | `30 17 * * *` UTC | calvin | NBA injury report check |
| 27 | 🏀 Calvin Daily Model Run | `850f6eb1` | `0 18 * * *` UTC | calvin | Daily NBA model run |
| 28 | 🏥 Final Injury Check | `8cc2d943` | `30 22 * * *` UTC | calvin | Late injury check |

## Weekly Reviews

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 29 | william-weekly-review | `8a9cbb24` | `0 18 * * 0` ET | ryan-chen | William's Sunday review |
| 30 | ryan-weekly-review | `bd9a4ddf` | `0 18 * * 0` ET | ryan-chen | Ryan's Sunday review |
| 31 | Research Lab Weekly Review | `e2e79c47` | `0 18 * * 0` ET | jack-sullivan | Research lab Sunday review |
| 32 | William Weekly Research | `b87e4ef9` | `0 23 * * 0` ET | main | William's Sunday research |

## Infrastructure

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 32 | CRM Keep-Alive Ping | `3ccfd330` | `0 0,6,12,18 * * *` UTC | ryan-chen | Every-6-hour ping to CRM + HQ — prevents Supabase pause, keeps Render warm, alerts William on failures |

## MLB Model (Nolan Price)

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 33 | Daily SIERA Scraper | `05e3d6a0` | `0 7 * * *` UTC | nolan-price | Daily FanGraphs pitcher stats pull (SIERA, FIP, xFIP, K%, BB%) for live 2026 model |

## History & Misc

| # | Name | ID | Schedule | Agent | Purpose |
|---|------|----|----------|-------|---------|
| 33 | daily-history-story | `ca10477c` | `30 6 * * *` ET | arthur-pembroke | Daily history story |
| 34 | Amherst NH Weekly Newsletter | `8d719e6e` | `0 11 * * 0` ET | — | Weekly Amherst NH newsletter |
| 35 | Yamanaka Factors Research | `ec5ed00f` | `0 14 1 * *` ET | main | Monthly Yamanaka research |

---

## Notes
- IDs shown as first 8 chars for readability; full UUID in `openclaw cron list`
- ET = America/New_York timezone
- Crons with status **error** on last run: `ca5d26c8` (Newsletter), `ca10477c` (History Story), `5f013eb7` (Elliot Portfolio), `fc4879ec` (Oliver Weekly Research)
- Count was 35 at inventory time; removed 4 Elliot crons → now 31
- Elliot crons were still active despite yesterday's cleanup — now fully removed
