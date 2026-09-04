# Weekly Research Lab Review — 2026-08-30 (Ryan)

**Bottom line:** I shipped three fixes this session, but the honest headline is
that **my own week was the anti-pattern** — and two decisions need you, one of
which expires Tuesday.

---

## 1. My week Aug 25–29 was 8 sessions of nothing (self-finding)

Every session Aug 25–29 logged the same thing: *"CRM healthy, HTTP 302, no files
changed."* Eight of them. That's the exp-060/061 regression we named in June.

**But it isn't a discipline failure, and I want to be precise about that.** The
keep-alive cron was `run-agent.sh ryan-chen "curl clientlist..."` — it spawns a
**full Opus session four times a day to perform one HTTP request**. In July
(exp-065) I fixed that cron's *prompt*. I never questioned its *form*.

**Fixed:** replaced it with `bin/crm-keepalive.sh`, a plain script.
- Retries once before alerting (a Render cold-start timeout is not an outage).
- Alerts Chris **only** on failure. Silence = healthy.
- **I tested the failure path, not just the happy one** — bad host → logs
  `DOWN first=000 retry=000` and fires a real Telegram alert with a resolved
  token. That is exactly the test Uptime Kuma never got before sitting six weeks
  "deployed" with zero notifications configured.
- Backup `crontab.bak-20260830-keepalive`, one-line diff, `crontab.txt`
  re-synced, no drift.

Second reason this matters beyond cost: on Aug 18–19 an OAuth expiry killed 16
agent-launched cron runs while the plain-python publish-gate ran straight
through. **Monitors shouldn't depend on the component most likely to break.**

---

## 2. issue-008, occurrence #4 — and this time it hurt another agent

Eno filed a blocked-on-FanGraphs request at **13:06 Aug 29**. It was auto-filed
to my `inbox/processed/` and **no session ever read it**. He waited a day, built
a workaround himself, and *still* logged "need to coordinate with Ryan."

This is the fourth instance (exp-067 → exp-070 → exp-073 → now), and the first
where the cost landed on a teammate rather than on us. `processed/` is automatic
— it means *delivered*, never *done*.

**I didn't just note it — I solved his problem.** Tested FanGraphs four ways
(curl + Chrome UA, Playwright headless, Playwright + webdriver stealth patch
with a 45s wait, plus Eno's scrapling): all 403. It's a Cloudflare **interactive
challenge**, not the ModSecurity/UA case in our TOOLS.md — so a UA swap *cannot*
work, and the useful deliverable was a definitive **stop trying** verdict.
Built and live-validated `statsapi_leaders.py` on MLB StatsAPI (official, free,
no challenge, true date-ranged splits): 57 SP rows, 46 under-26 hitters from 154
scanned. Reply is in his inbox.

**Ask:** I'd like to propose a shipped-vs-claimed reconciliation check —
anything landing in `processed/` without a deliverable or a reply gets re-raised
at the next review. Four occurrences is a pattern, not bad luck. Your call on
shape.

---

## 3. We couldn't verify our own monitor

Last week's lesson was literally *"verify every monitor's firing count."* I
tried this week and **couldn't** — the publish-gate only prints to the shared,
churning `logs/cron.log`, where only today's line survived. A monitor whose
fires can't be counted is indistinguishable from one that stopped.

**Fixed:** added `log_outcome()` → dated append-only
`logs/publish-gate-audit.log`. Dry-run verified; the gate itself is healthy
(1 post published today). Next review can just `wc -l` it.

---

## Decisions I need from you

**A. opus-5 registry — WEEK 4 INERT.** `anthropic/claude-opus-5` is still not in
`agents.defaults.models` (registry holds only opus-4-6, sonnet-4-6, gpt-5.4,
gemini-2.5-pro). All 11 agents set to it are silently falling back to opus-4-8.
The config edit has looked "done" for four weeks while changing nothing. One
registry entry + a verify run. I've deliberately not hot-patched 11 prod agents
without sign-off — but four weeks is long enough that I'd rather you say no than
say nothing.

**B. Sonnet 5 pilot — expires Tuesday.** Intro pricing ends **Sep 1**, i.e. two
days out, and it's sequenced *behind* (A). Realistically this is now
lose-it-or-use-it. If you want the fiona+derek pilot, it needs a call
essentially now; otherwise I'll close it out as missed and stop carrying it.

**C. Secrets cluster (still open, unchanged).** `publish-aug-15.py` hardcodes a
live WP app password + Late API key; the CRM `sk_3957…` key appears in 19 files.
Both are live credentials in source. I'd like one batched pass onto
`secrets_loader`.

Also still open: issue-003 (thht-hq/thht-social re-suspend, Chris's kill/keep/pay
call) and your items 1–6 from Aug 24, which I have not touched.

— Ryan
