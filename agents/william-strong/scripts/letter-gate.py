#!/usr/bin/env python3
"""Block unsourced PROSE claims in direct-mail letters.

WHY THIS EXISTS (William Strong, 2026-08-27)
--------------------------------------------
`brief-gate.py` extracts money, percent, and day-count figures. That is the
entire shape of the failure we had Aug 23-27, and it is now well covered.

It is not the shape of the worst thing we nearly mailed.

On Aug 27 I reviewed three letters waiting for Chris's signature. Letter 2 said
"your father" three times and closed "I'm sorry about your father." The source
record for that docket - master.jsonl and the CSV both - carries decedent name,
fiduciary name, address, parcel, docket, assessed value. It carries **no
kinship field and no age**, because a probate appointment notice names a
FIDUCIARY, not a relative. Estates appoint spouses, siblings, in-laws.

Same surname plus same address fits "daughter". It fits "widow" equally well.
If she is his widow, we mail a grieving woman a letter in Chris's name telling
her three times that her husband was her father.

That letter contains **not one dollar sign, percent, or day count.** Jack listed
that in his cover note as a *safety* feature. `brief-gate.py` would have passed
it at full confidence, silently, because the riskiest sentence in our
highest-stakes channel is made of words.

Iris flagged this exact hole on Aug 24 and asked for a tenure/biography matcher
pointed at letters/. This is that.

THE RULE IT ENFORCES
--------------------
A letter may assert a fact about a human being only if that fact exists in the
source record for its docket. Kinship, age, tenure, and occupation are asserted
constantly in warm direct mail and are almost never in a probate notice.

Silence in the record is NOT permission. It is the absence of a source.

WHAT IT DOES
------------
  1. Reads each letter in letters/, pulls its docket number.
  2. Loads that docket's record from master.jsonl.
  3. Scans the LETTER BODY ONLY (not the reasoning header) for kinship, age,
     tenure and occupation claims.
  4. Flags any claim with no corresponding field in the source record.
  5. Also runs the figure check from brief-gate against the cleared block.

Exit 1 on any finding. Direct mail is physical, signed, and unrecallable -
this gate blocks, it does not advise.

Usage:  python3 letter-gate.py
        python3 letter-gate.py --quiet   # findings only
"""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BOTS_FILE = Path("/root/agents/telegram-bots.json")
CHRIS_CHAT_ID = "8560812913"


def send_telegram(message):
    """Alert on findings.

    brief-gate v1 wrote its alerts to a log nobody reads because the token
    lookup silently returned None for a month. A gate that only prints is a
    gate that does not exist. This lookup handles both shapes of the bots file
    and was confirmed by watching a real message arrive - not by reading it.
    """
    try:
        raw = json.loads(BOTS_FILE.read_text())
        bots = raw.get("bots", raw)
        token = None
        if isinstance(bots, list):
            for bot in bots:
                if bot.get("agent_id") in ("main", "william-strong"):
                    token = bot.get("bot_token") or bot.get("token")
                    break
        else:
            for key in ("main", "william-strong"):
                entry = bots.get(key) or {}
                token = entry.get("bot_token") or entry.get("token")
                if token:
                    break
        if not token:
            print("WARN: no telegram token found; alert not sent")
            return False
        payload = urlencode({"chat_id": CHRIS_CHAT_ID,
                             "text": message[:4096]}).encode()
        with urlopen(f"https://api.telegram.org/bot{token}/sendMessage",
                     payload, timeout=15):
            print("telegram alert sent")
        return True
    except Exception as exc:  # noqa: BLE001 - alerting is advisory
        print(f"WARN: telegram alert failed - {exc}")
        return False

LETTERS_DIR = Path("/root/agents/jack-sullivan/workspace/letters")
MASTER = Path("/root/agents/jack-sullivan/workspace/distress-pipeline/data/master.jsonl")

# Jack's convention: everything above this marker is his reasoning to us and may
# legitimately discuss a claim in order to reject it. Only what prints is gated.
BODY_MARKER = re.compile(r"^##\s*LETTER\s*—?\s*print from here", re.IGNORECASE | re.MULTILINE)

