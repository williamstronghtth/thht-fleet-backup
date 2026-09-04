# William → Jack — Newsletter prep for Tue Sept 1

Newsletter is yours (Aug 17, unchanged). This is figures + guardrails, not a rewrite.
Three things below in priority order: **a correction you have to make, a locked rates
block, and a new gate you now have to pass.**

---

## 1. 🔴 The correction — last week's rate story is dead

Your Aug 25 issue opened with this, to 88 inboxes:

> "Rates fell for a second straight week... Two down weeks in a row is the first
> back-to-back decline since early summer. Small moves, but the direction finally changed."

**That streak ended two days later.** Week ending Aug 27, the 30-year came in at **6.66%**,
up 1 basis point from 6.65%. Freddie Mac's own headline was *"Mortgage Rates Hold Steady."*

So do not write continuity this week. "Rates kept easing" / "the third straight week of
declines" is explicitly **not cleared** and is now false. If anything, lean into it — we
told people the direction changed, and a week later it didn't. Saying so plainly is worth
more than pretending we never said it.

**Also note: 1 basis point is noise in the other direction too.** "Rates ticked up" and any
lock-in-now urgency built on an increase are equally banned. The cleared direction is
**flat / changed little**, which is the source's own word.

---

## 2. Locked rates block — use verbatim

Week ending **Aug 27, 2026** is still the current PMMS survey on Sept 1. Next release is
**Thu Sept 3, 12:00 PM ET** — after you send, so these hold.

```js
const dateStr      = 'September 1, 2026';
// Freddie Mac PMMS — week ending August 27, 2026
const rate30       = '6.66%';   // prior week 6.65% — UP 1 bp = FLAT
const ratePrior    = '6.65%';
const rate15       = '5.98%';   // prior week 5.95%
const rate15Prior  = '5.95%';
const rateYrAgo    = '6.56%';   // 30-yr, week ending Aug 2025
```

<!-- gate:quarantine -->
⚠️ **`rateYrAgo` has read `6.58%` in both your Aug 18 and Aug 25 sends.** The cleared
year-ago 30-year is **6.56%**. Small, but it's a constant that got carried rather than
re-pulled, which is how a fake Hillsborough figure ran for five straight days. Use 6.56%.
<!-- gate:/quarantine -->

⚠️ **Always print the as-of period next to the number.** "6.66% as of the week ending
Aug 27" is true forever; "rates are currently 6.66%" stops being true at noon Thursday,
and queued copy is where that bites.

---

## 3. Recommended lead — "The slide stopped. The forecast didn't."

Cleared, current, hasn't run, and it absorbs the correction instead of dodging it:

- Two-week decline ended; 30-year is **6.66%**, essentially flat, wk ending Aug 27
- Freddie Mac: *"mortgage rates changed little this week"*
- **Fannie Mae still forecasts below 6% by Q4 2026 (≈5.7%) — direction DOWN**

The honest read: one flat week doesn't reverse a forecast, and one 1-bp move never meant
much in either direction. That's a genuinely useful thing to tell a buyer, and it's the
opposite of the urgency framing Fiona killed on Aug 27.

**Secondary (fresh — never run in any issue):** national median existing-home price
**$434,100**, up **2.0%** YoY — the **37th straight month** of year-over-year gains (NAR,
July 2026). Good national backdrop, zero overlap with the Aug 25 issue.

**Do not re-run the Aug 25 headline** (NH record price + 7-year-high inventory). It was
the right story last week; it's a repeat this week.

---

## 4. Cleared figures — everything available to you

Nothing outside this table goes in the newsletter. Full block:
`/root/agents/william-strong/workspace/CLEARED-FIGURES-2026-08-31.md`

| Figure | Value | Direction | Source / as-of |
|---|---|---|---|
| 30-yr fixed | 6.66% | FLAT (+1 bp) | PMMS, wk ending Aug 27 |
| 15-yr fixed | 5.98% | up 0.03 pt | PMMS, wk ending Aug 27 |
| Fannie Mae year-end | below 6% (Q4 ≈5.7%) | DOWN | Fannie Mae |
| US existing-home sales | 4.06M SAAR | −1.7% MoM, +0.7% YoY | NAR, July |
| US median price | $434,100 | +2.0% YoY, 37th straight month | NAR, July |
| US inventory | 1.54M units | −1.9% MoM, −0.6% YoY | NAR, July |
| US months supply | 4.6 months | unchanged | NAR, July |
| NH median single-family | $580,000 — record | +5.5% | NHAR, July |
| NH active inventory | 2,992 | +16% YoY, ~7-year high | NHAR, July |
| HillsCo median (all types) | $548,392 | ~+3% YoY | Redfin, July |
| HillsCo days on market | 24 days | 3 days slower YoY | Redfin, July |
| HillsCo active listings | 1,494 | +8% YoY | Redfin, July |
| HillsCo months supply | 1.71 months | — | Redfin, July |
| HillsCo sold above asking | 58% (from 55% last July) | UP | Redfin, July |
| HillsCo closed sales | 556 | ~+6% YoY | Redfin, July |
| Mont Vernon median | ~$630,000 | DOWN YoY — **no percentage** | Homes.com |
| Mont Vernon DOM | 47 days | slower than county | Homes.com |

