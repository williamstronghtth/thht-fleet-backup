#!/usr/bin/env python3
"""Publish the Aug 31, 2026 blog post (Angle 3: Nashua median down 2.7%).

Figures traced to CLEARED-FIGURES-2026-08-31.md only.
Uploads featured image, publishes in Gutenberg block format, sets Yoast meta.
"""
import os
import sys
import subprocess
import xmlrpc.client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wp_config import get_credentials  # noqa: E402

SITE, USER, APP_PASSWORD = <REDACTED:CREDENTIAL>()
API = f"{SITE}/wp-json/wp/v2"

KEYPHRASE = "Nashua home prices"
SEO_TITLE = "Nashua Home Prices Fell 2.7% as New Hampshire Set a Record"
META_DESC = (
    "Nashua home prices fell 2.7% to $576,500 in July while New Hampshire set an "
    "all time record median of $580,000. Here is what that means for you."
)
SLUG = "nashua-home-prices-down-2-7-percent-july-2026"
POST_TITLE = "Nashua Home Prices Fell 2.7% While New Hampshire Set an All Time Record"
IMAGE_PATH = "/root/agents/fiona-murphy/workspace/inbox/file_194.jpg"
ALT_TEXT = "Nashua home prices July 2026, classic New England entry hall of a Southern NH home"

BLOCKS = [
    ("p", "Nashua home prices moved the opposite direction from the rest of the state in July. "
          "The median sale price in Nashua came in at $576,500, down 2.7% from a year ago and the "
          "lowest figure since March, while New Hampshire posted an all time record statewide median "
          "of $580,000 for single family homes. Two numbers, two directions, one month. Here is what "
          "that actually means if you are buying or selling around the Souhegan Valley."),

    ("h2", "Why Nashua Home Prices Fell While the State Set a Record"),
    ("p", "The record comes from the New Hampshire Association of Realtors, which put the July median "
          "single family sale price at $580,000, up 5.5% from $549,700 a year earlier. Nashua is the "
          "largest city in Hillsborough County, and a single city median reflects what actually closed "
          "that month, not what every home in town is worth. A month heavier on condos and smaller "
          "properties pulls the median down on its own."),
    ("p", "So a 2.7% year over year dip is worth naming honestly, and it is not evidence that values "
          "collapsed. It is one city, one month, running against a statewide record."),

    ("h2", "The Market Around Nashua Is Still Competitive"),
    ("p", "Zoom out to Hillsborough County and the picture is steady. Redfin puts the July median sale "
          "price across all housing types at $548,392, up roughly 3% year over year. Homes went under "
          "agreement in an average of 24 days, three days slower than last year. There were 1,494 "
          "active listings, up 8% from a year ago, with 1.71 months of supply, and 58% of homes sold "
          "above asking, up from 55%."),
    ("p", "Statewide, active inventory reached 2,992 homes, up 16% year over year and the highest level "
          "in about seven years. NHAR president Josh Greenwald describes inventory as improving while "
          "noting the state remains far from a balanced housing market. Both halves of that sentence "
          "are doing real work."),

    ("h2", "What Nashua Home Prices Mean If You Are Buying"),
    ("p", "You have more to choose from than buyers have had at any point since roughly 2019. That is "
          "the genuine good news, and almost nobody is saying it plainly. At the same time, 58% of "
          "homes are still selling above asking and the average listing is spoken for in 24 days, so "
          "more choice does not mean more time to decide."),
    ("p", "On financing, the 30 year fixed averaged 6.66% in the week ending August 27, one basis point "
          "from 6.65% the week before. That is noise, not a trend, and Freddie Mac's own headline called "
          "it holding steady. Fannie Mae currently forecasts rates below 6% by the fourth quarter, so "
          "there is no honest case for rushing a purchase to beat a rate increase. Get your financing "
          "in order because it makes you a stronger buyer, not because the clock is ticking."),

    ("h2", "What It Means If You Are Selling"),
    ("p", "Price to the data in front of you rather than to last spring. Nashua home prices softened "
          "while the statewide median set a record, which means a comparable sale from a different town "
          "is not your comparable sale. Ask for the numbers from your own street and your own price band."),
    ("p", "The demand is still there for correctly priced homes. Homes across the county are moving in "
          "24 days and well over half are closing above asking. What has changed is that buyers now have "
          "1,494 other listings to look at, so a stretch price gets skipped instead of negotiated."),

    ("h2", "The Honest Read"),
    ("p", "One softening city median inside a record setting state is not a contradiction. It is what a "
          "normalizing market looks like from close up. We publish the unflattering numbers alongside "
          "the flattering ones because that is the only way the flattering ones mean anything."),
    ("p", "If you want to know what your specific street is doing rather than what the county average is "
          'doing, <a href="/contact/">get in touch with The Hoover Home Team</a> and we will pull the '
          "comparable sales for you. Figures in this post come from Redfin, Freddie Mac, and the "
          '<a href="https://www.nhar.org/" target="_blank" rel="noopener">New Hampshire Association of '
          "Realtors</a>, July 2026 data."),
]


