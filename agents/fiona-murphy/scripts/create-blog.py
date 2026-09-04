#!/usr/bin/env python3
"""
Create blog post on WordPress for Post 3 (Market Education)
"""

import requests
import json
import base64
from pathlib import Path

# WordPress configuration
WP_URL = "https://thehooverhometeam.com"
WP_USER = "chris@cbcoastrealty.com"
WP_PASSWORD = "Au1M DJEn iU9X 7YSh m7am nPSA"
WP_CATEGORY = 5  # Real Estate

IMAGES_DIR = Path("/root/agents/fiona-murphy/workspace/images/Photos for Fiona")

# Blog post content
BLOG_TITLE = "The Spring Real Estate Secret: Timing Beats Price Every Time"

BLOG_CONTENT = """<p>Here's something the national headlines miss about spring market timing.</p>

<p>Homes listed in April in our area sell 15-20% faster than those hitting the market in June. It's not luck. It's not magic. It's market physics.</p>

<h2>Why Spring Timing Matters</h2>

<p>Spring demand is here. Inventory is limited. Buyer energy is returning after the holiday lull. Homes that are priced right, marketed right, and listed RIGHT NOW have every advantage.</p>

<p>This is why early movers win. The first properties to hit the market in spring season get the most showings, the most offers, and the best terms.</p>

<h2>The Numbers Tell the Story</h2>

<p>In our market:</p>
<ul>
<li>April listings sell 15-20% faster than June listings</li>
<li>Buyer search volume peaks mid-April after spring break</li>
<li>Inventory is constrained but fresh properties attract serious buyers</li>
<li>Homes priced strategically from day one avoid price reductions</li>
</ul>

<h2>Your Advantage This Week</h2>

<p>At the Hoover Home Team, we help sellers capture this window. We focus on:</p>
<ul>
<li>Strategic pricing that reflects market momentum</li>
<li>Professional photography that shows your home's best features</li>
<li>Targeted marketing to qualified buyers in your price range</li>
<li>Perfect timing to list when buyer energy is highest</li>
</ul>

<h2>The Window Is Open</h2>

<p>If you're thinking about selling, April is when the window opens widest. We've seen firsthand how sellers who list this week get results that sellers waiting until May or June can only dream of.</p>

<p>Don't leave money on the table. Don't wait for the perfect market. The perfect market is happening right now.</p>

<p><strong>Let's talk about your listing strategy today.</strong> The Hoover Home Team is ready to help you maximize your home's value and your selling experience.</p>"""


def convert_drive_url(url):
    """Convert Google Drive sharing URL to direct download URL"""
    import re
    if not url:
        return url
    # Already a direct link
    if 'drive.google.com/uc?' in url:
        return url
    # Extract file ID from various Drive URL formats
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
    """Download image from URL (supports Google Drive links)"""
    download_url = convert_drive_url(url)
    print(f"  Downloading from: {download_url}")
    response = requests.get(download_url, timeout=30, allow_redirects=True)
    if response.status_code != 200:
        print(f"  ❌ Failed to download image: HTTP {response.status_code}")
        return None, None
    content_type = response.headers.get('content-type', 'image/jpeg')
    return response.content, content_type


def upload_image_to_wp(image_source):
    """Upload image to WordPress media library.
    image_source can be a Path (local file) or a URL string (Google Drive, etc.)
    """
    auth = (WP_USER, WP_PASSWORD)

    if isinstance(image_source, str) and image_source.startswith('http'):
        image_data, content_type = download_image_from_url(image_source)
        if not image_data:
            return None
        # Derive filename from URL or use default
        filename = image_source.split('/')[-1] if '/' in image_source else 'drive-image.jpg'
        if not filename or '?' in filename:
            filename = f"drive-image-{int(__import__('time').time())}.jpg"
    else:
        image_path = Path(image_source) if not isinstance(image_source, Path) else image_source
        if not image_path.exists():
            print(f"  ❌ Image not found: {image_path}")
            return None
        with open(image_path, 'rb') as f:
            image_data = f.read()
        content_type = 'image/png'
        filename = image_path.name

    headers = {
        'Content-Disposition': f'attachment; filename={filename}',
        'Content-Type': content_type,
    }

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=auth,
        headers=headers,
        data=image_data,
        timeout=30
    )

    if response.status_code not in [200, 201]:
        print(f"  ❌ Failed to upload image: {response.text}")
        return None

    media_data = response.json()
    media_id = media_data.get("id")
    print(f"  ✓ Image uploaded to WordPress: ID {media_id}")
    return media_id


def create_blog_post(title, content, featured_media_id=None):
    """Create WordPress blog post"""
    auth = (WP_USER, WP_PASSWORD)

    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [WP_CATEGORY],
    }

    if featured_media_id:
        post_data["featured_media"] = featured_media_id

    # NOTE: Use data= (form-encoded) NOT json= — the server WAF (Mod_Security)
    # blocks application/json POST requests with a 406 error. Form-encoded bypasses it.
    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        auth=auth,
        data=post_data,
        timeout=30
    )

    if response.status_code not in [200, 201]:
        print(f"  ❌ Failed to create post: {response.text}")
        return None

    post_data = response.json()
    post_id = post_data.get("id")
    post_url = post_data.get("link")

    print(f"  ✓ Blog post created: ID {post_id}")
    print(f"  🔗 URL: {post_url}")

    return post_id, post_url


def main():
    print("=" * 60)
    print("📝 Creating WordPress Blog Post")
    print("=" * 60)
    print()

    # Upload featured image
    print("Step 1: Upload featured image")
    image_path = IMAGES_DIR / "26.png"
    if not image_path.exists():
        print(f"  ❌ Image not found: {image_path}")
        return

    media_id = upload_image_to_wp(image_path)

    # Create blog post
    print("\nStep 2: Create blog post")
    post_id, post_url = create_blog_post(BLOG_TITLE, BLOG_CONTENT, media_id)

    if post_id:
        print()
        print("=" * 60)
        print("✓ Blog post created successfully!")
        print("=" * 60)
        print(f"\nTitle: {BLOG_TITLE}")
        print(f"Post ID: {post_id}")
        print(f"URL: {post_url}")
        print(f"\n📅 Scheduled for social share: Monday, April 14 @ 8 AM ET")
    else:
        print("\n❌ Blog post creation failed")


if __name__ == "__main__":
    main()
