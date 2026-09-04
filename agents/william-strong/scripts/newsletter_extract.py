#!/usr/bin/env python3
"""Turn a send_newsletter_*.js into the prose a subscriber actually reads.

WHY THIS EXISTS (William Strong, 2026-08-31)
--------------------------------------------
Every gate on this team protects an INTERNAL artifact. `brief-gate.py` has two
targets: the daily brief to Fiona, and the morning brief to Chris. Both are
readers inside the building.

The weekly newsletter is the only thing we publish to people who are not on the
team - 88 unique inboxes - and it has never passed a check of any kind. It is
generated as a JavaScript file with the figures hardcoded as string constants
and interpolated into an HTML email, so it does not look like a "brief" and it
never got a target.

That is the FIFTH instance of the error already written into the cleared block
as a standing amendment:

    Controls are named by the artifact they protect, not by the reader they
    happened to be built for.

Backtested against the Aug 25 send: it published `49 days` as a national
days-on-market figure. That number appears in no cleared block, ever. It went
to every subscriber and no control saw it, because no control was looking.

THE EXTRACTION PROBLEM
----------------------
A raw .js email template is ~20,000 characters of HTML and inline CSS. Fed
straight into extract_claims() it produces junk: `padding:30px`, `width=600`,
`rgba(0,0,0,0.08)`, `#0f3d2e`. A gate that flags forty false figures every
Tuesday is a gate Jack learns to ignore in two weeks, and alert fatigue is how
controls die quietly.

So: reduce the file to what a HUMAN READING THE EMAIL sees.

  1. Substitute the `const` figure values into their `${...}` placeholders.
     The figures live in constants (`const rate30 = '6.66%'`) and appear in the
     body only as `${rate30}`. Without substitution the gate checks a template
     and clears an email it never read.
  2. Drop <style> and <head> blocks entirely.
  3. Strip HTML TAGS but keep their inner text. This is what removes the CSS:
     every colour, pixel and opacity value lives inside an attribute, and
     attributes die with the tag.

What survives is the subject line and the visible copy - which is exactly the
surface where a wrong median or a steering line does its damage.

Bare integers are safe to leave behind (`port: 465`, `width 600`): every
extractor in brief-gate.py is unit-anchored - `$` for money, `%` for percent,
the literal word "days"/"months supply". An unlabelled number is not a claim.
"""

import re

# Order matters: <style> and <head> hold text that is NOT tags and would
# survive tag-stripping as a wall of CSS. They must go first, whole.
BLOCK_ELEMENTS = re.compile(
    r"<(style|head|script)\b.*?</\1>", re.DOTALL | re.IGNORECASE)

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")

# `const rate30 = '6.66%';` / "6.66%" / `6.66%`
CONST_STRING = re.compile(
    r"""^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(['"`])(.*?)\2\s*;?\s*$""",
    re.MULTILINE | re.DOTALL,
)

PLACEHOLDER = re.compile(r"\$\{\s*([A-Za-z_$][\w$]*)\s*\}")

# Lines that are unambiguously machinery, never subscriber-visible copy. Kept
# deliberately short: anything not listed here stays in and gets checked. The
# failure mode of an over-broad skip list is a figure that quietly stops being
# gated, which is the whole disease.
CODE_NOISE = re.compile(
    r"^\s*(?:const\s+\w+\s*=\s*require\(|require\(|console\.|process\.|"
    r"module\.exports|import\s|//)",
    re.MULTILINE,
)


def collect_constants(source):
    """Map single-line string constants to their values.

    Only string literals are collected. A const holding an object, a function
    or a template with its own interpolation is skipped rather than guessed at
    - a wrong substitution would invent a figure that nobody wrote.
    """
    return {name: value for name, _quote, value in CONST_STRING.findall(source)
            if "\n" not in value}


def substitute(text, constants, depth=2):
    """Resolve ${name} placeholders against the collected constants.

    Two passes by default: constants routinely reference other constants (a
    subject line built from `dateStr`). Bounded rather than recursive so a
    self-referential template cannot spin.
    """
    for _ in range(depth):
        if not PLACEHOLDER.search(text):
            break
        text = PLACEHOLDER.sub(
            lambda m: constants.get(m.group(1), m.group(0)), text)
    return text


def to_prose(source):
    """Reduce newsletter JavaScript to the visible text of the email."""
    constants = collect_constants(source)
    text = substitute(source, constants)
    text = CODE_NOISE.sub(" ", text)
    text = BLOCK_ELEMENTS.sub(" ", text)
    text = HTML_COMMENT.sub(" ", text)
    # Newline, not space: Fair Housing and the months-supply check are
    # line-scoped. Collapsing an email into one line would let a steering
    # sentence merge with its neighbours and change what the line-based rules
    # see.
    text = HTML_TAG.sub("\n", text)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


if __name__ == "__main__":
    import sys
    print(to_prose(open(sys.argv[1]).read()))
