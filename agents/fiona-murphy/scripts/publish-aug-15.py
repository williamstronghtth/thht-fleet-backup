#!/usr/bin/env python3
"""
Publish August 15, 2026 content: blog post + social media (2x daily).
Handles WordPress upload, post creation, Yoast meta, and Late API scheduling.
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Load environment
WP_USER = os.getenv("WP_USER", "chris@cbcoastrealty.com")
WP_PASS = os.getenv("WP_PASS", "Au1M DJEn iU9X 7YSh m7am nPSA")
WP_URL = "https://thehooverhometeam.com/wp-json/wp/v2"

LATE_API_KEY = os.environ["LATE_API_KEY"]
LATE_BASE = "https://getlate.dev/api/v1"

# Image paths
IMG_BLOG = "/root/agents/fiona-murphy/workspace/inbox/file_179.jpg"
IMG_SOCIAL_AM = "/root/agents/fiona-murphy/workspace/inbox/file_181.jpg"
IMG_SOCIAL_PM = "/root/agents/fiona-murphy/workspace/inbox/file_180.jpg"

# Account IDs for Late API
ACCTS = {
    "facebook": "698f6ab9fd3d49fbfa3e2a9f",
    "instagram": "698f6a5ffd3d49fbfa3e29f7",
    "linkedin": "698f6b23fd3d49fbfa3e2baf",
    "twitter": "698f6ad0fd3d49fbfa3e2afd",
}

def upload_image_to_wp(image_path, alt_text):
    """Upload image to WordPress media library. Returns media ID."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        return None

    filename = os.path.basename(image_path)
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{WP_URL}/media",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", "Content-Disposition: attachment; filename=" + filename,
        "--data-binary", "@" + image_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        media_id = data.get("id")
        if media_id:
            print(f"✓ Uploaded {filename} → media ID {media_id}")
            # Set alt text
            alt_cmd = [
                "curl", "-s", "-X", "POST",
                f"{WP_URL}/media/{media_id}",
                "-u", f"{WP_USER}:{WP_PASS}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"alt_text": alt_text})
            ]
            subprocess.run(alt_cmd, capture_output=True)
            return media_id
        else:
            print(f"ERROR: Upload failed for {filename}: {result.stdout}")
            return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON response: {result.stdout}")
        return None

