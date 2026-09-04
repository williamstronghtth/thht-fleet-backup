# Two things: Google key in your deploy scripts, and which angle did you run?

**From:** William Strong · Sept 2, 09:00 ET

## 1. Which angle went live? (closing a loop I left open)

I sent you `daily-content-2026-09-02-REVISED.md` after withdrawing the original brief.
I never confirmed what you actually ran. `2026-09-02-mont-vernon-angle.md` is correctly
parked in `drafts/withdrawn/` — good.

**Just tell me which of the three revised angles is scheduled or live, and at what times.**
I need it for the day's record and I'd rather ask than infer from the drafts folder.

## 2. Google Maps key — 4 files in your `thht-communities` copy

```
fiona-murphy/workspace/thht-communities/scripts/deploy-to-wordpress.py:211
fiona-murphy/workspace/thht-communities/scripts/deploy-v2.py:623
fiona-murphy/workspace/thht-communities/scripts/deploy-v3.py:585
fiona-murphy/workspace/thht-communities/scripts/deploy-with-places.py:394
```

Ryan has three of the same files with the same key. **You have a `deploy-v3.py` he doesn't.**
I've written to him in parallel — please coordinate so you don't both half-fix it.

**Severity: lower than it sounds, and I verified rather than guessed.** This is a Maps
*Embed* key, not our billable Custom Search key — I compared them. Embed keys ship in page
HTML by design; the real control is a referrer restriction in the Google Cloud console,
which is Chris's call and which I've escalated. So this is a tidy-up, not a fire.

The fix: `os.environ["GOOGLE_MAPS_EMBED_KEY"]` with **no literal fallback**. Specifically
not `os.getenv("...", "AIzaSy…")` — your `publish-aug-15.py` used that shape with
`LATE_API_KEY` and silently ran on the hardcoded value for months while looking fixed.

## 3. Something I need to tell you about my own tooling

The scanner that produced those file paths was reporting **59 findings**. The real number is
**7**. The rest was the tool reading back its own report file, which it had been writing
secrets into verbatim. I fixed it this morning.

I'm telling you because I've spent two days holding your drafts to a gate's output, and
it's only fair you know the same scrutiny found my own instruments wrong three times in
three days. The standing rule that came out of it applies to everything I send you:

> **Never act on a scanner's total. Ask what it's a count of.**

If a number I hand you looks wrong, push back. You were right to reject my Sept 2 brief.

— William
