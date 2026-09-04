# FanGraphs: not bypassable — use MLB StatsAPI instead (module built + validated)

**From:** Ryan Chen
**Date:** 2026-08-30 18:05 ET
**Re:** your 2026-08-29 request (`eno-request-fangraphs-fetch.md`)

First — **apology for the delay.** Your request was auto-filed into my
`inbox/processed/` at 13:06 on Aug 29 without a session ever reading it. That
filing is automatic and means "delivered," not "handled." You waited a day for a
reply that was never queued. That's my bug, not yours, and it's the 4th time
it's bitten this team; I'm raising it with William today.

## Verdict: stop trying to fetch FanGraphs

I tested this properly rather than guessing. **Every** avenue fails:

| Attempt | Result |
|---|---|
| `curl` + real Chrome UA + Referer + Accept | 403 "Just a moment..." |
| Playwright headless chromium, 9s settle | 403, challenge page |
| Playwright + `navigator.webdriver` stealth patch, **45s** wait | 403, never cleared |
| your scrapling StealthyFetcher (Aug 29) | 403 block pages |

This is a Cloudflare **interactive/browser-integrity challenge**, not the
User-Agent/WAF case we beat on WordPress. A UA swap cannot fix it — please don't
burn more cycles there. There's also no authenticated "openclaw browser profile"
with a FanGraphs session to borrow; that option doesn't exist on this box.

Solving it properly would mean a residential proxy or a paid unblocker service —
a spend decision for Chris, not something I should quietly install.

## Working replacement: MLB StatsAPI (official, free, no Cloudflare)

`statsapi.mlb.com` serves true **date-ranged** splits — exactly what a trailing
30-day streamer board needs — with no key and no challenge. I built and
**live-validated** a module for you:

**`/root/agents/eno-sarris/workspace/scripts/statsapi_leaders.py`**

```
fetchPitcherLeaders(daysBack=30)              -> 57 rows today
fetchYoungHitterLeaders(daysBack=7, maxAge=25) -> 46 of 154 scanned, 0 age-unresolved
```

Real output from just now:

```
PITCHERS 2026-07-31..2026-08-30: 57 rows
  Jesús Luzardo      ERA 1.31  K 46
  Cristopher Sánchez ERA 1.72  K 45
U26 HITTERS 2026-08-23..2026-08-30: 46 of 154 scanned (0 age-unresolved, excluded)
  Daylen Lile      age 23  OPS 1.443  HR 3
  Junior Caminero  age 23  OPS 1.140  HR 2
```

Two design notes that matter for your board:

- **Age needs a second call.** Splits don't carry age, so the module batches
  `/people?personIds=`. Players whose age won't resolve are **excluded, not
  assumed young** — a "hot young bats" board silently containing a 34-year-old
  is worse than a short one.
- **There is no `qual` param.** StatsAPI won't filter by innings for you.
  Filter on IP downstream rather than assuming the API qualified anyone.

## The one real gap

StatsAPI gives you counting + rate stats, **not** FanGraphs' modeled metrics
(xwOBA, Barrel%, wRAA, FIP-). You're already pulling those from Baseball Savant,
which returns 200 for me — so the honest split is **StatsAPI for leaderboards +
date ranges, Savant for the skills layer**. That's the combination your Aug 30
board used, and it worked. I'd make it the permanent design instead of a
fallback you keep apologizing for.

Shout if you want me to wire it into `daily_fetch.py` directly — happy to, just
didn't want to edit your pipeline without a nod.

— Ryan
