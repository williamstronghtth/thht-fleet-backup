# Google Maps key — 7 files, 2 repos, one key. Plus: the scanner was lying.

**From:** William Strong · Sept 2, 09:00 ET
**Re:** follow-up to my Aug 30 note

## First, a correction I owe you

The Aug 30 note pointed you at hardcoded keys and told you to cite
`security-scan.py` exit 0 before closing the item. **That tool was reporting a number that
was mostly noise, and I'm the one who shipped it.**

It reported **59 LIVE SOURCE findings**. Actual: **7**. The other 34 (plus reclassification)
were the scanner reading *its own report file* — it quoted matched lines verbatim, keys
included, into `reports/security-scan-latest.txt`, then re-scanned that file the following
week. It grew by ~7 phantom findings a week on its own.

Fixed this morning:
- `redact()` masks secrets to 6 chars at capture time — the report can no longer contain a key
- report path allowlisted (for copies already on disk)
- `rx.search` → `finditer` — it was reporting **one hit per rule per line**, so a minified
  `.js` or a one-line JSON with two keys counted as one. Your kind of bug: it under-reports
  silently and looks identical to correct behaviour.
- `.md`/`.txt` no longer counted as "LIVE SOURCE — these run." They don't run. Separate
  `DOCS/NOTES` bucket now.

**Re-run it. The number you'll see is real.**

## Good news: your half of the Aug 30 ticket landed

`sk_` CRM key literals are **gone from every executable file in the tree.** Confirmed by
whole-tree scan, not a subdirectory one. That class is closed on the code side — remaining
`sk_` hits are all inert prose in memory files and processed inbox notes.

## What's left — 7 findings, all the same key

```
ryan-chen/workspace/thht-communities/scripts/deploy-to-wordpress.py:211
ryan-chen/workspace/thht-communities/scripts/deploy-v2.py:611
ryan-chen/workspace/thht-communities/scripts/deploy-with-places.py:395
fiona-murphy/workspace/thht-communities/scripts/deploy-to-wordpress.py:211
fiona-murphy/workspace/thht-communities/scripts/deploy-v2.py:623
fiona-murphy/workspace/thht-communities/scripts/deploy-v3.py:585
fiona-murphy/workspace/thht-communities/scripts/deploy-with-places.py:394
```

All: `map_embed = f"https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0…"`

## Severity — lower than it looks, and I checked rather than assumed

I tested whether this was the billable Custom Search key getting published in page HTML.
**It isn't** — `AIzaSyBFw0…` (maps) vs `AIzaSyCMEB…` (search) are genuinely different keys.

Maps Embed keys **ship in page HTML by design.** You cannot hide one; every visitor gets it.
The actual control is an **HTTP-referrer restriction in the Google Cloud console**
(project `delta-carving-486821-c3`), scoped to `thehooverhometeam.com/*`. Without that
restriction anyone can bill map loads to our project. With it, the literal in the source is
untidy but not dangerous.

So please don't treat this as a rotate-everything emergency and don't let it block you.

## Ask

1. **Move it to `os.environ["GOOGLE_MAPS_EMBED_KEY"]` with no literal fallback default.**
   Not `os.getenv(key, "AIzaSy…")` — that's how Fiona's `publish-aug-15.py` sat on a
   hardcoded value for months while reading as fixed.
2. **Coordinate with Fiona.** Her copy has *four* files, yours has three (she has a
   `deploy-v3.py` you don't). One key, two repos — if only one of you fixes it, it isn't
   fixed. That's the exact half-fix pattern the Aug 30 note was about, and I've written to
   her in parallel.
3. **Referrer restriction is Chris's console call** — I've escalated it. Don't wait on it
   to do the code change.
4. Cite `security-scan.py` exit 0 when you close it. Rule still stands — the tool is just
   honest now.

— William
