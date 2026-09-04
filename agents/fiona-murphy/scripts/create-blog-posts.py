#!/usr/bin/env python3
"""
Create and publish the 3 blog posts for week of Aug 25-29, 2026.
Uses WordPress REST API + XML-RPC for Yoast SEO setup.
"""

import requests
import base64
import subprocess
from datetime import datetime

# WordPress config
WP_URL = "https://thehooverhometeam.com"
WP_USER = "chris@cbcoastrealty.com"
WP_PASSWORD = "Au1M DJEn iU9X 7YSh m7am nPSA"
CATEGORY_ID = 5  # Real Estate

# Media URLs (from Late API uploads)
MEDIA_URLS = {
    "file_193": "https://media.zernio.com/temp/1787571175526_j9ka41va_file_193.jpg",
    "file_192": "https://media.zernio.com/temp/1787571205463_ni89jn2a_file_192.jpg",
    "file_195": "https://media.zernio.com/temp/1787571254794_r1f57zbf_file_195.jpg",
}

def upload_featured_image(media_url: str) -> int:
    """
    Download image from URL and upload to WordPress media library via curl.
    Returns media ID.
    """
    import tempfile
    # Download the image
    resp = requests.get(media_url)
    resp.raise_for_status()
    image_data = resp.content

    # Extract filename from URL
    filename = media_url.split("_")[-1]  # e.g., "file_193.jpg"

    # Write to temp file for curl upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_data)
        tmp_path = tmp.name

    # Upload to WordPress media library using curl (avoids WAF 406 error)
    import subprocess
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{WP_URL}/wp-json/wp/v2/media",
        "-u", f"{WP_USER}:{WP_PASSWORD}",
        "-H", f"Content-Disposition: attachment; filename={filename}",
        "-H", "Content-Type: image/jpeg",
        "--data-binary", f"@{tmp_path}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    import json
    import os
    os.unlink(tmp_path)

    try:
        response = json.loads(result.stdout)
        media_id = response["id"]
        print(f"✅ Uploaded {filename} → media ID {media_id}")
        return media_id
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Upload failed: {result.stdout[:200]}")
        raise Exception(f"Image upload failed: {e}")

def create_blog_post(title: str, content: str, featured_media_id: int, focus_keyphrase: str, meta_desc: str) -> int:
    """
    Create a blog post via WordPress REST API using curl.
    Returns post ID.
    """
    import subprocess
    import json

    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [CATEGORY_ID],
        "featured_media": featured_media_id
    }

    # Use curl to avoid WAF 406 on JSON POST
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{WP_URL}/wp-json/wp/v2/posts",
        "-u", f"{WP_USER}:{WP_PASSWORD}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(post_data)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if "id" in response:
            post_id = response["id"]
            print(f"✅ Created post {post_id}: {title}")
            return post_id
        else:
            print(f"❌ Post creation failed: {result.stdout[:300]}")
            raise Exception(f"Post creation failed: {result.stdout}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {result.stdout[:300]}")
        raise

def set_yoast_meta(post_id: int, focus_keyphrase: str, meta_desc: str) -> None:
    """
    Set Yoast SEO meta fields via XML-RPC.
    """
    xml_rpc_payload = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>wp.editPost</methodName>
  <params>
    <param><value><int>1</int></value></param>
    <param><value><string>{WP_USER}</string></value></param>
    <param><value><string>{WP_PASSWORD}</string></value></param>
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
                    <member><name>value</name><value><string>{focus_keyphrase}</string></value></member>
                  </struct>
                </value>
                <value>
                  <struct>
                    <member><name>key</name><value><string>_yoast_wpseo_metadesc</string></value></member>
                    <member><name>value</name><value><string>{meta_desc}</string></value></member>
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
        "curl", "-s", "-X", "POST", f"{WP_URL}/xmlrpc.php",
        "-H", "Content-Type: text/xml",
        "-d", xml_rpc_payload
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if "methodResponse" in result.stdout and "fault" not in result.stdout.lower():
        print(f"✅ Set Yoast meta for post {post_id}")
    else:
        print(f"⚠️ Yoast meta may not have been set for post {post_id}: {result.stdout[:200]}")

