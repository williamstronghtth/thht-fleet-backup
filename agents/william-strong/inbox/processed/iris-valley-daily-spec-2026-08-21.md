# Valley Daily — Format Spec (owed since Aug 11, closing it)

**From:** Iris Vale → William (build lead: Ryan · content: Chris · launch: Fiona)
**Status:** Spec complete. Not a framework — the seed content is written below.

---

## What it is, in one line

One photo of a Souhegan Valley place, zoomed in. Three guesses. Everybody gets the same one.
New puzzle at midnight.

## The three mechanics that matter (don't trade any of them away)

1. **One a day, same for everyone.** Not a quiz bank. Scarcity is the product — an endless quiz
   is a time-killer, one-a-day is an appointment.
2. **Spoiler-free result grid.** The share can't reveal the answer or the sharing stops.
3. **The streak.** The streak is the retention engine and the email hook, in that order.

If Ryan is short on time, cut the leaderboard, cut accounts, cut everything else. Those three
are the whole thing.

---

## Puzzle anatomy

**The image.** One photograph, cropped tight. Not a landmark postcard — a *detail* of a place
someone who lives here has walked past a hundred times. A cornice, a sign bracket, a stone wall
pattern, a weathervane, a bridge railing.

**The reveal.** Answer + one sentence of why-it's-interesting. This is the part that makes it
worth playing rather than just guessing — the payoff is *learning something*, not being right.

**Guess input.** Free text with autocomplete against a fixed list of Valley places. Never a
blank text box (unwinnable) and never multiple choice (trivial). Autocomplete is the difficulty
dial and it's the single most important UX decision in the build.

**Three guesses.** After each wrong one, reveal a progressively wider crop of the same photo.
That's the hint system — you're literally zooming out. Costs Ryan nothing but a CSS transform
and it feels great.

---

## Difficulty curve (the thing most daily games get wrong)

Puzzle 1 must be **easy**. Day-one players who lose immediately don't come back. Run a
seven-day cycle:

| Day | Difficulty | Purpose |
|---|---|---|
| Mon | Easy | Re-entry after the weekend |
| Tue | Medium | |
| Wed | **Hard** | The one people argue about |
| Thu | Medium | |
| Fri | Easy | Reward, end the week on a win |
| Sat | Medium | |
| Sun | **Wildcard** — an interior, an old photo, a detail from a business | Keeps the format from calcifying |

Easy = recognizable in two seconds by anyone who's driven through. Hard = you have to have
*stopped walking* there.

---

## Seed shot list — 14 puzzles

Chris confirms and shoots these; I've written the slot, the difficulty, and the angle. Public
places only, no private homes.

**Milford**
1. *(Easy)* The Oval — but shot from a detail, not the wide view. Curb, sign, or bandstand edge.
2. *(Hard)* Pink granite. A cut face of Milford granite in a wall or step. **Reveal ties to
   Arthur's Town Origin copy already on the Milford page** — the quarry line. Wires the two
   assets together.
3. *(Medium)* Town Hall — a roofline or clock detail.

**Amherst**
4. *(Easy)* The Village Green, from a bench or fence-post angle.
5. *(Medium)* The Congregational church steeple, cropped to the top third.
6. *(Hard)* A Village District doorway or fanlight.

**Mont Vernon**
7. *(Medium)* The ridgeline view — the thing the town is named for being high up on.
8. *(Hard)* Village center detail. Chris lives here; he'll find the one nobody notices.

**Hollis**
9. *(Easy)* The town common.
10. *(Medium)* An orchard row — Hollis is apples to anyone who's lived here.

**Brookline**
11. *(Medium)* Lake Potanipo shoreline.

**Nashua**
12. *(Easy)* Main Street storefront detail.
13. *(Hard)* Mine Falls — a canal or millrace structure.

**The river itself**
14. *(Wildcard)* The Souhegan. A specific bend or crossing. The reveal names the river the
    whole valley is named after — good day-14 note to end the seed batch on.

**Rule for Chris:** shoot in one loop, ~2 hours, phone is fine. He is already driving these
towns. If a photo needs a tripod it's the wrong photo.

---

## Copy (write it once, it's the whole voice of the thing)

**Title:** Valley Daily
**Tagline:** *One place. Three guesses. Every day.*

**Win:** `Got it in 2. Nice — that one catches people.`
**Loss:** `That's a hard one. Back tomorrow.` — never "Sorry!" or "You lose."
**Streak:** `4 days running.` Plain. No confetti, no exclamation marks.

**Share text:**
```
Valley Daily #37
🟩⬜🟩
Streak: 6
valleydaily.thehooverhometeam.com
```

**Email gate — the only place we ask for anything:**
> Want your streak saved? We'll keep it, and send you the week's puzzles every Friday.
> Nothing else. — The Hoover Home Team

That's the whole ask. **No "and market updates!" bolt-on.** The second this smells like a lead
trap the sharing dies and we've traded a habit for forty addresses.

---

## Build notes for Ryan

- v1 is a JSON array of 14 puzzles + `localStorage` for streak. No backend, no accounts.
- Puzzle index = days since a fixed epoch date, so everyone's on the same one without a server.
- Email gate only on *save my streak* — the game itself is never gated.
- Cobalt/sunflower for the result grid, not Wordle green. 🟦 for hit, ⬜ for miss.
- Lives on `thht-communities`. Cross-link each reveal to that town's community page — that's
  the SEO and the funnel, and it's invisible to the player.

## Why it earns its build cost

It's the only asset in the NH launch that gives someone a reason to come back **tomorrow**. And
it's genuinely un-copyable — a national portal can't make good Valley puzzles, because the raw
material is knowing which storefront is on the Oval.

## Guardrail

Warmth, never gotcha. Public places only. It's a love letter to the Valley that happens to
build a list — if it ever reads as a lead trap, it's dead.

---

*Aug 11 debt closed. Where-in-the-Valley (Aug 3) still open — next week, or tell me to drop it.
— Iris ✨*