def build_content():
    parts = []
    for tag, text in BLOCKS:
        if tag == "p":
            parts.append(f"<!-- wp:paragraph --><p>{text}</p><!-- /wp:paragraph -->")
        else:
            parts.append(
                f'<!-- wp:heading {{"level":2}} --><h2>{text}</h2><!-- /wp:heading -->'
            )
    return "\n\n".join(parts)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {result.stderr[:400]}")
    return result.stdout


def upload_image():
    """Upload the featured image and set keyphrase-bearing alt text."""
    out = run([
        "curl", "-s", "-X", "POST", f"{API}/media",
        "-u", f"{USER}:{APP_PASSWORD}",
        "-H", f'Content-Disposition: attachment; filename={os.path.basename(IMAGE_PATH)}',
        "-H", "Content-Type: image/jpeg",
        "--data-binary", f"@{IMAGE_PATH}",
    ])
    import json
    media_id = json.loads(out)["id"]
    run([
        "curl", "-s", "-X", "POST", f"{API}/media/{media_id}",
        "-u", f"{USER}:{APP_PASSWORD}",
        "--data-urlencode", f"alt_text={ALT_TEXT}",
    ])
    return media_id


def create_post(media_id):
    import json
    out = run([
        "curl", "-s", "-X", "POST", f"{API}/posts",
        "-u", f"{USER}:{APP_PASSWORD}",
        "--data-urlencode", f"title={POST_TITLE}",
        "--data-urlencode", f"content={build_content()}",
        "--data-urlencode", f"slug={SLUG}",
        "--data-urlencode", "status=publish",
        "--data-urlencode", "categories[]=5",
        "--data-urlencode", f"featured_media={media_id}",
    ])
    return json.loads(out)


def set_yoast(post_id):
    """Yoast meta is not exposed over REST, so write it over XML-RPC."""
    server = xmlrpc.client.ServerProxy(f"{SITE}/xmlrpc.php")
    fields = {
        "_yoast_wpseo_focuskw": KEYPHRASE,
        "_yoast_wpseo_metadesc": META_DESC,
        "_yoast_wpseo_title": SEO_TITLE,
    }
    return server.wp.editPost(1, USER, APP_PASSWORD, post_id, {
        "custom_fields": [{"key": k, "value": v} for k, v in fields.items()]
    })


if __name__ == "__main__":
    print(f"meta description: {len(META_DESC)} chars")
    print(f"seo title: {len(SEO_TITLE)} chars")
    media = upload_image()
    print(f"media id: {media}")
    post = create_post(media)
    print(f"post id: {post.get('id')} — {post.get('link')}")
    print(f"yoast: {set_yoast(post['id'])}")