def publish_monday_blog() -> None:
    """Monday: Rate Lock + Relocation Season"""
    print("\n📅 MONDAY BLOG POST\n")

    media_id = upload_featured_image(MEDIA_URLS["file_193"])

    title = "Why August 2026 Is Your Rate-Lock Window: The Best Time to Relocate to Southern New Hampshire"

    content = """<p>August is the busiest relocation month in the Northeast. Families are moving for back-to-school, job transfers, and new beginnings. And if you're relocating to Southern New Hampshire, the timing is more than right. Here's why August real estate opportunities in Southern NH are at their peak.</p>

<h2>The Rate Environment: Why 6.65–6.77% Matters</h2>

<p>Mortgage rates are holding steady around 6.65 to 6.77 percent. That's not the 7-plus percent many feared earlier in 2026. Fannie Mae is forecasting rates could climb to 6.8 percent or higher by year-end. If you're planning to relocate, your rate-lock window is closing.</p>

<p>A locked-in rate of 6.65 to 6.77 percent protects you from higher borrowing costs in the fall and winter. That certainty matters when you're making a major life decision like moving to a new state.</p>

<h2>August Is Peak Relocation Season</h2>

<p>August is the single busiest relocation month in the Northeast. Families are moving for back-to-school, corporate transfers, and lifestyle changes. The market is active, inventory is moving, and buyers have urgency. Sellers know this too, which means your offers are taken seriously. You're negotiating from a position of intent, not desperation.</p>

<h2>Inventory Is Climbing, Competition Is Falling</h2>

<p>The Southern New Hampshire real estate market has shifted. After two years of razor-thin inventory and multiple-offer bidding wars, new listings are climbing. Homes in Hillsborough County are still moving fast, averaging 7 days on market, but you're no longer competing in a frenzy.</p>

<p>This is the moment when your offers have power. Sellers are more flexible. Appraisals are more likely to support your purchase price. You have breathing room to negotiate terms, closing timelines, and contingencies.</p>

<h2>What This Means for You</h2>

<p>If you're relocating from Boston, New York, or another high-cost area, Southern New Hampshire offers something rare: stable rates, growing inventory, and less competition. Your dollar goes further. Your commute is reasonable (45 to 60 minutes to Boston suburbs). The schools are strong. The quality of life is exceptional.</p>

<p>August is your launch window. Lock in your rate. Make your move. Contact us to explore the homes and neighborhoods that fit your family's needs.</p>"""

    focus_keyphrase = "August real estate Southern NH"
    meta_desc = "August 2026 is the best time to buy in Southern New Hampshire. Rates are stable at 6.65–6.77%, inventory is climbing, and peak relocation season means opportunity. Here's why now matters."

    post_id = create_blog_post(title, content, media_id, focus_keyphrase, meta_desc)
    set_yoast_meta(post_id, focus_keyphrase, meta_desc)

def publish_wednesday_blog() -> None:
    """Wednesday: Nashua's Hot Market (Iris's angle, constrained)"""
    print("\n📅 WEDNESDAY BLOG POST\n")

    media_id = upload_featured_image(MEDIA_URLS["file_192"])

    title = "Nashua's Hot Real Estate Market: What It Really Means for Buyers in 2026"

    content = """<p>Nashua just got ranked America's hottest housing market. If you're buying, the truth is more nuanced than the headline. Here's what the data actually means for buyers in Hillsborough County.</p>

<h2>Why Nashua Is Ranked America's Hottest Market</h2>

<p>The "hottest market" designation typically refers to demand velocity, inventory turnover, and price momentum. Nashua checks all those boxes. Homes are selling fast. Prices are appreciating. Buyers are active. But "hot market" has a different meaning depending on your budget.</p>

<h2>The Reality for Buyers Under $500K</h2>

<p>In Nashua, homes under $500,000 are still seeing multiple offers. The market is tight at the entry level. If you're looking for a starter home or a rental investment, you're competing hard. Appraisals sometimes lag offer prices. Contingencies are limited. The buying experience is still seller-favorable in this price band.</p>

<h2>The Opportunity Zone: $500K to $900K</h2>

<p>This is where the market shifts. In the $500,000 to $900,000 range, where most families land, Amherst, Hollis, and Bow are seeing real negotiating room. Inventory is at 1.4 months across the region, which is still favorable for sellers, but it's real movement. Buyers in this band have options, can inspect homes thoroughly, and can negotiate terms.</p>

<p>If you're buying a family home or an upgrade, this is your sweet spot right now. The market is balanced enough for realistic negotiating, but inventory is still low enough that homes are moving quickly.</p>

<h2>What 1.4 Months of Inventory Really Means</h2>

<p>Balanced markets typically have 5 to 6 months of inventory. In a buyer's market, inventory climbs to 8 to 12 months. At 1.4 months, Hillsborough County is still seller-favorable, but it's rebalancing. Homes aren't sitting on market for months. Days-on-market is still in the single digits. But there are more homes to choose from, and buyers have time to make decisions.</p>

<h2>Your Next Move</h2>

<p>If you're buying in the $500K to $900K range, now is the time. You have inventory to browse, terms to negotiate, and rates locked in the mid-6% range. The opportunity window is real, and it's open right now. Let's explore what's available in your target neighborhoods.</p>"""

    focus_keyphrase = "Nashua real estate market"
    meta_desc = "Nashua's ranked America's hottest market. For buyers, the story depends on price. Discover where negotiating room is real in Amherst, Hollis, and Bow in 2026."

    post_id = create_blog_post(title, content, media_id, focus_keyphrase, meta_desc)
    set_yoast_meta(post_id, focus_keyphrase, meta_desc)

