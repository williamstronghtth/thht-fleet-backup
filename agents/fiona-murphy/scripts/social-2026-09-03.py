#!/usr/bin/env python3
"""Sept 3, 2026 social posts.

Brief was rejected 07:30 ET on two gates. Chris cleared the run at 08:04 ET with the
instruction to pivot off the Fair Housing violation rather than hold.

  - Fair Housing: Angle 1 (school district) DROPPED entirely, not reworded. No school,
    demographic, or calendar-deadline reference appears in either post.
  - Figures: none of the 10 uncleared brief figures are used. Every number below is read
    verbatim from CLEARED-FIGURES-2026-09-03.md with its cleared direction.
  - No rate figure appears anywhere: the cleared block expires today at 12:00 PM ET when
    new PMMS lands, and the evening post is scheduled for 7:30 PM.
"""
import os
import sys

import requests

API = "https://getlate.dev/api/v1"
KEY = os.environ["LATE_API_KEY"]
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

INSTAGRAM = {"platform": "instagram", "accountId": "698f6a5ffd3d49fbfa3e29f7"}
FACEBOOK = {"platform": "facebook", "accountId": "698f6ab9fd3d49fbfa3e2a9f"}
LINKEDIN = {"platform": "linkedin", "accountId": "698f6b23fd3d49fbfa3e2baf"}
GOOGLE = {"platform": "googlebusiness", "accountId": "6a1f19432b2567671aa1ea24"}
TWITTER = {"platform": "twitter", "accountId": "698f6ad0fd3d49fbfa3e2afd"}
BLUESKY = {"platform": "bluesky", "accountId": "6a62203c542d8bc5a6c8168d"}

INBOX = "/root/agents/fiona-murphy/workspace/inbox"
MORNING_IMAGE = f"{INBOX}/file_226.jpg"
EVENING_IMAGE = f"{INBOX}/file_212.jpg"
EVENING_ET = "2026-09-03T19:30:00"

MORNING_LONG = """The county went up. Nashua went down.

In July the Hillsborough County median sale price was $548,392, up about 3 percent year over year across all home types. Nashua's median was $576,500, down 2.7 percent year over year and its lowest reading since March.

Same county, same month, opposite directions.

That matters in two directions. If you are pricing a Nashua home off a county headline, the headline is describing a different market than yours. And if you have been told the whole region is climbing, that is not what the town level numbers say.

Nashua still carries a higher median than the county as a whole. It simply is not moving the same way, and a single regional number will never tell you which of those two facts applies to your street.

Sources: Redfin and NHAR, July 2026.

#Nashua #SouthernNH #NHRealEstate"""

MORNING_SHORT = """The county went up. Nashua went down.

Hillsborough County median in July: $548,392, up about 3% YoY. Nashua: $576,500, down 2.7% and its lowest since March.

Same county, same month, opposite directions.

Redfin/NHAR, July 2026."""

EVENING_LONG = """Two July numbers that seem to argue with each other.

Homes in Hillsborough County took a median 24 days to sell, three days slower than a year ago. In the same month, 58 percent of homes sold above asking.

Slower and more competitive at once.

The reconciliation is that an average hides a split. A correctly priced home in an active band still draws competition and still moves quickly. Everything else sits, and the sitting is what pulls the median days upward.

So if you are selling this fall, the pace of the market is not really your question. Your price against the current market is. Those two numbers are the same market, measured from opposite ends.

Source: Redfin, Hillsborough County, July 2026.

#SouthernNH #NHRealEstate"""

EVENING_SHORT = """Two July numbers that argue with each other.

Hillsborough County homes took a median 24 days to sell, 3 days slower than a year ago. In the same month, 58% sold above asking.

An average hides a split. Priced right, it moves. Priced wrong, it sits.

Redfin, July 2026."""

BANNED = [
    "school", "family", "families", "parents", "safe neighborhood", "good area",
    "up-and-coming", "community feel", "belonging", "kid", "church",
]
UNCLEARED = ["510,000", "635,000", "$500,000", "$900,000", "23 days", "14 days", "2.5%", "11%", "1.5%"]


def preflight():
    """Fail loudly rather than publish a gated phrase or an uncleared figure."""
    for label, text in [
        ("morning-long", MORNING_LONG), ("morning-short", MORNING_SHORT),
        ("evening-long", EVENING_LONG), ("evening-short", EVENING_SHORT),
    ]:
        lowered = text.lower()
        for word in BANNED:
            if word in lowered:
                sys.exit(f"FAIR HOUSING preflight failed: '{word}' in {label}")
        for figure in UNCLEARED:
            if figure.lower() in lowered:
                sys.exit(f"FIGURE preflight failed: uncleared '{figure}' in {label}")
    assert len(MORNING_SHORT) <= 275, f"morning twitter {len(MORNING_SHORT)}"
    assert len(EVENING_SHORT) <= 275, f"evening twitter {len(EVENING_SHORT)}"
    print(f"preflight OK - twitter lengths: morning {len(MORNING_SHORT)}, evening {len(EVENING_SHORT)}")


def upload(image_path):
    filename = os.path.basename(image_path)
    presign = requests.post(
        f"{API}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg"},
        timeout=60,
    )
    if presign.status_code != 200:
        sys.exit(f"presign failed for {filename}: {presign.status_code} {presign.text[:300]}")
    data = presign.json()
    with open(image_path, "rb") as handle:
        put = requests.put(data["uploadUrl"], data=handle.read(), timeout=120)
    if put.status_code not in (200, 201):
        sys.exit(f"upload failed for {filename}: {put.status_code} {put.text[:300]}")
    print(f"  uploaded {filename}")
    return data["publicUrl"]


def post(platforms, content, media_url, scheduled=None, label=""):
    payload = {
        "platforms": platforms,
        "content": content,
        "mediaItems": [{"type": "image", "url": media_url}],
    }
    if scheduled:
        payload["scheduledFor"] = scheduled
        payload["timezone"] = "America/New_York"
    else:
        payload["publishNow"] = True
    response = requests.post(f"{API}/posts", headers=HEADERS, json=payload, timeout=90)
    if response.status_code >= 300:
        print(f"  [FAIL] {label}: {response.status_code} {response.text[:400]}")
        return None
    post_id = response.json().get("post", {}).get("_id")
    print(f"  [OK] {label}: {post_id}")
    return post_id


def main():
    preflight()

    print("morning image")
    morning_url = upload(MORNING_IMAGE)
    print("morning posts")
    post([INSTAGRAM, FACEBOOK, LINKEDIN, GOOGLE], MORNING_LONG, morning_url, label="morning batch")
    post([TWITTER], MORNING_SHORT, morning_url, label="morning twitter")
    post([BLUESKY], MORNING_SHORT, morning_url, label="morning bluesky")

    print("evening image")
    evening_url = upload(EVENING_IMAGE)
    print("evening posts (scheduled 7:30 PM ET)")
    post([INSTAGRAM, FACEBOOK, LINKEDIN, GOOGLE], EVENING_LONG, evening_url, EVENING_ET, "evening batch")
    post([TWITTER], EVENING_SHORT, evening_url, EVENING_ET, "evening twitter")
    post([BLUESKY], EVENING_SHORT, evening_url, EVENING_ET, "evening bluesky")


if __name__ == "__main__":
    main()
