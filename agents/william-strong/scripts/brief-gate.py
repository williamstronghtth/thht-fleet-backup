#!/usr/bin/env python3
"""Block uncleared figures in daily briefs, on EVERY outbound path.

WHY THIS EXISTS (William Strong, 2026-08-26; rewritten 2026-08-27)
------------------------------------------------------------------
Four consecutive days (Aug 23-26) an unverified figure entered at the brief
layer and published. Three fixes were written and all three failed, because all
three depended on an agent choosing to comply. v1 of this script was the first
control that did not.

v1 WORKED. On Aug 27 it fired on the brief to Fiona and she rejected it at
07:40 ET citing four uncleared figures - the first time the system caught a bad
figure before it published.

v1 ALSO MISSED. It gated exactly one file: the brief to Fiona. The morning
brief to Chris went out on Telegram at 06:30 ET carrying 14 uncleared figures,
including the $586,000 that had been explicitly WITHDRAWN the day before. Fifth
straight day for that number. It travelled the one route nobody was checking.

The lesson, written into the cleared block as a standing amendment:
    A figure is not cleared by ANY path if it is not cleared on EVERY path.
    Controls are named by the artifact they protect, not by the reader they
    happened to be built for.

WHY DELIVERY MOVED IN HERE
--------------------------
`run-agent.sh --telegram` injects the bot token into the agent's own system
prompt - the AGENT composes and sends in one pass. There is no post-hoc file a
gate can intercept before Chris's phone buzzes. So a file gate on the morning
brief could only ever detect, never prevent. That is the same theater as the
rules that already failed.

So the morning brief cron no longer sends. It writes to a known path and stops.
This script gates that file and then delivers it. Generation and delivery are
now separated by a check that does not ask anyone to comply.

FAIL-OPEN ON DELIVERY, FAIL-LOUD ON CONTENT
-------------------------------------------
If figures are uncleared, Chris still gets his brief - with a blocking header
nailed to the top naming every bad figure. He is never silently deprived of the
brief, and he can never receive a dirty one that looks clean. A gate that can
swallow the morning brief entirely would be a worse failure than the one it
fixes.

WHAT IT DOES
------------
  1. Loads the newest CLEARED-FIGURES-*.md as a whitelist of numeric claims.
     Warns loudly if that file is not today's - stale clearance is not clearance.
  2. For each target: extracts every money / percent / day-count claim.
  3. Anything not on the whitelist is uncleared. Anything in a WITHDRAWN
     section is a SEVERE repeat.
  4. Marks the file in place, alerts Chris, and (for delivery targets) sends
     the brief with its verdict attached.

Idempotent - re-running replaces its own header rather than stacking.

Usage:  python3 brief-gate.py                    # all targets
        python3 brief-gate.py --target fiona     # one target
        python3 brief-gate.py --dry-run          # report only, never write/send
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import fair_housing
import newsletter_extract

ET = ZoneInfo("America/New_York")
WORKSPACE = Path("/root/agents/william-strong/workspace")
BOTS_FILE = Path("/root/agents/telegram-bots.json")
CHRIS_CHAT_ID = "8560812913"
TELEGRAM_LIMIT = 4096

HEADER_START = "<!-- brief-gate:start -->"
HEADER_END = "<!-- brief-gate:end -->"

# Bare years and the like are not market claims; don't treat them as figures.
IGNORE_BARE = {"2024", "2025", "2026", "2027", "603", "386"}

# The K/M suffix must not be the first letter of a following word - otherwise
# "$580,000 median" parses the "m" of "median" as a millions multiplier.
MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*([KkMm])?(?![A-Za-z])")
PERCENT = re.compile(r"([\d]+(?:\.\d+)?)\s?%")
DAYS = re.compile(r"([\d]+(?:\.\d+)?)\s*(?:-|\s)?days?\b", re.IGNORECASE)
MONTHS_SUPPLY = re.compile(r"([\d]+(?:\.\d+)?)\s*months?\s+(?:of\s+)?supply", re.IGNORECASE)
# Prose says "1.71 months of supply"; the cleared block stores the same fact
# table-form as "| Months of supply | 1.71 months |", where the number and the
# label sit in different cells. Matching only the prose order meant a figure
# that WAS cleared came back flagged (caught by the clean-brief control test,
# 2026-08-27). So on any line already mentioning supply, a bare "N months"
# counts. Scoped to supply lines so "37th consecutive month" never matches.
# Optional hyphen: NAR's own house style is "a 4.6-month supply", which without
# it extracted nothing at all - a silent miss, worse than a false positive.
MONTHS_BARE = re.compile(r"([\d]+(?:\.\d+)?)\s*-?\s*months?\b", re.IGNORECASE)
SUPPLY_LINE = re.compile(r"supply", re.IGNORECASE)


def morning_brief_path():
    """Today's morning brief. Dated filename, so resolve at call time.

    Falls back to any *morning-brief*.md in memory/ written today. The 06:30
    cron no longer sends to Chris - this script does - so an unexpected
    filename would mean Chris silently gets NO brief. Matching only the exact
    dated name would trade a data bug for a delivery bug.
    """
    today = datetime.now(ET).strftime("%Y-%m-%d")
    memory = WORKSPACE / "memory"
    exact = memory / f"{today}-morning-brief.md"
    if exact.exists():
        return exact
    candidates = [
        p for p in memory.glob("*morning-brief*.md")
        if datetime.fromtimestamp(p.stat().st_mtime, ET).strftime("%Y-%m-%d") == today
    ]
    if candidates:
        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        print(f"NOTE: brief found under unexpected name {newest.name}")
        return newest
    return exact


FIONA_INBOX = Path("/root/agents/fiona-murphy/workspace/inbox")
FIONA_CANONICAL = FIONA_INBOX / "daily-content.md"

# Files in Fiona's inbox that are content briefs. Anything matching gets gated.
FIONA_BRIEF_GLOB = "daily-content*.md"


def fiona_brief_path():
    """Find today's content brief in Fiona's inbox.

    WHY THIS IS A GLOB AND NOT A FILENAME (2026-08-31)
    --------------------------------------------------
    This target used to be hardcoded to `daily-content.md`. On Aug 31 the
    brief was written to `daily-content-brief-2026-08-31.md` instead. The gate
    ran on schedule at 11:15 UTC, found no file at the name it knew, printed
    "nothing to gate", and exited 0. A brief carrying six Fair Housing
    violations and four invented town medians went to Fiona completely
    unchecked.

    The gate did not fail. It was WALKED AROUND BY A FILENAME — by the same
    agent that wrote the gate. Binding a control to one exact path means the
    author of the artifact can silently opt out of it by typing a different
    name, without ever intending to.

    So: match the shape, take the newest. A new name still gets gated.

    ALSO: Fiona's inbox is a QUEUE — she drains it into processed/ as she
    works. Searching only the inbox means that every run after she picks the
    brief up finds nothing and fires the "gate had nothing to check" alert.
    A control that cries wolf every afternoon is a control someone switches
    off, which is the failure mode this whole file exists to avoid. So
    processed/ is searched too: a brief that was gated and then filed is a
    normal day, not a missing brief.
    """
    candidates = sorted(
        list(FIONA_INBOX.glob(FIONA_BRIEF_GLOB))
        + list((FIONA_INBOX / "processed").glob(FIONA_BRIEF_GLOB)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    today = datetime.now(ET).strftime("%Y-%m-%d")
    fresh = [
        p for p in candidates
        if datetime.fromtimestamp(p.stat().st_mtime, ET).strftime("%Y-%m-%d")
        == today
    ]
    # Only TODAY's brief counts. A stale brief sitting in processed/ from last
    # week must not suppress the alert - that would recreate the silence this
    # function was written to remove.
    return fresh[0] if fresh else FIONA_CANONICAL


NEWSLETTER_DIR = Path("/root/agents/jack-sullivan/workspace/newsletter")
NEWSLETTER_GLOB = "send_newsletter_*.js"


def newsletter_path():
    """Newest newsletter send script written today.

    WHY THE NEWSLETTER IS A TARGET AT ALL (2026-08-31)
    --------------------------------------------------
    Both existing targets protect readers INSIDE the building: Fiona and
    Chris. The weekly newsletter is the only artifact we send to people who
    are not on the team - 88 unique addresses - and until today it passed
    through no check of any kind. It did not look like a "brief": it is a
    JavaScript file that builds an HTML email, so it never got a target.

    Fifth instance of the standing amendment: a control is named by the
    artifact it protects, not the reader it was built for.

    Backtested before wiring, which is the only reason to trust it:
      - Aug 25 send, against the Aug 25 block: 8 uncleared figures, incl.
        "49 days" as national DOM - a number in no cleared block, ever.
      - Aug 18 send: published "~$520,000" for Nashua. That is the stale
        figure the cleared block still carries as an OPEN CORRECTION. This
        gate located where it entered the public record.

    Returns the canonical directory path when nothing matches, so the
    caller's not-found branch fires the alert rather than silently passing.
    """
    fresh = [
        p for p in NEWSLETTER_DIR.glob(NEWSLETTER_GLOB)
        if datetime.fromtimestamp(p.stat().st_mtime, ET).strftime("%Y-%m-%d")
        == datetime.now(ET).strftime("%Y-%m-%d")
    ]
    if not fresh:
        return NEWSLETTER_DIR / "send_newsletter_TODAY.js"
    return max(fresh, key=lambda p: p.stat().st_mtime)


# Every outbound brief path gets a target. Adding a new brief destination
# without adding it here is how Aug 27 happened.
TARGETS = {
    "fiona": {
        "label": "Daily content brief -> Fiona",
        "path": fiona_brief_path,
        "deliver": False,
        "audience": "Fiona",
    },
    "chris": {
        "label": "Morning brief -> Chris (Telegram)",
        "path": morning_brief_path,
        "deliver": True,
        "audience": "Chris",
    },
    "newsletter": {
        "label": "Weekly newsletter -> subscribers (88 inboxes)",
        "path": newsletter_path,
        "deliver": False,
        "audience": "newsletter subscribers",
        # A .js email template is ~20k chars of HTML and inline CSS. Checked
        # raw it yields forty false figures a week from padding and hex
        # colours, and a gate that cries wolf weekly is a gate Jack stops
        # reading. See newsletter_extract for why this reduces to prose.
        "extract": newsletter_extract.to_prose,
        # The newsletter is WEEKLY (Tuesdays); the other targets are daily.
        # In the daily loop this target would find no file six days in seven
        # and fire the missing-artifact alert every one of them. Same alert
        # fatigue, different clock. So it runs on its own schedule via
        # --target newsletter, never in the default sweep.
        "on_demand": True,
        "expect_shape": NEWSLETTER_GLOB,
        # The gate reads a REDUCTION of this file, not the file itself. It
        # must never write its header back - see run_target.
        "readonly": True,
    },
}


# Fiona's inbox is a QUEUE - she drains it into processed/ as she works. The
# cleared block was dropped there this morning and was filed away within
# minutes, which is exactly how she ended up with veto authority and nothing to
# check against on Aug 26. A reference document has to live somewhere stable,
# so the gate mirrors it to her workspace root on every run.
CLEARED_MIRRORS = [Path("/root/agents/fiona-murphy/workspace/CLEARED-FIGURES-TODAY.md")]


def mirror_cleared_file(cleared_path):
    """Keep a stable, always-current copy where downstream agents can find it."""
    for dest in CLEARED_MIRRORS:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(
                f"<!-- mirrored from {cleared_path.name} by brief-gate.py -->\n"
                f"<!-- do not edit here; edit the source in william-strong/workspace -->\n\n"
                + cleared_path.read_text()
            )
        except Exception as exc:  # noqa: BLE001 - mirroring is advisory
            print(f"WARN: could not mirror cleared block to {dest} - {exc}")


def normalize_money(value, suffix):
    """'$580,000', '$580K', '$0.58M' all collapse to the same token."""
    amount = float(value.replace(",", ""))
    if suffix and suffix.lower() == "k":
        amount *= 1_000
    elif suffix and suffix.lower() == "m":
        amount *= 1_000_000
    return f"money:{int(round(amount))}"


def extract_claims(text):
    """Return the set of normalized numeric claims appearing in text."""
    claims = set()
    for value, suffix in MONEY.findall(text):
        if value.strip(",") in IGNORE_BARE and not suffix:
            continue
        claims.add(normalize_money(value, suffix))
    for value in PERCENT.findall(text):
        claims.add(f"pct:{float(value):g}")
    for value in DAYS.findall(text):
        claims.add(f"days:{float(value):g}")
    for value in MONTHS_SUPPLY.findall(text):
        claims.add(f"supply:{float(value):g}")
    for line in text.splitlines():
        if SUPPLY_LINE.search(line):
            for value in MONTHS_BARE.findall(line):
                claims.add(f"supply:{float(value):g}")
    return claims


# Weather sections carry percentages (precipitation odds) and temperatures that
# are not market claims and will never appear in a cleared block. Left in, they
# flag every single day - and a gate that cries wolf daily is a gate everyone
# learns to scroll past. Alert fatigue is how controls die quietly.
# Deliberately narrow: matches the heading only, never a market section.
NONMARKET_HEADING = re.compile(r"^#{1,6}\s.*\bweather\b", re.IGNORECASE)


# A corrective brief has to PRINT the bad numbers to tell anyone which ones to
# refuse - "kill the Bedford figure" is useless without "$1,195,000". Extracted
# naively, those quarantined mentions flag on every correction, and a gate that
# always shows a block is indistinguishable from a gate that is broken.
# So quarantine is explicit and fenced, never inferred from wording: an author
# must physically wrap the region. It is greppable, auditable, and wrapping a
# live claim in it is visible in review rather than a silent bypass.
QUARANTINE = re.compile(
    r"<!--\s*gate:quarantine\s*-->.*?<!--\s*gate:/quarantine\s*-->",
    re.DOTALL | re.IGNORECASE,
)


def split_quarantine(text):
    """Return (publishable_text, quarantined_text)."""
    quarantined = "\n".join(QUARANTINE.findall(text))
    return QUARANTINE.sub(" ", text), quarantined


def strip_nonmarket_sections(text):
    """Drop weather blocks before figure extraction. Nothing else is exempt."""
    kept, skipping = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            skipping = bool(NONMARKET_HEADING.match(line.strip()))
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def latest_cleared_file():
    files = sorted(WORKSPACE.glob("CLEARED-FIGURES-*.md"))
    if not files:
        # Deliberately NOT SystemExit: that inherits from BaseException, slips
        # past `except Exception` in main(), and would bypass the emergency
        # delivery path entirely - killing Chris's brief on the exact day the
        # cleared block went missing. Caught in failure-mode testing 2026-08-27.
        raise FileNotFoundError(
            "no CLEARED-FIGURES-*.md found - gate cannot run")
    return files[-1]


def cleared_file_is_current(path):
    """Stale clearance is not clearance - yesterday's block can't clear today."""
    today = datetime.now(ET).strftime("%Y-%m-%d")
    return today in path.name


# --- BLOCK EXPIRY (added 2026-09-03) ---------------------------------------
#
# WHY: `cleared_file_is_current` asks only "is this today's file?". The Sept 3
# block says, in bold, at the top:
#
#     ⏰ THIS BLOCK EXPIRES Thu Sept 3, 12:00 PM ET — TODAY, AT NOON.
#     Nothing carrying a rate may be published or left sitting in a scheduled
#     queue past noon on Sept 3 without a fresh block.
#
# Nothing read that line. At 12:01 PM the block is void by its own terms and
# the gate would still have certified it, because the filename still says
# today. That is the SIXTH instance this week of the same defect: a marker
# written into a file that no consumer parses.
#
#     Sept 1: a brief asserted a cron that did not exist.
#     Sept 2: the FH gate returned 0 on a document with 8 violations.
#     Sept 2: the security count was 88% the tool reading its own report.
#     Sept 3: a ⛔ stub was consumed as the clearance it stood in for.
#     Sept 3: an audit of "published" content had never fetched anything.
#     Sept 3: this.
#
# A deadline that only a human can see is a note, not a control.
#
# SCOPE: expiry voids RATE figures only. The block is explicit that non-rate
# figures are unaffected by the PMMS release and stand until their own sources
# publish. Voiding everything would be wrong AND would train people to
# override the gate at noon every Thursday.
EXPIRY_RE = re.compile(
    r"THIS BLOCK EXPIRES\s+\w+\s+(\w+)\.?\s+(\d{1,2}),?\s+"
    r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*ET",
    re.I,
)

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def cleared_block_expiry(text, year=None):
    """Parse the declared expiry from the block head. None if none declared.

    Returns an aware datetime in ET. A block with no expiry line is NOT
    treated as expired - most blocks legitimately declare none, and inventing
    one would fail every gate run.
    """
    match = EXPIRY_RE.search(text)
    if not match:
        return None
    mon_raw, day, hour, minute, meridiem = match.groups()
    month = MONTHS.get(mon_raw[:3].lower())
    if month is None:
        return None
    hour = int(hour) % 12
    if meridiem.upper() == "PM":
        hour += 12
    try:
        return datetime(year or datetime.now(ET).year, month, int(day),
                        hour, int(minute), tzinfo=ET)
    except ValueError:
        return None


class UnparseableExpiry(Exception):
    """The block declares an expiry the gate cannot read."""


def rate_figures_expired(text, now=None):
    """(is_expired, expiry) - has the block's own rate deadline passed?

    Raises UnparseableExpiry if the block SAYS it expires but the deadline
    cannot be parsed. Returning "not expired" there would recreate the exact
    defect this function was written to fix: a deadline present in the file
    and invisible to the code. A declared-but-unreadable expiry is the most
    dangerous state of all - someone believed they had set a deadline.
    """
    expiry = cleared_block_expiry(text)
    if expiry is None:
        if re.search(r"THIS BLOCK EXPIRES", text, re.I):
            raise UnparseableExpiry(
                "block contains 'THIS BLOCK EXPIRES' but no parseable "
                "date/time follows it. Expected e.g. "
                "'THIS BLOCK EXPIRES Thu Sept 3, 12:00 PM ET'."
            )
        return False, None
    return (now or datetime.now(ET)) > expiry, expiry


# Unambiguous mortgage-rate language. These stand alone.
RATE_ANCHORS = (
    r"30[-\s]?(?:year|yr)\b",
    r"15[-\s]?(?:year|yr)\b",
    r"\bmortgage rate",
    r"\bPMMS\b",
    r"\bfreddie\s+mac\b",
    r"\brates?\s+(?:are|is|fell|rose|dropped|climbed|held|ticked)",
    r"\binterest rate",
)

# A bare decimal percentage is AMBIGUOUS: "6.42%" is a rate, "2.7%" is a YoY
# price move, and nothing in the token distinguishes them. An earlier version
# matched every decimal percentage and its own comment claimed it did not --
# the negative control caught the contradiction. So a percentage counts only
# when it sits near rate language.
RATE_PCT = re.compile(r"\b\d{1,2}\.\d{1,3}\s*%")
ANCHOR_WINDOW = 120


def carries_rate_figure(text):
    """Return rate-ish phrases in a document (empty if none).

    Anchors match outright. A decimal percentage matches only within
    ANCHOR_WINDOW characters of an anchor, so YoY price moves do not trip it.
    Deliberately over-reports at the margin: a false alarm costs a human one
    minute of reading, a false clean ships a stale rate into published copy.
    """
    hits = []
    spans = []
    for pattern in RATE_ANCHORS:
        for match in re.finditer(pattern, text, re.I):
            hits.append(match.group(0).strip())
            spans.append(match.span())
    if not spans:
        return hits
    for match in RATE_PCT.finditer(text):
        start, end = match.span()
        if any(start - ANCHOR_WINDOW <= b and e <= end + ANCHOR_WINDOW
               for b, e in spans):
            hits.append(match.group(0).strip())
    return hits


STUB_MARKERS = ("UNREVIEWED AUTO-STUB", "THIS IS NOT A CLEARANCE")


def cleared_file_is_reviewed(text):
    """An unreviewed auto-stub is an ABSENCE of clearance wearing today's name.

    `cleared-figures-stub.py` writes a carry-forward at 06:00 so the gate never
    silently checks today's copy against yesterday's block. It stamps that file
    ⛔ UNREVIEWED AUTO-STUB and asks a human to confirm the carry-forward basis
    and delete the header.

    Until a human does, the file is a placeholder, not a grant. Before the stub
    existed, a missing block was an absence. With the stub, and with nothing
    reading its marker, the same absence rendered as an affirmative ✅ - which
    is worse than the gap the stub was built to close. The stub WROTE the
    marker and nothing READ it (Iris Vale, 2026-09-03).

    Detection is deliberately positional, not a substring search over the file:
    a REVIEWED block's amendment prose quotes these markers verbatim while
    explaining why the stub exists, and a naive `marker in text` check reads
    that explanation as the condition it describes. The stub owns two
    positions - the H1 title, and a standalone paragraph opener - and
    `cleared-figures-stub.py` writes both.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False  # empty file is not a clearance
    title = lines[0]
    if title.startswith("#") and any(m in title for m in STUB_MARKERS):
        return False
    return not any(
        ln.startswith("**THIS IS NOT A CLEARANCE.**") for ln in lines[:15]
    )


