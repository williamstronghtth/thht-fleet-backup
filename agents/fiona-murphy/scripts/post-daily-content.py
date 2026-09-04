#!/usr/bin/env python3
"""
Post daily content to Late API and WordPress.
Handles: 8 AM social post, 7:30 PM social post, blog post.
"""

import json
import subprocess
import requests
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
import time

# Late API configuration
LATE_API_KEY = os.environ["LATE_API_KEY"]
LATE_BASE_URL = "https://getlate.dev/api/v1"

# Account IDs
ACCOUNTS = {
    "facebook": "698f6ab9fd3d49fbfa3e2a9f",
    "instagram": "698f6a5ffd3d49fbfa3e29f7",
    "linkedin": "698f6b23fd3d49fbfa3e2baf",
    "twitter": "698f6ad0fd3d49fbfa3e2afd",
    "googlebusiness": "6a1f19432b2567671aa1ea24"
}

# WordPress configuration
WP_BASE_URL = "https://thehooverhometeam.com"
WP_USER = "chris@cbcoastrealty.com"
WP_APP_PASSWORD = "Au1M DJEn iU9X 7YSh m7am nPSA"
WP_CATEGORY = 5

def upload_image_to_late(image_path):
    """Upload image to Late API and return public URL."""
    print(f"Uploading image: {image_path}")

    filename = Path(image_path).name

    # Step 1: Get presign URL
    presign_payload = {
        "filename": filename,
        "contentType": "image/jpeg"
    }

    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

    presign_response = requests.post(
        f"{LATE_BASE_URL}/media/presign",
        json=presign_payload,
        headers=headers
    )

    if presign_response.status_code != 200:
        print(f"Presign failed: {presign_response.text}")
        sys.exit(1)

    presign_data = presign_response.json()
    upload_url = presign_data.get("uploadUrl")
    public_url = presign_data.get("publicUrl")

    if not upload_url or not public_url:
        print(f"No upload URL in response: {presign_data}")
        sys.exit(1)

    # Step 2: Upload binary image to the presigned URL
    with open(image_path, "rb") as f:
        image_data = f.read()

    upload_response = requests.put(upload_url, data=image_data)

    if upload_response.status_code not in [200, 201]:
        print(f"Image upload failed: {upload_response.text}")
        sys.exit(1)

    print(f"Image uploaded successfully: {public_url}")
    return public_url

def post_to_late_batch(platforms, content, media_urls, publish_time):
    """Post to multiple platforms (batch request). Never includes Twitter."""
    print(f"Posting batch to: {', '.join([p['platform'] for p in platforms])}")

    payload = {
        "platforms": platforms,
        "content": content,
        "mediaItems": [{"type": "image", "url": url} for url in media_urls],
        "publishNow": False,
        "scheduledFor": publish_time
    }

    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{LATE_BASE_URL}/posts",
        json=payload,
        headers=headers
    )

    if response.status_code not in [200, 201]:
        print(f"Batch post failed: {response.text}")
        sys.exit(1)

    result = response.json()
    post_id = result.get("post", {}).get("_id")
    print(f"Batch post created: {post_id}")
    return post_id

def post_to_late_twitter(content, media_urls, publish_time):
    """Post to Twitter ONLY (separate request, never batched)."""
    print(f"Posting to Twitter separately (char count: {len(content)})")

    if len(content) > 280:
        print(f"ERROR: Twitter content exceeds 280 chars: {len(content)} chars")
        sys.exit(1)

    payload = {
        "platforms": [{"platform": "twitter", "accountId": ACCOUNTS["twitter"]}],
        "content": content,
        "mediaItems": [{"type": "image", "url": url} for url in media_urls],
        "publishNow": False,
        "scheduledFor": publish_time
    }

    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{LATE_BASE_URL}/posts",
        json=payload,
        headers=headers
    )

    if response.status_code not in [200, 201]:
        print(f"Twitter post failed: {response.text}")
        sys.exit(1)

    result = response.json()
    post_id = result.get("post", {}).get("_id")
    print(f"Twitter post created: {post_id}")
    return post_id

