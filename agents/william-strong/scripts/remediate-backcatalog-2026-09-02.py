#!/usr/bin/env python3
"""One-shot Fair Housing remediation of EDITABLE back-catalog copy.

Run date: 2026-09-02. Kept in the repo as the record of what was changed and
why, because these edits alter published marketing copy.

METHOD
------
Every replacement below is hand-authored, exact-match, and fails loudly if the
anchor text is not found. Nothing is regex-rewritten in bulk. A Fair Housing
fix is a judgement about what the sentence was trying to say -- delete the
steer, keep the fact -- and that judgement cannot be made by pattern.

THE RULE APPLIED IN EVERY CASE
------------------------------
    A town may be described. The people who live in it may not.

So: school VERDICTS ("top-rated", "good districts") are cut, never softened.
Where the sentence needed a reason to prefer the town, it is replaced with a
CHECKABLE town fact -- lot size, commute, tax structure, conservation land --
never with a gentler adjective. "Excellent schools" -> "strong schools" would
be a rewording, not a remedy.

NOT TOUCHED
-----------
  * drafts/withdrawn/  -- already pulled 2026-09-02, no exposure to remediate
  * any FIGURE         -- the $514K Nashua median in social-posts-2026-07-29
                          is flagged to Chris separately. Editing a number
                          under cover of a language fix is how a figure gets
                          changed with nobody reviewing it.
"""

import sys
from pathlib import Path

DRAFTS = Path("/root/agents/fiona-murphy/workspace/drafts")

