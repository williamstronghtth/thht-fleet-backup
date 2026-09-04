#!/usr/bin/env python3
"""Test fair_housing.py against real failures and real safe copy.

The must-IGNORE set matters more than the must-CATCH set. A checker that
flags honest town content gets switched off within a week, and a gate that is
off is worse than no gate because everyone believes it is running.

Run: python3 test-fair-housing.py
Exit 0 = all pass.
"""

import sys

import fair_housing as fh

# ---------------------------------------------------------------------------
# 1. The actual lines from daily-content-brief-2026-08-31.md.
#    These shipped to Fiona. Every one must be caught.
# ---------------------------------------------------------------------------
REAL_FAILURES = [
    '  - **Amherst:** ~$647,000 (premium for schools, lot size, character)',
    '- **Content:** Highlight families who moved TO schools they love in '
    'Amherst, Nashua, Salem districts',
    '3. **"Amherst schools don\'t compromise."** Neither do we. $647K median'
    '—premium for a reason.',
    '  - Amherst home at $647K (4BR/3BA, 1+ acres, top schools)',
    '2. **"$500K in Southern NH = Your Choice."** Merrimack for new '
    'construction. Nashua for walkability. Amherst for schools.',
    # Added 2026-09-01 — found by the back-catalog audit, not by review.
    # Both lines were LIVE in the Mont Vernon video description (published
    # Aug 3, still up 29 days later) and both slipped the gate as first
    # written: "raise a family" had no pattern at all, and bare-noun "safety"
    # in an amenity list never touched a place noun for the safety rule to
    # anchor on. These are regression locks, not hypotheticals.
    'If you are a family looking for space, safety, strong small schools, '
    'and a slower pace, Mont Vernon deserves a spot on your list.',
    '- Why Mont Vernon is a wonderful place to raise a family',

    # Added 2026-09-02 — the Sept 2 content brief to Fiona. scan() returned
    # ZERO findings on the file these came from; Iris found them by reading.
    # Not one contains an evaluative word, which is exactly why the
    # verdict-based rules above could not see them: the steer is carried by
    # the NOUN. Every line below is verbatim from the withdrawn brief.
    'Families who spent the long weekend in NH — visiting, driving through, '
    'staying at bed & breakfasts — now think differently about what "home" '
    'feels like.',
    "Mont Vernon's quiet, low-traffic layout, community feel, and school "
    'reopening week create a moment to speak to transplant intent.',
    '- 5-minute school commute from most homes (verify: K–6 consolidation '
    'on Beard Road)',
    '- Labor Day to Labor Day: one-year marker for families who moved in '
    'last September',
    '**Tone:** Warmth, recognition, belonging.',
    'September is Nashua\'s busiest month for families relocating before '
    'school starts (Sept 4).',
    'Now is the moment to own the "move before school opens" narrative.',
    '- Nashua school choice (SACS calendar, magnet schools, proximity to '
    'NH public universities)',
    '- Families repositioning from neighboring states (MA, VT, Maine)',
    '- Out-of-state buyer trend: Boston-area families priced out, moving '
    'north to NH',
]

# ---------------------------------------------------------------------------
# 2. Phrasings that must be caught even though we have not written them yet.
# ---------------------------------------------------------------------------
MUST_CATCH = [
    "This home is perfect for families with young children.",
    "A quiet, family-friendly street.",
    "One of the safest neighborhoods in Hillsborough County.",
    "A really good area to raise a family.",
    "An up-and-coming neighborhood with lots of potential.",
    "Walking distance to three churches.",
    "An exclusive enclave off Route 101.",
    "Great for young professionals and empty nesters.",
    "This is an adult community.",
    "A diverse neighborhood with lots of character.",
    "Award-winning schools within walking distance.",
    "Blue-ribbon schools are the reason people move here.",
    "Buyers pay a premium for the schools.",
    "Not suitable for wheelchair users.",
    "The perfect bachelor pad downtown.",
    "Ideal for English-speaking buyers.",
    "A traditional community that has not changed in decades.",
    "Move to Amherst for the schools.",
    "Families relocate here for the school district.",
    "Highly-rated schools nearby.",
]

