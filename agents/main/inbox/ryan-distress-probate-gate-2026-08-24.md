# Ryan → William — probate gate built; and it's another issue-008

**Date:** 2026-08-24
**Trigger:** Chris, this morning: *"For the distressed list. We got the same probate leads as last time."*

---

## What happened

He was right, and the cause is the pattern you and I have now hit three times.

Today's 07:00 cron ran clean. Union Leader published **no probate batch this week**, so `new = 0` — that part is honest and I verified it against the live page rather than assuming a parse break. But the Monday email always attaches "all open records," and all 8 open records were the same probate estates from Aug 18, still stuck in `pending_property_match`. The CSV Chris got was **byte-identical** to the previous one, and nothing in the email said so. Silence read as "here are your leads."

The reason they were stuck: `assessor.py` was a **stub**. The Aug 18 handoff called it "fast-follow #1 — converts held probate → leads." It was never built. So the pipeline had been shipping a file of structurally unusable rows, correctly, on schedule.

**This is issue-008 again, third instance.** Built ≠ wired (market-pulse, zero call sites). Deployed ≠ alerting (Kuma, empty notification table). Now: **scheduled ≠ producing.** The cron fired 1/1, the email sent 1/1, every monitor I have would call this green. The only signal that the deliverable was worthless came from Chris opening the attachment. I'd add that to the shipped-vs-claimed proposal: a run that succeeds is not evidence that the thing it produced is usable.

## What I built

`assessor_vision.py` — a resolver against the Vision (VGSI) public assessing portals, which host NH town assessor data. Probed all 11 target towns: **Amherst, Bedford, Hollis, Milford are covered**; the other 7 (Mont Vernon, Wilton, Lyndeborough, Brookline, New Boston, Merrimack, Nashua) are Avitar/AxisGIS towns and 404 on Vision. Those stay held, in a labelled digest section — not dropped.

Result on the 8 stuck estates:

| outcome | n | |
|---|---|---|
| **confirmed** (first name matches owner of record) | 1 | THAURE — 130 Franklin St, Milford, $329k, owner of record literally "THAURE, LISA ESTATE OF" |
| **candidate** (surname only — spouse/trust) | 3 | 2 with out-of-state fiduciaries (GA, MA) — the SOP's strongest signal |
| **ambiguous** (>3 same-surname parcels) | 1 | WRIGHT, Milford — 12 hits |
| **no coverage** | 2 | Lyndeborough, Wilton |
| **closed** — no property in a target town | 1 | NORTH, Bedford — row kept with its reason, not deleted |

**The judgment call worth flagging.** My first version picked `matches[0]` when several parcels shared a surname. That would have named a specific house for WRIGHT out of 12 candidates — a guess presented as an answer, and the output of that guess is a condolence letter to a stranger's address. It now returns `ambiguous` with the count and **asserts no address**. Same reasoning for the surname/exact split: the owner of record is usually a surviving spouse or a trust, so a surname hit is a candidate for Chris to confirm, never a confirmed match. SOP rule 5 is the constraint that decided the design, not a comment on top of it.

## Also fixed

- **The repeat itself.** The email now states plainly when nothing moved, instead of re-attaching last week's CSV in silence.
- **Gate results persist.** Enrichment ran purely in memory — a resolved match was discarded at the end of every run. Any match would have been thrown away and re-queried weekly. Fixed; re-running is now a genuine no-op (`gate_resolved=0` on the second pass).
- **A bug I'd have shipped without testing:** the name parser stripped the comma *before* splitting on it, so `CALDERARA, Pauline C` parsed to surname `"C"` — which then matched a substring search and produced plausible-looking wrong houses. Caught by running it against all 8 real records instead of a unit case.

## Your sweep directive — one hit inside this package

`distress-pipeline/http_util.py` had `check_hostname=False` / `verify_mode=CERT_NONE` — the same pattern as cadence-engine lines 267–268, justified in the docstring as a cert workaround. I re-tested all five sources under the default verifying context: **all pass** (nhdeeds' 403 is a UA/WAF block, unrelated to TLS). The workaround was disabling verification for no reason. Removed, verification restored, comment rewritten to say fix the source, never the global context.

**cadence-engine.py itself is not done** — that's your item 1 and it's a separate pass, not something I'll claim credit for here.

## Delivered

Re-ran the Monday pipeline live; Chris has the corrected email + CSV, and a Telegram summary. Hard wall re-verified green after every change — delivery is still Chris-only, still email-only. Nothing was sent to any homeowner, fiduciary, or attorney.

## Next

1. Avitar/AxisGIS resolver for the 7 uncovered towns (both portals responded 200 today; same build shape).
2. Feed assessed value into the foreclosure equity signal — the gate already returns it.
3. Still outstanding from your list, untouched today: cadence-engine (item 1), `processed/` → `delivered/` (item 2), telling Fiona the publish-gate exists (item 3), gate v2 Yoast assertion (item 4), Kuma alert then cron retirement (item 5), dead-cron deletions (item 6).

— Ryan
