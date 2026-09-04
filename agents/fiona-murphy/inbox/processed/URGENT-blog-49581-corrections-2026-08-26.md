# URGENT — Blog post 49581 has factual errors. Fix today.

**From:** William Strong · Aug 26, 09:20 ET
**Post:** https://thehooverhometeam.com/new-hampshire-home-prices-record-2026/ (ID 49581, PUBLISHED)

This is not your fault. **The errors came from my brief.** I wrote it, you built from it in good faith. I'm fixing the source; this is the cleanup.

Two things before the edits:

1. Your memory file lists my figures under the heading **"Market data (CLEARED)"**. They were not cleared. Only the $580,000 state median was. Mont Vernon $635K, the 13.3% inventory number, Nashua $549,900, Amherst $654,900, Milford $595,000, and 47 days — **none** of those are in `CLEARED-FIGURES-2026-08-25.md`. Please don't mark anything "CLEARED" unless you have read it in that file yourself.
2. You were given authority yesterday to reject any brief of mine containing an uncleared figure. You couldn't use it because **nobody gave you the cleared file to check against.** That's my failure, not yours. Fixed below.

---

## Edit 1 — the inventory claim is backwards (most important)

**Current text:**
> Yet New Hampshire home prices have not softened. Why? Because even with a 13% increase, inventory remains historically low.

**Problem:** NHAR reports **2,992 active listings in July 2026, up 16% YoY — the highest in roughly seven years / a post-pandemic peak.** "Historically low" is the opposite of what the source says. Also, "13.3% through May" is *new listings* for a different month, used in an article about July.

**Replace with:**
> Yet New Hampshire home prices have not softened. That is the genuinely interesting part, because inventory is not scarce anymore. NHAR counted 2,992 homes actively for sale in July 2026, up 16% from a year earlier and the highest level in about seven years. Supply is rising and prices are still setting records — which tells you demand is absorbing the new listings rather than being satisfied by them. NHAR president Josh Greenwald put it plainly: inventory is improving, but the state is "far from a balanced housing market."

Delete the "Through May 2026, new listings were up 13.3%" sentence entirely. Wrong month, wrong metric.

## Edit 2 — the town table mixes three different metrics

**Current text:**
> Mont Vernon: $635,000 median (47 days to sale)
> Nashua: $549,900 median list price
> Amherst: $654,900 average
> Milford: $595,000 average
> These are solid, mixed markets with breadth across price tiers and buyer profiles. No flash bubble, no distress, just steady, strong demand.

**Problems:** median vs. *list* price vs. *average* in one table, presented as comparable — they aren't. And Mont Vernon and Nashua are both **declining**, which the surrounding copy claims is "strong demand."

**Replace the whole block with:**
> The county-level number hides more than it reveals, and the honest version is that our towns are not moving together.
>
> Hillsborough County's median was $548,392 across all home types in July, up about 3% year over year, with homes selling in a median of 24 days (Redfin, July 2026). But Nashua's median came in at $576,500 — **down 2.7%** from a year ago and its lowest since March. Mont Vernon, where my own family is moving next summer, sits around $630,000 and is **also down** year over year, with homes taking roughly 47 days to sell — about twice the county pace.
>
> That is not a distressed market. It is a market where the town you are in matters more than the county you are in. If you price a Mont Vernon or Nashua home off county comps right now, you will sit.

**Do not** publish Amherst or Milford figures. I have not sourced them and neither have you.

## Edit 3 — soften the buyer section

Section 5 says "If you're waiting for prices to drop 10 or 15 percent, that's not the dynamic in play." Given Nashua −2.7% and Mont Vernon down 4–7%, that sentence is defensible for the state but wrong for two of our four towns.

**Add after it:**
> Town by town, though, some prices *have* come down. Nashua and Mont Vernon are both below where they were a year ago. If those are your towns, you have more room than the statewide headline suggests.

---

## Your standing veto — now usable

`CLEARED-FIGURES-2026-08-26.md` is in my workspace and readable by you:
`/root/agents/william-strong/workspace/CLEARED-FIGURES-2026-08-26.md`

**From today: read that file before you build anything from my brief.** If a number in my brief is not in that file, do not publish it — reject the brief back to me and say which figure. You will not be second-guessed for doing this, and you will not be blamed for a delayed post. You *will* be covered if a wrong number goes out because you checked and I overrode you.

There is also now an automated gate (`brief-gate.py`) that flags uncleared figures in my brief before you ever see it. If you get a brief with a `⛔ GATE` header, that's the machine, not me. Trust it.

## Report back

Reply in your memory + inbox with: which edits you applied, the post revision ID, and anything you disagreed with. I'll verify against the live page myself.

— William
