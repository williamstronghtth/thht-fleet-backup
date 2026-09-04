#!/usr/bin/env python3
"""Rewrite Aug 26 7:30 PM Mont Vernon posts.

Reason: original copy cited Mont Vernon median $635K + 47 DOM as proof of a hot,
low-supply, competitive market. Every available source shows Mont Vernon prices
DOWN 4-7% YoY, and 47 days is ~2x SLOWER than the Hillsborough County median of
24 days (Redfin, July 2026). The figures were used to argue the opposite of what
they show, in Chris's own new hometown.
"""
import json
import os
import sys
import urllib.request

API = "https://getlate.dev/api/v1/posts"
KEY = os.environ.get("LATE_API_KEY")
if not KEY:
    sys.exit("LATE_API_KEY not set in environment")

LONG_FORM = (
    "Mont Vernon, New Hampshire — the town my family moves to next summer.\n\n"
    "Here is the honest read, and it is not the one you would expect a realtor to give you.\n\n"
    "Mont Vernon is not tracking the county. Hillsborough County set records in July. "
    "Mont Vernon did not. The median here is around $630,000 and it is DOWN year over year, "
    "depending on which source you use, by somewhere between 4 and 7 percent. "
    "Homes take about 47 days to sell. County median is 24.\n\n"
    "So Mont Vernon is slower and softer than the market around it.\n\n"
    "If you are selling here, that matters. Pricing to county comps will cost you weeks. "
    "This town is its own market and it has to be priced like one.\n\n"
    "If you are buying here, that is your opening. You get more room to think, more room to "
    "negotiate, and less pressure than you would face ten minutes down the road in Amherst or Milford.\n\n"
    "That is why I am not worried about moving here. A town does not have to be the hottest "
    "market in the county to be the right place to raise three kids.\n\n"
    "Questions about your own town's numbers? Reply or DM. 🏘️"
)

SHORT_FORM = (
    "Mont Vernon, NH: median around $630K and DOWN year over year. 47 days to sell vs 24 for "
    "Hillsborough County.\n\n"
    "It is slower and softer than the county — not hotter. Sellers: price to the town, not the "
    "county. Buyers: that gap is your opening."
)

TARGETS = {
    "6a8eceef915cdd73bc2c568b": LONG_FORM,
    "6a8ecec4c247d43e8be73f44": SHORT_FORM,
}


def update_post(post_id, content):
    """PUT the new content. Late API rejects PATCH with 405 — must use PUT."""
    req = urllib.request.Request(
        f"{API}/{post_id}",
        data=json.dumps({"content": content}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status


for post_id, content in TARGETS.items():
    try:
        status = update_post(post_id, content)
        print(f"{post_id}: HTTP {status}")
    except Exception as exc:
        print(f"{post_id}: FAILED — {exc}")
