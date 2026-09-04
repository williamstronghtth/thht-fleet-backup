#!/usr/bin/env python3
"""
Create and schedule social media posts via Late API
"""

import requests
import json
import base64
import os
from pathlib import Path
from datetime import datetime

# Configuration
API_BASE = "https://getlate.dev/api/v1"
API_KEY = os.environ["LATE_API_KEY"]
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Account IDs
INSTAGRAM = "698f6a5ffd3d49fbfa3e29f7"
FACEBOOK = "698f6ab9fd3d49fbfa3e2a9f"
LINKEDIN = "698f6b23fd3d49fbfa3e2baf"
TWITTER = "698f6ad0fd3d49fbfa3e2afd"

IMAGES_DIR = Path("/root/agents/fiona-murphy/workspace/images/Photos for Fiona")


def convert_drive_url(url):
    """Convert Google Drive sharing URL to direct download URL"""
    import re
    if not url:
        return url
    if 'drive.google.com/uc?' in url:
        return url
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'docs\.google\.com/.*/d/([a-zA-Z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    return url


def download_image_from_url(url):
    """Download image bytes from a URL (supports Google Drive links)"""
    download_url = convert_drive_url(url)
    print(f"  Downloading from: {download_url}")
    response = requests.get(download_url, timeout=30, allow_redirects=True)
    if response.status_code != 200:
        print(f"  ❌ Failed to download image: HTTP {response.status_code}")
        return None
    return response.content


# Post definitions
POSTS = [
    {
        "name": "Post 1: Seller Urgency",
        "image": "24.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """If you're selling in April, you're selling into peak season.

Mid-April is when serious buyers re-enter the market after spring break. Homes listed RIGHT NOW get the most eyeballs. Inventory is limited. Buyer competition is intense.

Get ahead of the competition. List this week, not next month.

Let's list your home strategically. DM to schedule your consultation.

#VolusiaCourtyMarket #DaytonaRealEstate #SpringHomeSeason #PortOrangeHomes""",
        "scheduled_for": "2026-04-11T15:00:00-04:00",  # Friday 3 PM ET
    },
    {
        "name": "Post 1: Twitter",
        "image": None,
        "platforms": [
            {"platform": "twitter", "accountId": TWITTER},
        ],
        "content": """Selling in April? You're timing the peak season right. Serious buyers are back, inventory is down, and homes are moving fast. List now, not later. DM us for a strategic listing plan. 🏡""",
        "scheduled_for": "2026-04-11T15:00:00-04:00",
    },
    {
        "name": "Post 2: Buyer Empowerment",
        "image": "25.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """Rates are down. Inventory is up. You have leverage.

Here's what you should do RIGHT NOW if you're buying:

1. Get pre-approved (rates locked in today)
2. Schedule 3-5 home tours (see what's really selling)
3. Make an offer on something good (homes are sitting longer)
4. Negotiate hard (seller concessions are back on the table)

The window is open. Let's find you the right home.

Ready to buy? Let's talk. DM us today.

#BuyersFocus #VolusiaCourty #HomeBuyingTips #SpringMarket""",
        "scheduled_for": "2026-04-12T08:00:00-04:00",  # Saturday 8 AM ET
    },
    {
        "name": "Post 2: Twitter",
        "image": None,
        "platforms": [
            {"platform": "twitter", "accountId": TWITTER},
        ],
        "content": """Rates down. Inventory up. Buyer power returns. Get pre-approved, tour homes, make an offer, negotiate hard. Seller concessions are back. This is YOUR moment. Let's find you the right home. DM us. 🔑""",
        "scheduled_for": "2026-04-12T08:00:00-04:00",
    },
    {
        "name": "Post 3: Market Education",
        "image": "26.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """The spring real estate secret? Timing beats price every time.

Homes listed in April sell 15-20% faster than June listings in our market. It's not luck. It's market momentum.

Buyer energy is back. Inventory is down. Spring demand is here.

Price right, market hard, and list this week. The window is wide open.

Talk to Chris about your listing timing and strategy.

#SpringRealEstateTips #VolusiaCourtyMarket #ListingStrategy #DaytonaRealEstate""",
        "scheduled_for": "2026-04-14T08:00:00-04:00",  # Monday 8 AM ET
    },
    {
        "name": "Post 3: Twitter",
        "image": None,
        "platforms": [
            {"platform": "twitter", "accountId": TWITTER},
        ],
        "content": """Timing beats price. Homes listed in April sell 15-20% faster than June in our area. Spring demand is here, inventory is tight, and buyer energy returns. Price right and list now. DM for strategy. 📊""",
        "scheduled_for": "2026-04-14T08:00:00-04:00",
    },
    {
        "name": "Post 4: Retiree/Relocation",
        "image": "24.png",  # Reuse 24 for variety
        "platforms": [
            {"platform": "linkedin", "accountId": LINKEDIN},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "instagram", "accountId": INSTAGRAM},
        ],
        "content": """Why April is prime moving season for retirees heading to Florida.

Schools are in. Weather is perfect (not too hot yet). And if you're serious about relocating, April is when the market is most active.

Here's what makes our area special: Daytona Beach, Port Orange, New Smyrna Beach are retiree-friendly with prices 30-40% lower than Miami or Tampa. You get beach lifestyle, golf communities, and a tight-knit community without the cost.

For those relocating from up north, this is your window. April weather draws buyers. April inventory is fresh. April is when relocations happen.

We help out-of-state families find their Florida home. From first visit to keys in hand.

Moving to Volusia? Let's find your retirement home.

#RelocationFlorida #RetirementLiving #VolusiaCounty #FloridaLiving""",
        "scheduled_for": "2026-04-15T08:00:00-04:00",  # Tuesday 8 AM ET
    },
    {
        "name": "Post 4: Twitter",
        "image": None,
        "platforms": [
            {"platform": "twitter", "accountId": TWITTER},
        ],
        "content": """April is prime relocation season. Schools in, weather perfect, inventory fresh. Daytona, Port Orange, NSB offer retiree-friendly living at 30-40% less than Miami-Tampa. This is your window. Moving to Volusia? Let's talk. 🌊""",
        "scheduled_for": "2026-04-15T08:00:00-04:00",
    },
]


