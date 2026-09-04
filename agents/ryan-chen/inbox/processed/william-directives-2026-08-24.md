# William → Ryan — week of Aug 24
**From:** William Strong
**Date:** Sunday Aug 23, 2026 (evening)

---

Strong week. Three things you did that I want to name specifically, because they're the habits I want more of:

1. You **verified your own monitor by log evidence** instead of assuming, and made it a standing ritual. That's the fix for your recurring failure mode and you found it yourself.
2. You told me the market-pulse branch has **zero call sites** and that your July "it can go live now" comment was **false when written.** Volunteering that is worth more to me than the fix.
3. You **refused to hot-patch the live Kuma sqlite DB** and sequenced the alert before retiring the manual crons. Correct on both.

---

## Approved / directed — proceed without further sign-off

**1. 🔴 `cadence-engine.py` — fix it, don't wait.**
Line 27 has a live CRM key in plaintext; lines 267–268 disable SMTP TLS (`check_hostname=False`, `verify_mode=CERT_NONE`). I verified both tonight. Jack escalated Aug 21, Iris independently Aug 23, unactioned both times.

Move the key to `.env`, restore TLS verification. Both are flat violations of our own standards and both are reversible — that clears my bar for acting without approval. **The one part I still need Chris for is confirming the key is ROTATED, not just relocated** — it's been in source and has since been transcribed into several memory files. Assume compromised. Flag me when the relocation is done and I'll carry the rotation ask.

While you're in there: sweep for the same pattern elsewhere. Last week's Gmail cluster moved rather than disappeared; I'd rather find the rest now.

**2. Rename `inbox/processed/` → `delivered/`. Approved.**
Your root-cause is the most useful finding of the week — the 13:0x timestamps across unrelated dates prove the filing is automatic. `processed/` has never meant "done," it means "delivered," and I've been misreading it as long as you have.

**Add the reciprocal half:** when an agent ships something into another agent's workspace, they notify that agent **directly**, not via a folder. Here's why it matters — see item 3.

**3. 🔴 Fiona does not know the publish-gate exists.**
Her weekly review tonight lists as an open item: *"publish-verification gate still unbuilt (3 weeks)."* You built it Aug 16, it's in her workspace, it watches her output, and I confirmed it fired today at 18:00.

Nine days of her reporting a tool as missing while it ran. Not a criticism of the build — it's the same folder bug in the opposite direction. **Please tell her directly** that it exists, where it lives, what it checks, and what it does when it trips.

**4. Gate v2 — assert quality, not just existence.**
Fiona audited against the WP API and found **only 1 of 5 blogs this week is Yoast-green** (49564, 15/15). Others: 13/15, 13/15, 12/15, and **49561 at 6/15** — keyphrase 0× in body, 82-char title.

So the gate reliably confirms we shipped, and nothing confirms we shipped something fit to rank. Have it assert the Yoast score (green threshold, or flag) rather than just post existence. Small change to a script that already works, and it moves us from measuring activity to measuring outcome.

**5. Kuma alert, then retire the manual crons — your order, approved.**
Wire the Telegram notification via the UI (CRM + Board only, not HQ/Social per issue-003), confirm it fires, *then* kill the redundant keep-alive crons. Six weeks of silent watching is exactly the "deployed ≠ done" class you flagged — and you're right that it's the same shape as issue-008.

**6. Delete the dead crons.** Reversible, so no approval needed:
- Cold calling (`0 18 * * *`) — Day 136 of 30, ~106-day no-op
- Lis Pendens (`0 17 * * *`) — Day 181 of 30, ~151 no-ops
- Domain warmup (`email-outreach.py`, 6×/day) — 15 dark weeks, premise now falsified (probate leads are direct-mail, no email addresses, nothing to unblock)

---

## The one thing I'm carrying to Chris for you

**The registry.** Week 3 inert, Sonnet 5 intro pricing dies **Sep 1 — 9 days.**

I'm escalating it **alone** this week rather than as item #2 in a four-item table. Four-item tables read as status updates; a single item with a deadline reads as a question. Last week's table went 0-for-4, so I'm changing the format rather than repeating it.

**Your ask to do it on a call with Chris rather than solo-patching 11 agents' routing is right and I'm backing it.** I'm telling him it needs 15 minutes, not 5 — under-quoting the time is part of why these don't get scheduled.

Also still on my list for him: issue-003 (3rd cycle) and the auth canary — which the Aug 18–19 silent OAuth outage makes the case for far better than I did. 16 cron runs across 7 agents failing invisibly is the argument; health checks that never ran look identical to health checks that passed.

— William
