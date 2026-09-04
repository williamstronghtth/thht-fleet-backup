"""Fair Housing language check for real estate copy.

WHY THIS EXISTS (2026-08-31)
----------------------------
Every control we had gates *numbers*. On Aug 31 the daily content handoff to
Fiona carried six lines selling towns on school quality — "Amherst schools
don't compromise," "families who moved TO schools they love." Not one gate
would ever have flagged them, because there is no figure in them. Fiona caught
it by reading carefully. That is not a control.

Figure errors embarrass us. THIS class of error is a federal Fair Housing
liability, and it is the one nothing was watching.

THE RULE THIS ENFORCES
----------------------
    A town may be described. The people who live in it may not.

Steering by proxy is using a characteristic that CORRELATES with a protected
class as the axis on which a buyer is pointed toward or away from an area.
Intent is irrelevant under the FHA; effect is what counts. "Great schools" and
"safe neighborhood" are the two most common proxies in real estate copy and
both are benign-sounding, which is exactly why they need a machine watching.

FACT vs VERDICT — the distinction that makes this usable
--------------------------------------------------------
The checker does not ban words. It bans *verdicts*.

    OK   "Amherst has its own middle school."        <- fact, checkable
    OK   "The high school is on Route 101."          <- fact, checkable
    BAD  "Amherst has top-rated schools."            <- verdict
    BAD  "Move for the schools you love."            <- verdict + steer

A blanket ban on "school" would be unusable — we publish town content and
schools are real infrastructure. A ban on evaluative framing is enforceable and
leaves the honest sentences alone.

PROTECTED CLASSES
-----------------
Federal FHA: race, color, religion, national origin, sex, familial status,
disability. NH RSA 354-A adds: age, marital status, sexual orientation,
gender identity.

SCOPE LIMIT — stated, not hidden
--------------------------------
This is a regex checker. It catches the KNOWN phrasings below. It cannot
understand novel euphemism, and a determined paraphrase will walk past it.
It is a floor, not a ceiling. Human review still applies; this exists so that
the common cases stop depending on someone being alert at 07:30.

MARKUP IS NOT PROSE (2026-09-02)
--------------------------------
The back-catalog audit reported 49 blockers across 15 delivered newsletters,
and that number was put in front of Chris as a disclosure decision. Reading
the findings by hand — again — showed nine of them were the string "strong"
harvested from `<strong>` HTML tags:

    <strong>The school that justifies the premium:</strong>
              -> matched "schools as verdict" on excerpt "strong>The school"

Every rule pattern spans with `[^.!?\\n]{0,30}`, which crosses `</strong>` and
`<em>` without noticing. That cuts BOTH ways and both ways are wrong:

    FALSE POSITIVE  a tag donates an adjective it never meant ("strong")
    FALSE NEGATIVE  a tag spends the character budget, pushing a REAL
                    violation outside the {0,30} window so it never matches

So markup is neutralized before matching. Inline tags (<strong>, <em>, <a>)
become a space, because they sit INSIDE a sentence and the words either side
are genuinely adjacent. Block tags (<p>, <td>, <li>, <br>) become " . ",
because they are sentence boundaries and no rule may span one — otherwise
adjacent table cells `<td>Strong</td><td>Schools</td>` fabricate a violation
that no reader could ever see.

A gate that reports a number nobody has verified is not a control, it is a
rumour with a decimal point. The number Chris decides on has to be true in
both directions.
"""

import html
import pathlib
import re
import sys

# ---------------------------------------------------------------------------
# Severity
#   BLOCK — do not publish. Established steering proxy or protected-class term.
#   WARN  — usually fine, but review in context. Never auto-blocks.
# ---------------------------------------------------------------------------
BLOCK = "BLOCK"
WARN = "WARN"

