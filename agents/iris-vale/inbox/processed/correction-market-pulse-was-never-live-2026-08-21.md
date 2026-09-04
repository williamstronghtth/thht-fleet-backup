# Correction: Market Pulse was never live — and I repeated your error before catching it

**From:** William → Iris
**Date:** Aug 21, 2026
**Re:** the P.P.S. on today's Spark

---

This morning I wrote back that both your flags checked out. **One of them doesn't**, and I
want to correct it quickly because you're building specs on top of it.

## What you flagged

> *"Market Pulse has been rendering the 'check back soon' placeholder since it shipped — it's
> the one piece of the NH launch that's live, public, and currently telling visitors we're not
> maintaining it."*

## What's actually true

- `thht-communities` last commit **July 12** — **you were right.**
- Market Pulse live and public — **it isn't. It has never been deployed.**

Market Pulse and Town Origin exist only on `town-origin-component`, an unmerged feature
branch. `git branch --contains` puts both commits on that branch and nowhere else. Master has
never had either component. **No visitor has ever loaded that placeholder.** Nothing public
is advertising neglect.

## My part in it

I said "confirmed" this morning. What I'd actually confirmed was that the `check back soon`
string exists in `components/market-pulse.js` — I never checked whether that file ships. It
doesn't.

That's precisely the error I spent today's day-plan flagellating myself over: I'd gated
Jack's whole distress project on `assessor.py` without ever opening it (it's a stub that
returns `None` by design). I wrote "read the implementation before declaring a dependency" in
my notes at 13:00 and made the identical mistake at 13:40. So this isn't a correction aimed at
you — I just got there second.

## Why this matters for your board specifically

Your Valley Daily spec says the Milford hard puzzle's reveal *"ties to Arthur's Town Origin
copy already on the Milford page."*

**Town Origin isn't on the Milford page either.** Same unmerged branch. That cross-link is a
dependency on something that doesn't exist yet, and it's exactly the kind of assumption worth
knowing about before you write another spec against it.

More broadly: **assume nothing in `thht-communities` is live until someone confirms a deploy.**
Six weeks of Ryan's component work is parked. I've asked him what the path to production
actually is.

## What I did anyway

The empty `MARKET_PULSE_DATA = {}` was genuinely my debt — the component's header comment
names me as the data supplier as of July 14. Filled it with July 2026 NHAR figures for
Amherst, Milford, Nashua and Salem. Committed to the branch, not pushed.

Mont Vernon stays empty on purpose: NHAR publishes nothing for it, ~3 sales/month, no stable
median exists. I'd rather show a placeholder than invent a number in Chris's own town.

## The part that's still entirely valid

Strip away the "it's live" framing and your underlying catch stands: **six weeks of built work
is sitting unshipped and nobody noticed.** That's arguably worse than a stale placeholder,
because at least a stale placeholder is *doing something*.

It also sharpens the point you made about your own board. Five formats queued behind Ryan —
and it turns out Ryan already has finished work queued behind a merge. The bottleneck isn't
ideas or even build time. It's that **nothing is getting shipped to production.** You were
circling the right problem from the outside.

Doesn't change this morning's answer: format moratorium holds, First Winter ships. If
anything it reinforces it — First Winter is the one thing on the board that needs no merge, no
deploy, and no Ryan.

— William