# ---------------------------------------------------------------------------
# 3. Honest copy that MUST NOT be flagged. Real sentences from the reissued
#    brief and from published town content.
# ---------------------------------------------------------------------------
MUST_IGNORE = [
    "Amherst has its own middle school.",
    "The high school is on Route 101.",
    "Souhegan High School serves Amherst and Mont Vernon.",
    "Homes in Mont Vernon take 47 days to sell. County average is 24.",
    "Nashua's median is $576,500 — down 2.7% from last year.",
    "30-year fixed is 6.66%. Last week it was 6.65%.",
    "2,992 homes for sale across New Hampshire.",
    "Hillsborough County has 1,494 homes listed, up 8% from last year.",
    "The property sits on 1.2 acres with a three-bay garage.",
    "Well water and a septic system, both serviced in 2024.",
    "The town holds its transfer station open Saturdays.",
    "Purgatory Falls is a fifteen-minute drive.",
    "This town is not for you if you want a five-minute commute.",
    "The driveway is steep and unpaved — plan for winter.",
    "Property tax rates are set town by town in New Hampshire.",
    "Lamson Farm hosts the town's fall festival.",
    "A 4-bedroom colonial with a renovated kitchen.",
    "The Souhegan River runs through Milford.",
    "Route 101A is the main commuter artery toward Nashua.",
    "Chris moved to Mont Vernon on July 1, 2026.",
    # Mentions steering without containing any steering phrase.
    "This is steering by proxy and must never ship.",
    # Added 2026-09-01 alongside the bare-noun "safety" rule. This is
    # ordinary transaction vocabulary. If the safety rule ever starts
    # flagging these, it has become noise and someone will mute it — which
    # is worse than not having the rule.
    "The safety inspection is scheduled for Tuesday.",
    "Sellers want the safety disclosure returned by Friday.",
    "We provide a safety report with every listing.",
    "Buyers should review the safety code requirements.",
    # Added 2026-09-02 with the demographic-subject and school-amenity rules.
    # These are the sentences those rules must NOT eat. The new rules are the
    # broadest in the file — they match bare nouns — so the false-positive
    # floor matters more here than anywhere else. A gate that flags ordinary
    # market writing gets muted, and a muted gate is worse than no gate.
    "Demand in the $500K–$600K band held through August.",
    "Buyers who toured in July are still active.",
    "Households in that price range have more choice than a year ago.",
    "The middle school is on Beard Road.",
    "Souhegan High School is a fifteen-minute drive from the town center.",
    "The school district boundary is on Route 101.",
    "Closings tend to cluster in September across Hillsborough County.",
    "Inventory rose 16% year over year statewide.",
    "Two families are listed as co-owners on the deed.",
    "The town meeting approved the school budget in March.",
]

# ---------------------------------------------------------------------------
# 4. Guardrail prose — our own rules, which must not trip the rules they teach.
# ---------------------------------------------------------------------------
MUST_IGNORE_GUARDRAIL = [
    "❌ School quality as a reason to prefer a town",
    '- ❌ "family-oriented" · "safe neighborhood" · "good area"',
    "🚫 Banned today: any claim that a town has good schools",
    "✅ Roads, commute, taxes, lot size, inventory, DOM, price",
]

# ---------------------------------------------------------------------------
# 5. Guardrail prose written WITHOUT a marker. These ARE flagged, and that is
#    the correct, deliberate behaviour — not a defect.
#
#    "Never describe an area as a safe neighborhood" is structurally identical
#    to a violation. The only way to tell them apart is to guess from
#    vocabulary ("never", "don't", "avoid") — and v1 did exactly that, which
#    silently disabled the rule for "Amherst schools don't compromise", the
#    worst line in the brief that caused this file to exist.
#
#    The costs are wildly asymmetric:
#      false positive on our own rules -> a human sees L42, marks it, moves on
#      false negative on live copy      -> a Fair Housing complaint
#
#    So: bias toward flagging, and require authors to MARK guardrail prose
#    (❌ 🚫 ✅) or put it under a Fair Housing heading. Both are deliberate
#    acts by the author, not inferences by the checker.
# ---------------------------------------------------------------------------
EXPECTED_FALSE_POSITIVES = [
    "Never describe an area as a safe neighborhood.",
    "Do not use family-friendly in any listing copy.",
]

# ---------------------------------------------------------------------------
# 6. HTML MARKUP must not manufacture violations. (added 2026-09-02)
#
#    Every line below is verbatim from a DELIVERED newsletter. Each one was
#    reported as a BLOCK by the back-catalog audit, and each was a lie: the
#    "adjective" was the tag name `<strong>`. Nine of the 49 findings put in
#    front of Chris as a disclosure decision were this.
#
#    The cost of THIS false positive is unusually high. It does not just
#    annoy an author — it inflates a compliance-exposure number that a human
#    is making a legal-ish disclosure decision on. An overstated number burns
#    the credibility of the gate as fast as an understated one.
# ---------------------------------------------------------------------------
MUST_IGNORE_MARKUP = [
    '<p style="margin:0 0 6px;"><strong>The school that justifies the '
    'premium:</strong></p>',
    '<td style="padding:10px"><strong>Bedford</strong></td>'
    '<td style="padding:10px">School enrollment: 4,200</td>',
    'Mont Vernon Village School is ranked <strong>#11 of 224 NH elementary '
    'schools</strong>.',
    # Adjacent table cells must not fuse into a violation across the boundary.
    '<td>Strong</td><td>Schools open Sept 3</td>',
    '<li><strong>Milford</strong> — the middle school is on Route 101.</li>',
]