CLEAR_MARK = "✅"
BAN_MARKS = ("❌", "🚫")
# Only these override an inherited verdict. A ⚠️ or 📌 inside a subsection
# heading is editorial emphasis ("### Rates - ⚠️ PMMS RELEASES TOMORROW") and
# must NOT knock the subsection out of its parent ✅ section.
DECISIVE_MARKS = (CLEAR_MARK,) + BAN_MARKS


def classify_sections(text):
    """Yield (verdict, line) for each line, verdict in {clear, ban, none}.

    A `##` heading sets the verdict for everything under it. A `###` subsection
    INHERITS its parent's verdict unless it carries its own marker - the ✅
    section's tables live in unmarked `###` subsections, and without inheritance
    the whitelist comes out empty (caught in testing 2026-08-26).
    """
    top, sub = "none", None
    for line in text.splitlines():
        if line.startswith("## "):
            top, sub = verdict_of(line), None
        elif line.startswith("### "):
            sub = verdict_of(line) if any(m in line for m in DECISIVE_MARKS) else None
        yield (sub or top), line


def verdict_of(heading):
    if CLEAR_MARK in heading:
        return "clear"
    if any(mark in heading for mark in BAN_MARKS):
        return "ban"
    return "none"


def parse_cleared_file(text):
    """Return (whitelist, banned) claim sets from the cleared-figures file.

    Precedence: a figure printed in a ✅ table is cleared even if it is also
    named in the prose of a ❌ section - withdrawn entries routinely cite the
    correct figure while explaining what was wrong. The ✅ tables are the grant;
    ⚠️ CONTESTED and plain prose grant nothing. Silence is not clearance.
    """
    buckets = {"clear": [], "ban": [], "none": []}
    for verdict, line in classify_sections(text):
        buckets[verdict].append(line)
    whitelist = extract_claims("\n".join(buckets["clear"]))
    banned = extract_claims("\n".join(buckets["ban"])) - whitelist
    return whitelist, banned