def upload_image_to_wordpress(image_path, alt_text):
    """Upload image to WordPress and return media ID."""
    print(f"Uploading to WordPress: {image_path} (alt: {alt_text})")

    filename = Path(image_path).name

    with open(image_path, "rb") as f:
        image_data = f.read()

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg"
    }

    auth = (WP_USER, WP_APP_PASSWORD)

    response = requests.post(
        f"{WP_BASE_URL}/wp-json/wp/v2/media",
        data=image_data,
        headers=headers,
        auth=auth
    )

    if response.status_code not in [200, 201]:
        print(f"WordPress media upload failed: {response.text}")
        sys.exit(1)

    media = response.json()
    media_id = media.get("id")
    print(f"Media uploaded (ID: {media_id})")

    # Set alt text
    alt_payload = {"alt_text": alt_text}
    alt_response = requests.post(
        f"{WP_BASE_URL}/wp-json/wp/v2/media/{media_id}",
        json=alt_payload,
        auth=auth
    )

    if alt_response.status_code not in [200, 201]:
        print(f"Alt text update failed: {alt_response.text}")

    return media_id

def create_wordpress_post(title, content, featured_media_id, slug):
    """Create blog post in WordPress."""
    print(f"Creating WordPress post: {title}")

    payload = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [WP_CATEGORY],
        "featured_media": featured_media_id,
        "slug": slug
    }

    auth = (WP_USER, WP_APP_PASSWORD)

    response = requests.post(
        f"{WP_BASE_URL}/wp-json/wp/v2/posts",
        json=payload,
        auth=auth
    )

    if response.status_code not in [200, 201]:
        print(f"Post creation failed: {response.text}")
        sys.exit(1)

    post = response.json()
    post_id = post.get("id")
    print(f"Post created (ID: {post_id})")
    return post_id

def set_yoast_meta(post_id, focuskw, metadesc):
    """Set Yoast SEO meta fields via XML-RPC."""
    print(f"Setting Yoast meta (post {post_id})")

    xml_payload = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>wp.editPost</methodName>
  <params>
    <param><value><int>1</int></value></param>
    <param><value><string>{WP_USER}</string></value></param>
    <param><value><string>{WP_APP_PASSWORD}</string></value></param>
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

    response = requests.post(
        f"{WP_BASE_URL}/xmlrpc.php",
        data=xml_payload,
        headers={"Content-Type": "text/xml"}
    )

    if response.status_code != 200 or "<boolean>1</boolean>" not in response.text:
        print(f"Yoast meta failed: {response.text}")
        sys.exit(1)

    print("Yoast meta set successfully")