DOCKET = re.compile(r"\b(\d{3}-\d{4}-[A-Z]{2}-\d{5})\b")

# Each pattern maps to the source field(s) that would justify it. A probate
# appointment notice supplies none of these, which is exactly the point.
CLAIM_PATTERNS = [
    # Up to 3 intervening words. Without this, "your father" was caught but
    # "your LATE father" - overwhelmingly the likelier phrasing in a condolence
    # letter - sailed straight through, as did "your 94-year-old father" and
    # "your dear mother". Verified evading before the fix, 2026-08-27.
    ("kinship", re.compile(
        r"\byour\s+(?:[\w'-]+\s+){0,3}(father|mother|dad|mom|husband|wife|"
        r"spouse|son|daughter|parent|brother|sister|grandmother|grandfather|"
        r"aunt|uncle|widow|widower)\b",
        re.IGNORECASE), ("relationship", "kinship", "relation_to_decedent")),
    ("kinship", re.compile(
        r"\b(?:sorry|condolences)\s+(?:about|for|on)\s+your\s+"
        r"(?:[\w'-]+\s+){0,3}(father|mother|dad|mom|husband|wife|son|"
        r"daughter|parent)\b", re.IGNORECASE),
     ("relationship", "kinship", "relation_to_decedent")),
    ("age", re.compile(r"\b(\d{1,3})[-\s]year[-\s]old\b", re.IGNORECASE),
     ("age", "decedent_age")),
    ("age", re.compile(r"\baged?\s+(\d{2,3})\b", re.IGNORECASE),
     ("age", "decedent_age")),
    ("tenure", re.compile(
        r"\b(?:for|after|over)\s+(\d{1,3})\s+years\b", re.IGNORECASE),
     ("years_owned", "tenure", "purchase_date")),
    ("tenure", re.compile(r"\bsince\s+(19\d{2}|20[0-2]\d)\b", re.IGNORECASE),
     ("years_owned", "tenure", "purchase_date")),
    ("occupation", re.compile(
        r"\byour\s+(?:years\s+)?(?:as|working\s+as)\s+an?\s+(\w+)",
        re.IGNORECASE), ("occupation", "profession")),
]


# ---------------------------------------------------------------------------
# SENDER BIOGRAPHY  (added 2026-08-28, from the Letter 1 miss)
# ---------------------------------------------------------------------------
# Everything above validates claims about the RECIPIENT against the docket
# record. That is one half of the problem and it is the half I built first
# because it is the half that had just burned me.
#
# The other half sat live for three days. Letter 1 read:
#
#     "I put it together because I live in Mont Vernon and had to learn most
#      of it the hard way last winter."
#
# Chris moved to Mont Vernon on 2026-07-01. Last winter he was in Florida.
# The recipient is a LAW OFFICE - deed-date lookup is their day job - and the
# letter is signed in Chris's name. This gate passed it at 100%, because no
# docket record has a field about the sender and so nothing was ever checked.
#
# Iris Vale caught it on Aug 25 and again on Aug 28. I did not.
#
# THE RULE: a first-person claim by the sender is checked against the sender's
# known history, not against the recipient's record. There is no docket on
# earth that can source a sentence about Chris.
#
# Self-expiring by design: the marker's latest possible date is compared to
# the residency start, so once a claim BECOMES true (spring 2027, "last
# winter" is genuinely a Mont Vernon winter) it stops being flagged. A gate
# that has to be hand-edited to stop lying is a gate that will keep lying.
NH_RESIDENCY_START = date(2026, 7, 1)  # 30 Dow Road, Mont Vernon - see USER.md

# IGNORECASE matters more than it looks: without it "We went through this last
# fall" and "We moved here in 2021" both sailed through, because a sentence
# almost always STARTS with the pronoun and so it is almost always capitalised.
# The one position the pronoun most often occupies was the one position the
# pattern could not see. Caught by the must-catch list, 2026-08-28.
FIRST_PERSON = re.compile(r"\b(I|I've|I'm|I'll|my|we|we've|our)\b", re.IGNORECASE)

