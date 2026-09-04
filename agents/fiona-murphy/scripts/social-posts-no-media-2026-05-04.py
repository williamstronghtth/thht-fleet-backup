#!/usr/bin/env python3
"""
Create social media posts without media for May 4, 2026
Will schedule for publishing; images can be added via dashboard
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

# Timezone
ET = pytz.timezone('America/New_York')

def post_to_late_api(platforms, content, scheduled_for):
    """Create and schedule a post via Late API (no media)"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "platforms": platforms,
        "content": content,
        "mediaItems": [],
        "scheduledFor": scheduled_for,
        "timezone": "America/New_York"
    }

    response = requests.post(f"{BASE_URL}/posts", json=payload, headers=headers)

    if response.status_code == 201:
        data = response.json()
        post_id = data.get("post", {}).get("_id")
        return post_id
    elif response.status_code == 202:
        data = response.json()
        post_id = data.get("post", {}).get("_id")
        print(f"  (Saved as draft)")
        return post_id
    else:
        print(f"  Error {response.status_code}: {response.text}")
        return None

# Schedule times
now = datetime.now(ET)
morning_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
if now.hour >= 8:
    morning_time = morning_time  # Already scheduled for today if before 8 AM

evening_time = now.replace(hour=19, minute=30, second=0, microsecond=0)

morning_iso = morning_time.isoformat()
evening_iso = evening_time.isoformat()

print(f"Scheduling for: {morning_iso} and {evening_iso}\n")

# MORNING POST: Market Cooling ≠ Buyers Market Yet
morning_content = """The Southern NH market is cooling, but it's not a buyer's market yet.

What's happening: 36.6% of homes sold above asking price in March (down from 43.1% last year). Homes in Mont Vernon are taking 35 days to sell, up 50% year over year. This looks like softening, but here's the reality:

Inventory is still 50% below pre-COVID levels. There simply aren't enough homes for sale. That structural shortage is keeping prices elevated and keeping sellers in a strong negotiating position.

The cooldown is actually a window of opportunity for strategic sellers. Less competition, more time to showcase, and buyers who are serious rather than desperate.

Is your Southern NH home ready to take advantage of this buyer moment? Let's talk positioning.

#MontVernon #NH #RealEstate #MarketUpdate #SouthernNH"""

morning_platforms = [
    {"platform": "instagram", "accountId": INSTAGRAM_ID},
    {"platform": "facebook", "accountId": FACEBOOK_ID},
    {"platform": "linkedin", "accountId": LINKEDIN_ID}
]

print("Creating MORNING post (8 AM ET)...")
morning_post_id = post_to_late_api(
    morning_platforms,
    morning_content,
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

print("Creating EVENING post (7:30 PM ET)...")
evening_post_id = post_to_late_api(
    evening_platforms,
    evening_content,
    evening_iso
)
if evening_post_id:
    print(f"✓ Evening post created: {evening_post_id}\n")
else:
    print("✗ Evening post failed\n")

print("="*70)
print("SOCIAL MEDIA POSTS CREATED (NO MEDIA)")
print("="*70)
if morning_post_id:
    print(f"Morning post (FB/IG/LI):  {morning_post_id}")
    print(f"  Add images via: https://getlate.dev/dashboard")
if evening_post_id:
    print(f"Evening post (FB/IG/LI):  {evening_post_id}")
    print(f"  Add images via: https://getlate.dev/dashboard")
print("="*70)
print(f"\nNote: Twitter account is INACTIVE and needs reactivation by Chris")