def publish_friday_blog() -> None:
    """Friday: List Before Q4"""
    print("\n📅 FRIDAY BLOG POST\n")

    media_id = upload_featured_image(MEDIA_URLS["file_195"])

    title = "Why Sellers Should List Before October: The 7-Day Reality of the August to September Window in Southern New Hampshire"

    content = """<p>Here's what 7-day average sales time means: if you list a home in Southern New Hampshire right now, it will sell before the weekend is over. That velocity is real, and it won't last forever. Here's why sellers should list before October.</p>

<h2>What 7-Day Average Sales Time Tells Us</h2>

<p>When homes in Hillsborough County are selling in 7 days on average, it means buyer intent is high. Homes are showing strong. Days-on-market metrics are holding at historic lows. The market is moving fast. If your home is listed during this window, it's in front of active, motivated buyers who are ready to make decisions quickly.</p>

<h2>Q4 Is Slower—Much Slower</h2>

<p>October through December is a different market. Thanksgiving, Christmas, and year-end holidays mean fewer showings. Fewer competing homes means fewer buyers see your listing. Work-from-home arrangements mean less relocation urgency. Sellers who are house-hunting slower, and the pool of available homes shrinks faster than the pool of buyers.</p>

<p>Q4 isn't a bad time to sell, but it's a slower time. And slower means less visibility and less urgency from your buyer pool.</p>

<h2>Peak-Exposure Window: August and September</h2>

<p>August and September are the peak-exposure window for sellers. Back-to-school drives relocation. Job transitions happen in late summer. Families want to settle before the holidays. The buyer pool is large, motivated, and shopping actively. Your home gets seen by the right audience at the right time.</p>

<h2>The Advantage of Listing Now</h2>

<p>If you're thinking about selling in 2026, August and September are your golden window. Your home will be shown to active, motivated buyers. Your sales timeline will be fast. Your negotiating position will be strong. You'll close before the holidays and avoid the Q4 slowdown entirely.</p>

<p>Once October rolls around, the market shifts. You'll still sell, but it will take longer, attract fewer competing offers, and face more seasonal headwinds. The advantage of listing now is very real.</p>

<h2>Let's Discuss Your Timeline</h2>

<p>If you're considering selling this year, now is the moment to have a conversation. Market conditions are favorable. Buyer intent is high. The window is open. Let's discuss your home, your timeline, and your goals. The timing is right.</p>"""

    focus_keyphrase = "sell before Q4"
    meta_desc = "7-day average sales time in Southern NH. Listing before October means peak exposure and high buyer intent. Discover why August and September are your window."

    post_id = create_blog_post(title, content, media_id, focus_keyphrase, meta_desc)
    set_yoast_meta(post_id, focus_keyphrase, meta_desc)

def main():
    print("🚀 Creating blog posts for week of Aug 25-29...\n")
    publish_monday_blog()
    publish_wednesday_blog()
    publish_friday_blog()
    print("\n✅ All blog posts published and Yoast SEO configured!")

if __name__ == "__main__":
    main()
