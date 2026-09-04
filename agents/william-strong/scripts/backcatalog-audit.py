#!/usr/bin/env python3
"""Fair Housing audit of ALREADY-PUBLISHED content.

WHY THIS EXISTS (2026-09-01)
----------------------------
Every control we own looks FORWARD. `brief-gate.py` checks tomorrow's brief.
`fair_housing.py` checks tomorrow's copy. `letter-gate.py` checks unsent mail.

On 2026-09-01 Iris pointed out the obvious thing none of us had done: nothing
had ever checked what we ALREADY PUBLISHED. The Fair Housing gate was built
Aug 31. Every artifact published before Aug 31 — four months of newsletters,
blog posts, and video descriptions — predates the only control that would
have caught it.

The first run found 46 BLOCK-severity findings across 26 published artifacts,
including 13 newsletters that had already been delivered to subscribers.
Not one of them had ever been checked by anything.

THE DISTINCTION THAT DRIVES REMEDIATION
---------------------------------------
Published is not one category. It is two, and they have different fixes:

    EDITABLE   video descriptions, blog pages, GBP profile, site copy
               -> fix the live text; the exposure ends when you do.

    DELIVERED  sent newsletters, mailed letters
               -> cannot be recalled. The finding is a RECORD, not a task.
               Its value is that it tells you what is out there if anyone
               ever asks, and it stops you repeating the pattern.

Reporting these together as one number would be a lie in both directions:
it overstates what is fixable and understates what is already gone.

This is a REPORT-ONLY tool. It never edits an artifact. Remediation of live
copy is a human decision (see the EDITABLE list), because retitling a video
or rewriting a blog page has SEO and brand consequences a script cannot judge.
"""

import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import fair_housing  # noqa: E402

# Roots to sweep. Each is tagged with whether its artifacts can still be
# edited after publication - that tag is what splits the report.
ROOTS = [
    ("/root/agents/fiona-murphy/workspace/drafts", "EDITABLE"),
    ("/root/agents/jack-sullivan/workspace/newsletter", "DELIVERED"),
    ("/root/agents/jack-sullivan/workspace/letters", "DELIVERED"),
]

# .html added 2026-09-02. The drafts tree held 35 .html files -- MORE than its
# 34 .md files -- and not one had ever been scanned, because the original
# suffix list was written from a guess about what we author in rather than
# from a listing of what is actually there. Several are numbered like
# WordPress post IDs (49426.html), i.e. live posts on the public site.
#
# An audit that silently skips a file type reports "clean" for content it
# never opened. That is the same failure as a gate that is not wired up, and
# it is harder to notice because the report looks identical either way.
#
# If a new extension shows up in these roots, add it here. Check with:
#   find <root> -type f | sed 's/.*\.//' | sort | uniq -c
SUFFIXES = {".md", ".js", ".txt", ".html", ".htm"}
SKIP_PARTS = {"node_modules", "__pycache__", ".git"}


def iter_files(root: Path):
    """Yield checkable files under root, skipping vendored/dependency dirs."""
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        if SKIP_PARTS & set(path.parts):
            continue
        yield path


# A draft that was pulled before publication is not published content and must
# not sit in a remediation queue. On 2026-09-02 four of the forty "FIXABLE NOW"
# blockers were in drafts/withdrawn/ -- copy that had been killed that same
# morning. Counting it as outstanding work overstates live exposure, which is
# the same class of error as the <strong> tag false positives: a number nobody
# can act on, presented as one they must.
#
# It is still SCANNED and still REPORTED, in its own bucket. Silently dropping
# it would hide the case where someone edits a withdrawn file and re-queues it.
# --- LIVE VERIFICATION (added 2026-09-03) ----------------------------------
#
# WHY: for three days this audit reported "35 LIVE WordPress blockers" and was
# escalated to Chris in those words. It had never made an HTTP request. It
# scans drafts/yoast-fixes/<postid>.html -- LOCAL COPIES named after WordPress
# post IDs. The word "live" was an inference from a filename, not a
# measurement.
#
# On 2026-09-03 the live site was checked by hand and the count held: the
# violations really are published. But the local tree was an accurate mirror
# BY ACCIDENT. Had anyone edited the live posts without syncing the copies,
# the report would have been phantom findings and nothing would have said so
# -- the exact shape of the security scanner that spent weeks reading its own
# output back to itself.
#
#     An audit of "published" content must fetch the published content.
#     A file named after a post ID is not the post.
#
# So --live re-scans the rendered body from the REST API and reports DRIFT
# between local and live. Drift in either direction is the alarm:
#   local > live  -> we are quoting findings that were already fixed
#   live > local  -> published copy carries violations no local file shows
WP_API = "https://thehooverhometeam.com/wp-json/wp/v2/posts/{id}?_fields=id,content,modified"
FETCH_TIMEOUT = 30