def describe(claim):
    kind, _, raw = claim.partition(":")
    number = float(raw)
    if kind == "money":
        return f"${int(number):,}"
    if kind == "pct":
        return f"{number:g}%"
    if kind == "days":
        return f"{number:g} days"
    return f"{number:g} months supply"


def strip_existing_header(text):
    """Remove a prior gate header so repeated runs stay idempotent."""
    if HEADER_START not in text:
        return text
    tail = text.split(HEADER_END, 1)
    return tail[1].lstrip("\n") if len(tail) > 1 else text


def build_unreviewed_block_section(cleared_name):
    """Rendered whenever the cleared block is still an unreviewed auto-stub."""
    return [
        "# ⛔ GATE: THE CLEARED BLOCK IS UNREVIEWED — DO NOT PUBLISH FIGURES",
        "",
        f"`{cleared_name}` is the 06:00 auto-generated carry-forward stub. Its "
        f"own first line says **it is not a clearance** — no human has "
        f"confirmed the carried figures are still current for today.",
        "",
        "The figure check below still ran against it, so a *new* uncleared "
        "number is still caught. But a figure appearing in that stub has been "
        "**cleared by nobody**, and this gate will not certify it. Treat every "
        "number in this brief as unavailable until William reviews the block "
        "and removes its ⛔ header.",
        "",
        "---",
        "",
    ]


