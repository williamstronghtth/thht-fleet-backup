# Source 2 replaced: mypublicnotices → Nashua Telegraph + Milford Cabinet

**From:** Ryan Chen · 2026-08-24 · Chris approved the replacement this morning.

## What changed in `distress-pipeline/`

- **NEW** `source_nashua_telegraph.py`, `notice_pdf.py`, `notice_classify.py`
- **RETIRED** `source_mypublicnotices.py` → `retired/` (kept for provenance, not imported)
- **EDITED** `run_monday.py` (wiring), `config.py` (URLs), `http_util.py`, `store.py`, `digest.py`, `README.md`

`verify_wall.py` green after every change. Full `DISTRESS_DRY_RUN=1 run_monday.py`
passes; `data/master.jsonl` byte-identical before/after (no store pollution).

## Why this source

`nh.mypublicnotices.com` is NXDOMAIN on every host variant and produced **zero
records in its lifetime**. `publicnoticeads.com` looked like the obvious statewide
substitute — it resolves and returns 200, but it now serves a **GoDaddy placeholder
page**, not notices. The old Telegraph path in config 404s; the live one is
`/news/public-notice/`.

The win is the **Milford Cabinet**, which publishes on that same page. It's the
Souhegan Valley weekly — Milford, Amherst, Mont Vernon, Wilton, Lyndeborough,
Brookline, Hollis. A Cabinet-only notice never appears in the Manchester Union
Leader, so this closes a genuine coverage hole rather than just restoring a link.

## Three things worth your attention

1. **Don't "fix" the S3 TLS by disabling verification.** Notice PDFs sit at
   `ogden_images.s3.amazonaws.com`; the underscore means Python's `ssl` won't match
   the `*.s3.amazonaws.com` wildcard, while curl will — so a curl spot-check passes
   and the pipeline fails. The fix is `http_util.s3_path_style()`, which rewrites to
   `s3.amazonaws.com/ogden_images/...` for an exact CN match. Verification stays ON.
   This is exactly the temptation that put `CERT_NONE` into four files.

2. **`pdftotext -layout` would have fabricated leads.** These are 6-column
   broadsheet pages; in `-layout` mode one output line interleaves unrelated
   notices, so a town name from column 1 lands beside a notice in column 3.
   Extraction uses default reading-order mode. Documented in `notice_pdf.py`.

3. **Precision was the actual work.** The 2026-08-23 issue contains "Notice of
   Foreclosure of Lien" — a tow company auctioning seven cars under RSA 262 — plus a
   Mont Vernon Planning Board driveway hearing. Naive keyword matching ships both as
   distressed homeowners. Vehicle (RSA 262) and storage (RSA 451-C) liens are
   unconditional vetoes; municipal board/hearing/RFP notices are vetoed unless
   strong RSA 479 language is present. Exclusions run before inclusions.

## Validation (production data, both directions)

- **Precision:** 6 live issues, 183 notices → 19 excluded, **each one hand-read** and
  correct (zoning agendas, tow auctions, selectmen hearings). 0 qualifying — an
  honest zero, which independently confirms the "no new leads" answer Chris got.
- **Recall:** 10 real Union Leader notices → 8/8 foreclosures classified, 0 false
  positives. Necessary because the new source itself yields nothing yet, and a
  source that always returns `[]` is indistinguishable from a broken one.

## Bug fixed in your `store.py`

`record_key()` returned `"|"` for any record with **neither** address nor owner, so
all such records collapsed onto one key and silently overwrote each other. Added a
`notice_uid` fallback (sha1 of the notice text — deliberately not the block index,
which shifts if poppler's reading-order heuristic changes). Existing records all
have addresses, so no keys changed.

## New in Chris's email

A coverage line: `📖 nashua_telegraph: 6/6 issues read, 183 notices scanned, 19
excluded as non-distress, 0 out of area, 0 in scope.` After the stale-probate week,
a quiet source and a broken source should not look the same to him.

## Open / needs a decision

- **Chris's call:** Superior Court **quiet-title** citations (e.g. *Town of Hudson v
  Unknown Persons, 79 Highland St*) — real property distress, but the defendant is
  "unknown persons", so there's nobody to mail. Asked him; not collected for now.
- The notice index holds only ~6 issues and has **no pagination** — no back-catalogue
  to seed from.
- No Cabinet/Telegraph issue since 2026-08-01 has carried a qualifying notice, so the
  positive path is proved by test, not yet in production. If `in scope` is still 0
  after ~8 weeks, question the filter, not the market.
- **`distress-pipeline/` is entirely untracked in git** — no history, no backup. It
  needs a `.gitignore` for `data/` first (client PII). Your workspace, your call —
  flagging, not acting.
- Still open from earlier: auctioneer listing parser (the monthly hash-diff is
  structurally invalid), Avitar/AxisGIS assessor resolver for the 7 uncovered towns.

— Ryan
