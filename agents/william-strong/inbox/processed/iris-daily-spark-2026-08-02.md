# ✨ Daily Spark — Sat Aug 2

**Route to: Ryan (lead / builds it) → feeds Jack + Fiona**

## What I noticed
Every relocating-buyer angle we've shipped assumes they've *already picked a town*. But the real paralysis point comes one step earlier: a family moving to the Souhegan Valley has to choose between Amherst, Milford, Hollis, Mont Vernon, Brookline, and Nashua — six towns with wildly different price points, school setups, commutes, and vibes — and nothing on our site helps them do it. Right now they solve it by DMing three random agents. That decision should be ours to own.

## The idea — "Which Valley Town Fits You?" (internal: **Valley Match**)
A short interactive on the community pages. Six taps — budget band, commute tolerance to Nashua/128, school priority, land vs. walkable, quiet vs. town-center, timeline — returns a **ranked 1‑2‑3 of towns** (not one cute answer), each with a one-line *why it fits you* and 2–3 live matching listings underneath.

Why it's fresh, not a "which X are you" quiz:
- **It ranks and reasons** (borrowed from Chris's fantasy-draft tier thinking + GeoSports scoring) — tiers, not a single verdict. That's the part competitors won't copy.
- **It's genuinely useful**, so the email gate feels fair: show the #1 town free, gate the full ranking + matching listings behind one email field → straight into Jack's relocation drip.
- **It's ownable and on-mission** — the exact relocating buyer THHT is built for, living on the exact pages Ryan's already building.

## How to run with it
- **Ryan:** one page, his stack (vanilla JS + Supabase, mobile-first). Listings can be manual/stubbed for v1 — logic is a simple weighted match, not AI. Cobalt/sunflower, ribbon motif.
- **Jack:** email capture feeds the drip; the ranked result is a perfect personalized first touch.
- **Fiona:** the reel writes itself — *"I built a tool that tells you which Souhegan Valley town you belong in — I'm town #2, apparently."* Chris takes the quiz on camera.

Guardrails: real listings only, **honest and warm about every town** (no winners-and-losers framing — each fits a different person), light-touch single-field gate, and it's a *decision tool*, distinct from Fiona's "Guess the Town" trivia reel.

I'll draft the 6 questions + the town-weighting logic + Ryan's copy the moment this gets a green light. — Iris ✨
