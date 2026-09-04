#!/usr/bin/env python3
"""
Create and schedule social media posts via Late API
May 3, 2026 content for Southern NH market
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

IMAGES_DIR = Path("/root/agents/fiona-murphy/workspace/media/Photos for Fiona")


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


# Post definitions for May 3, 2026
POSTS = [
    {
        "name": "Post 1: Seller Advantage",
        "image": "45.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """Thinking about selling in Southern NH? The market is in YOUR favor.

With only 1.43 months of inventory, your home will have less competition. Homes in Hillsborough County are selling strong at 100.86% of asking.

Here's what that means: less time on market, more buyer interest, stronger negotiating position.

The window is open. Let's list your home strategically and capture this momentum.

#SouthernNH #HillsboroughCounty #RealEstateMarket #MontVernon #NashuaRealty #SellerAdvantage""",
        "scheduled_for": "2026-05-03T08:00:00-04:00",  # 8 AM ET
    },
    {
        "name": "Post 2: Buyer Resilience",
        "image": "48.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """Buyers: Don't let low inventory discourage you. Here's what's really happening in the Southern NH market.

Closed sales in Hillsborough County are UP 6.6% compared to last year. That means more activity, more deals, more opportunity for smart buyers.

The market is moving. And homes? 62 days to close on average, homes selling strong. This is an active market.

Smart buyers know this. They're out looking. They're making offers. They're finding homes.

Let's find YOUR home. DM to start your search.

#SouthernNH #HillsboroughCounty #HomeBuying #BuyersFocus #NHRealEstate""",
        "scheduled_for": "2026-05-03T19:30:00-04:00",  # 7:30 PM ET
    },
    {
        "name": "Post 3: Market Trend",
        "image": "47.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """New Hampshire just ranked #8 hottest real estate market in 2026. And Southern NH is leading the charge.

From Mont Vernon to Nashua, from Amherst to Milford, Salem, quality of life drives demand. Strong communities. New England character. Real estate that holds value.

Median home price in Hillsborough County is holding steady at $548,750. Buyer interest is up 6.6% year over year. Smart investors are paying attention.

Why? Because Southern NH offers what every homebuyer wants: quality, community, and strong market fundamentals.

This is why we're here. This is why we focus on YOUR success in this market.

#SouthernNH #HillsboroughCounty #RealEstateMarket #MontVernon #NashuaRealty #NHHomes""",
        "scheduled_for": "2026-05-04T08:00:00-04:00",  # May 4, 8 AM
    },
    {
        "name": "Post 4: Affordability Awareness",
        "image": "50.png",
        "platforms": [
            {"platform": "instagram", "accountId": INSTAGRAM},
            {"platform": "facebook", "accountId": FACEBOOK},
            {"platform": "linkedin", "accountId": LINKEDIN},
        ],
        "content": """Affordability challenge in the market? Yes. And it's real.

Here's what we know: median home price in Hillsborough County sits at $548,750. Prices are holding steady. Forecasts show 2 to 4% growth through 2026, moderate and measured.

But here's what matters more: smart planning plus expert guidance equals opportunity.

Whether you're first time buyers, growing families, or thinking about your next move, the market works when you work with someone who understands YOUR situation, YOUR budget, YOUR goals.

We don't push people into homes they can't afford. We find homes that fit your life and your finances. We negotiate hard. We guide smart.

Let's talk about what's realistic in YOUR market, in YOUR budget.

#SouthernNH #HillsboroughCounty #HomeBuying #RealEstate #NHLiving""",
        "scheduled_for": "2026-05-04T19:30:00-04:00",  # May 4, 7:30 PM
    },
]


def upload_image(image_path):
    """Upload image to Late API and return the public URL"""
    filename = image_path.name

    # Determine content type based on file extension
    content_type = "image/png"
    if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
        content_type = "image/jpeg"
    elif filename.lower().endswith('.webp'):
        content_type = "image/webp"

    # Step 1: Get presign URL
    presign_data = {
        "filename": filename,
        "contentType": content_type
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
        headers={"Content-Type": content_type}
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
        "scheduledFor": scheduled_for,
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
    print("  1. Posts created as drafts and scheduled")
    print("  2. Blog post to be published next")
    print()


if __name__ == "__main__":
    main()