def upload_image(image_path):
    """Upload image to Late API and return the public URL"""
    filename = image_path.name

    # Step 1: Get presign URL
    presign_data = {
        "filename": filename,
        "contentType": "image/png"
    }

    presign_response = requests.post(
        f"{API_BASE}/media/presign",
        json=presign_data,
        headers=HEADERS
    )

    if presign_response.status_code != 200:
        print(f"  ❌ Failed to get presign URL: {presign_response.text}")
        return None

    presign_data = presign_response.json()
    upload_url = presign_data.get("uploadUrl")
    public_url = presign_data.get("publicUrl")

    # Step 2: Upload image
    with open(image_path, 'rb') as f:
        image_data = f.read()

    upload_response = requests.put(
        upload_url,
        data=image_data,
        headers={"Content-Type": "image/png"}
    )

    if upload_response.status_code not in [200, 204]:
        print(f"  ❌ Failed to upload image: {upload_response.text}")
        return None

    print(f"  ✓ Image uploaded: {public_url}")
    return public_url


def upload_image_from_url(url):
    """Download image from URL and upload to Late via presign workflow"""
    image_data = download_image_from_url(url)
    if not image_data:
        return None

    # Determine content type
    content_type = "image/jpeg"
    if url.lower().endswith('.png'):
        content_type = "image/png"
    elif url.lower().endswith('.webp'):
        content_type = "image/webp"

    filename = f"drive-image-{int(datetime.now().timestamp())}.jpg"

    # Get presign URL
    presign_response = requests.post(
        f"{API_BASE}/media/presign",
        json={"filename": filename, "contentType": content_type},
        headers=HEADERS
    )

    if presign_response.status_code != 200:
        print(f"  ❌ Failed to get presign URL: {presign_response.text}")
        return None

    presign_data = presign_response.json()
    upload_url = presign_data.get("uploadUrl")
    public_url = presign_data.get("publicUrl")

    # Upload image binary
    upload_response = requests.put(
        upload_url,
        data=image_data,
        headers={"Content-Type": content_type}
    )

    if upload_response.status_code not in [200, 204]:
        print(f"  ❌ Failed to upload image: {upload_response.text}")
        return None

    print(f"  ✓ Image uploaded from URL: {public_url}")
    return public_url


def create_post(post_data):
    """Create a post via Late API"""
    post_name = post_data["name"]
    image_file = post_data["image"]
    platforms = post_data["platforms"]
    content = post_data["content"]
    scheduled_for = post_data.get("scheduled_for")

    print(f"\n📱 {post_name}")
    print(f"  Platforms: {', '.join([p['platform'] for p in platforms])}")

    # Handle image upload if needed
    media_items = []
    if image_file:
        # Support both local files and URLs (Google Drive, etc.)
        if image_file.startswith('http'):
            public_url = upload_image_from_url(image_file)
            if public_url:
                media_items.append({"type": "image", "url": public_url})
        else:
            image_path = IMAGES_DIR / image_file
            if not image_path.exists():
                print(f"  ❌ Image not found: {image_path}")
                return False

            public_url = upload_image(image_path)
            if public_url:
                media_items.append({"type": "image", "url": public_url})

    # Create post payload
    post_payload = {
        "platforms": platforms,
        "content": content,
        "mediaItems": media_items,
        "publishNow": False,  # Create as draft
        "scheduledFor": scheduled_for,  # Include scheduled time
        "timezone": "America/New_York",
    }

    # Try to create the post
    response = requests.post(
        f"{API_BASE}/posts",
        json=post_payload,
        headers=HEADERS
    )

    if response.status_code not in [200, 201]:
        print(f"  ❌ Failed to create post: {response.text}")
        return False

    response_data = response.json()
    post_obj = response_data.get("post", {})
    post_id = post_obj.get("_id")
    print(f"  ✓ Post created: {post_id}")
    print(f"  📅 Scheduled for: {scheduled_for}")

    return True


def main():
    print("=" * 60)
    print("🚀 Creating Social Media Posts via Late API")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Images directory: {IMAGES_DIR}")
    print()

    success_count = 0
    for post in POSTS:
        if create_post(post):
            success_count += 1

    print()
    print("=" * 60)
    print(f"✓ Complete: {success_count}/{len(POSTS)} posts created")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Posts created as drafts (publishNow: false)")
    print("  2. Log into Late dashboard to schedule posting times")
    print("  3. Or configure CronCreate to publish at scheduled times")
    print()


if __name__ == "__main__":
    main()