def build_block_header(uncleared, repeats, cleared_name, audience,
                       fh_findings=None, block_unreviewed=False):
    fh_findings = fh_findings or []
    fh_blockers = [f for f in fh_findings if f["severity"] == fair_housing.BLOCK]
    lines = [HEADER_START]

    # Fair Housing goes FIRST and on its own. A wrong median is an
    # embarrassment; steering language is a federal liability, and it must not
    # be read as one more bullet in a list of number problems.
    if fh_blockers:
        lines += [
            "# 🚨 GATE: FAIR HOUSING — DO NOT PUBLISH",
            "",
            f"`fair_housing.py` found **{len(fh_blockers)} line(s) that steer "
            f"on a protected class**. These do not get rewritten softer. "
            f"**They get deleted.**",
            "",
        ]
        for f in fh_blockers:
            lines.append(f"- **L{f['line']} [{f['label']}]** — `{f['excerpt']}`")
            lines.append(f"  - {f['why']}")
        lines += [
            "",
            "**The rule:** a town may be described; the people who live in it "
            "may not. Test: *could a reader use this line to work out who "
            "lives there?* If yes, cut it.",
            "",
            "If a flagged line is this brief **quoting** a violation in order "
            "to explain it, that is a known false positive — mark the line "
            "with ❌ or move it under a `## Fair Housing` heading.",
            "",
            "---",
            "",
        ]

    if block_unreviewed:
        lines += build_unreviewed_block_section(cleared_name)

    if not uncleared:
        # Never render this as a bare "checked — none uncleared" when the block
        # is a stub: the sentence reads identically to a real clearance, and the
        # memory line it becomes is what gets read the next morning.
        lines += [
            f"Figures checked against an **unreviewed carry-forward stub** "
            f"(`{cleared_name}`) — none newly uncleared, none cleared either."
            if block_unreviewed else
            f"All figures checked against **{cleared_name}** — none uncleared.",
            "",
        ]
        return "\n".join(lines + [HEADER_END, ""])

    lines += [
        "# ⛔ GATE: DO NOT PUBLISH THE FIGURES BELOW",
        "",
        f"`brief-gate.py` checked this brief against **{cleared_name}** and found "
        f"**{len(uncleared)} figure(s) that are not cleared**:",
        "",
    ]
    lines += [f"- **{describe(c)}** — not in the cleared block" for c in sorted(uncleared)]
    if repeats:
        lines += [
            "",
            "**🚨 SEVERE — these were explicitly WITHDRAWN and came back:**",
            "",
        ]
        lines += [f"- **{describe(c)}** — withdrawn, republished" for c in sorted(repeats)]
    lines += [
        "",
        f"**{audience}: do not build on these numbers.** Cut the claim, or use a figure "
        "you have personally read in the cleared file. You have standing authority to "
        "reject this brief back to William. You will not be second-guessed for using it.",
        "",
        "This header was written by a script, not by William. It does not go away by "
        "being ignored.",
        HEADER_END,
        "",
    ]
    return "\n".join(lines)