# Local files whose name is NOT the post ID. Without this map they are skipped
# by --live and silently drop out of the live total -- which is how a report
# says "30 live" while 35 are actually published. Resolved 2026-09-03 via
# /wp-json/wp/v2/posts?search=... and confirmed by scanning the fetched body.
#
# If you add a draft here, VERIFY the ID by fetching it and checking the
# blocker count matches the local file. A wrong ID reports a real violation
# against innocent copy.
FILENAME_TO_POST_ID = {
    "23-austin-lane-just-sold": "49484",   # /23-austin-lane-hollis-nh-just-sold/
    "2026-08-29-blog-body": "49597",       # /choosing-between-southern-nh-towns/
}


def strip_html(markup: str) -> str:
    """Rendered HTML -> plain text, so the scanner sees prose not tags.

    Entities are unescaped BEFORE tag-stripping: the Aug 31 gate under-counted
    because `<strong>top</strong> schools` hid the phrase behind a tag
    boundary.

    KNOWN AND ACCEPTED FALSE-POSITIVE: tags become spaces, so adjacent block
    elements fuse across the boundary -- `<td>top</td><td>school</td>` reads as
    the phrase "top school" though it was never written as one. Verified by
    control C3 on 2026-09-03; this is a real limitation, not a theoretical one.

    It is accepted deliberately. The alternative -- deleting tags -- turns
    `<strong>top</strong>schools` into "topschools" and MISSES it. For a
    compliance scanner a false alarm costs a human one minute of reading; a
    false clean costs a published violation. So this over-reports by design,
    and every --live finding must be eyeballed against the real sentence
    before it is quoted to anyone.
    """
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", markup,
                  flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def fetch_live_post(post_id: str):
    """Return (text, modified) for a live post, or (None, reason) on failure.

    A fetch failure must never read as 'clean' -- it returns a reason that the
    caller reports as UNVERIFIED, never as zero findings.
    """
    # An explicit User-Agent is required: the site's WAF answers urllib's
    # default with 406. Caught by control C5 -- without it every post reports
    # UNVERIFIED and the whole live mode is decorative.
    req = urllib.request.Request(
        WP_API.format(id=post_id),
        headers={"User-Agent": "THHT-FairHousingAudit/1.0 (internal)",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as err:
        return None, f"fetch failed: {type(err).__name__}: {err}"
    try:
        rendered = payload["content"]["rendered"]
    except (KeyError, TypeError):
        return None, "unexpected API shape: no content.rendered"
    return strip_html(rendered), payload.get("modified", "unknown")


def audit_live(local_results):
    """Re-scan numbered posts against the live site. Returns drift rows."""
    rows = []
    for local_count, _findings, path in local_results:
        post_id = path.stem
        if not post_id.isdigit():
            post_id = FILENAME_TO_POST_ID.get(path.stem)
        if not post_id:
            # Not skipped silently: an unmappable file is reported as
            # UNMAPPED so it cannot quietly vanish from the live total.
            rows.append((path.stem, local_count, None,
                         "UNMAPPED — no post ID; add to FILENAME_TO_POST_ID"))
            continue
        text, meta = fetch_live_post(post_id)
        if text is None:
            rows.append((post_id, local_count, None, meta))
            continue
        blockers = [f for f in fair_housing.scan(text)
                    if f["severity"] == fair_housing.BLOCK]
        rows.append((post_id, local_count, len(blockers), meta))
    return rows


def render_live(rows):
    """Print the live-verification section. Returns (live_total, n_unverified)."""
    print(f"\n## LIVE VERIFICATION — {len(rows)} numbered post(s) fetched "
          f"from the public site")
    if not rows:
        print("   (no numbered post IDs in the editable set)")
        return 0, 0
    live_total = 0
    unverified = 0
    for post_id, local_n, live_n, meta in sorted(rows, key=lambda r: r[0]):
        if live_n is None:
            unverified += 1
            print(f"   ?? UNVERIFIED  {post_id}  local={local_n}  {meta}")
            continue
        live_total += live_n
        flag = "  <-- DRIFT" if live_n != local_n else ""
        print(f"   {'!!' if live_n else 'ok'} {post_id}  "
              f"local={local_n}  live={live_n}  modified={meta}{flag}")
    if unverified:
        print(f"\n   {unverified} post(s) COULD NOT BE VERIFIED. "
              f"Unverified is not clean — do not quote a live total.")
    return live_total, unverified


WITHDRAWN_PARTS = {"withdrawn", "retired", "killed"}


def bucket_for(path: Path, default: str) -> str:
    """Withdrawn drafts are reclassified out of the actionable bucket."""
    if default == "EDITABLE" and WITHDRAWN_PARTS & {p.lower() for p in path.parts}:
        return "WITHDRAWN"
    return default


def audit_root(root: Path):
    """Scan one root. Returns [(block_count, findings, path)] for hits only."""
    results = []
    for path in iter_files(root):
        try:
            text = path.read_text(errors="ignore")
        except OSError as err:
            print(f"  ! could not read {path}: {err}", file=sys.stderr)
            continue
        findings = fair_housing.scan(text)
        blockers = [f for f in findings if f["severity"] == fair_housing.BLOCK]
        if blockers:
            results.append((len(blockers), findings, path))
    results.sort(key=lambda r: -r[0])
    return results


def render(bucket, results, verbose):
    """Print one bucket's section. Returns total blocker count."""
    total = sum(r[0] for r in results)
    if not results:
        print(f"\n## {bucket} — clean\n")
        return 0

    if bucket == "EDITABLE":
        header = f"\n## {bucket} — {total} blocker(s) in {len(results)} file(s) — FIXABLE NOW\n"
    elif bucket == "WITHDRAWN":
        header = (
            f"\n## {bucket} — {total} blocker(s) in {len(results)} file(s) — "
            f"pulled before publication, no exposure (record only)\n"
        )
    else:
        header = (
            f"\n## {bucket} — {total} blocker(s) in {len(results)} file(s) — "
            f"ALREADY OUT, cannot be recalled (record only)\n"
        )
    print(header)

    for count, findings, path in results:
        print(f"  {count:>2} BLOCK  {path.name}")
        if verbose:
            for f in findings:
                if f["severity"] != fair_housing.BLOCK:
                    continue
                print(f"           - [{f['label']}] {f['excerpt'][:90]}")
    return total


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    live = "--live" in sys.argv

    print("# Fair Housing — Back-Catalog Audit")
    print("# Scans content ALREADY PUBLISHED. Report only; edits nothing.")
    if not live:
        print("# LOCAL FILES ONLY — these are copies named after post IDs, "
              "not the posts.")
        print("# Do NOT describe this count as 'live'. Use --live to verify "
              "against the site.")

    grand = {}
    for root_str, bucket in ROOTS:
        for result in audit_root(Path(root_str)):
            path = result[2]
            grand.setdefault(bucket_for(path, bucket), []).append(result)

    editable = sorted(grand.get("EDITABLE", []), key=lambda r: -r[0])
    delivered = sorted(grand.get("DELIVERED", []), key=lambda r: -r[0])
    withdrawn = sorted(grand.get("WITHDRAWN", []), key=lambda r: -r[0])

    n_edit = render("EDITABLE", editable, verbose)
    n_deliv = render("DELIVERED", delivered, verbose)
    n_withdrawn = render("WITHDRAWN", withdrawn, verbose)

    print("\n" + "=" * 62)
    print(f"FIXABLE NOW:     {n_edit:>3} blocker(s) in {len(editable)} file(s)")
    print(f"ALREADY OUT:     {n_deliv:>3} blocker(s) in {len(delivered)} file(s)")
    print(f"WITHDRAWN:       {n_withdrawn:>3} blocker(s) in "
          f"{len(withdrawn)} file(s) — no exposure")
    print("=" * 62)

    live_total = 0
    unverified = 0
    if live:
        live_total, unverified = render_live(audit_live(editable))
        print("\n" + "=" * 62)
        print(f"LOCAL COPIES:    {n_edit:>3} blocker(s)")
        print(f"LIVE ON SITE:    {live_total:>3} blocker(s) "
              f"(posts resolved to a live URL)")
        print("=" * 62)

    if not verbose:
        print("\nRun with --verbose to see the offending lines.")
    if not live:
        print("Run with --live to check these against the published site.")

    # Exit 1 when live, editable copy still carries a blocker - that is the
    # only condition anyone can still ACT on. Delivered mail is history: it
    # must be reported, but it must never hold an exit code hostage forever,
    # or the signal becomes permanent noise and gets muted.
    # An unverifiable post is not a clean post. If --live was asked for and a
    # fetch failed, fail the run rather than let a network error read as
    # "nothing published is broken."
    if live and unverified:
        return 2
    return 1 if n_edit else 0


if __name__ == "__main__":
    sys.exit(main())