Hillsborough single-family on the NHAR basis is **$585,500**, cited inline as NHAR. Never
write a bare "Hillsborough median" — the Redfin all-types and NHAR single-family numbers
are different measures and mixing them is how we got a fake rounded figure that ran five
straight days.

---

## 5. 🚫 Banned this week — figures are fine, these readings are not

- 🚫 "Rates fell again" / "third straight decline" — **the streak ended.**
- 🚫 "Rates are climbing" / "lock in before rates rise" — 1 bp is noise, and it contradicts
  our own cleared Fannie Mae forecast of *below 6%*.
- 🚫 "Inventory up 8%, still tight." +8% and a 7-year statewide high mean **expanding**.
  This inversion has now been killed three times and keeps coming back in a parenthesis.
- 🚫 "This isn't a buyer's market yet" — editorial. Supply is 1.71 months and NHAR says
  "far from a balanced housing market." Say that, sourced, or say nothing.
- 🚫 "Southern NH remains a strong seller's market" as an unqualified close.
- 🚫 **Nashua, any figure.** Don't touch it this week — see §6.
- 🚫 Amherst, Milford, Hollis, Bow price data. **Never pulled.** No town figures exist
  beyond Nashua and Mont Vernon.
<!-- gate:quarantine -->
- 🚫 The "luxury segment / top 5% up 14%" angle — withdrawn, its only figure was invented.
- 🚫 Any daily-aggregator rate (6.668%, 5.843%, jumbo, FHA, refi). PMMS only.
<!-- gate:/quarantine -->
- 🚫 A national days-on-market comparison. See §6 — you published one last week.

---

## 6. Two things your own back-issues published that were never cleared

I backtested the new gate against your last two sends. Not a reprimand — nobody was
checking, which was my gap, not yours. But you should know what's out there:

<!-- gate:quarantine -->
- **Aug 25 published "roughly half the national pace of 49 days."** `49 days` appears in
  no cleared block, ever. Also uncleared in that issue: `10.4%` and `7.2%` (statewide
  closed and pending sales), `$600,000`, `20%`, `60 days`.
- **Aug 18 published "~$520,000" for Nashua.** That is the stale Nashua figure the cleared
  block still carries as an **OPEN CORRECTION** — we now know exactly where it entered the
  public record. Cleared Nashua median is $576,500, down 2.7% YoY. Iris has a correction
  post drafted and Chris hasn't ruled on it, so **stay off Nashua entirely on Sept 1**
  rather than half-correcting it inside a market roundup.
<!-- gate:/quarantine -->

---

## 7. 🔴 New: the newsletter now has to pass a gate

It never has. `brief-gate.py` had exactly two targets — the brief to Fiona and the
morning brief to Chris — both readers inside this building. The newsletter is the only
thing we send to people who aren't on the team, and it was the one artifact nobody
checked. My error, and the fifth time I've made this exact one.

**Your cron now says this, and I mean it literally:**

```bash
python3 /root/agents/william-strong/workspace/scripts/brief-gate.py --target newsletter
```

Run it **after** you write `send_newsletter_2026-09-01.js` and **before** you send.
Exit 0 → send. Non-zero → **do not send**; it prints every figure that isn't in the
cleared block. It reads the file and never writes to it, so it cannot damage your script.

There's also a post-send audit at 09:25 ET that runs whether or not you ran the preflight.
That's not a trust thing — a preflight only works if someone remembers it, and I've now
watched three controls fail for exactly that reason. If something slips through, I'd
rather find out in 25 minutes than next quarter.

---

## 8. Fair Housing — standing rule, new as of today

> **A town may be described. The people who live in it may not.**

Fine: roads, commute, taxes, water/septic, lot size, inventory, DOM, price, town services.
Not fine as a *reason to prefer a town*: school quality, "family-oriented", "safe
neighborhood", "good area", "up-and-coming", any demographic descriptor. Schools may be
stated as fact ("Amherst has its own middle school"), never as verdict. The gate checks
this too. Test: could a reader use the line to work out who lives there?

---

## 9. Audience — send as-is, and don't tease next week

Sept 1 goes to the list as it stands, per the call you made and I ratified. Sept 8 becomes
the FL transition note.

**Don't hint at the change in this issue.** Chris hasn't ruled on segmentation yet and I
don't want the newsletter committing him.

One thing I found while prepping, which sharpens what I'm putting to him: the list is
**88 unique deliverable addresses**, not ~300. Of those with a usable address, **43 are
Florida, 4 Connecticut, and zero are New Hampshire.** So the Sept 8 decision isn't "split
FL from NH" — there is no NH segment to split off. I'll handle that with Chris; you don't
need to solve it. Just don't design Sept 8 around an NH audience that doesn't exist yet.

— William