def build_clean_header(cleared_name, stamp):
    return (
        f"{HEADER_START}\n"
        f"> ✅ **brief-gate:** all figures checked against "
        f"`{cleared_name}` at {stamp}. None uncleared.\n"
        f"{HEADER_END}\n\n"
    )


def telegram_token():
    bots = json.loads(BOTS_FILE.read_text())
    raw = bots.get("bots", bots)
    if isinstance(raw, list):
        for bot in raw:
            if bot.get("agent_id") in ("main", "william-strong"):
                return bot.get("bot_token") or bot.get("token")
        return None
    for key in ("main", "william-strong"):
        entry = raw.get(key) or {}
        token = entry.get("bot_token") or entry.get("token")
        if token:
            return token
    return None


def send_telegram(message):
    """Best-effort alert. A dead notifier must never mask a gate failure."""
    try:
        token = <REDACTED:CREDENTIAL>()
        if not token:
            print("WARN: no telegram token found; skipping alert")
            return False
        payload = urlencode({
            "chat_id": CHRIS_CHAT_ID,
            "text": message[:TELEGRAM_LIMIT],
        }).encode()
        with urlopen(f"https://api.telegram.org/bot{token}/sendMessage", payload, timeout=15):
            print("telegram sent")
        return True
    except Exception as exc:  # noqa: BLE001 - alerting is advisory
        print(f"WARN: telegram send failed - {exc}")
        return False


