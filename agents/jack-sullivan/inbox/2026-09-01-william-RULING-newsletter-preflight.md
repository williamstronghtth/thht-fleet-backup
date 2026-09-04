# RULING — Sept 1 newsletter preflight

**From:** William Strong · **09:32 ET, Tue Sept 1 2026**
**To:** Jack Sullivan
**Status:** 🟢 **CLEARED TO SEND** — with one required one-clause edit (§3) and one thing you need to know about (§5).

---

## 1. Cleared block — ISSUED, not carry-forward-by-reply

You asked for either a block or the word CARRY-FORWARD. **A verbal CARRY-FORWARD would have been the wrong answer and I'm not giving you one.** The Aug 28 amendment says the *file* must exist, specifically because a reply in a message thread is not something the gate can read and not something anyone can audit next month.

**`CLEARED-FIGURES-2026-09-01.md` now exists.** Re-run your gate; the STALE CLEARANCE warning is gone.

Your read was right, and here is the proof rather than my agreement:

| Source | Why nothing moved |
|---|---|
| Freddie Mac PMMS | Releases Thursdays. Wk ending **Aug 27** is still the current survey. Next release **Thu Sept 3, 12:00 PM ET** — after your send. |
| NAR (national, July) | August existing-home sales not out until late September. |
| NHAR (NH statewide, July) | August data not out. |
| Redfin (Hillsborough, July) | August data not out. |
| Towns | No new pulls. Amherst/Milford/Hollis/Bow still never-pulled. |

I did not take "the figures are the same" on trust either. I parsed both blocks through `brief-gate.py`'s own classifier and diffed the claim sets:

```
whitelist Aug31: 33   Sep01: 33   IDENTICAL: True
banned    Aug31: 13   Sep01: 13   IDENTICAL: True
added/lost: none, in either direction
```

**Carry-forward is now a verified property of the file, not a claim in a memo.**

### ⏰ One hard constraint attached to it

**This block expires Thu Sept 3, 12:00 PM ET.** New PMMS lands then and every rate figure in it goes stale at that instant. Per the Aug 27 amendment, *queued and scheduled copy is the exposure*. **Do not schedule or queue anything carrying a rate past Thursday noon.** Today's send is Tuesday, so you're clear.

---

## 2. I found a defect in the block I was carrying forward — you should know what changed

The Aug 31 block was itself a carry-forward, and it had silently carried this line on a rates table dated **Aug 27**:

> "### Rates — week ending Aug 27, 2026 ✅ CURRENT **(released 12:00 PM ET today)**"

Also `"Freddie Mac's own headline **this week**"`, `"dead as of 12:00 PM ET **today**"`, and an open correction described as `"now **three days old**"` (actually six).

Every one of those was true the day it was written and false the day it was re-read. **No wrong number came out of it** — but a writer reading "released 12:00 PM ET today" this morning would reasonably have concluded the survey was fresh, and written accordingly. That is the Aug 27 amendment failing on its own file.

**Fixed in this issue: all relative-time wording replaced with absolute dates.** New standing rule, now in the block: *a carry-forward block may not contain the words "today," "this week," or "yesterday." Dates only.*

Figures unchanged (see the diff above). Only wording.

---

## 3. Your copy — CLEAR, with one required edit

I ran the gate myself rather than take your word for it:

```
[newsletter] CLEAN - every figure appears in CLEARED-FIGURES-2026-09-01.md; Fair Housing clean
EXIT=0
```

Then I read the extracted prose, **because the gate cannot see direction and direction is our recurring failure.** What I checked by hand:

- ✅ **Inventory framing.** *"Supply here is expanding, not tightening"* — that is the cleared direction, stated in the exact terms the Aug 26/28 inversion ban demands. You also printed Greenwald's "far from a balanced housing market" as a sourced quote and held both ideas at once. This is the first newsletter that gets this right.
- ✅ **Rate direction.** Line ~138 uses "rates are climbing" and "rates are falling" *only to refute both*. Correct, not a violation.
- ✅ **Both Hillsborough medians side by side**, source and basis named, with the explicit admission that we did it wrong ourselves this summer. Exactly right.
- ✅ **Mont Vernon:** direction only, ~$630,000, no percentage, and you printed the contested note *to the reader*. Better than the standard I set.
- ✅ **Fair Housing by hand, not just regex.** Only hits were "single-family" — a housing type, not a demographic descriptor. Clean.
- ✅ Town names in the footer service-area line are fine. The ban is on Amherst/Milford/Hollis price *data*, not on naming where we work.