# ---------------------------------------------------------------------------
# 7. Markup must not HIDE a real violation either. Same root cause, opposite
#    direction: tags spend the [^.!?\n]{0,30} character budget, pushing a
#    genuine match outside the window. Neutralization has to restore these.
# ---------------------------------------------------------------------------
MUST_CATCH_PREDICATE = [
    # Verbatim from live/published copy, found by hand-reading remediated
    # files on 2026-09-02. Every school rule written before this required the
    # adjective BEFORE the noun, so all three were invisible.
    'Southern NH remains one of the most sought-after regions for Boston '
    'commuters. Schools are still excellent. Communities are still charming.',
    '<p>Why? Schools are top 5 percent in the state, town character is '
    'exceptional, and there is proximity to everything.</p>',
    '<p>Schools are strong, the downtown is vibrant, and you can actually '
    'afford to live here.</p>',
    # Bare audience labels — no following verb, so the Sept 2 rule missed them.
    '### The School-Year Connection (For Families)',
    '- best small towns in southern New Hampshire for families',
]

MUST_CATCH_THROUGH_MARKUP = [
    '<p>Amherst has <strong style="color:#c00">top-rated</strong> '
    'schools.</p>',
    '<p>A wonderful place to <em>raise a family</em>.</p>',
    '<p>Amherst schools <strong>don&#39;t compromise</strong>.</p>',
    '<p><strong>Families who</strong> are relocating this fall.</p>',
]

# Whole-document check: guardrail sections under a Fair Housing heading are
# exempt, so the reissued brief must pass cleanly end to end.
GUARDRAIL_SECTION_DOC = """\
## Three angles

Homes in Mont Vernon take 47 days to sell. County average is 24.

## Fair Housing — standing rule

A town may be described. The people who live in it may not.
Never write "safe neighborhood", "family-oriented", or "good area".
Do not use school quality as a reason to prefer a town.

## Cadence

Angle 1 anchors the 9 AM slot.
"""


def run_group(name, cases, expect_catch):
    """Return list of failure strings for one group."""
    failures = []
    for text in cases:
        findings = fh.scan(text)
        caught = fh.has_blockers(findings)
        if expect_catch and not caught:
            failures.append(f"  MISSED   [{name}] {text[:80]}")
        elif not expect_catch and caught:
            hit = findings[0]
            failures.append(
                f"  FALSE +  [{name}] {text[:60]}\n"
                f"           tripped [{hit['label']}] on \"{hit['excerpt']}\""
            )
    return failures


def main():
    groups = [
        ("real-aug31", REAL_FAILURES, True),
        ("must-catch", MUST_CATCH, True),
        ("must-ignore", MUST_IGNORE, False),
        ("guardrail-marked", MUST_IGNORE_GUARDRAIL, False),
        # Documented, deliberate: unmarked guardrail prose IS flagged.
        ("expected-fp", EXPECTED_FALSE_POSITIVES, True),
        ("markup-not-prose", MUST_IGNORE_MARKUP, False),
        ("catch-through-markup", MUST_CATCH_THROUGH_MARKUP, True),
        ("predicate-verdict", MUST_CATCH_PREDICATE, True),
        # The predicate rule must not swallow factual predicates about
        # schools, which are exactly what the FACT/VERDICT split permits.
        ("predicate-factual", [
            "Schools are located on Route 101.",
            "Schools are open starting September 3.",
            "The schools are administered by SAU 37.",
            "Buses for families and staff run from the village common.",
        ], False),
    ]
    all_failures = []
    total = 0
    for name, cases, expect in groups:
        total += len(cases)
        all_failures.extend(run_group(name, cases, expect))

    # Every violation on a line must be counted, not just the first.
    # A newsletter paragraph is ONE line of HTML; `search` stopped at the
    # first hit per rule and silently dropped the rest, undercounting the
    # delivered-newsletter exposure. Three distinct verdicts, one line.
    total += 1
    multi = ("Amherst has top-rated schools, Bedford has excellent schools, "
             "and Hollis has great schools")
    n_verdicts = len([f for f in fh.scan(multi)
                      if f["label"] == "schools as verdict"])
    if n_verdicts < 3:
        all_failures.append(
            f"  UNDERCOUNT [multi-match] reported {n_verdicts} of 3 verdicts "
            f"on one line — scan() must use finditer, not search"
        )

    # Section-level exemption: a Fair Housing heading covers its whole section,
    # while surrounding content is still scanned.
    total += 1
    section_findings = fh.scan(GUARDRAIL_SECTION_DOC)
    if fh.has_blockers(section_findings):
        hit = section_findings[0]
        all_failures.append(
            f"  FALSE +  [guardrail-section] L{hit['line']} "
            f"[{hit['label']}] \"{hit['excerpt']}\" — a Fair Housing heading "
            f"must exempt its entire section"
        )

    if all_failures:
        print(f"FAIL — {len(all_failures)} of {total} cases wrong:\n")
        print("\n".join(all_failures))
        return 1

    print(f"PASS — {total} cases.")
    print(f"  {len(REAL_FAILURES)} real Aug 31 failures caught")
    print(f"  {len(MUST_CATCH)} synthetic steering phrasings caught")
    print(f"  {len(MUST_IGNORE)} honest sentences left alone")
    print(f"  {len(MUST_IGNORE_GUARDRAIL)} marked guardrail lines exempt")
    print(f"  {len(EXPECTED_FALSE_POSITIVES)} unmarked guardrail lines flagged "
          f"(deliberate — see comment)")
    print("  1 guardrail SECTION exempt, surrounding content still scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