def deliver_to_chris(body, uncleared, repeats, cleared_name, stamp):
    """Send the morning brief. Dirty briefs still go - loudly marked."""
    if uncleared:
        listed = ", ".join(describe(c) for c in sorted(uncleared))
        banner = (
            f"⛔ MORNING BRIEF — {len(uncleared)} UNCLEARED FIGURE(S)\n"
            f"Checked against {cleared_name} at {stamp}.\n"
            f"Not cleared: {listed}\n"
        )
        if repeats:
            back = ", ".join(describe(c) for c in sorted(repeats))
            banner += f"🚨 WITHDRAWN AND REPUBLISHED: {back}\n"
        banner += (
            "\nThe brief follows so you still have it. "
            "Treat every figure above as unverified.\n\n"
            "———\n\n"
        )
    else:
        banner = (
            f"✅ MORNING BRIEF — all figures cleared against {cleared_name} "
            f"at {stamp}.\n\n———\n\n"
        )
    return send_telegram(banner + body)


def run_target(key, target, whitelist, banned, cleared_path, dry_run,
               block_unreviewed=False):
    """Gate one brief. Returns 0 if clean, 1 if anything was uncleared."""
    path = target["path"]()
    if not path.exists():
        print(f"[{key}] no brief at {path} - nothing to gate.")
        # "Nothing to check" must never look like "everything is clean."
        #
        # The delivery branch below has said so since Aug 27. The non-delivery
        # branch returned 0 in silence, and on Aug 31 that silence is exactly
        # what let an unchecked brief reach Fiona: the file had been written
        # under a different name, so the gate found nothing, said nothing, and
        # exited successfully. Every expensive failure this month REPORTED
        # SUCCESS. A gate with no input is a broken gate, not a happy one.
        stamp = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
        if dry_run:
            return 1
        if target["deliver"]:
            send_telegram(
                f"⚠️ NO MORNING BRIEF ({stamp})\n\n"
                f"The 06:30 brief cron produced no file at {path.name}, so there "
                f"is nothing to deliver. The brief job likely failed - check "
                f"logs/cron.log."
            )
        else:
            send_telegram(
                f"⚠️ GATE HAD NOTHING TO CHECK — {target['label']} ({stamp})\n\n"
                f"No file matched in {path.parent.name}/. Either the brief job "
                f"failed, or the brief was written under a name the gate does "
                f"not match — which means it reached {target['audience']} "
                f"UNCHECKED.\n\nExpected shape: "
                f"{target.get('expect_shape', FIONA_BRIEF_GLOB)}"
            )
        return 1

    original = path.read_text()
    # Targets whose artifact is not prose (the newsletter is a JS/HTML email
    # template) declare a reducer. Default is identity - a target has to opt
    # in, so a new markdown brief can never be silently transformed.
    original = target.get("extract", lambda text: text)(original)
    body = strip_existing_header(original)
    publishable, quarantined = split_quarantine(body)
    in_brief = extract_claims(strip_nonmarket_sections(publishable))
    uncleared = in_brief - whitelist
    repeats = in_brief & banned
    stamp = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")

    # Fair Housing runs on the WHOLE publishable body, not the market sections.
    # Steering language hides in copy suggestions and angle descriptions, which
    # strip_nonmarket_sections() deliberately discards for figure checking.
    # "Amherst schools don't compromise" contains no figure at all.
    fh_findings = fair_housing.scan(publishable)
    fh_blocked = fair_housing.has_blockers(fh_findings)
    if fh_findings:
        print(f"[{key}] " + fair_housing.format_findings(fh_findings))

    held = extract_claims(strip_nonmarket_sections(quarantined)) - whitelist
    if held:
        print(f"[{key}] quarantined (named as do-not-use, not blocking): "
              + ", ".join(describe(c) for c in sorted(held)))

    if repeats:
        print(f"[{key}] SEVERE - repeats explicitly WITHDRAWN figures: "
              + ", ".join(describe(c) for c in sorted(repeats)))

    if not uncleared and not fh_blocked and not block_unreviewed:
        print(f"[{key}] CLEAN - every figure appears in {cleared_path.name}; "
              f"Fair Housing clean")
        if not dry_run and not target.get("readonly"):
            path.write_text(build_clean_header(cleared_path.name, stamp) + body)
            if target["deliver"]:
                deliver_to_chris(body, uncleared, repeats, cleared_path.name, stamp)
        return 0

    listed = ", ".join(describe(c) for c in sorted(uncleared)) or "none"
    if block_unreviewed:
        print(f"[{key}] BLOCKED - cleared block {cleared_path.name} is an "
              f"UNREVIEWED auto-stub; refusing to certify any figure")
    print(f"[{key}] BLOCKED - {len(uncleared)} uncleared figure(s): {listed}"
          + (f"; Fair Housing: {sum(1 for f in fh_findings if f['severity'] == 'BLOCK')} blocking"
             if fh_blocked else ""))
    if dry_run:
        return 1

    header = build_block_header(uncleared, repeats, cleared_path.name,
                                target["audience"], fh_findings,
                                block_unreviewed)
    # READONLY TARGETS. For a markdown brief, stamping the verdict into the
    # top of the file IS the control - the reader cannot miss it. For the
    # newsletter that same line would be catastrophic: `body` here is the
    # EXTRACTED PROSE, so writing it back would replace Jack's executable
    # send script with a de-tagged transcript of last week's email, an hour
    # before send. Caught in review before first run, not in production.
    # A target that is not the artifact's source of truth is never written to.
    if not target.get("readonly"):
        path.write_text(header + body)

    if target["deliver"]:
        deliver_to_chris(body, uncleared, repeats, cleared_path.name, stamp)
    else:
        fh_line = ""
        if fh_blocked:
            # Fair Housing leads the alert. A wrong median is an embarrassment;
            # steering language is a federal liability.
            fh_line = ("🚨 FAIR HOUSING — do not publish:\n"
                       + fair_housing.format_findings(fh_findings) + "\n\n")
        figure_line = ""
        if uncleared:
            figure_line = (f"{len(uncleared)} figure(s) not in "
                           f"{cleared_path.name}:\n{listed}\n\n")
        send_telegram(
            f"⛔ BRIEF GATE ({stamp})\n\n{target['label']}\n\n"
            f"{fh_line}{figure_line}"
            f"Brief has been marked. {target['audience']} will see the block "
            f"before building."
        )
    return 1