# (filename, exact old text, new text, one-line rationale)
EDITS = [
    # -- school calendar as a buying deadline; familial-status subject -------
    ("2026-08-02-blog-draft.md",
     "If you're relocating to Southern NH for schools, August is also critical "
     "for a different reason. A closing now means you'll have time to move, "
     "unpack, and settle before students return to school. Waiting until "
     "September could mean missing the best school enrollment windows and "
     "disrupting your family's plans.",
     "If you're relocating to Southern NH this fall, August matters for a "
     "practical reason. A closing now leaves time to move, unpack, and settle "
     "before fall listings thin out. Waiting until September generally means "
     "choosing from less inventory, not more.",
     "Removed school-enrollment urgency; kept the inventory-timing argument."),

    ("2026-08-02-evening-post.md",
     "If back-to-school is your deadline, today is your action window.",
     "If you're aiming to be settled before fall inventory thins, here's the "
     "timing math.",
     "School calendar as transaction deadline. Also drops the urgency frame "
     "banned Aug 27 rather than re-housing it in new words."),

    ("2026-08-02-evening-post.md",
     "First day of school is late August. Closing, moving, unpacking, settling "
     "into a new home and new school requires 45 to 60 days. For families "
     "relocating this fall, the decision window closes THIS WEEK.",
     "Closing, moving, unpacking, and settling into a new home typically takes "
     "45 to 60 days. For buyers targeting a fall move-in, that puts the "
     "decision point in early August.",
     "'For families relocating' -> 'for buyers'. Protected class removed as "
     "the subject of the market claim."),

    # -- resident character, safety proxy, familial status ------------------
    ("2026-08-03-mont-vernon-video2-description.md",
     "a real sense of community pride that runs through everything from town "
     "meetings to the local events calendar",
     "an active town meeting schedule and a full local events calendar",
     "A town has a meeting schedule; it does not have pride. Residents do."),

    ("2026-08-03-mont-vernon-video2-description.md",
     "If you are a family looking for space, safety, strong small schools, and "
     "a slower pace",
     "If you are looking for larger lots, a small village school, and a slower "
     "pace",
     "Drops the familial-status address, the bare-noun 'safety' racial proxy, "
     "and the school verdict. 'Small village school' is a countable fact."),

    ("2026-08-03-mont-vernon-video2-description.md",
     "- The culture and community feel of a true small town",
     "- Town meeting government, the general store, and the village common",
     "'Community feel' describes residents. The three replacements are places "
     "and institutions a viewer can verify."),

    ("2026-08-03-mont-vernon-video2-description.md",
     "- Why Mont Vernon is a wonderful place to raise a family",
     "- What daily life in Mont Vernon actually looks like",
     "'Raise a family' is a direct familial-status appeal."),

    ("2026-08-28-wilton-video-packaging.md",
     "Living in Wilton NH: A Small Town Guide for Families Who Want a Slower "
     "Pace",
     "Living in Wilton NH: A Small Town Guide to a Slower Pace",
     "Working title, not yet published, so no SEO cost to changing it."),

    # -- schools as verdict -------------------------------------------------
    ("blog-2026-05-27-just-sold-9-louis-drive.md",
     "driven by top tier schools, conservation land, and a quality of life "
     "that is genuinely hard to replicate",
     "driven by conservation land, large lots, and quick access to the "
     "Massachusetts line",
     "School verdict cut and replaced with checkable town attributes."),

    ("blog-2026-05-27-market-snapshot.md",
     "reflecting the area's proximity to Boston, quality school systems, and "
     "strong appeal to remote workers relocating from Massachusetts",
     "reflecting the area's proximity to Boston, large lot sizes, and steady "
     "demand from remote workers relocating from Massachusetts",
     "'Quality school systems' offered as price justification."),

    ("blog-2026-05-28-just-sold-95-wright-road-hollis.md",
     "offering small-town character, strong schools, and easy access to the "
     "Massachusetts border",
     "offering large lots, conservation land, and easy access to the "
     "Massachusetts border",
     "School verdict cut. 'Small-town character' also removed -- it passes the "
     "checker but is the same unfalsifiable resident-description."),

    ("blog-2026-05-28-market-cooling.md",
     "They're realistic, sustainable prices for quality homes in desirable "
     "neighborhoods.",
     "They're realistic, sustainable prices for well-maintained homes on large "
     "lots.",
     "'Desirable neighborhoods' is an unquantified area-quality judgement."),

    ("blog-2026-05-28-market-cooling.md",
     "The summer market typically sees even more supply as families prepare "
     "for school moves.",
     "The summer market typically sees even more supply as sellers time "
     "listings to the season.",
     "Removes both the familial-status subject and the school-calendar frame."),

    ("blog-2026-06-01-nashua-fastest-growing.md",
     "Nashua offers proximity to the city (under an hour commute), excellent "
     "schools, and lower cost of living than Massachusetts suburbs.",
     "Nashua offers proximity to the city (under an hour commute), no state "
     "income or sales tax, and lower cost of living than Massachusetts "
     "suburbs.",
     "School verdict replaced with NH tax structure -- a genuine, checkable "
     "reason buyers cross the border."),

    ("blog-2026-06-01-nashua-fastest-growing.md",
     "Good schools, strong job market, reliable appreciation, and a growing "
     "community of remote workers who understand the lifestyle you're looking "
     "for.",
     "A diversified job market, reliable appreciation, and steady in-migration "
     "from Massachusetts.",
     "School verdict cut; 'community of people who understand your lifestyle' "
     "is a resident-character claim."),

    ("blog-buyers-market-june-24.md",
     "Still move fast (7-14 days in good school districts), but poorly-priced "
     "homes sit.",
     "Still move fast (7-14 days), but poorly-priced homes sit.",
     "The DOM figure stands on its own; the district qualifier only steered."),

    ("blog-buyers-market-june-24.md",
     "on market data, school district guides, or specific town spotlights",
     "on market data or specific town spotlights",
     "Internal-linking note proposing school-district guides as a content "
     "line. Cut at the source rather than after it is written."),

    ("blog-buyers-market-june-25.md",
     "Let's be clear: well-priced homes in good school districts still move "
     "fast (7-14 days).",
     "Let's be clear: well-priced homes still move fast (7-14 days).",
     "Same verdict as june-24; same fix."),

    ("blog-buyers-market-june-25.md",
     "For remote workers and growing families, Milford offers space, "
     "affordability, and access to top schools. It's the gateway town for "
     "professionals discovering Southern New Hampshire.",
     "Milford offers larger lots, lower price points, and quick access to "
     "Route 101. It's the gateway town for buyers discovering Southern New "
     "Hampshire.",
     "Drops 'growing families' as audience and the school verdict."),

    # -- schools as a property marketing bullet -----------------------------
    ("just-sold-14-boylston-terrace-amherst-nh.md",
     "on a quiet cul-de-sac, with top-rated schools, three heat sources,",
     "on a quiet cul-de-sac, with three heat sources",
     "'Top-rated schools' listed as a property feature."),

    ("just-sold-14-boylston-terrace-amherst-nh.md",
     "<li>Amherst School District, Souhegan High School</li>\n",
     "",
     "School district as a property-detail bullet. Removed rather than "
     "reworded: in a just-sold feature list there is no framing that makes it "
     "a fact rather than an offer."),

    ("just-sold-14-boylston-terrace-amherst-nh.md",
     "buyers who want acreage, privacy, and the Souhegan school district "
     "without sacrificing convenience to Route 101",
     "buyers who want acreage and privacy without sacrificing convenience to "
     "Route 101",
     "District named as a reason to buy."),

    ("just-sold-150-greenville-road-mason-nh.md",
     "- School District: Mason Elementary, Milford Middle School, Milford High "
     "School\n",
     "",
     "Same marketing-bullet pattern as Boylston Terrace."),

    ("just-sold-26-snow-lane-hollis-nh.md",
     "draws buyers who want privacy, acreage, and top tier schools, and "
     "properties that deliver on all three",
     "draws buyers who want privacy and acreage, and properties that deliver "
     "on both",
     "School verdict cut; 'all three' corrected to 'both' so the sentence "
     "still counts correctly."),

    # -- the Mont Vernon town scripts ---------------------------------------
    ("mont-vernon-town-video-scripts.md",
     "The school district is SAU 37. Kids go to Mont Vernon Village School "
     "through eighth grade, then Milford High School for ninth through "
     "twelfth. The school is small, which means your kid is not a number.",
     "The district is SAU 37. Students attend Mont Vernon Village School "
     "through eighth grade, then Milford High School for ninth through "
     "twelfth.",
     "Kept the factual attendance pattern, cut 'your kid is not a number' -- "
     "a familial-status sell dressed as a fact about class size."),

    ("mont-vernon-town-video-scripts.md",
     "It is for families who want a tight-knit school environment and outdoor "
     "access as a real part of daily life.",
     "It suits buyers who want outdoor access as a real part of daily life.",
     "'Families who' as sentence subject + 'tight-knit' resident character."),

    ("mont-vernon-town-video-scripts.md",
     "It is for families who want a tight school community and outdoor access "
     "built into the week, not just the weekend.",
     "It suits buyers who want outdoor access built into the week, not just "
     "the weekend.",
     "Same steer, second script variant."),

    # -- social ------------------------------------------------------------
    ("social-posts-2026-07-29.md",
     "Same access to top schools as pricier towns.",
     "Same commute to Nashua and Manchester as pricier towns.",
     "School verdict swapped for the commute fact that carries the same "
     "value argument honestly."),

    ("social-posts-2026-07-29.md",
     "Top schools, New England charm, 30min to Boston, and actual negotiating "
     "room.",
     "New England charm, 30min to Boston, and actual negotiating room.",
     "School verdict cut. NOTE: the $514K median on this line is NOT touched "
     "-- see the figure question flagged to Chris."),
]


def main():
    applied, failed = 0, []
    by_file = {}
    for fname, old, new, why in EDITS:
        by_file.setdefault(fname, []).append((old, new, why))

    for fname, edits in by_file.items():
        path = DRAFTS / fname
        if not path.exists():
            failed.append(f"MISSING FILE  {fname}")
            continue
        text = original = path.read_text(errors="ignore")
        for old, new, why in edits:
            if old not in text:
                failed.append(f"ANCHOR NOT FOUND  {fname}\n    {old[:90]}...")
                continue
            if text.count(old) > 1:
                failed.append(f"AMBIGUOUS ANCHOR ({text.count(old)}x)  "
                              f"{fname}\n    {old[:90]}...")
                continue
            text = text.replace(old, new)
            applied += 1
            print(f"  ✓ {fname}\n      {why}")
        if text != original:
            path.write_text(text)

    print(f"\nApplied {applied} of {len(EDITS)} edits.")
    if failed:
        print(f"\n{len(failed)} FAILED — nothing partial was hidden:")
        for f in failed:
            print(f"  ✗ {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
