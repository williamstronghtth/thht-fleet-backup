#!/usr/bin/env python3
"""
Schedule social media posts for week of Aug 25-29, 2026.
Handles image uploads, presigning, and Late API posting.
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Load secrets from environment — NEVER hardcode API keys
LATE_API_KEY = os.getenv("LATE_API_KEY")
if not LATE_API_KEY:
    print("ERROR: LATE_API_KEY not set in environment. Set it before running this script.")
    sys.exit(1)

LATE_BASE = "https://getlate.dev/api/v1"

# Account IDs
ACCOUNTS = {
    "facebook": "698f6ab9fd3d49fbfa3e2a9f",
    "instagram": "698f6a5ffd3d49fbfa3e29f7",
    "linkedin": "698f6b23fd3d49fbfa3e2baf",
    "twitter": "698f6ad0fd3d49fbfa3e2afd",
    "googlebusiness": "6a1f19432b2567671aa1ea24",
}

def headers():
    return {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

def upload_image_from_local(image_filename: str) -> str:
    """
    Upload a local image file to Late API and return the publicUrl.
    """
    local_path = f"/root/agents/fiona-murphy/workspace/inbox/{image_filename}"

    if not Path(local_path).exists():
        raise FileNotFoundError(f"Image not found: {local_path}")

    # Step 1: Get presign URL
    presign_data = {
        "filename": image_filename,
        "contentType": "image/jpeg"
    }
    presign_resp = requests.post(
        f"{LATE_BASE}/media/presign",
        json=presign_data,
        headers=headers()
    )
    presign_resp.raise_for_status()
    presign_result = presign_resp.json()
    upload_url = presign_result["uploadUrl"]
    public_url = presign_result["publicUrl"]

    # Step 2: Upload binary data to presigned URL
    with open(local_path, "rb") as f:
        image_data = f.read()

    upload_resp = requests.put(upload_url, data=image_data)
    upload_resp.raise_for_status()

    print(f"✅ Uploaded {image_filename} → {public_url}")
    return public_url

def create_post(platforms: list, content: str, media_url: str = None, scheduled_for: str = None):
    """
    Create a Late API post.
    """
    post_data = {
        "platforms": platforms,
        "content": content,
        "publishNow": False if scheduled_for else True
    }

    if media_url:
        post_data["mediaItems"] = [{"type": "image", "url": media_url}]

    if scheduled_for:
        post_data["scheduledFor"] = scheduled_for
        post_data["timezone"] = "America/New_York"

    resp = requests.post(
        f"{LATE_BASE}/posts",
        json=post_data,
        headers=headers()
    )
    resp.raise_for_status()
    result = resp.json()
    post_id = result.get("post", {}).get("_id", "unknown")
    print(f"✅ Created post {post_id}")
    return result

def schedule_posts():
    """
    Schedule all posts for the week.
    """
    print("🚀 Starting post scheduling...\n")

    # Mon Aug 25, 8 AM - with file_193
    print("📅 MONDAY AUG 25, 8 AM\n")
    try:
        media_url = upload_image_from_local("file_193.jpg")
    except Exception as e:
        print(f"⚠️ Image upload failed: {e}. Proceeding text-only.")
        media_url = None

    mon_8am_copy = """August is the busiest relocation month in the Northeast. Families are moving for back-to-school, job transfers, and new beginnings. And here's the good news: mortgage rates are holding steady around 6.65 to 6.77 percent.

This isn't the 7-plus percent many feared. This is your rate-lock window before forecasts predict rates climbing to 6.8 percent or higher by year-end.

If you're relocating to Southern New Hampshire, now is the time. The market is shifting: inventory is climbing, and buyers finally have negotiating room. Homes in Hillsborough County are still moving fast at an average of 7 days on market, but you're no longer competing in a frenzy.

