#!/usr/bin/env python3
"""Pre-publish / post-publish Yoast green-score checker for thehooverhometeam.com.

Usage:
    python3 yoast-check.py <POST_ID>

Replicates the Yoast Premium SEO analysis checks locally so a post can be
verified BEFORE (or immediately after) publishing, instead of waiting to see
an orange dot in wp-admin. See memory/yoast-green-checklist.md.
"""
import re
import sys
from pathlib import Path
import html
import xmlrpc.client

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_config import get_credentials, get_server

SITE, USER, APP_PASSWORD = <REDACTED:CREDENTIAL>()

MIN_WORDS = 300
DENSITY_MIN, DENSITY_MAX = 0.5, 2.5
META_MIN, META_MAX = 120, 156
TITLE_MAX = 60
KEYPHRASE_WORDS_MAX = 4


def fetch_post(post_id):
    server = get_server()
    return server.wp.getPost(1, USER, APP_PASSWORD, post_id)


def get_meta(post, key):
    for field in post.get("custom_fields", []):
        if field.get("key") == key:
            return field.get("value", "")
    return ""


def strip_tags(raw_html):
    text = re.sub(r"<!--.*?-->", " ", raw_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def count_occurrences(haystack, needle):
    return len(re.findall(re.escape(needle.lower()), haystack.lower()))


def keyphrase_in_slug(keyphrase, slug):
    """Match keyphrase words against whole slug tokens, not raw substrings.

    A plain substring test passes on accidents like "nh" inside "nhs", so compare
    against the hyphen separated tokens and allow only a simple plural/possessive
    suffix (markets, nhs, buyers).
    """
    tokens = [t for t in re.split(r"[^a-z0-9]+", slug.lower()) if t]
    for word in re.split(r"[^a-z0-9]+", keyphrase.lower()):
        if not word:
            continue
        if not any(t == word or t in (word + "s", word + "es") for t in tokens):
            return False
    return True


def check(label, passed, detail=""):
    icon = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {label}" + (f" — {detail}" if detail else ""))
    return passed


def run_checks(post):
    content = post.get("post_content", "")
    text = strip_tags(content)
    words = text.split()
    keyphrase = get_meta(post, "_yoast_wpseo_focuskw").strip()
    metadesc = get_meta(post, "_yoast_wpseo_metadesc").strip()
    # Yoast scores the SEO title (snippet preview), falling back to the post title
    # when _yoast_wpseo_title is empty. Match that behaviour.
    seo_title = get_meta(post, "_yoast_wpseo_title").strip()
    title = html.unescape(seo_title or post.get("post_title", ""))
    slug = post.get("post_name", "")
    headings = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", content, flags=re.S | re.I)
    first_para = strip_tags(re.search(r"<p[^>]*>(.*?)</p>", content, flags=re.S | re.I).group(1)) if re.search(r"<p[^>]*>(.*?)</p>", content, flags=re.S | re.I) else text[:400]
    links = re.findall(r'href="([^"]+)"', content)
    # Relative hrefs are always internal; absolute ones are internal only on our domain.
    internal = [u for u in links if not u.startswith("http") or "thehooverhometeam.com" in u]
    external = [u for u in links if u.startswith("http") and "thehooverhometeam.com" not in u]

    print(f"\nPost {post.get('post_id')} — {title}")
    print(f"Keyphrase: {keyphrase or '(none set)'}\n")

    results = []
    if not keyphrase:
        results.append(check("Focus keyphrase set", False, "no _yoast_wpseo_focuskw"))
        return results

    kw_words = len(keyphrase.split())
    occurrences = count_occurrences(text, keyphrase)
    # Yoast density = keyphrase occurrences / total words (the phrase counts as one hit).
    density = (occurrences / len(words) * 100) if words else 0

    results.append(check("Keyphrase length 2-4 words", 2 <= kw_words <= KEYPHRASE_WORDS_MAX, f"{kw_words} words"))
    results.append(check("Keyphrase in title", keyphrase.lower() in title.lower()))
    results.append(check("Title <= 60 chars", len(title) <= TITLE_MAX, f"{len(title)} chars"))
    results.append(check("Keyphrase in slug", keyphrase_in_slug(keyphrase, slug), slug))
    results.append(check("Keyphrase in first paragraph", keyphrase.lower() in first_para.lower()))
    results.append(check("Keyphrase in an H2/H3", any(keyphrase.lower() in strip_tags(h).lower() for h in headings), f"{len(headings)} subheadings"))
    results.append(check("Word count >= 300", len(words) >= MIN_WORDS, f"{len(words)} words"))
    results.append(check("Keyphrase density 0.5-2.5%", DENSITY_MIN <= density <= DENSITY_MAX, f"{density:.2f}% ({occurrences}x)"))
    results.append(check("Meta description 120-156 chars", META_MIN <= len(metadesc) <= META_MAX, f"{len(metadesc)} chars"))
    results.append(check("Keyphrase in meta description", keyphrase.lower() in metadesc.lower()))
    results.append(check("At least one internal link", len(internal) >= 1, f"{len(internal)} found"))
    results.append(check("At least one outbound link", len(external) >= 1, f"{len(external)} found"))
    # wp.getPost returns {} for a set thumbnail and [] when none is set.
    thumb = post.get("post_thumbnail") or {}
    thumb_id = thumb.get("attachment_id", "") if isinstance(thumb, dict) else ""
    results.append(check("Featured image set", bool(thumb_id), str(thumb_id)))
    results.append(check("Gutenberg block markup present", "<!-- wp:" in content, f"{content.count('<!-- wp:')} blocks"))
    results.append(check("Images have alt text", "<img" not in content or 'alt="' in content))
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 yoast-check.py <POST_ID>")
        sys.exit(1)
    try:
        post = fetch_post(int(sys.argv[1]))
    except Exception as err:
        print(f"Failed to fetch post: {err}")
        sys.exit(1)
    results = run_checks(post)
    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} checks passed.")
    print("GREEN — ready to publish." if failed == 0 else f"NOT GREEN — {failed} check(s) to fix.")
    sys.exit(0 if failed == 0 else 2)


if __name__ == "__main__":
    main()