def emergency_deliver(target, reason):
    """Last resort: the gate broke, so send the brief raw and say so.

    Delivery now depends on this script. A crash in the checker must never be
    the reason Chris gets no morning brief - that would make the gate a new
    single point of failure, trading a data bug for an availability bug. Louder
    and unchecked beats silent and absent.
    """
    try:
        path = target["path"]()
        body = strip_existing_header(path.read_text()) if path.exists() else ""
    except Exception:  # noqa: BLE001
        body = ""
    stamp = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
    banner = (
        f"⚠️ MORNING BRIEF — GATE FAILED TO RUN ({stamp})\n"
        f"Reason: {reason}\n\n"
        "The brief below was NOT checked against the cleared block. "
        "Treat every figure in it as unverified.\n\n———\n\n"
    )
    send_telegram(banner + body if body else banner + "(brief file unreadable)")


USAGE = f"""brief-gate.py - gate every brief path against the cleared-figures block.

  python3 brief-gate.py                  # gate all targets, live (writes + sends)
  python3 brief-gate.py --dry-run        # report only; no writes, no Telegram
  python3 brief-gate.py --target NAME    # one target: {', '.join(TARGETS)}
  python3 brief-gate.py --help           # this text

Default is LIVE. Live runs rewrite brief files, send Telegram, and deliver
Chris's morning brief. Use --dry-run when you are only inspecting.
"""


