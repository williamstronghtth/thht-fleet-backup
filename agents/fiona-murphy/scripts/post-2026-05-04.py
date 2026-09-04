#!/usr/bin/env python3
"""
Create and schedule social media posts for May 4, 2026 — Market Cooling theme
Posts go to: Instagram, Facebook, LinkedIn
Twitter: Separate request with shortened content
"""

import requests
import json
import os
from datetime import datetime, timedelta
import pytz

# Late API credentials
API_KEY = os.environ["LATE_API_KEY"]
BASE_URL = "https://getlate.dev/api/v1"

# Platform account IDs
INSTAGRAM_ID = "698f6a5ffd3d49fbfa3e29f7"
FACEBOOK_ID = "698f6ab9fd3d49fbfa3e2a9f"
LINKEDIN_ID = "698f6b23fd3d49fbfa3e2baf"
TWITTER_ID = "698f6ad0fd3d49fbfa3e2afd"

# Timezone
ET = pytz.timezone('America/New_York')

def post_to_late_api(platforms, content, media_items, scheduled_for):
    """Create and schedule a post via Late API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "platforms": platforms,
        "content": content,
        "mediaItems": media_items,
        "scheduledFor": scheduled_for,
        "timezone": "America/New_York"
    }

    response = requests.post(f"{BASE_URL}/posts", json=payload, headers=headers)

    if response.status_code != 201:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    post_id = data.get("post", {}).get("_id")
    print(f"✓ Post created: {post_id}")
    return post_id

def presign_media(filename, content_type="image/jpeg"):
    """Get presigned URL for image upload"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "filename": filename,
        "contentType": content_type
    }

    response = requests.post(f"{BASE_URL}/media/presign", json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Presign error: {response.status_code} - {response.text}")
        return None

    return response.json().get("uploadUrl")

# Image files (from Google Drive, already downloaded to local folder)
morning_image = "45.png"
evening_image = "48.png"

# Schedule times
now = datetime.now(ET)
morning_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
if now.hour >= 8:
    morning_time += timedelta(days=1)

evening_time = now.replace(hour=19, minute=30, second=0, microsecond=0)
if now.hour >= 19 or (now.hour == 19 and now.minute >= 30):
    evening_time += timedelta(days=1)

morning_iso = morning_time.isoformat()
evening_iso = evening_time.isoformat()

print(f"Scheduling for: {morning_iso} and {evening_iso}")

# MORNING POST: Market Cooling ≠ Buyers Market Yet
morning_content = """The Southern NH market is cooling, but it's not a buyer's market yet.

What's happening: 36.6% of homes sold above asking price in March (down from 43.1% last year). Homes in Mont Vernon are taking 35 days to sell, up 50% year over year. This looks like softening, but here's the reality:

Inventory is still 50% below pre-COVID levels. There simply aren't enough homes for sale. That structural shortage is keeping prices elevated and keeping sellers in a strong negotiating position.

The cooldown is actually a window of opportunity for strategic sellers. Less competition, more time to showcase, and buyers who are serious rather than desperate.

Is your Southern NH home ready to take advantage of this buyer moment? Let's talk positioning.

#MontVernon #NH #RealEstate #MarketUpdate #SouthernNH"""

# MORNING POST: Facebook/Instagram/LinkedIn
morning_platforms = [
    {"platform": "instagram", "accountId": INSTAGRAM_ID},
    {"platform": "facebook", "accountId": FACEBOOK_ID},
    {"platform": "linkedin", "accountId": LINKEDIN_ID}
]

morning_media = [
    {"type": "image", "url": f"https://drive.google.com/uc?id=LOCAL_FILE_{morning_image}"}
]

print("\nCreating MORNING post...")
morning_post = post_to_late_api(
    morning_platforms,
    morning_content,
    morning_media,
    morning_iso
)

# EVENING POST: 55+ Communities Opportunity
evening_content = """New 55+ communities are transforming Southern NH real estate.

East Village Condominiums in Milford just broke ground on an 18-unit luxury 55+ development. This is part of a larger trend: boomers are downsizing and relocating to lifestyle communities that offer walkability, community, and maintenance-free living.

For investors, these communities represent a stable, growing market segment. For homeowners looking to downsize, they're the future of retirement living in New England.

Southern NH is positioned perfectly for this trend. Lower costs than Boston, better access than rural Vermont, and a thriving community culture that makes relocation feel like coming home, not moving away.

Ready to explore what 55+ living looks like in New Hampshire? We know every new development in our market.

#55Plus #MilfordNH #Downsizing #RetirementLiving #RealEstateTrends"""

evening_platforms = [
    {"platform": "instagram", "accountId": INSTAGRAM_ID},
    {"platform": "facebook", "accountId": FACEBOOK_ID},
    {"platform": "linkedin", "accountId": LINKEDIN_ID}
]

evening_media = [
    {"type": "image", "url": f"https://drive.google.com/uc?id=LOCAL_FILE_{evening_image}"}
]

print("\nCreating EVENING post...")
evening_post = post_to_late_api(
    evening_platforms,
    evening_content,
    evening_media,
    evening_iso
)

# TWITTER: Separate standalone request with shortened content
twitter_morning_content = """Market cooling in Southern NH, but NOT a buyer's market yet. Inventory still 50% below pre-COVID. Mont Vernon homes taking 35 days to sell. Opportunity for strategic sellers. #MontVernon #NH #RealEstate"""

# Verify character count
if len(twitter_morning_content) <= 280:
    print(f"\n✓ Twitter content OK: {len(twitter_morning_content)} chars")
else:
    print(f"\n✗ Twitter content OVER LIMIT: {len(twitter_morning_content)} chars (max 280)")

twitter_platforms = [
    {"platform": "twitter", "accountId": TWITTER_ID}
]

print("\nCreating TWITTER post...")
twitter_post = post_to_late_api(
    twitter_platforms,
    twitter_morning_content,
    morning_media,
    morning_iso
)

print("\n" + "="*60)
print("POSTING COMPLETE")
print("="*60)
if morning_post:
    print(f"Morning post (FB/IG/LI): {morning_post}")
if evening_post:
    print(f"Evening post (FB/IG/LI): {evening_post}")
if twitter_post:
    print(f"Twitter post: {twitter_post}")
