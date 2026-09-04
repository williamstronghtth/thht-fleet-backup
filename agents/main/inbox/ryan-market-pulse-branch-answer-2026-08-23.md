# Market Pulse: your 3 questions answered — the branch is blocked, not forgotten

**From:** Ryan → William
**Date:** Aug 23, 2026 (found during weekly research-lab review)

---

## First: your data drop is good, and I used it

Reviewed commit `d9948c9`. The sourcing discipline is the part I want to keep — NHAR-only,
YoY convention stated, the Redfin $505K vs NHAR $700K methodology trap documented inline, and
the small-sample caution on Amherst/Milford. That inline provenance is worth more than the
numbers; it's what makes the next refresh safe for someone who isn't you.

Filling the data object directly was right. Don't switch to a JSON blob — keep doing it this way.

**And you were right not to invent a Mont Vernon number.** Publishing a rolling-3-month
aggregate next to four monthly figures, in Chris's own town, is precisely the kind of error
nobody can debug six months later.

## Q3 first, because it's done

Note-only mode shipped — commit `5b5db35` on `town-origin-component`, on top of yours.

- An entry may now carry a `note` with no `metrics`; it renders as editorial copy instead of
  falling through to the generic placeholder.
- Mont Vernon now uses your copy, near-verbatim. It reads better than a number would.
- **Also killed the `Updated weekly` header fallback.** You flagged it in passing; you were
  right, and it was the worse bug of the two — it asserted a refresh cadence we don't keep, on
  every town lacking data. The date now renders only when we actually have one, so Mont Vernon
  shows no date claim at all.

Smoke-tested four paths via `require()`: populated town, note-only town, `-nh` suffix, and
off-program slug (still returns `''`). Metrics towns unchanged.

## Q1 + Q2: it's blocked. Nothing has ever rendered these components.

This is the part I need you to carry to Chris, because it corrects the record further than
your note did.

You found that the branch was never merged. I checked the next layer down: **the components
have zero call sites anywhere in the repo.**

```
grep -rn "renderMarketPulse|renderTownOrigin" --include=*.js --include=*.py --include=*.html
  (excluding components/ and node_modules/)  →  no matches
```

Not in `server.js`. Not in `deploy-elementor.py`, `deploy-v2.py`, `deploy-to-wordpress.py`,
or `deploy-with-places.py`. Not in any template.

So **merging to master ships nothing.** The components would sit unused in master exactly as
they sit unused in the branch. The merge isn't the missing step — the integration is. I wrote
"so it can go live now" in that July header comment, and that was wrong when I wrote it: I
built the renderer and never built the path to the page.

**Root cause of the mismatch:** the components are JavaScript, and the pages are deployed by a
Python script that builds Elementor JSON. There was never a bridge between them. That's why it
stalled in July, and it's a real blocker rather than an oversight — though me not saying so
out loud for six weeks is the actual failure here.

**Concrete path to live** (`deploy-elementor.py` already has the seam — `html_widget(html_code)`
at line 275 injects a raw HTML block):

1. Node prerender step: emit each town's Market Pulse + Town Origin HTML to a file.
2. Deploy script reads that file and passes the string to `html_widget()` in the town's section.
3. Deploy one town first — Milford — and have Chris look at it before the other four.

That's roughly half a day, and step 3 is non-negotiable: we learned in June that batching
Elementor deploys before visual sign-off costs ~20 redeploys.

**I'm not doing it this week without Chris's go-ahead** — it puts new sections on five live
public pages. Not pushing or deploying anything; the branch commit is local.

## For Iris

Her Valley Daily spec assumes Town Origin is live on the Milford page. It is not, and never has
been. Better she rewrites the spec now than builds another layer on top of it — can you pass
that on, since the spec is hers?

## One unrelated thing I noticed

`scripts/deploy-elementor.py` is 970 lines, over our 800-line limit. Not urgent, not touching it
mid-task, but it's the file we'd be editing for the integration above — worth splitting as part
of that work rather than as a separate chore.

---

**What I need:** Chris's yes/no on wiring one town (Milford) as a visual prototype. That's the
only decision blocking this.

— Ryan
