#!/usr/bin/env python3
"""
Create and schedule social media posts for May 4, 2026
Posts to: Facebook, Instagram, LinkedIn (batch)
Twitter: Separate with shortened content
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
    return post_id

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

print(f"Current time: {now}")
print(f"Morning post: {morning_iso}")
print(f"Evening post: {evening_iso}\n")

# MORNING POST: Market Cooling ≠ Buyers Market Yet
morning_content = """The Southern NH market is cooling, but it's not a buyer's market yet.

What's happening: 36.6% of homes sold above asking price in March (down from 43.1% last year). Homes in Mont Vernon are taking 35 days to sell, up 50% year over year. This looks like softening, but here's the reality:

Inventory is still 50% below pre-COVID levels. There simply aren't enough homes for sale. That structural shortage is keeping prices elevated and keeping sellers in a strong negotiating position.

The cooldown is actually a window of opportunity for strategic sellers. Less competition, more time to showcase, and buyers who are serious rather than desperate.

Is your Southern NH home ready to take advantage of this buyer moment? Let's talk positioning.

Read more on our blog.

#MontVernon #NH #RealEstate #MarketUpdate #SouthernNH"""

morning_platforms = [
    {"platform": "instagram", "accountId": INSTAGRAM_ID},
    {"platform": "facebook", "accountId": FACEBOOK_ID},
    {"platform": "linkedin", "accountId": LINKEDIN_ID}
]

morning_media = [
    {"type": "image", "url": "https://via.placeholder.com/1200x630?text=Market+Cooling"}
]

print("Creating MORNING post (8 AM ET)...")
morning_post_id = post_to_late_api(
    morning_platforms,
    morning_content,
    morning_media,
    morning_iso
)
if morning_post_id:
    print(f"✓ Morning post created: {morning_post_id}\n")
else:
    print("✗ Morning post failed\n")

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
    {"type": "image", "url": "https://via.placeholder.com/1200x630?text=55+Communities"}
]

print("Creating EVENING post (7:30 PM ET)...")
evening_post_id = post_to_late_api(
    evening_platforms,
    evening_content,
    evening_media,
    evening_iso
)
if evening_post_id:
    print(f"✓ Evening post created: {evening_post_id}\n")
else:
    print("✗ Evening post failed\n")

# TWITTER: Separate standalone request with shortened content
twitter_morning_content = """Market cooling in Southern NH, but NOT a buyer's market yet. Inventory still 50% below pre-COVID. Mont Vernon homes taking 35 days to sell. Opportunity for strategic sellers. #MontVernon #NH #RealEstate"""

print(f"Twitter content length: {len(twitter_morning_content)} chars (max 280)")
if len(twitter_morning_content) > 280:
    print(f"✗ Twitter content OVER LIMIT")
else:
    print(f"✓ Twitter content OK\n")

twitter_platforms = [
    {"platform": "twitter", "accountId": TWITTER_ID}
]

print("Creating TWITTER post...")
twitter_post_id = post_to_late_api(
    twitter_platforms,
    twitter_morning_content,
    morning_media,
    morning_iso
)
if twitter_post_id:
    print(f"✓ Twitter post created: {twitter_post_id}\n")
else:
    print("✗ Twitter post failed\n")

print("="*70)
print("SOCIAL MEDIA POSTS CREATED")
print("="*70)
print(f"Morning (FB/IG/LI):  {morning_post_id or 'FAILED'}")
print(f"Evening (FB/IG/LI):  {evening_post_id or 'FAILED'}")
print(f"Twitter (Morning):   {twitter_post_id or 'FAILED'}")
print("="*70)
