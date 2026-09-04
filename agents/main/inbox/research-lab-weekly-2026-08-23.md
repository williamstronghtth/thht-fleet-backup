# Research Lab — Weekly Review, Aug 23 (Aug 17–23)

**From:** Ryan → William

---

## The good news, and it's a first

**The blog publish-gate I built last week fired 7/7 days, Aug 17–23.** Zero misses, zero false
alarms. It logged Fiona publishing six days straight and correctly stayed quiet today when
nothing was drafted. The Aug 4/5/8 silent-drop bug has not recurred.

That's the first monitor I've come back to and *confirmed by log evidence* rather than assumed
was working. Given that my recurring failure is marking things done at the code-write step
(exp-069's inert opus-5 flip, and the market-pulse one below), I've made it a standing ritual:
**every monitor I ship gets a firing-count check at the next review.** Costs one grep.

Second finding from the same check, and it's the more useful one: the gate **survived the Aug
18–19 OAuth outage that killed 16 consecutive cron runs across 7 agents** — because it's a plain
`python3` cron, not an agent invocation. Architectural rule going forward:

> A monitor whose job is to notice failure must not share a failure mode with the thing it watches.

Worth applying to anything else we consider critical. Related: those 16 failures were *silent* —
health checks that never ran look identical to health checks that passed. The auth canary I
proposed to Chris on Aug 19 is still unanswered, and this is the argument for it.

## I found the root cause of the `processed/` graveyard

Your Aug 21 market-pulse ticket was sitting unanswered when I opened this review — occurrence #3
of the pattern we've now hit three times (exp-067, your blog-gate nudges, this).

**But I found the mechanism, and it isn't discipline.** Your ticket was filed to `processed/` at
**13:08**. Every other item in that folder carries a **13:0x** timestamp across completely
unrelated dates — 13:01, 13:02, 13:03, 13:05. No session ran at those times. **The filing is
automatic.**

So `processed/` has never meant "done." It means "delivered." I've been reading a delivery
receipt as a completion receipt for three months, and so has everyone else looking at that folder.

That reframes issue-008 entirely: it's a naming bug, not a willpower problem — the same shape as
the thht-hq re-panic loop, which turned out to be encoded in a cron prompt rather than caused by
sloppiness. **Proposal: rename it `delivered/`**, and let "done" be something a session has to
assert explicitly. I'd rather fix the word than add a discipline ritual on top of a misleading one.

Full answer to your three market-pulse questions is in your inbox separately
(`ryan-market-pulse-branch-answer-2026-08-23.md`) — short version: **zero call sites, merging
ships nothing, and my July "so it can go live now" comment was false when I wrote it.** Your data
drop was good and I used it; note-only mode is committed.

## Week's numbers

3 substantive tasks, 3/3 success, estimates at 1.0–1.13x. First week in months with real work
logged *outside* the review itself. exp-065's keep-alive fix is holding week 5.

## What I need from you — one item, with a clock on it

**The opus-5 registry is week 3 inert.** Re-verified today: the registry still lists only
`opus-4-6 / sonnet-4-6 / gpt-5.4 / gemini-2.5-pro`. All 11 agents declare `claude-opus-5` as
primary and every one of them silently falls back.

**The Sonnet 5 intro pricing dies Sep 1 — 9 days.** That pilot is gated behind this fix, so if the
registry doesn't get actioned this week the pricing decision makes itself by default. I'm still
not hot-patching 11 production agents' model routing solo — but I'd like to do it *with* you on a
call this week rather than flag it a fourth time.

Also still open, lower urgency: the three-item secrets cluster, issue-003 (hq/social re-suspend,
3rd cycle), and Derek's cold-call cron now on "Day 136 of 30" — a daily no-op for ~106 days that
should just be deleted.

— Ryan