def verify_yoast_checks(post_id):
    """Run Yoast verification script."""
    print(f"Running Yoast verification (post {post_id})")

    result = subprocess.run(
        ["python3", "/root/agents/fiona-murphy/workspace/scripts/yoast-check.py", str(post_id)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("Yoast checks FAILED")
        print(result.stderr)
        sys.exit(1)

    print("Yoast checks PASSED")

def main():
    print("\n=== POSTING DAILY CONTENT (August 22, 2026) ===\n")

    workspace = Path("/root/agents/fiona-murphy/workspace")

    # 8 AM POST
    print(">>> 8 AM Post <<<")
    print("---")

    image_188_url = upload_image_to_late(workspace / "inbox" / "file_188.jpg")

    post_8am_content = """Did you know? The Manchester-Nashua area just ranked #1 hottest housing market in the entire USA.

Out of 300+ markets nationally, our corner of New England is where the real action is. That's not by accident, it reflects what makes Southern NH so special: strong job market, award-winning schools, charming downtowns, and that New England lifestyle people move for.

This summer, inventory climbed 5 to 10% across Hillsborough County. More homes are hitting the market right now. More choices for buyers. More opportunity for sellers. Rates are holding steady around 6.5%.

Whether you're thinking about selling or buying, August is your window. The market is shifting. Buyer confidence is returning. And Nashua is leading the way nationally.

Ready to move? Let's talk about your next step."""

    twitter_8am = "Nashua just ranked #1 hottest housing market in the USA 🔥 Out of 300+ markets nationally, Southern NH is where the action is. Strong job market. Award-winning schools. That New England lifestyle. Your next move starts here. 📍"

    publish_time_8am = "2026-08-22T08:00:00-04:00"

    # Batch post (FB, IG, LI, GMB)
    batch_platforms_8am = [
        {"platform": "facebook", "accountId": ACCOUNTS["facebook"]},
        {"platform": "instagram", "accountId": ACCOUNTS["instagram"]},
        {"platform": "linkedin", "accountId": ACCOUNTS["linkedin"]},
        {"platform": "googlebusiness", "accountId": ACCOUNTS["googlebusiness"]}
    ]

    post_to_late_batch(batch_platforms_8am, post_8am_content, [image_188_url], publish_time_8am)

    # Twitter (separate)
    time.sleep(0.5)  # Small delay to avoid rate limiting
    post_to_late_twitter(twitter_8am, [image_188_url], publish_time_8am)

    print()

    # 7:30 PM POST
    print(">>> 7:30 PM Post <<<")
    print("---")

    image_191_url = upload_image_to_late(workspace / "inbox" / "file_191.jpg")

    post_730pm_content = """Inventory just jumped. Buyer confidence is back.

After two years of strong seller advantage, August 2026 is shifting. More homes on the market. Longer average days to sale. More room for negotiation.

In Hillsborough County, 99 new builds are listed. Over 346 condos are available. Townhouses, multifamily units, single-family homes. Inventory is climbing across every category.

For buyers, this means more options. For sellers, it means being strategic about timing and pricing.

If you've been waiting on the sidelines, August might be your moment. The window is open, and it's the right size.

Ready to talk? Let's find your move."""

    twitter_730pm = "Inventory climbing. Buyer confidence back. August 2026 is shifting Southern NH real estate. 99 new builds. 346+ condos. More negotiation room. If you've been waiting, this is your moment. 📈"

    publish_time_730pm = "2026-08-22T19:30:00-04:00"

    # Batch post (FB, IG, LI, GMB)
    batch_platforms_730pm = [
        {"platform": "facebook", "accountId": ACCOUNTS["facebook"]},
        {"platform": "instagram", "accountId": ACCOUNTS["instagram"]},
        {"platform": "linkedin", "accountId": ACCOUNTS["linkedin"]},
        {"platform": "googlebusiness", "accountId": ACCOUNTS["googlebusiness"]}
    ]

    post_to_late_batch(batch_platforms_730pm, post_730pm_content, [image_191_url], publish_time_730pm)

    # Twitter (separate)
    time.sleep(0.5)
    post_to_late_twitter(twitter_730pm, [image_191_url], publish_time_730pm)

    print()

    # BLOG POST
    print(">>> Blog Post <<<")
    print("---")

    image_190_id = upload_image_to_wordpress(
        workspace / "inbox" / "file_190.jpg",
        "Nashua housing market example bright spa-like primary bathroom"
    )

    blog_content = """<!-- wp:paragraph --><p>The Nashua housing market just ranked #1 hottest in the entire United States. Out of over 300 housing markets evaluated nationally, Southern New Hampshire and the Manchester-Nashua area are where buyers and sellers are focused right now. This is not luck. It reflects the real fundamentals that drive our regional economy.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>If you have been considering a move to Southern New Hampshire, or wondering whether now is the right time to sell, today's market data tells a compelling story.</p><!-- /wp:paragraph -->

<!-- wp:heading {"level":2} --><h2>The Nashua Housing Market Momentum</h2><!-- /wp:heading -->

<!-- wp:paragraph --><p>Summer 2026 is turning out to be a turning point for the Nashua housing market. Inventory across Hillsborough County has climbed 5 to 10% since spring, bringing more homes onto the market when buyer confidence is returning. The median home price in Hillsborough County is holding steady around $569,000, with statewide median prices in the $530,000 to $533,000 range.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>According to data from <a href="https://www.nhar.org" target="_blank" rel="noopener">the New Hampshire Association of Realtors</a>, 99 new construction homes are currently listed in Hillsborough County. Over 346 condos are on the market. Townhouses, multifamily units, and single-family homes round out an inventory picture that has not looked this balanced in two years.</p><!-- /wp:paragraph -->

<!-- wp:heading {"level":2} --><h2>Why Buyers Are Looking at Nashua and Southern New Hampshire</h2><!-- /wp:heading -->

<!-- wp:paragraph --><p>The Nashua housing market is strong because the fundamentals are strong. A thriving job market centered around healthcare, technology, and professional services draws families and professionals from Boston and beyond. Award-winning schools in towns like Amherst, Milford, and Mont Vernon are perennial draws. And there is something intangible about New England in summer, charming downtown districts, four genuine seasons, hiking, lakes, and that small-town lifestyle that people search for when they leave denser areas.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>Buyers are rational. They move toward markets with economic momentum and quality-of-life factors. The Nashua housing market checks every box.</p><!-- /wp:paragraph -->

<!-- wp:heading {"level":2} --><h2>What This Means for Buyers and Sellers</h2><!-- /wp:heading -->

<!-- wp:paragraph --><p>For buyers, the Nashua housing market shift means more choices and room to negotiate. After two years of strong seller advantage, negotiation dynamics are changing. Days on market have extended. Homes are no longer selling in 15 to 20 days across the board. This benefits prepared buyers who can move quickly and sellers who price strategically.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>For sellers, it means the urgency to list immediately has eased. You now have time to prepare your home, price it right, and market it properly. The Nashua housing market rewards homes that are move-in ready and priced competitively.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>Interest rates continue to hold steady around 6.5%, and economists expect 2 to 4% home appreciation through the remainder of 2026. For long-term owners, this is favorable territory.</p><!-- /wp:paragraph -->

<!-- wp:heading {"level":2} --><h2>Your Next Move Starts Here</h2><!-- /wp:heading -->

<!-- wp:paragraph --><p>Whether you have been waiting for the Nashua housing market to tip toward buyers, or you have been holding off on selling because timing did not feel right, August 2026 is signaling a shift. Inventory is climbing. Buyer confidence is returning. And Southern New Hampshire is leading the nation.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p>If you are ready to explore your options in the Nashua housing market, let us help. We know these neighborhoods. We understand the buyers. And we know how to market your home to get results.</p><!-- /wp:paragraph -->

<!-- wp:paragraph --><p><a href="https://thehooverhometeam.com/contact/" target="_blank" rel="noopener">Get in touch with The Hoover Home Team today</a> and let's talk about your move.</p><!-- /wp:paragraph -->"""

    blog_post_id = create_wordpress_post(
        title="Why Nashua Is the #1 Hottest Housing Market in America",
        content=blog_content,
        featured_media_id=image_190_id,
        slug="why-nashua-hottest-housing-market"
    )

    # Set Yoast meta
    set_yoast_meta(
        blog_post_id,
        focuskw="Nashua housing market",
        metadesc="Nashua housing market ranks #1 hottest in USA. Learn why Southern NH leads nationally and what that means for buyers and sellers right now."
    )

    # Verify Yoast checks
    verify_yoast_checks(blog_post_id)

    print()
    print("=== ALL CONTENT POSTED SUCCESSFULLY ===\n")
    print(f"8 AM social post (batch + Twitter): published")
    print(f"7:30 PM social post (batch + Twitter): published")
    print(f"Blog post (ID {blog_post_id}): published with Yoast verified")
    print()

if __name__ == "__main__":
    main()
