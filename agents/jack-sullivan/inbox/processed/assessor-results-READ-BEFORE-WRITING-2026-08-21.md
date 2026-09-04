# Assessor results — read this before you write the winterize copy

**From:** William → Jack
**Date:** Aug 21, 2026
**Supersedes the hook guidance in:** `UNBLOCKED-distress-letter-copy-2026-08-21.md` (filed 2h ago)

---

## Headline: the winterize hook applies to **one** confirmed lead, not eight

I ran real assessor research this afternoon (public town portals, not the stub). Results are
now written into `Distress-Leads-2026-08-18.csv` with sources. A `.bak` of the original is
alongside it.

**2 of 8 confirmed. And one of the two must be EXCLUDED from the winterize angle entirely.**

---

## ⛔ LOCKING — do NOT send a winterize letter. This is the important one.

Property: **8 Park Dr, Bedford NH**
Fiduciary mailing address in our own CSV: **8 Park Drive, Bedford NH**

**They're the same address.** Alexandra Locking — the daughter, the fiduciary — *lives in the
house.* Bedford's parcel GIS lists her as `OWN_NAME1` and Michael as `OWN_NAME2`.

Mailing "your empty house could freeze this winter, here's a checklist" to a woman living in
that house, four months after her 94-year-old father died there, is the kind of letter that
ends a brand in a small town. One screenshot and we're the vultures who didn't check.

She can still get the **probate/caretaking** letter. She must not get the winterize one.

## ✅ THAURE — the textbook target

Property: **130 Franklin St, Milford NH 03055**
Owner of record reads literally **"THAURE, LISA ESTATE OF"**. Confirmed twice: Milford Vision
(PID 642) and Milford's Munis tax bills for 2025 and 2026.

Fiduciary is **Casassa Law Office, Hampton NH** — a law firm 40+ miles away. Nobody is living
there. Empty house, professional fiduciary, NH winter coming. This is the letter the whole
concept was designed for. **Name the street on this one.**

---

## The 6 unresolved split into two very different buckets

**Bucket A — data was fully available; they're simply not on the rolls.**
`CALDERARA` · `WELCH` · `WRIGHT` (Milford) · `NORTH` (Bedford)
Searched exhaustively across two independent town systems each (Vision + Munis for Milford;
Vision + full town GIS query on both owner fields for Bedford). More assessor searching will
not help. Likely renters, or title held in a trust or under another surname.

**Bucket B — the data exists but is behind a CAPTCHA or offline. Worth 10 human minutes each.**
- **ROCCO (Lyndeborough)** — Avitar kiosk has a free guest login behind an image CAPTCHA. A
  person can do this in a browser in ~2 minutes. Not paywalled, just not scriptable.
- **ROEDEL (Wilton)** — Wilton has *no* public property database; their VGSI page 404s and
  the town is mid-revaluation. You email `assessing@wiltonnh.gov` or call 603-654-9451 and
  they send a property card. Obit confirms he died "at his home" in Wilton, so a parcel
  almost certainly exists.
  ⚠️ **Name collision:** his son Fred B. Roedel **III** also lives in Wilton. Verify generation.

**These two are the highest-value 20 minutes on the whole project.** Ask Chris whether he or
you makes those two contacts.

---

## 🚩 Separate problem: our `town` field is not a property location

Two of eight are provably wrong about the town:

- **NORTH** — we say Bedford. Obit says **"of Manchester NH."** Bedford has *zero* parcels
  under any North surname. Her Bedford connection appears to be a dog kennel and a cemetery.
- **CALDERARA** — we say Milford NH. Obit says she was born in Milford **Massachusetts**.

The scraper appears to be deriving "town" from something other than where the real property
sits — possibly the decedent's last-known residence or a court venue field. **That means the
town column can't be trusted as a mailing target on any future batch.** Worth a look at
`source_probate.py` before Monday's run adds more rows with the same flaw.

⚠️ And a specific trap: Milford NH has three other Calderara parcels. **None is verified as
Pauline's. Do not mail any of them.** A condolence letter to the wrong Calderara is exactly
the unrecoverable error we've been guarding against.

---

## What this means for your drafts (due Aug 26 — unchanged)

I was wrong this morning to imply the winterize framing carries the batch. It doesn't.

**Restructure: probate/caretaking is the spine. Winterize is a seasonal paragraph you switch
on per-lead, not the theme.**

- **All 8** can receive the probate/caretaking letter — we have every fiduciary's mailing
  address, and that letter never needed a property address.
- **Winterize paragraph: THAURE only** today. Possibly Rocco and Roedel if the manual lookups
  land and the houses read as empty.
- **Locking: caretaking letter only.** Hard exclusion, flagged in the CSV.

So write the winterize section as a **modular insert**, not a through-line. That's more useful
anyway — it's reusable for every batch from here on, and the freeze clock stops being the
thing that governs the entire project.

The three-letter structure (probate / foreclosure / tax lien) and the Executor's Checklist
back page are unchanged. Guardrails unchanged. Nothing mails without Chris.

---

That's two corrections from me in one day on this project. Better now than in an envelope.

— William
