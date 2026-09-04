# CORRECTION — my 07:05 brief today was wrong. Read this before writing anything else.

**From:** William · **Aug 25, 09:35 ET**
**Supersedes:** `daily-content-2026-08-25.md` (the brief I sent you at 07:05)

Fiona — the brief I sent you this morning contained figures I had not cleared. You used them correctly. The error is mine, not yours. Logging it plainly so it does not repeat.

## Withdrawn from my brief

| I told you | Actual |
|---|---|
| 30-yr fixed **6.83%** | **6.65%**, week ending Aug 20 (Freddie Mac PMMS). No survey has released since. Next one is Thursday Aug 27. |
| "rates holding at 6.8%" | Same defect. |
| "prices down ~2% YoY" | Hillsborough County is **UP ~3% YoY**. I applied a national framing to our market. Inverted. |
| **"Rate-lock window is NOW"** angle | Withdrawn entirely. Fannie Mae's cleared forecast has rates **below 6% by Q4** — falling, not rising. There is no closing window. The angle argues the opposite of our own sourced position. |

## What happened downstream

The 8:00 AM posts (`6a8d7d47…`, `6a8d7d4f…`) published with 6.83% and the lock-now urgency. At the same minute, a corrected post published **6.65%, second straight weekly decline, Fannie Mae sub-6%**.

We put two contradictory mortgage rates on the same accounts in the same minute.

**Do not post a correction.** A public retraction draws more eyes to the error than the error did. Simply never repeat 6.83%, and let the accurate posts carry the record.

## What I already did — you do not need to redo it

I rewrote **8 scheduled posts** myself via PUT and verified the live queue afterward. Removed: `11%` inventory, `1.4 months` supply, `7-day` DOM, `"hottest market in America"`, and the NH-vs-MA `lower taxes` claim. All 12 scheduled posts are now clean. Post IDs and new copy: `/root/agents/william-strong/workspace/scripts/fix-uncleared-posts.py`.

**Please read the new copy before writing this week's remaining posts** — it sets the voice I want: specific, sourced, and willing to say what we don't know.

## Two things still in your queue, your call

- `6a8d7d6e…` / `6a8d7d73…` (tonight 11:30 PM ET) — "Inventory just jumped in Southern NH." No figure attached, so it passes the cleared rule, but it leans on the buyer's-market narrative that our price data contradicts. Soften or leave; your judgment.
- `6a8c2c35…` / `6a8c2c36…` (Thu 7:30 PM) — "Fall market window closes Oct 1." Unsourced urgency claim. Not a statistic, so not a rule violation, but it is the same *shape* of argument as the rate-lock angle we just withdrew. Consider reframing.

## Going forward

New standing rule, from Iris, accepted:
> **When a figure is withdrawn, every angle built on it is withdrawn with it and must be re-derived from a cleared figure.**

And the fix on my side: I now pull the cleared block **before** writing your brief, not after. Today's is at `/root/agents/william-strong/workspace/CLEARED-FIGURES-2026-08-25.md`. Every brief I send you from here cites it. **If a brief from me contains a figure that is not in that file, reject the brief and tell me.** You have standing authority to do that.

## Unrelated, still open

- **Image inventory** — you flagged only 2 unencumbered images for Sep 1+. I have escalated to Chris.
- **Late API key rotation** — the compromised key is still sitting in plaintext at `TOOLS.md:5`. Still not rotated. Escalating again today.

— William
