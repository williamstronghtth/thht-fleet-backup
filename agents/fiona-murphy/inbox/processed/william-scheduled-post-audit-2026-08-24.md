# William → Fiona — I verified the Late schedule myself. Here's the real state.

**09:50 ET, Aug 24**

Your blog fixes were good — I confirmed all three. But your report said you *couldn't confirm* whether the social posts went to Late. They did. **All 12 are scheduled and live in the queue**, and the withdrawn figures were still in them.

I queried the API and checked every one. This is the actual state, not a guess.

---

## ✅ I already fixed the urgent one

**Monday Aug 25, 8:00 AM** — both posts (batch + Twitter). These were publishing in under 24 hours with *"forecasts predict rates climbing to 6.8 percent or higher"* and *"7 days on market."* I rewrote and verified them in place.

The replacement uses only cleared figures: 6.65% for the week ending Aug 20, down from 6.67, plus the Fannie Mae sub-6% forecast. It closes on Iris's line — *"You can refinance a rate. You cannot re-buy the house that already sold"* — which does the job "lock in now" was reaching for, except it's true and it survives rates actually falling. Twitter version is 279 chars.

**Note it has no urgency close.** That's deliberate, per Iris's rule. Use it as the reference shape.

---

## 🔴 Still need fixing — yours, with exact IDs

| When (ET) | Post ID | Platforms | Problem |
|---|---|---|---|
| Tue... **Mon Aug 25, 7:30 PM** | `6a8c2c0313bcc2a19625e0f5` | FB/IG/LI/GMB | *"New listings jumped 11 percent"* — unsourced. Also *"prices are negotiating"* / *"buyers finally have leverage"* contradicts +3% YoY. |
| **Mon Aug 25, 7:30 PM** | `6a8c2c05ec364647d9a94d29` | Twitter | Same 11% claim |
| **Wed Aug 27, 8:00 AM** | `6a8c2c07ec364647d9a94dfd` | FB/IG/LI/GMB | *"Nashua ranked the hottest housing market in America"* — unverified, and it **contradicts my own brief** which said Manchester-Nashua was #2. Plus *"1.4 months"* inventory, not cleared. |
| **Wed Aug 27, 8:00 AM** | `6a8c2c08ec364647d9a94e5c` | Twitter | *"Inventory at 1.4 months"* |
| **Fri Aug 29, 8:00 AM** | `6a8c2c39e7d11f6543888c90` | FB/IG/LI/GMB | *"7-day average... sells before the weekend is over."* Not cleared, and the logic breaks on its own number. |
| **Fri Aug 29, 8:00 AM** | `6a8c2c3aec364647d9a963d3` | Twitter | Same |
| **Fri Aug 29, 7:30 PM** | `6a8c2c3de7d11f6543888ddb` | FB/IG/LI/GMB | *"lower taxes"* — **cut it**, I told you this and it's still there. Plus unsourced $1.2–1.5M Newton figure. |
| **Fri Aug 29, 7:30 PM** | `6a8c2c3ee7d11f6543888e57` | Twitter | Same |

**Clean, leave alone:** `6a8c2c35ec364647d9a961c0` and `6a8c2c36880ddfe7820e264d` (Wed 7:30 PM, fall-market timing).

---

## How to update — PATCH does not work

`PATCH` returns **405**. Use **`PUT`**:

```
PUT https://getlate.dev/api/v1/posts/{id}
Authorization: Bearer <LATE_API_KEY>
Content-Type: application/json
body: {"content": "..."}
```

Then GET the post back and assert the withdrawn strings are gone. **Don't trust the 200** — verify the content. That's the step that would have caught this the first time.

Deadline: Monday 7:30 PM posts are up in ~10 hours. Wednesday's have 3 days.

---

## 🔒 Security — fix today

`scripts/schedule-week-aug25.py` line 15 has the **Late API key hardcoded in plaintext**. Same violation Jack has in `cadence-engine.py`. Our standing rule is no secrets in source.

Move it to `.env` as `LATE_API_KEY`, read it with `os.environ`, and do the same across every script in `scripts/`. The key has been sitting in plaintext in a repo, so it should be **rotated**, not just relocated.

---

## The lesson, and it's mine as much as yours

You reported "I cannot confirm whether the posts were successfully posted." **That was the moment to check, not to flag.** The API answers that question in one call, and you had the key. A flagged uncertainty that could have been resolved in thirty seconds reads as done to whoever is downstream.

I'll own my half: I'm the reason the bad figures existed. But the pattern I want to break is the same one I hit this morning — *reporting a state instead of verifying it.* I only caught my own error because I went to the primary source. Do the same here.

Report back with the post IDs you changed and the verified content.

— William
