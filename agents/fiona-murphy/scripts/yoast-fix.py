#!/usr/bin/env python3
"""Apply Yoast fixes to an existing WordPress post.

Usage:
    python3 yoast-fix.py <SPEC_JSON_PATH>

Spec shape (all keys optional except post_id):
    {
      "post_id": 49419,
      "keyphrase": "New Hampshire market report",
      "seo_title": "June 2026 New Hampshire Market Report",   # sets _yoast_wpseo_title
      "metadesc":  "...120-156 chars, contains keyphrase...",
      "content_file": "drafts/fix-49419.html"                  # optional full body replacement
    }

Always converts the final body to Gutenberg block markup, because posts created
through the REST API store classic HTML and Yoast's editor analyser reads that
as zero words. Meta writes update the existing row instead of appending a
duplicate (XML-RPC custom_fields ADDS by default).
"""
import json
import re
import sys
from pathlib import Path
import xmlrpc.client

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_config import get_credentials, get_server

SITE, USER, APP_PASSWORD = <REDACTED:CREDENTIAL>()

META_KEYS = {
    "keyphrase": "_yoast_wpseo_focuskw",
    "seo_title": "_yoast_wpseo_title",
    "metadesc": "_yoast_wpseo_metadesc",
}


def connect():
    return get_server()


def to_blocks(raw_html):
    """Wrap classic HTML chunks in Gutenberg block delimiters."""
    if "<!-- wp:" in raw_html:
        return raw_html
    chunks = [c.strip() for c in re.split(r"\n\s*\n", raw_html.strip()) if c.strip()]
    out = []
    for chunk in chunks:
        heading = re.match(r"<h([2-6])\b", chunk, flags=re.I)
        if heading:
            out.append(f'<!-- wp:heading {{"level":{heading.group(1)}}} -->\n{chunk}\n<!-- /wp:heading -->')
        elif re.match(r"<(ul|ol)\b", chunk, flags=re.I):
            out.append(f"<!-- wp:list -->\n{chunk}\n<!-- /wp:list -->")
        elif re.match(r"<blockquote\b", chunk, flags=re.I):
            out.append(f"<!-- wp:quote -->\n{chunk}\n<!-- /wp:quote -->")
        elif re.match(r"<p\b", chunk, flags=re.I):
            out.append(f"<!-- wp:paragraph -->\n{chunk}\n<!-- /wp:paragraph -->")
        elif chunk.startswith("<"):
            out.append(f"<!-- wp:html -->\n{chunk}\n<!-- /wp:html -->")
        else:
            out.append(f"<!-- wp:paragraph -->\n<p>{chunk}</p>\n<!-- /wp:paragraph -->")
    return "\n\n".join(out)


def build_custom_fields(existing, spec):
    """Return custom_fields entries, reusing meta ids so values overwrite."""
    by_key = {}
    for field in existing:
        by_key.setdefault(field.get("key"), []).append(field)
    entries = []
    for spec_key, meta_key in META_KEYS.items():
        if spec_key not in spec:
            continue
        rows = by_key.get(meta_key, [])
        if rows:
            entries.append({"id": rows[0]["id"], "key": meta_key, "value": spec[spec_key]})
            # Drop any duplicate rows left behind by earlier appends.
            for stale in rows[1:]:
                entries.append({"id": stale["id"]})
        else:
            entries.append({"key": meta_key, "value": spec[spec_key]})
    return entries


def main():
    spec = json.load(open(sys.argv[1]))
    post_id = int(spec["post_id"])
    server = connect()
    post = server.wp.getPost(1, USER, APP_PASSWORD, post_id)

    content = post.get("post_content", "")
    if spec.get("content_file"):
        content = open(spec["content_file"]).read()
    payload = {"post_content": to_blocks(content)}

    if spec.get("post_title"):
        payload["post_title"] = spec["post_title"]

    fields = build_custom_fields(post.get("custom_fields", []), spec)
    if fields:
        payload["custom_fields"] = fields

    server.wp.editPost(1, USER, APP_PASSWORD, post_id, payload)
    print(f"Updated post {post_id}")


if __name__ == "__main__":
    main()