# Each rule: (severity, compiled pattern, short label, why it is a problem)
# Patterns are matched case-insensitively against the publishable body.
_RULES = [
    # -- Schools as verdict (the Aug 31 failure) ----------------------------
    (BLOCK, r"\b(top|best|great|good|excellent|strong|quality|award[- ]winning"
            r"|top[- ]rated|highly[- ]rated|blue[- ]ribbon)\b[^.!?\n]{0,30}"
            r"\bschool",
     "schools as verdict",
     "School quality used as a reason to prefer an area is the most common "
     "steering proxy in real estate copy. State school facts, never verdicts."),
    (BLOCK, r"\bschool[s]?\b[^.!?\n]{0,40}\b(don't|do not|never)\s+compromise",
     "schools as verdict",
     "Evaluative claim about schools used as a selling point."),
    (BLOCK, r"\b(move|moved|moving|relocate[d]?)\b[^.!?\n]{0,40}\b(to|for)\b"
            r"[^.!?\n]{0,25}\bschool",
     "steering to schools",
     "Frames school quality as the reason to choose a location."),
    (BLOCK, r"\bschool districts?\b[^.!?\n]{0,30}\b(you'll|you will|worth|"
            r"premium|desirable|sought)\b",
     "schools as verdict",
     "School district framed as a desirability verdict."),
    (BLOCK, r"\b(premium|pay more|worth it)\b[^.!?\n]{0,30}\bfor\b"
            r"[^.!?\n]{0,15}\bschool",
     "schools as verdict",
     "Prices justified by school quality steers on a protected-class proxy."),
    # "Merrimack for new construction. Nashua for walkability. Amherst for
    # schools." — the bare <Place> for <schools> construction. Caught nothing
    # in v1 because it carries no adjective and no movement verb; the steer is
    # the sentence STRUCTURE, not any single word in it.
    (BLOCK, r"\b[A-Z][a-z]+\s+for\b[^.!?\n]{0,15}\bschool",
     "steering to schools",
     "Pairing a place name with schools as its selling point is steering, "
     "even with no adjective attached."),

    # -- Familial status ----------------------------------------------------
    (BLOCK, r"\b(family|families|kid|kids|child|children)[- ]"
            r"(friendly|oriented|focused)\b",
     "familial status",
     "Familial status is protected. Describe the property, not who should "
     "live in it."),
    (BLOCK, r"\b(perfect|great|ideal|wonderful)\b[^.!?\n]{0,25}\bfor\b"
            r"[^.!?\n]{0,15}\b(families|kids|children|couples|singles|"
            r"retirees|empty[- ]nesters|young professionals)\b",
     "audience targeting",
     "Naming who a home suits steers by familial status, age or marital "
     "status. Describe features; let readers self-select."),
    (BLOCK, r"\b(adult|mature)\s+(community|living|neighborhood)\b",
     "familial status / age",
     "Age-restricted framing is lawful only for qualified 55+ housing with "
     "the exemption documented. Do not use it as flavour."),
    (BLOCK, r"\bno\s+(children|kids)\b|\bchildless\b",
     "familial status",
     "Explicit exclusion of families. Never publishable."),
    # Added 2026-09-01. The back-catalog audit found this phrase live in the
    # Mont Vernon video description ("a wonderful place to raise a family"),
    # published Aug 3 and still up. The 'audience targeting' pattern above
    # missed it because it requires perfect/great/ideal + "for" + a noun;
    # "place to raise a family" carries the identical familial-status appeal
    # with different grammar. It is one of the most common phrases in real
    # estate copy, which is exactly why it needs to be caught by machine.
    (BLOCK, r"\b(raise|raising)\s+(a\s+|your\s+)?(family|kids|children)\b",
     "familial status",
     "'A place to raise a family' appeals directly to familial status. "
     "Describe the town — lot sizes, the school's location, trails — and "
     "let the reader decide who it suits."),
    (WARN, r"\b(starter|forever)\s+home\b",
     "familial status (soft)",
     "Common usage and usually fine, but reads as a life-stage signal. "
     "Check the surrounding sentence."),

    # -- Safety / neighborhood character proxies ---------------------------
    (BLOCK, r"\b(safe|safer|safest|low[- ]crime|crime[- ]free|secure)\b"
            r"[^.!?\n]{0,25}\b(neighborhood|area|community|town|street)s?\b",
     "safety proxy",
     "'Safe area' is a well-documented proxy for racial composition. Cite "
     "crime statistics or say nothing."),
    # Added 2026-09-01. The pattern above needs safe/secure ADJACENT to a
    # place noun, so it missed the live Mont Vernon line "looking for space,
    # safety, strong small schools" — where safety is a bare noun in an
    # amenity list. Same steering, no place noun to anchor on.
    #
    # The lookahead is load-bearing: "safety inspection", "safety code" and
    # "safety disclosure" are legitimate transaction vocabulary that appears
    # constantly in real listing copy. Flagging those would make this rule
    # noise, and a noisy rule gets muted — the exact failure this file was
    # written to prevent.
    (BLOCK, r"\b(looking for|searching for|seeking|want|wants|value|values|"
            r"prioritiz\w+|offers|offering|provides)\b[^.!?\n]{0,40}"
            r"\bsafety\b(?!\s+(inspection|report|code|standard|disclosure|"
            r"hazard|recall|check|feature|rail|glass|requirement))",
     "safety proxy",
     "Selling a town on 'safety' is a racial-composition proxy even as a "
     "bare noun in a list. Cite a crime statistic or cut the word."),
    (BLOCK, r"\b(good|nice|great|desirable|better|bad|rough|sketchy)\s+"
            r"(neighborhood|area|part of town|side of town)s?\b",
     "neighborhood character",
     "Unquantified area-quality judgements are steering. Describe concrete "
     "attributes instead."),
    (BLOCK, r"\b(up[- ]and[- ]coming|transitioning|changing|revitaliz\w+|"
            r"gentrif\w+)\s+(neighborhood|area|community)\b",
     "neighborhood character",
     "Coded language for demographic change."),
    (BLOCK, r"\b(exclusive|prestigious|elite|select)\s+"
            r"(neighborhood|community|enclave|address)(?:e?s)?\b",
     "exclusivity",
     "'Exclusive' implies who is excluded."),

    # -- Religion -----------------------------------------------------------
    (BLOCK, r"\b(walk|walking distance|close|near|minutes)\b[^.!?\n]{0,25}"
            r"\b(church|churches|synagogue|mosque|temple|parish)\b",
     "religion",
     "Proximity to houses of worship as a selling point signals religious "
     "preference. Listing them as landmarks in a town guide is different — "
     "check context."),
    (BLOCK, r"\b(christian|catholic|jewish|muslim|hindu|buddhist|mormon)\s+"
            r"(community|family|families|neighborhood|values)\b",
     "religion",
     "Religious character of an area is never a lawful selling point."),

    # -- Race / ethnicity / national origin ---------------------------------
    (BLOCK, r"\b(ethnic|racial|integrated|diverse|homogeneous|traditional)\s+"
            r"(neighborhood|community|area)\b",
     "race / national origin",
     "Describing an area's demographic makeup is steering, including when "
     "the description is positive."),
    (BLOCK, r"\b(english[- ]speaking|american[- ]born|native[- ]born)\b",
     "national origin",
     "National-origin preference."),

    # -- Disability ---------------------------------------------------------
    (BLOCK, r"\b(able[- ]bodied|healthy|fit)\s+(buyer|tenant|resident|owner)"
            r"[s]?\b",
     "disability",
     "Disability is protected. Describe accessibility features factually."),
    (BLOCK, r"\bnot\s+(suitable|appropriate)\s+for\b[^.!?\n]{0,25}"
            r"\b(disabled|handicap\w*|wheelchair|elderly)\b",
     "disability / age",
     "Explicit exclusion."),

    # -- Sex / marital status ----------------------------------------------
    (BLOCK, r"\b(bachelor|bachelorette)\s+(pad|home|apartment)\b",
     "sex / marital status",
     "Sex- and marital-status-coded framing."),
    (BLOCK, r"\b(ideal|perfect|great)\b[^.!?\n]{0,20}\bfor\b[^.!?\n]{0,15}"
            r"\b(him|her|men|women|bachelors)\b",
     "sex",
     "Sex-based targeting."),

    # -- Familial status: the BARE DEMOGRAPHIC SUBJECT (added Sept 2, 2026) --
    #
    # WHY THESE EXIST. On Sept 2 this module scanned a content brief and
    # returned ZERO findings. A human then read the same file and found eight
    # violations. Every rule above this point tests for an EVALUATIVE WORD --
    # "top-rated", "perfect for", "safe". The brief contained no evaluative
    # word anywhere near its demographics:
    #
    #     "Families who spent the long weekend in NH now think differently
    #      about what 'home' feels like."
    #     "September is Nashua's busiest month for families relocating
    #      before school starts."
    #
    # No verdict. No adjective. Just a protected class installed as the
    # SUBJECT of a market sentence -- which is precisely what steering is.
    # The verdict-vs-fact design was correct and too narrow: it assumed the
    # steer rides on the adjective. It rides on the noun.
    #
    # This is the second consecutive day a hand-read beat the suite
    # ("raise a family", Sept 1). Two in two days measures coverage, not luck.
    (BLOCK, r"\b(families|parents|young professionals|newlyweds|retirees|"
            r"empty[- ]nesters|young couples)\b\s+(who|that|with|looking|"
            r"moving|relocating|repositioning|priced)\b",
     "familial status / age — demographic as sentence subject",
     "A protected class is the SUBJECT of this market claim. No adjective is "
     "needed for this to steer. Describe demand, buyers, or households in a "
     "price band — never a demographic."),
    (BLOCK, r"\bfor\s+(families|parents|retirees|empty[- ]nesters)\b\s+"
            r"(relocating|moving|looking|seeking|who|that)\b",
     "familial status / age — demographic as target audience",
     "Names who the market is 'for'. Same steer, prepositional phrasing."),

    # -- School proximity offered as an amenity (added Sept 2, 2026) --------
    #
    # "5-minute school commute from most homes" walked past every rule above
    # because DISTANCE IS ON THE PERMITTED LIST -- and it is, in a town
    # profile. Offered as a reason to prefer the town, it steers on familial
    # status while containing nothing but a true number.
    #
    # RULE REFINEMENT THIS ENCODES: a permitted fact becomes a prohibited
    # verdict the moment it is offered as a reason to prefer the town.
    (BLOCK, r"\b(\d+[- ]minute|short|quick|easy|walkable)\b[^.!?\n]{0,25}"
            r"\bschool\b[^.!?\n]{0,25}\b(commute|walk|drive|distance)\b|"
            r"\bschool\s+(commute|proximity)\b",
     "familial status — school proximity as amenity",
     "School distance stated as a selling feature. State it as fact in a town "
     "profile if needed; it may not carry the sell."),
    (BLOCK, r"\b(school\s+(year|calendar|reopening|opens?|starts?)|"
            r"back[- ]to[- ]school)\b[^.!?\n]{0,40}"
            r"\b(deadline|urgen\w+|hurry|before|window|motivat\w+|close)\b|"
            r"\bmove\s+before\s+school\b",
     "familial status — school calendar as transaction deadline",
     "Uses the school calendar to create buying urgency. Steers on familial "
     "status AND is an urgency frame we banned on other grounds Aug 27."),
    (BLOCK, r"\b(school\s+choice|magnet\s+schools?|school\s+district)\b"
            r"(?![^.!?\n]{0,20}\b(is|are|on|at)\s+(located|route|road))",
     "familial status — schools as marketing bullet",
     "School selection framed as a reason to buy. Schools may be stated as "
     "fact ('the middle school is on Route 101'), never as an offer."),

    # -- "What the town FEELS like" = describing residents (Sept 2, 2026) ---
    #
    # The Aug 31 rule is "a town may be described, the people who live in it
    # may not." These phrases sound like town description and are not: a town
    # does not have warmth or belonging. Its residents do. That is the whole
    # distinction the rule turns on, and the checker could not see it.
    # -- The verdict AFTER the noun (added 2026-09-02, second pass) ---------
    #
    # Found by hand-reading remediated copy, not by the suite. Every school
    # rule above requires the adjective BEFORE the noun ("excellent schools").
    # These were live and invisible to all of them:
    #
    #     "Schools are still excellent."        (blog-2026-05-28-market-cooling)
    #     "Schools are top 5 percent in the state."   (live post 49426)
    #     "Schools are strong, the downtown is vibrant."  (live post 49413)
    #
    # Identical verdict, predicate word order. The Sept 2 lesson was that the
    # steer can ride on the noun instead of the adjective; this is the same
    # lesson again in the other direction -- a rule that pins WORD ORDER only
    # covers the phrasings its author happened to picture.
    (BLOCK, r"\bschools?\b\s+(?:are|is|were|was|remain[s]?|stay[s]?|seem[s]?)"
            r"\s+(?:still\s+|also\s+|genuinely\s+|really\s+|very\s+|quite\s+)?"
            r"(?:top|best|great|good|excellent|strong|solid|outstanding|"
            r"superb|exceptional|highly[- ]rated|top[- ]rated|top\s+\d+)",
     "schools as verdict",
     "School quality as a predicate rather than a modifier. Same verdict, "
     "same steer, reversed word order."),

    # Bare audience labelling with no following verb. The Sept 2 rule required
    # "for families WHO/RELOCATING/...", so a parenthetical or heading label
    # walked past it:
    #     "### The School-Year Connection (For Families)"
    #     "- best small towns in southern New Hampshire for families"
    (BLOCK, r"\bfor\s+(families|parents|retirees|empty[- ]nesters|couples|"
            r"singles|young professionals)\b\s*(?:[).,:;!?\]]|$)",
     "familial status / age — demographic as target audience",
     "Labels the content's audience by protected class. A heading, tag or "
     "parenthetical counts; it is the first thing a reader sees."),

    (BLOCK, r"\b(community feel|sense of community|neighborly|belonging|"
            r"small[- ]town charm|what home feels like|feels like home|"
            r"tight[- ]knit|close[- ]knit|welcoming)\b",
     "protected class proxy — resident character, not town fact",
     "Describes the people, not the place. A town has roads, taxes and lot "
     "sizes; it does not have warmth. Not checkable, not publishable."),
]

