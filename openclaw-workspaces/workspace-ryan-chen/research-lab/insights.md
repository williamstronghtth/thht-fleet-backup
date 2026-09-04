# Ryan's Engineering Insights

*Last updated: 2026-04-05*

## Weekly Review — 2026-04-05

### Snapshot
- Tasks completed this review period: **1**
- Success rate: **100%**
- First-try success rate: **100%**
- Estimation accuracy: **50%** (estimated 0.5h, actual 0.25h)

### This Week's Pattern
- Tiny sample size, but the one logged task landed cleanly and faster than expected.
- Current bias is **overestimating small internal scaffolding/setup work**, which is better than underestimating integration-heavy tasks.
- The bigger issue is still **coverage**: not enough tasks are being logged to make the loop statistically useful.

## What's Working ✅

### Browser Automation
- `profile="openclaw"` for sandbox browser — reliable
- `profile="chrome"` — fails, requires user's active browser

### Deployment
- Push to BOTH `main` and `master` for Render — some repos have legacy branch issues
- Supabase free tier — solves Render ephemeral filesystem problem

### Stack Selection
- Express + vanilla JS for simple dashboards (faster, less overhead)
- Supabase for any data that needs to survive redeploys

## What's Not Working ❌

### Scraping
- Zillow/Redfin — aggressive bot detection, even with Scrapling
- Trulia — slightly better but still unreliable
- Skip trace sites — all block headless browsers

### Estimation
- Integration tasks (Supabase, APIs) — consistently underestimate by 2-3x
- Browser automation — unpredictable, add 2x buffer
- Logging discipline — missing experiment/outcome entries means the review loop is underpowered

## Patterns to Test 🧪

1. **Log every meaningful task at start** — highest leverage fix right now
2. **Time-box exploration** — Cap "figuring it out" at 30 min before asking
3. **Smaller PRs** — Ship incrementally vs big-bang deploys
4. **Separate internal setup from external integrations** — different estimation behavior, should likely use different buffers

### Config Management
- `tools.sessions.visibility` and `tools.agentToAgent` are TOP-LEVEL config keys, NOT under `agents.defaults`
- Agent identity: new agents MUST have AGENTS.md in workspace or they inherit the default agent's identity
- Telegram routing: `openclaw agents bind --agent <id> --bind telegram:<account-key>` — account key name alone doesn't auto-bind
- Gateway validates config strictly — test with `openclaw gateway status` before assuming restart worked

### Git/GitHub
- Some repos use `master`, some use `main` — always push to both to be safe
- `.gitignore` patterns for raw book files: `*.epub`, `*.pdf`, `*.djvu`, `*_extracted/`
- `git rm --cached` to remove files from repo without deleting locally

## Historical Learnings

| Date | Lesson |
|------|--------|
| 2026-04-05 | Data quality is now the bottleneck — one clean task log isn't enough to tune config confidently |
| 2026-04-05 | Small internal scaffolding work may be slightly overestimated; don't generalize this to integration work |
| 2026-03-23 | Config keys placement matters — tools.sessions goes top-level, agents.defaults.tools is REJECTED |
| 2026-03-23 | New agent setup checklist: workspace + AGENTS.md + bind command + gateway restart |
| 2026-03-23 | Cron audit: Oil Spike Monitor at 10min intervals = 96 runs/day — check frequency vs value |
| 2026-02-23 | Supabase migration took 3x estimate — env vars are always the gotcha |
| 2026-02-20 | OpenPhone API is read-only for calls — can't dial programmatically |
| 2026-02-13 | Render ephemeral FS resets data.json — need external DB |

---

*This file updated weekly during Sunday review.*