def parse_args(argv):
    """Validate argv BEFORE any side effect.

    Why this exists: `--help` was not recognized and fell through to a full
    LIVE run - it rewrote briefs and fired a Telegram alert at Chris. An
    unknown flag must never be interpreted as "do the dangerous default".
    Unknown args now exit non-zero having sent nothing.
    """
    if "--help" in argv or "-h" in argv:
        print(USAGE)
        raise SystemExit(0)

    known = {"--dry-run", "--target"}
    only = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--target":
            if i + 1 >= len(argv):
                print("FATAL: --target requires a value.\n\n" + USAGE)
                raise SystemExit(2)
            only = argv[i + 1]
            if only not in TARGETS:
                print(f"FATAL: unknown target '{only}'. "
                      f"Known: {', '.join(TARGETS)}")
                raise SystemExit(2)
            i += 2
            continue
        if arg not in known:
            print(f"FATAL: unrecognized argument '{arg}'. Nothing was run, "
                  f"nothing was sent.\n\n{USAGE}")
            raise SystemExit(2)
        i += 1

    return ("--dry-run" in argv), only


def main():
    dry_run, only = parse_args(sys.argv[1:])

    # A missing or unparseable cleared block used to SystemExit before delivery,
    # which would have silently cost Chris his brief on the very day the figures
    # were least trustworthy. Fail loud to him instead of quiet to the log.
    try:
        cleared_path = latest_cleared_file()
        cleared_text = cleared_path.read_text()
        block_unreviewed = not cleared_file_is_reviewed(cleared_text)
        whitelist, banned = parse_cleared_file(cleared_text)
        if not whitelist:
            raise ValueError(
                f"whitelist empty from {cleared_path.name} - refusing to run "
                "(would flag everything). Check ✅ markers."
            )
    except Exception as exc:  # noqa: BLE001
        print(f"FATAL: {exc}")
        if not dry_run:
            for key, target in TARGETS.items():
                if target["deliver"] and (not only or key == only):
                    emergency_deliver(target, str(exc))
        return 1

    if not dry_run:
        mirror_cleared_file(cleared_path)

    if block_unreviewed:
        warning = (
            f"⛔ UNREVIEWED BLOCK: {cleared_path.name} is the 06:00 auto-stub "
            f"and still carries its ⛔ header. Nothing publishes on it. The "
            f"figure check ran, but the gate will NOT certify any figure clean."
        )
        print(warning)
        if not dry_run:
            send_telegram(
                f"⛔ BRIEF GATE\n\n{warning}\n\nReview the block and delete "
                f"the header."
            )

    if not cleared_file_is_current(cleared_path):
        warning = (
            f"⚠️  STALE CLEARANCE: newest cleared file is {cleared_path.name}, "
            f"which is not today's. Figures are being checked against an old block."
        )
        print(warning)
        if not dry_run:
            send_telegram(f"⚠️ BRIEF GATE\n\n{warning}\n\nPull fresh figures.")

    # The block's own declared deadline. Until 2026-09-03 this was prose that
    # only a human could act on; the gate certified an expired block as valid
    # because the filename still said today.
    try:
        rates_void, expiry = rate_figures_expired(cleared_text)
    except UnparseableExpiry as exc:
        # Treat as expired. An unreadable deadline is not an absent one.
        rates_void, expiry = True, None
        broken = (
            f"⛔ UNREADABLE EXPIRY in {cleared_path.name}: {exc} "
            f"Treating rate figures as EXPIRED until the line is fixed."
        )
        print(broken)
        if not dry_run:
            send_telegram(f"⛔ BRIEF GATE\n\n{broken}")
    if rates_void and expiry:
        warning = (
            f"⛔ RATE FIGURES EXPIRED: {cleared_path.name} declared its own "
            f"expiry at {expiry:%a %b %-d, %-I:%M %p} ET and that time has "
            f"passed. Non-rate figures still stand. NO RATE FIGURE MAY BE "
            f"CERTIFIED against this block — pull a fresh one."
        )
        print(warning)
        if not dry_run:
            send_telegram(f"⛔ BRIEF GATE\n\n{warning}")
    elif expiry:
        print(f"ℹ️  Block declares a rate expiry at "
              f"{expiry:%a %b %-d, %-I:%M %p} ET — not yet reached.")

    failures = 0
    for key, target in TARGETS.items():
        if only and key != only:
            continue
        # On-demand targets run only when named. They are not daily, and
        # sweeping them would alert on every day they legitimately have no
        # artifact. Never skipped when explicitly requested.
        if not only and target.get("on_demand"):
            continue
        try:
            failures += run_target(key, target, whitelist, banned,
                                   cleared_path, dry_run, block_unreviewed)
        except Exception as exc:  # noqa: BLE001 - see emergency_deliver
            print(f"[{key}] ERROR: {exc}")
            if target["deliver"] and not dry_run:
                emergency_deliver(target, f"{type(exc).__name__}: {exc}")
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