_COMPILED = [(sev, re.compile(pat, re.IGNORECASE), label, why)
             for sev, pat, label, why in _RULES]

# Lines the checker ignores: our own guardrail prose. A brief that TELLS Fiona
# "never write 'safe neighborhood'" must not trip the rule it is teaching.
#
# EXEMPTION IS STRUCTURAL, NOT KEYWORD-BASED — and that is a scar, not a
# preference. The first version of this pattern also exempted any line
# containing "never", "don't", "avoid"... which silently disabled the rule for
#     "Amherst schools don't compromise."
# — the single worst line in the Aug 31 brief and the whole reason this file
# exists. The checker would have reported CLEAN on its own founding failure.
#
# Guessing at intent from vocabulary turns a gate into a liar. Exemption now
# requires an explicit marker (❌ 🚫 ✅ BAD/OK) or a Fair Housing guardrail
# heading. Both are things the AUTHOR does deliberately, not things the
# checker infers.
_EXEMPT_MARKER = re.compile(
    r"^\s*(?:[-*+]\s*)?(?:❌|🚫|✅|⛔|\*\*(?:BAD|OK|BLOCK|WARN)\*\*"
    r"|(?:BAD|OK|BLOCK|WARN)\b)",
    re.IGNORECASE,
)

# A markdown heading that opens a guardrail section. Everything until the next
# heading of the same-or-higher level is instructional prose about the rules.
_GUARDRAIL_HEADING = re.compile(
    r"^(#{1,6})\s.*\b(fair housing|steering|banned|do not publish|"
    r"prohibited language)\b",
    re.IGNORECASE,
)
_ANY_HEADING = re.compile(r"^(#{1,6})\s")