Stable rates. Growing inventory. Less competition. This is your window."""

    # Batch post (FB/IG/LI/GMB)
    batch_platforms = [
        {"platform": "facebook", "accountId": ACCOUNTS["facebook"]},
        {"platform": "instagram", "accountId": ACCOUNTS["instagram"]},
        {"platform": "linkedin", "accountId": ACCOUNTS["linkedin"]},
        {"platform": "googlebusiness", "accountId": ACCOUNTS["googlebusiness"]},
    ]
    create_post(
        batch_platforms,
        mon_8am_copy,
        media_url=media_url,
        scheduled_for="2026-08-25T08:00:00"
    )

    # Twitter post (separate, shorter)
    twitter_copy = "August is peak relocation season, and mortgage rates are holding steady at 6.65–6.77%. Before forecasters predict 6.8%+, now is your rate-lock window. Southern NH inventory is climbing, homes still move in 7 days, and you have negotiating room. Time to move."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_copy,
        media_url=media_url,
        scheduled_for="2026-08-25T08:00:00"
    )
    print()

    # Mon Aug 25, 7:30 PM - with file_165
    print("📅 MONDAY AUG 25, 7:30 PM\n")
    try:
        media_url_165 = upload_image_from_local("file_165.jpg")
    except Exception as e:
        print(f"⚠️ Image upload failed: {e}. Proceeding text-only.")
        media_url_165 = None

    mon_730pm_copy = """Something shifted in Hillsborough County this summer. After two years of razor-thin inventory and multiple-offer bidding wars, supply finally started climbing.

New listings jumped 11 percent in the past month. Homes are sitting a few days longer. Sellers are negotiating. Buyers are breathing easier.

If you've been waiting on the sidelines for a buyer-friendlier market, this is your signal. The transition is real, and it's happening now."""

    create_post(
        batch_platforms,
        mon_730pm_copy,
        media_url=media_url_165,
        scheduled_for="2026-08-25T19:30:00"
    )

    twitter_mon_730 = "Inventory in Hillsborough County jumped 11%. Homes are sitting longer, prices are negotiating, and buyers finally have leverage. The seller's market is shifting. Your opportunity window is now."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_mon_730,
        media_url=media_url_165,
        scheduled_for="2026-08-25T19:30:00"
    )
    print()

    # Wed Aug 27, 8 AM - with file_192 (Iris's Nashua angle)
    print("📅 WEDNESDAY AUG 27, 8 AM\n")
    try:
        media_url_192 = upload_image_from_local("file_192.jpg")
    except Exception as e:
        print(f"⚠️ Image upload failed: {e}. Proceeding text-only.")
        media_url_192 = None

    wed_8am_copy = """Nashua just got ranked the hottest housing market in America. If you're buying, that's the bad news.

Here's the full picture: homes in Nashua under $500,000 are still seeing multiple offers. But in the $500,000 to $900,000 range where most families land, the market is opening up. Amherst, Hollis, and Bow all have negotiating room in this band.