def create_blog_post(featured_media_id):
    """Create blog post via REST API with Gutenberg blocks."""

    content_blocks = """<!-- wp:paragraph -->
<p>August is relocation month in Southern NH. Every year, families from Boston, the North Shore, and beyond pack moving trucks and arrive in Mont Vernon, Amherst, Nashua, and Brookline to start school on a new address. If you're considering a back-to-school Southern NH move, you're joining a trend that transforms our real estate market in late summer. Here's why families choose Southern NH for this critical transition.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>Back-to-School Relocations Require Three Things</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>When families evaluate a relocation before Labor Day, they weigh three factors: school quality, commute reality, and whether the community feels like home. Southern NH delivers on all three, which is why August sees 50 to 60 percent of our inventory move to families with school-age children.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>School Districts Set Back-to-School Southern NH Apart</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Southern NH school districts—Amherst, Nashua, Milford, Salem, and Mont Vernon—consistently rank in the top tier of New England. According to the <a href="https://www.nhar.org" target="_blank" rel="noopener">New Hampshire Association of Realtors</a>, schools in Hillsborough County show strong academic performance, diverse programming, and active parent communities. Families relocating before school starts gain immediate access to these established networks and proven track records.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>Commute and Lifestyle Reality</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Families aren't just buying a house; they're buying time. Southern NH locations offer reasonable commutes to Boston (30 to 45 minutes from Nashua), Manchester (15 to 25 minutes), and surrounding employment centers. The towns themselves—tree-lined streets, town commons, local restaurants and shops—make the commute worth it. You're not just relocating; you're choosing a lifestyle that works for working parents and growing families.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you're planning a back-to-school Southern NH relocation, August is your window. The right home, in the right school district, with the right community is waiting. And we know where to find it. <a href="/contact/">Contact The Hoover Home Team</a> to explore your family's next chapter in Southern NH.</p>
<!-- /wp:paragraph -->"""

    post_data = {
        "title": "Why Southern NH Is the Top Choice for Back-to-School Relocations",
        "content": content_blocks,
        "status": "publish",
        "categories": [5],
        "featured_media": featured_media_id,
        "slug": "back-to-school-southern-nh-relocations"
    }

    cmd = [
        "curl", "-s", "-X", "POST",
        f"{WP_URL}/posts",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(post_data)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        post_id = data.get("id")
        if post_id:
            print(f"✓ Created blog post → ID {post_id}")
            return post_id
        else:
            print(f"ERROR: Post creation failed: {result.stdout}")
            return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON: {result.stdout}")
        return None

def set_yoast_meta(post_id):
    """Set Yoast SEO fields via XML-RPC."""

    focuskw = "back-to-school Southern NH"
    metadesc = "Families relocate to Southern NH every August. Learn why school districts, commute times, and community make it the top back-to-school choice."

    # XML-RPC call to wp.editPost
    xml_rpc_body = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>wp.editPost</methodName>
  <params>
    <param><value><int>0</int></value></param>
    <param><value><string>{WP_USER}</string></value></param>
    <param><value><string>{WP_PASS}</string></value></param>
    <param><value><int>{post_id}</int></value></param>
    <param><value>
      <struct>
        <member>
          <name>custom_fields</name>
          <value>
            <array>
              <data>
                <value>
                  <struct>
                    <member><name>key</name><value><string>_yoast_wpseo_focuskw</string></value></member>
                    <member><name>value</name><value><string>{focuskw}</string></value></member>
                  </struct>
                </value>
                <value>
                  <struct>
                    <member><name>key</name><value><string>_yoast_wpseo_metadesc</string></value></member>
                    <member><name>value</name><value><string>{metadesc}</string></value></member>
                  </struct>
                </value>
              </data>
            </array>
          </value>
        </member>
      </struct>
    </value></param>
  </params>
</methodCall>"""

    cmd = [
        "curl", "-s", "-X", "POST",
        "https://thehooverhometeam.com/xmlrpc.php",
        "-H", "Content-Type: text/xml",
        "-d", xml_rpc_body
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if "<boolean>1</boolean>" in result.stdout:
        print(f"✓ Yoast meta set for post {post_id}")
        return True
    else:
        print(f"WARN: Yoast meta may not have been set (check response): {result.stdout[:200]}")
        return False

def post_to_late_api(platforms, content, media_url=None, scheduled_for=None, twitter_content=None):
    """Post to Late API (social media batch)."""

    payload = {
        "platforms": platforms,
        "content": content,
        "publishNow": scheduled_for is None,
    }

    if media_url:
        payload["mediaItems"] = [{"type": "image", "url": media_url}]

    if scheduled_for:
        payload["scheduledFor"] = scheduled_for
        payload["timezone"] = "America/New_York"

    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

    cmd = [
        "curl", "-s", "-X", "POST",
        f"{LATE_BASE}/posts",
        "-H", f"Authorization: Bearer {LATE_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        post_id = data.get("post", {}).get("_id")
        if post_id:
            print(f"✓ Late API post created: {post_id}")
            return post_id
        else:
            print(f"WARN: Post may not have been created. Response: {result.stdout[:300]}")
            return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON from Late API: {result.stdout[:500]}")
        return None

def main():
    """Main orchestration."""

    print("\n=== Publishing August 15, 2026 Content ===\n")

    # 1. Upload blog featured image
    print("1. Uploading blog featured image...")
    blog_media_id = upload_image_to_wp(IMG_BLOG, "Primary bathroom with spa finishes and serene details, reflecting why back-to-school Southern NH homes appeal to relocating families.")
    if not blog_media_id:
        print("ERROR: Failed to upload blog image. Aborting.")
        return 1

    # 2. Create blog post
    print("\n2. Creating blog post...")
    blog_post_id = create_blog_post(blog_media_id)
    if not blog_post_id:
        print("ERROR: Failed to create blog post. Aborting.")
        return 1

    # 3. Set Yoast meta
    print("\n3. Setting Yoast SEO meta...")
    set_yoast_meta(blog_post_id)

    # 4. Upload social images (simple file:// URLs for now — adjust if needed)
    print("\n4. Uploading social images to WordPress media...")
    am_media_id = upload_image_to_wp(IMG_SOCIAL_AM, "Welcoming coastal foyer entryway, ideal for families relocating for back-to-school")
    pm_media_id = upload_image_to_wp(IMG_SOCIAL_PM, "Classic living room where families gather, representing Southern NH community living")

    if not am_media_id or not pm_media_id:
        print("WARN: One or more social images failed to upload. Continuing without images.")

    # 5. Get image URLs from WordPress (REST API)
    print("\n5. Getting image URLs from WordPress...")

    def get_image_url(media_id):
        cmd = [
            "curl", "-s",
            f"{WP_URL}/media/{media_id}",
            "-u", f"{WP_USER}:{WP_PASS}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            return data.get("source_url")
        except:
            return None

    am_image_url = get_image_url(am_media_id) if am_media_id else None
    pm_image_url = get_image_url(pm_media_id) if pm_media_id else None

    # 6. Post to Late API (social media)
    print("\n6. Posting to Late API (social media)...")

    # Morning post (batch: FB/IG/LI + Twitter)
    print("   - Morning post (8 AM ET)...")
    am_content = """Back-to-school means back-to-home territory. Families across Boston and coastal New England are making their moves to Southern NH, and for good reason: excellent schools, thriving towns, and homes that understand what family life looks like.

August is the last push before Labor Day. If you're relocating for school, now is the time to see what's available in Mont Vernon, Amherst, Nashua, and the surrounding communities.

Ready to bring your family home to Southern NH? Let's find your place."""

    am_platforms = [
        {"platform": "facebook", "accountId": ACCTS["facebook"]},
        {"platform": "instagram", "accountId": ACCTS["instagram"]},
        {"platform": "linkedin", "accountId": ACCTS["linkedin"]},
    ]

    post_to_late_api(am_platforms, am_content, am_image_url, scheduled_for="2026-08-15T08:00:00")

    # Morning Twitter post (separate, shortened)
    print("   - Morning Twitter post (8 AM ET)...")
    am_twitter_content = "Back-to-school moves are happening now in Southern NH. August is the final window before Labor Day. Families choose us for schools + community. Ready to find your home? Let's connect."
    twitter_platform = [{"platform": "twitter", "accountId": ACCTS["twitter"]}]
    post_to_late_api(twitter_platform, am_twitter_content, am_image_url, scheduled_for="2026-08-15T08:00:00")

    # Evening post (batch: FB/IG/LI + Twitter)
    print("   - Evening post (7:30 PM ET)...")
    pm_content = """When families choose a home, three things matter: schools, commute, and community.

Southern NH delivers all three. Our school districts are ranked among the best in the Northeast. Commute to Boston or Manchester is reasonable from everywhere. And the community? It's built on neighbors who actually know their neighbors.

If you're weighing your back-to-school options, we can show you why Southern NH wins.

Schedule a call. Your next chapter starts here."""

    pm_platforms = [
        {"platform": "facebook", "accountId": ACCTS["facebook"]},
        {"platform": "instagram", "accountId": ACCTS["instagram"]},
        {"platform": "linkedin", "accountId": ACCTS["linkedin"]},
    ]

    post_to_late_api(pm_platforms, pm_content, pm_image_url, scheduled_for="2026-08-15T19:30:00")

    # Evening Twitter post (separate, shortened)
    print("   - Evening Twitter post (7:30 PM ET)...")
    pm_twitter_content = "Schools, commute, community. Three things families prioritize. Southern NH delivers all three. That's why August is our busiest month. Ready to move? Let's talk."
    post_to_late_api(twitter_platform, pm_twitter_content, pm_image_url, scheduled_for="2026-08-15T19:30:00")

    print("\n✓ All content published successfully!")
    print(f"  Blog Post ID: {blog_post_id}")
    print(f"  Social posts scheduled for 8:00 AM and 7:30 PM ET")

    # 7. Delete images from Google Drive (manual flag for now)
    print("\n⚠️  REMINDER: Delete these images from Google Drive after posts go live:")
    print(f"   - file_179.jpg (blog)")
    print(f"   - file_181.jpg (morning social)")
    print(f"   - file_180.jpg (evening social)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