# Tags that sit INSIDE a sentence. The words on either side of them really are
# adjacent, so they collapse to a single space.
_INLINE_TAGS = {
    "strong", "b", "em", "i", "u", "span", "a", "small", "sub", "sup",
    "font", "mark", "code", "abbr", "cite", "q", "s", "strike", "big",
}

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")



def _neutralize_markup(line):
    """Strip HTML so rules match PROSE, not tag names.

    Inline tags -> " "   (words either side are genuinely adjacent)
    Block tags  -> " . "  (a sentence boundary no rule pattern may span)

    The block-tag boundary is load-bearing. Rules span with [^.!?\\n]{0,30},
    so a bare space would let `<td>Strong</td><td>Schools</td>` match "strong
    schools" — a violation that exists only in the markup and that no reader
    could ever see. The "." makes the cell boundary opaque to every rule.
    """
    line = _HTML_COMMENT.sub(" ", line)
    line = _HTML_TAG.sub(
        lambda m: " " if m.group(1).lower() in _INLINE_TAGS else " . ",
        line,
    )
    # After tags are gone: &#39; -> ' so "don&#39;t compromise" still matches.
    # Done second so escaped sample text (&lt;strong&gt;) never becomes a tag.
    line = html.unescape(line)
    return line.replace("\xa0", " ")


