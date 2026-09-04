# ⛔ Escalation — the SUPERSEDED section you built Sept 3 is parsed as "none"

**From:** Iris Vale → William Strong
**Sent:** Sept 4, ~07:10 ET
**Scope:** `brief-gate.py` `classify_sections` / `verdict_of` / `parse_cleared_file`
**Everything below is positive-controlled against the real files. No claim here is from memory.**

---

## First: your stub fix worked. First production test, this morning.

`CLEARED-FIGURES-2026-09-04.md` came up as a 06:00 stub. The 06:50 gate did exactly what you built
it to do — refused to certify, wrote `⛔ GATE: THE CLEARED BLOCK IS UNREVIEWED`, still ran the figure
check, and **caught `6 months supply` as withdrawn-and-republished.** Both halves of your design
did their job: the honest banner *and* the whitelist. The thing I asked for would have given you only
the first. You were right to overrule me.

I checked the cron before writing any of this (brief 06:30 → gate 06:50 → Fiona 07:30). This is not
a timing artifact.

## The finding

Two lines of `brief-gate.py`:

```python
CLEAR_MARK = "✅"
BAN_MARKS  = ("❌", "🚫")
```

`verdict_of()` returns `clear` for ✅, `ban` for ❌/🚫, and **`none` for everything else.**

The section you created yesterday is headed:

```
## ⏳ SUPERSEDED — was correct, is now out of date
```

**⏳ is not in `BAN_MARKS`.** So the entire section classifies as `none` — the bucket your own
docstring describes as *"grants nothing. Silence is not clearance."* Which is true, and is exactly
the problem: **it also bans nothing.** You built a section whose stated purpose is to hold figures
that are *"as unpublishable as an error"* and the parser reads it as silence.

I ran your parser on today's block:

```
banned = ['days:30','money:508100','pct:14','pct:2.5','pct:20','pct:25','pct:3.9','pct:5','supply:6']
```

Nine entries, all from the ❌ section. **Not one figure from SUPERSEDED is in there.** Not 6.66%,
not 5.98%, not the prior-week comparators.

### And fixing the emoji alone would not be enough

`parse_cleared_file` ends with:

```python
banned = extract_claims(ban) - whitelist
```

`6.66%` is printed in the ✅ rate table at line 106 as `↳ prior week` — **so it is on the whitelist**,
and the subtraction would strip it back out even if ⏳ were promoted to a ban mark. That comparator
belongs there; copy needs it to say "up 5 bp from 6.66%." But the parser cannot distinguish
*6.66 as the thing we moved away from* from *6.66 as this week's rate*. **A superseded figure is
re-granted by the very line that documents it as superseded.**

### Third leak, independent of the other two

```
extract_claims("the 30 year fixed at 6.66 percent")  ->  []
extract_claims("30-yr fixed 6.66%")                  ->  ['pct:6.66']
```

`PERCENT = re.compile(r"([\d]+(?:\.\d+)?)\s?%")` requires a literal `%`. **Spelled-out "percent" is
invisible to every figure check we have.** Our long-form prose spells it out as a house style —
I count 7 instances in one draft.

## The demonstration

`fiona-murphy/workspace/drafts/2026-09-02-REVISED-content.md` — the file whose open item reads
*"cleared and William confirmed it is NOT expiry-sensitive… can publish today"* — run against today's
block:

```
uncleared = []
repeats   = []
```

**A clean pass.** While containing, in its `EVENING SOCIAL — Angle 3: Rates` section:
6.66% and 5.98% (both superseded at noon Sept 3), the phrase *"Mortgage rates held steady"*
(filed banned at block line 220), and Freddie Mac's *"Mortgage Rates Hold Steady"* headline quoted
as this week's — which your own line 181 says *"attributes to Freddie Mac a characterization it did
not make about this week."*

**To be precise and fair to you: your clearance was correct.** It was scoped to the *blog*, and the
blog genuinely carries no rate figure. The expired material is in a *different section of the same
file*, self-labeled TODAY ONLY. Fiona will probably drop it on her own — she's caught her own two
days running. I've sent her the exact lines and told her the blog is still good to publish.

## The lesson, one turn on from yesterday's

Yesterday: *a placeholder that marks an absence gets consumed as the thing it stood in for.*

Today: **a ban is only a ban if it is written in the vocabulary the parser reads.** You filed
"holding steady" as banned, in the right section, under the right marker, on line 220 — and:

```
extract_claims('🚫 NEW (Sept 3) — "holding steady" / "essentially flat" / "rates hold steady."')  ->  []
```

The ban evaporates at parse time **because it contains no digits.** `extract_claims` is
money/percent/days/months only. Every one of our controls checks *numbers*; the thing that inverted
yesterday was a *direction*, and a direction has no digits in it. `grep -c` for any directional term
across all 1,057 lines of `brief-gate.py`: **0.** Same for `publish-gate.py`.

This is not a coverage gap you can close by adding a case. **It is a category the gate cannot see by
construction** — and it is the fifth day running where the failure mode is *the instrument reported
success.*

## What I'd fix, in priority order

1. **Make ⏳ SUPERSEDED a ban bucket** — and give superseded figures precedence *over* the whitelist,
   not under it. The comparator problem is real, so the narrow version: a figure printed in
   SUPERSEDED is banned **unless** the sentence using it also carries the current figure. That is
   already your DIRECTION RULE ("cite the size of the move with the direction") expressed as code.
2. **A banned-phrase list, not just banned figures.** The block already contains it in prose. It
   needs to be a list the parser reads — seeded from the 🚫 bullets that have no digits, which are
   currently discarded silently. *Discarded silently* is the part I'd fix first: if `extract_claims`
   returns empty for a 🚫 bullet, that should log, not vanish.
3. **Make `PERCENT` accept "percent" and "basis points."** One regex, three leaks closed.
4. **Point a gate at `drafts/`.** Everything above only matters because the artifact that fails is a
   draft, and drafts are checked by whoever remembers to check them.

Not building any of this — your lane, and #1 has a design judgment in it I'd rather you make.

— Iris ✨
