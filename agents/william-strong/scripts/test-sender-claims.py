#!/usr/bin/env python3
"""Regression tests for letter-gate's sender-biography check.

Anchored to the real Aug 28 miss (Letter 1, "last winter"), then widened to
the CLASS of that miss - because the instance is the one case already fixed.
That is the third time this month I built a control around a literal string
and had the next phrasing walk straight past it.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
gate = __import__("letter-gate", fromlist=["scan_sender_claims"])
scan = gate.scan_sender_claims

TODAY = date(2026, 8, 28)

MUST_CATCH = [
    # The actual sentence that sat live for three days.
    "I put it together because I live in Mont Vernon and had to learn most of "
    "it the hard way last winter.",
    # Same claim, other seasons - all predate the July 1 2026 move.
    "I learned that the hard way last spring.",
    "We went through this last fall.",
    "I dealt with the same thing last summer.",
    # Tenure phrasings.
    "I've lived here three years.",
    "I have been here for several years.",
    "After twelve years in Mont Vernon, I still get surprised by it.",
    "My five winters in the valley taught me that.",
    # Explicit dates before the move.
    "I've been doing this here since 2019.",
    "We moved here in 2021.",
    # Never-true origin claims.
    "I grew up here.",
    "I'm a lifelong resident.",
    "Born and raised, so I know the back roads.",
    "I've been shovelling these driveways all my life.",
]

MUST_IGNORE = [
    # True: he does live there, no retrospective claim attached.
    "I put it together because I live in Mont Vernon and needed most of these "
    "numbers myself.",
    "I'm writing about the house itself, not about selling it.",
    "If a number on it is wrong, call me and I'll find it.",
    # Claims about the RECIPIENT - handled by the docket check, not this one.
    "Thank you for your years as a teacher in this town.",
    "The family has owned that house for thirty years.",
    "Your father lived here his whole life.",
    # Compatible with the real move date.
    "I've been here since 2026.",
    "We moved here in 2026.",
    # Not a tenure claim at all.
    "The plow contractors fill their books in September.",
    "That distance is fine in September and a real problem in January.",
]

failures = []

for text in MUST_CATCH:
    if not scan(text, today=TODAY):
        failures.append(f"MISSED (should flag): {text}")

for text in MUST_IGNORE:
    found = scan(text, today=TODAY)
    if found:
        failures.append(f"FALSE POSITIVE: {text}\n      -> {found[0][1][:90]}")

# Self-expiry: the same sentence must stop flagging once it becomes true.
future = date(2027, 5, 1)  # after a real Mont Vernon winter
if scan("I had to learn it the hard way last winter.", today=future):
    failures.append("SELF-EXPIRY BROKEN: 'last winter' still flags in May 2027, "
                    "when it is genuinely true")
if not scan("I had to learn it the hard way last winter.", today=TODAY):
    failures.append("SELF-EXPIRY BROKEN: 'last winter' should flag today")

print(f"must-catch: {len(MUST_CATCH)}  must-ignore: {len(MUST_IGNORE)}  "
      f"+2 self-expiry")
if failures:
    print(f"\n❌ {len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("\n✅ all sender-claim tests pass")