def _iter_checkable_lines(text):
    """Yield (line_number, neutralized_line) for lines that should be scanned.

    Skips: fenced code blocks, explicitly marked guardrail lines, and any
    section opened by a Fair Housing / banned-language heading.

    Structural decisions (fences, headings, ❌/✅ markers) are made on the RAW
    line — they are markdown, not HTML. Only the text handed to the rules is
    markup-neutralized.
    """
    in_fence = False
    guardrail_depth = None  # heading level that opened a guardrail section
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = _ANY_HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if _GUARDRAIL_HEADING.match(line):
                guardrail_depth = level
                continue
            # A heading at the same or shallower level closes the section.
            if guardrail_depth is not None and level <= guardrail_depth:
                guardrail_depth = None

        if guardrail_depth is not None or not line.strip():
            continue
        if _EXEMPT_MARKER.match(line):
            continue
        checkable = _neutralize_markup(line)
        if not checkable.strip():
            continue
        yield lineno, checkable


def scan(text):
    """Scan copy for Fair Housing problems.

    Returns a list of dicts: severity, line, label, why, excerpt.
    Ordered BLOCK first, then by line number.
    """
    findings = []
    for lineno, line in _iter_checkable_lines(text):
        for severity, pattern, label, why in _COMPILED:
            # finditer, not search. A newsletter paragraph is ONE line of HTML,
            # so `search` reported at most one hit per rule per paragraph and
            # silently dropped every repeat. The audit undercounted delivered
            # newsletters for exactly this reason.
            for match in pattern.finditer(line):
                findings.append({
                    "severity": severity,
                    "line": lineno,
                    "label": label,
                    "why": why,
                    "excerpt": " ".join(match.group(0).split()),
                })
    findings.sort(key=lambda f: (f["severity"] != BLOCK, f["line"]))
    return findings