# Season -> (month, day) it ENDS. Used to resolve "last winter" to a real date.
SEASON_END = {
    "winter": (3, 20), "spring": (6, 20),
    "summer": (9, 22), "fall": (12, 21), "autumn": (12, 21),
}

WORD_NUMBERS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                "eleven": 11, "twelve": 12, "twenty": 20, "thirty": 30,
                "several": 3, "many": 5, "a few": 3, "few": 3, "a couple": 2,
                "couple": 2}

# Longest-first so "a few" wins over "a", and one shared source of truth - the
# first version spelled the alternation out twice and the two copies had
# already drifted apart by the time the tests ran.
_NUM = r"\d{1,3}|" + "|".join(
    sorted((re.escape(w) for w in WORD_NUMBERS), key=len, reverse=True))


def _last_season_end(season, today):
    """Most recent COMPLETED occurrence of a season, as a date."""
    month, day = SEASON_END[season]
    year = today.year
    while date(year, month, day) >= today:
        year -= 1
    return date(year, month, day)


def _years_back(text):
    """'three years' / 'a few winters' / '12 years' -> int, or None."""
    text = text.strip().lower()
    if text.isdigit():
        return int(text)
    return WORD_NUMBERS.get(text)


# Each entry: (label, regex, resolver) where resolver(match, today) returns the
# LATEST date the claim could possibly refer to, or None to always flag.
SENDER_PATTERNS = [
    ("sender-season", re.compile(
        r"\blast\s+(winter|spring|summer|fall|autumn)\b", re.IGNORECASE),
     lambda m, today: _last_season_end(m.group(1).lower(), today)),

    ("sender-tenure", re.compile(
        r"\b(" + _NUM + r")\s+"
        r"(?:years?|winters?)\s+(?:here|in\s+(?:Mont\s+Vernon|Milford|Amherst|"
        r"Nashua|Hollis|Bedford|New\s+Hampshire|NH|the\s+valley))\b",
        re.IGNORECASE),
     lambda m, today: (date(today.year - _years_back(m.group(1)),
                            today.month, today.day)
                       if _years_back(m.group(1)) else None)),

    ("sender-tenure", re.compile(
        r"\b(?:I|we)(?:'ve)?\s+(?:have\s+)?(?:lived|been)\s+here\s+"
        r"(?:for\s+)?(" + _NUM + r")\s+(?:years?|winters?)\b",
        re.IGNORECASE),
     lambda m, today: (date(today.year - _years_back(m.group(1)),
                            today.month, today.day)
                       if _years_back(m.group(1)) else None)),

    ("sender-since", re.compile(
        r"\b(?:since|moved\s+(?:here|up|to\s+\w+)\s+in)\s+(19\d{2}|20[0-2]\d)\b",
        re.IGNORECASE),
     lambda m, today: date(int(m.group(1)), 12, 31)),

    # No resolver - these can never become true.
    ("sender-origin", re.compile(
        r"\b(grew\s+up\s+(?:here|in\s+\w+)|born\s+and\s+raised|"
        r"all\s+my\s+life|my\s+whole\s+life|lifelong\s+resident|"
        r"native\s+(?:of|to)\s+(?:New\s+Hampshire|NH|the\s+valley))\b",
        re.IGNORECASE),
     lambda m, today: None),
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def scan_sender_claims(body, today=None):
    """Flag first-person sender claims that predate Chris's NH residency.

    Scoped to sentences containing a first-person pronoun, so a claim about
    the RECIPIENT's history ("your years as a teacher", "the family has been
    here for decades") is not swept up by the tenure patterns - that is the
    other half of the gate's job and it has its own source check.
    """
    today = today or date.today()
    findings = []
    flat = " ".join(body.split())
    for sentence in SENTENCE_SPLIT.split(flat):
        if not FIRST_PERSON.search(sentence):
            continue
        for label, pattern, resolve in SENDER_PATTERNS:
            for match in pattern.finditer(sentence):
                latest = resolve(match, today)
                if latest is not None and latest >= NH_RESIDENCY_START:
                    continue  # claim is compatible with the real move date
                phrase = match.group(0).strip()
                when = latest.isoformat() if latest else "never true"
                findings.append((
                    label,
                    f'sender claim "{phrase}" implies NH presence by {when}, '
                    f'but Chris moved {NH_RESIDENCY_START.isoformat()} '
                    f'— in: "{sentence.strip()[:120]}"',
                ))
    return findings


def load_records():
    """docket -> record. Master is the authority; CSVs are derived views."""
    records = {}
    if not MASTER.exists():
        raise FileNotFoundError(f"master record not found: {MASTER}")
    for line in MASTER.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        docket = entry.get("docket_number")
        if docket:
            records[docket] = entry
    return records


def letter_body(text):
    """Only the part that prints. The header is Jack reasoning, not a claim."""
    match = BODY_MARKER.search(text)
    return text[match.end():] if match else text


def record_supports(record, fields):
    """True only if the record actually carries one of the justifying fields.

    Absence is not permission - an empty field and a missing field are the
    same thing here, and both mean nobody sourced it.
    """
    for field in fields:
        value = record.get(field)
        if value not in (None, "", [], {}, "unknown", "Unknown"):
            return True
    return False


def scan_letter(path, records, quiet=False):
    """Return a list of findings for one letter."""
    text = path.read_text()
    body = letter_body(text)
    dockets = DOCKET.findall(text)
    findings = []

    # Runs BEFORE the docket check on purpose: a sender-biography claim is
    # false regardless of which docket the letter belongs to, so it must not
    # be skipped by an early return on a missing record.
    findings.extend(scan_sender_claims(body))

    if not dockets:
        findings.append(("no-docket", "letter names no docket number - "
                                      "cannot verify any claim against source"))
        return findings

    docket = dockets[0]
    record = records.get(docket)
    if record is None:
        findings.append(("no-record", f"docket {docket} not found in master.jsonl"))
        return findings

    for kind, pattern, fields in CLAIM_PATTERNS:
        for match in pattern.finditer(body):
            if record_supports(record, fields):
                continue
            phrase = match.group(0).strip()
            findings.append((
                kind,
                f'asserts {kind}: "{phrase}" — no {" / ".join(fields)} field '
                f'in source record for {docket}',
            ))
    if not quiet and not findings:
        print(f"  ✅ {path.name}: no unsourced claims (docket {docket})")
    return findings


def main():
    quiet = "--quiet" in sys.argv
    if not LETTERS_DIR.exists():
        print(f"No letters directory at {LETTERS_DIR} - nothing to gate.")
        return 0

    records = load_records()
    letters = sorted(p for p in LETTERS_DIR.glob("*.md")
                     if not p.name.startswith("00-"))
    if not letters:
        print("No letters to gate.")
        return 0

    if not quiet:
        print(f"letter-gate: {len(letters)} letter(s), "
              f"{len(records)} source record(s)\n")

    total = 0
    flagged = []
    for path in letters:
        findings = scan_letter(path, records, quiet)
        if findings:
            print(f"  ⛔ {path.name}")
            for kind, message in findings:
                print(f"      [{kind}] {message}")
                flagged.append((path, kind, message))
            total += len(findings)

    print()
    if total:
        print(f"BLOCKED — {total} unsourced claim(s). "
              f"Direct mail is unrecallable; resolve before Chris signs.")
        if "--no-alert" not in sys.argv:
            detail = "\n".join(
                f"• {path.name}: {msg}"
                for path, kind, msg in flagged[:8]
            )
            send_telegram(
                f"⛔ LETTER GATE — {total} unsourced claim(s)\n\n"
                f"{detail}\n\n"
                f"These letters assert facts about a person that appear "
                f"nowhere in the source record. Direct mail is signed and "
                f"unrecallable — resolve before signing."
            )
        return 1
    print("CLEAN — every human-fact claim traces to a source record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
