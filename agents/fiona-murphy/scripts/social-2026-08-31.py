#!/usr/bin/env python3
"""Aug 31, 2026 social posts. Angle 1 (morning) + Angle 2 (evening, scheduled 7:30 PM ET).

Text only by design: photo inventory is under spacing holds and William's reissue brief
explicitly cleared running these as text cards. Instagram is skipped because it requires media.
Figures traced to CLEARED-FIGURES-2026-08-31.md only.
"""
import os
import sys
import requests

API = "https://getlate.dev/api/v1"
KEY = os.environ["LATE_API_KEY"]
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

FACEBOOK = {"platform": "facebook", "accountId": "698f6ab9fd3d49fbfa3e2a9f"}
LINKEDIN = {"platform": "linkedin", "accountId": "698f6b23fd3d49fbfa3e2baf"}
GOOGLE = {"platform": "googlebusiness", "accountId": "6a1f19432b2567671aa1ea24"}
TWITTER = {"platform": "twitter", "accountId": "698f6ad0fd3d49fbfa3e2afd"}
BLUESKY = {"platform": "bluesky", "accountId": "6a62203c542d8bc5a6c8168d"}

MORNING_LONG = """New Hampshire has 2,992 homes on the market right now. That is the most in about seven years, and it is up 16% from a year ago.

At the same time, 58% of homes in Hillsborough County are still selling above asking, supply sits at 1.71 months, and the average home goes under agreement in 24 days.

Both of those things are true at once. Buyers genuinely have more to choose from than at any point since roughly 2019, and they still need to be ready when the right one comes up.

Most accounts pick one half of that story. We would rather give you both halves and let you decide what it means for your move.

Sources: New Hampshire Association of Realtors and Redfin, July 2026 data."""

MORNING_SHORT = """New Hampshire has 2,992 homes for sale, the most in about 7 years and up 16% year over year.

58% still sell above asking. Supply is 1.71 months.

Both are true at once. More choice, still competitive.

NHAR and Redfin, July 2026."""

EVENING_LONG = """Homes in Mont Vernon take about 47 days to sell. Across Hillsborough County the average is 24.

That is not a weak market. It is a small one. Fewer homes come up for sale here, so the right buyer takes longer to arrive, and when they do arrive they are usually someone who specifically wanted this town rather than someone comparing forty listings at once.

If you are selling in Mont Vernon, patience is the strategy, not price cuts. If you are buying, the pace you feel in Nashua is not the pace you will feel here.

Chris lives in Mont Vernon. If you want a straight answer about the town, ask him.

Sources: Homes.com and Redfin, July 2026 data."""

EVENING_SHORT = """Homes in Mont Vernon take about 47 days to sell. The Hillsborough County average is 24.

That is not a weak market, it is a small one.

For sellers, patience beats price cuts. For buyers, the pace you feel in Nashua is not the pace here."""

EVENING_ET = "2026-08-31T19:30:00"


def post(platforms, content, scheduled=None, label=""):
    payload = {"platforms": platforms, "content": content}
    if scheduled:
        payload["scheduledFor"] = scheduled
        payload["timezone"] = "America/New_York"
    else:
        payload["publishNow"] = True
    response = requests.post(f"{API}/posts", headers=HEADERS, json=payload, timeout=60)
    if response.status_code >= 300:
        print(f"  [FAIL] {label}: {response.status_code} {response.text[:300]}")
        return None
    post_id = response.json().get("post", {}).get("_id")
    print(f"  [OK] {label}: {post_id}")
    return post_id


def verify_lengths():
    assert len(MORNING_SHORT) <= 275, f"morning twitter {len(MORNING_SHORT)}"
    assert len(EVENING_SHORT) <= 275, f"evening twitter {len(EVENING_SHORT)}"
    print(f"twitter lengths: morning {len(MORNING_SHORT)}, evening {len(EVENING_SHORT)}")


if __name__ == "__main__":
    verify_lengths()
    if "--dry-run" in sys.argv:
        sys.exit(0)

    print("Morning (Angle 1, inventory) — publish now")
    post([FACEBOOK, LINKEDIN, GOOGLE], MORNING_LONG, label="fb/li/gmb")
    post([TWITTER], MORNING_SHORT, label="twitter")
    post([BLUESKY], MORNING_SHORT, label="bluesky")

    print(f"Evening (Angle 2, Mont Vernon) — scheduled {EVENING_ET} ET")
    post([FACEBOOK, LINKEDIN, GOOGLE], EVENING_LONG, EVENING_ET, label="fb/li/gmb")
    post([TWITTER], EVENING_SHORT, EVENING_ET, label="twitter")
    post([BLUESKY], EVENING_SHORT, EVENING_ET, label="bluesky")