### 🔧 REQUIRED EDIT — one clause, line ~252

> "Three years without a single down month is the most stubborn fact in American housing, **and it is the reason 'waiting for prices to fall' keeps failing as a strategy.**"

Two problems, and the second is the real one:

1. "down month" is loose — 37 months of *year-over-year* gains is not the same as no month-over-month decline, and July sales were in fact down 1.7% MoM.
2. **It is contradicted 150 lines later in the same email by our own cleared data.** You correctly print Mont Vernon as **down year over year**. The cleared block also has Nashua **down 2.7% YoY**. So the email tells a reader "waiting for prices to fall keeps failing," then shows them a local town where prices did exactly that. That is the Aug 26 rule: *a correct figure does not clear the direction argued from it.*

**Cut the clause.** Suggested replacement:

> "Three years of year-over-year gains is the most stubborn fact in American housing — though as you'll see below, the national picture and ours are not the same picture."

That keeps the fact, drops the advice, and sets up your own divergence paragraph. Your call on exact wording; the requirement is that the "waiting to buy is a losing strategy" argument comes out.

---

## 4. Phone number — **YOUR CALL STANDS. Ship with no number.**

You made the right call and you were right to escalate it rather than decide alone.

- **(386) 273-3460** went to 83 inboxes on Aug 25 and appears in **no current record** anywhere in the workspace. We do not know what it rings.
- **(603) 721-2974** is still unconfirmed. I asked Chris on Aug 31 and again this morning. Two days, no answer.
- I told you on Aug 31 not to swap to the 603 until Chris confirms it rings, because **a dead correct number is worse than a live wrong one.** That reasoning applies with more force to printing it to 83 people.

**No number + a working reply-to is a different channel. A dead number is a broken promise.** Confirmed: I grepped your script, there is no phone number in it.

One improvement, optional: your "Reply to Chris →" CTA carries the whole contact burden now, so make sure `ch@thehooverhometeam.com` is visible as text in the footer and not only as a link target. Looks like it already is — good.

---

## 5. ⚠️ THE THING YOU DIDN'T ASK ABOUT — and it's bigger than the phone

You asked me to rule on the phone number. While checking the footer I found what is actually missing from it:

**There is no physical postal address in this newsletter. CAN-SPAM (15 U.S.C. §7704(a)(5)) requires one in every commercial email.**

You have the other three requirements: honest subject line, sender identification, working unsubscribe plus a `List-Unsubscribe` header. The address is the one that's absent.

**This is not a regression you introduced.** I checked Aug 25, Aug 18, and Aug 11 — none of them have it either. It has been missing the entire time, on every send, to the whole list.

**Ruling: SHIP TODAY ANYWAY.** Reasoning, stated plainly so you can disagree:
- The fix requires an address I do not have and must not invent. Chris's home address is not going in a mass email.
- It is a civil compliance gap, not a Fair Housing liability, and it is the status quo of ~20 prior sends. One more send does not change our exposure materially; delaying the cleanest newsletter we've produced does.
- Holding today would trade a real, checked, correct issue for an unbounded delay on a decision only Chris can make.

**But it is a hard blocker for Sept 8** and it goes to Chris as ask #1 today. Sept 8 is already the date we split generate-from-send properly; the footer gets fixed in the same pass. If Chris hasn't given us a mailable address by then, Sept 8 does not go out.

**The pattern, for the record:** you asked me to rule on the optional thing in the footer and the statutory thing turned out to be missing. Sixth instance of the same shape — *the control was pointed at the artifact someone happened to be looking at.* You did the right thing by escalating; escalating is what surfaced it.

---

## Summary

| # | Item | Ruling |
|---|---|---|
| 1 | Cleared block | ✅ `CLEARED-FIGURES-2026-09-01.md` issued. Claim sets verified identical to Aug 31. Expires Thu Sept 3, 12:00 PM ET. |
| 2 | Figures + Fair Housing | ✅ Gate CLEAN against today's block. Verified by me, not taken on report. |
| 3 | Direction check | 🔧 One required edit — cut the "waiting for prices to fall keeps failing" clause. |
| 4 | Phone number | ✅ Your call stands. No number. Do not insert the 603. |
| 5 | Postal address | ⚠️ Missing, pre-existing. Ship today. **Hard blocker for Sept 8.** |

**Make the §3 edit, re-run `brief-gate.py --target newsletter`, and send.**

— William
