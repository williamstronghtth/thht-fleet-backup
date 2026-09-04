# Research Lab Weekly Review — Jul 27–Aug 2, 2026
**From:** Jack Sullivan
**Full brief:** jack-sullivan/workspace/briefs/research-lab-weekly-2026-07-27-08-02.md

## TL;DR — holding-pattern week, two new frictions

- **NH pipeline: 0 leads, no movement.** Gated on the RedX-vs-build-scraper decision I
  escalated to you Jul 23 — now ~10 days pending. Nothing moves without it.
- **Newsletter shipped Jul 28** — 84/84 delivered, Amherst NH spotlight, rates 6.58%/5.96%.
  Still going to the legacy FL list. List-rebuild decision still open.
- **🔴 NEW: CRM is now auth-gated.** clientlist.onrender.com/api/clients returns
  "Authentication required." The lab has no credentials — lead-load/warmup blocked on
  access even once we have leads. Need the API key.
- **🔴 NEW: secret exposure wider than reported.** Same Gmail app password in plaintext in
  5 scripts (not 2). Should be rotated + moved to .env. Ryan task.
- FL cadences (Lis Pendens day 160, cold-calling day 115) + domain warmup (12th dark week,
  ~72 no-op runs) still firing daily. Recommend pausing/killing those crons.

**One ask that unblocks everything: get Chris to call RedX-or-build on NH lead sourcing.**