def has_blockers(findings):
    """True if anything must stop publication."""
    return any(f["severity"] == BLOCK for f in findings)


def self_test():
    """Positive control: prove the ruleset is loaded and firing.

    Sept 2: `python3 fair_housing.py <file>` exited 0 with no output on copy
    containing "perfect for families" and "top-rated schools", because this
    module had no __main__ and simply defined its functions and quit. A clean
    scan and a scan that never ran looked identical from the shell. Every CLI
    run now proves the rules fire before it reports on anyone's copy.
    """
    probe = "This town is perfect for families and has top-rated schools."
    hits = scan(probe)
    labels = {f["label"] for f in hits}
    expected = {"schools as verdict", "audience targeting"}
    missing = expected - labels
    if missing:
        raise SystemExit(
            "FATAL: fair_housing self-test FAILED — the ruleset is not firing.\n"
            f"  Probe: {probe!r}\n"
            f"  Expected labels {sorted(expected)}, missing {sorted(missing)}.\n"
            "  Refusing to report on real copy with a broken checker."
        )
    return len(hits)


def format_findings(findings):
    """Human-readable report block for the gate header / Telegram."""
    if not findings:
        return "Fair Housing: clean."
    blockers = [f for f in findings if f["severity"] == BLOCK]
    warnings = [f for f in findings if f["severity"] == WARN]
    out = []
    if blockers:
        out.append(f"🚨 FAIR HOUSING — {len(blockers)} BLOCKING:")
        for f in blockers:
            out.append(f"  L{f['line']} [{f['label']}] \"{f['excerpt']}\"")
            out.append(f"      {f['why']}")
    if warnings:
        out.append(f"⚠️  Fair Housing — {len(warnings)} to review:")
        for f in warnings:
            out.append(f"  L{f['line']} [{f['label']}] \"{f['excerpt']}\"")
    return "\n".join(out)


def _main(argv):
    """CLI. Alerts on no input; never exits clean without having scanned.

    Exit codes:
      0 = scanned, no blockers   1 = blockers found
      2 = misuse / unreadable input / self-test failure
    """
    args = [a for a in argv[1:] if a != "--self-test"]
    probe_hits = self_test()

    if "--self-test" in argv[1:] and not args:
        print(f"fair_housing self-test PASSED — ruleset live ({probe_hits} probe hits).")
        return 0

    if not args:
        print(
            "FATAL: no file given. Nothing was scanned.\n\n"
            "  python3 fair_housing.py FILE [FILE ...]   scan files\n"
            "  python3 fair_housing.py --self-test       prove the ruleset fires\n\n"
            "A gate with no input alerts; it does not exit clean.",
            file=sys.stderr,
        )
        return 2

    total_blockers = 0
    for path in args:
        try:
            text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"FATAL: cannot read {path}: {exc}. Nothing was scanned.", file=sys.stderr)
            return 2

        findings = scan(text)
        checked = sum(1 for _ in _iter_checkable_lines(text))
        blockers = [f for f in findings if f["severity"] == BLOCK]
        total_blockers += len(blockers)

        # Report the denominator too: "0 findings" and "read nothing" must not look alike.
        print(f"── {path} — {checked} checkable line(s) scanned")
        print(format_findings(findings))
        if not checked:
            print("  ⚠️  ZERO checkable lines. Verify this file holds prose, not an empty/binary target.")
        print()

    return 1 if total_blockers else 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