Inventory is at 1.4 months across the region. That's still favorable for sellers, but it's real movement. Translation: if you're buying in that sweet spot, you have options."""

    create_post(
        batch_platforms,
        wed_8am_copy,
        media_url=media_url_192,
        scheduled_for="2026-08-27T08:00:00"
    )

    twitter_wed_8am = "Nashua's market is hot, but there's a catch. Under $500K is still multiple-offer territory. Over $500K to $900K in Amherst and Hollis? Negotiating room is real. Inventory at 1.4 months. Context matters."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_wed_8am,
        media_url=media_url_192,
        scheduled_for="2026-08-27T08:00:00"
    )
    print()

    # Wed Aug 27, 7:30 PM - TEXT ONLY (no image)
    print("📅 WEDNESDAY AUG 27, 7:30 PM (TEXT ONLY)\n")

    wed_730pm_copy = """Let's talk timing. The fall real estate market runs October 1 to December 31. That's 12 weeks. If you want to list before the seasonal slowdown, the window closes fast.

August and September are your launch window. List now, and your home gets the benefit of late-summer showings plus the fall market push. Wait until October, and you're fighting the Thanksgiving holiday and the winter weather mentality.

If you're thinking about selling in 2026, now is not too early to start conversations."""

    # Text-only platforms (Instagram requires media, so exclude it)
    text_only_platforms = [
        {"platform": "facebook", "accountId": ACCOUNTS["facebook"]},
        {"platform": "linkedin", "accountId": ACCOUNTS["linkedin"]},
        {"platform": "googlebusiness", "accountId": ACCOUNTS["googlebusiness"]},
    ]
    create_post(
        text_only_platforms,
        wed_730pm_copy,
        scheduled_for="2026-08-27T19:30:00"
    )

    twitter_wed_730 = "Fall market window closes Oct 1. If you're selling, August and September are your launch window. List now and catch late-summer showings plus fall momentum. Wait until October and you're fighting seasonal headwinds. Now's the time to call."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_wed_730,
        scheduled_for="2026-08-27T19:30:00"
    )
    print()

    # Fri Aug 29, 8 AM - with file_195
    print("📅 FRIDAY AUG 29, 8 AM\n")
    try:
        media_url_195 = upload_image_from_local("file_195.jpg")
    except Exception as e:
        print(f"⚠️ Image upload failed: {e}. Proceeding text-only.")
        media_url_195 = None

    fri_8am_copy = """Here's what 7-day average sales time means: if you list a home, it sells before the weekend is over.

That's the velocity Hillsborough County is experiencing right now. Homes are showing strong. Days-on-market metrics are holding at historic lows. Buyer intent is high.

Q4 is slower. Thanksgiving, Christmas, fewer showings. Fewer competing homes too, which sounds good, but the buyer pool shrinks faster than the seller pool.

August and September are your peak-exposure window. The homes on market now are getting seen, shown, and sold quickly. That's not something to take for granted."""

    create_post(
        batch_platforms,
        fri_8am_copy,
        media_url=media_url_195,
        scheduled_for="2026-08-29T08:00:00"
    )

    twitter_fri_8am = "7-day average sales time in Hillsborough County. Q4 is slower. If you're selling, August and September are peak-exposure months. List now and get the benefit of strong velocity and high buyer intent before the seasonal slowdown hits."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_fri_8am,
        media_url=media_url_195,
        scheduled_for="2026-08-29T08:00:00"
    )
    print()

    # Fri Aug 29, 7:30 PM - with file_196
    print("📅 FRIDAY AUG 29, 7:30 PM\n")
    try:
        media_url_196 = upload_image_from_local("file_196.jpg")
    except Exception as e:
        print(f"⚠️ Image upload failed: {e}. Proceeding text-only.")
        media_url_196 = None

    fri_730pm_copy = """What does your money buy in Boston suburbs versus Southern New Hampshire?

In Boston metro areas like Newton, Wellesley, and Brookline, 1.2 to 1.5 million dollars is the entry point for a four-bedroom on a typical lot. In Southern New Hampshire, that same budget gets you a newer, larger home with more land and often a stronger yard.

Commute time? 45 to 60 minutes to Boston suburbs, depending on where you're coming from. Quality of life, school systems, and property taxes? Comparable or better.

This is why August is bringing Boston-area professionals to Mont Vernon, Amherst, and Hollis. They're not giving up convenience. They're gaining value."""

    create_post(
        batch_platforms,
        fri_730pm_copy,
        media_url=media_url_196,
        scheduled_for="2026-08-29T19:30:00"
    )

    twitter_fri_730 = "Boston suburbs: $1.2–$1.5M for four beds. Southern NH? Same budget, newer home, more land, comparable commute, lower taxes. That's why August is seeing Boston-area relocations to Mont Vernon and Amherst. It's not just lifestyle. It's math."
    create_post(
        [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        twitter_fri_730,
        media_url=media_url_196,
        scheduled_for="2026-08-29T19:30:00"
    )
    print()

    print("✅ All posts scheduled successfully!")

if __name__ == "__main__":
    schedule_posts()
