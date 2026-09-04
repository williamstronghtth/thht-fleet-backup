#!/bin/bash
# Create and publish blog post using curl workaround for Mod_Security
# May 3, 2026: New Hampshire's Hot Real Estate Market

WP_URL="https://thehooverhometeam.com"
WP_USER="chris@cbcoastrealty.com"
WP_PASSWORD="Au1M DJEn iU9X 7YSh m7am nPSA"
WP_CATEGORY="5"

# Blog content
BLOG_TITLE="Why New Hampshire Is the #8 Hottest Real Estate Market in 2026"

BLOG_CONTENT="<p>New Hampshire just earned a top ten ranking among the hottest real estate markets in 2026. And if you've been watching the Southern NH market, you know exactly why.</p>

<h2>The Numbers Are Clear</h2>

<p>Hillsborough County tells the story:</p>

<ul>
<li>Median home price: <strong>\$548,750</strong> (March 2026)</li>
<li>Closed sales up <strong>6.6%</strong> year over year (178 sold in March vs 167 last year)</li>
<li>Inventory: just <strong>1.43 months</strong> (balanced market is 5 to 6 months)</li>
<li>Price appreciation forecast: <strong>2 to 4%</strong> through 2026</li>
<li>Homes selling at <strong>100.86% of asking price</strong></li>
</ul>

<p>These aren't theoretical numbers. These are real transactions in real communities. Mont Vernon. Amherst. Milford. Nashua. Salem. Smart investors and homebuyers are choosing Southern NH.</p>

<h2>What Makes Southern NH Different</h2>

<p>So why is New Hampshire hot while other markets cool down?</p>

<p><strong>Quality of life</strong> tops the list. New England character, strong schools, outdoor recreation, thriving communities. You don't get that everywhere.</p>

<p><strong>Market fundamentals are solid.</strong> Limited inventory keeps prices stable. Strong buyer demand keeps the market active. Homes priced right sell quickly at or above asking. Homes that linger? They're overpriced, and the market corrects fast.</p>

<p><strong>Smart money is moving in.</strong> Out of state relocations, growing families escaping higher cost metros, retirees seeking quality communities. They're all recognizing what we already knew: Southern NH is worth the investment.</p>

<h2>What This Means for Sellers</h2>

<p>If you've been thinking about selling, the market is in your favor right now.</p>

<p>With only 1.43 months of inventory, your home will have less competition. Buyer interest is strong. Homes selling at 100.86% of asking means your pricing strategy matters enormously, but the fundamentals support strong results.</p>

<p>The window is open. Early movers who list now capture peak buyer interest and momentum.</p>

<h2>What This Means for Buyers</h2>

<p>Low inventory sounds discouraging, but here's the reality: with closed sales up 6.6%, the market is actively moving. Homes are selling. And buyers who move quickly, get pre-approved, and make informed offers are winning in this market.</p>

<p>The key? Work with someone who understands the market, knows what's realistic in your price range, and can help you move fast when the right home shows up.</p>

<h2>The Bottom Line</h2>

<p>New Hampshire's top ten ranking isn't random. It reflects real value, real opportunity, and real quality. The Hoover Home Team focuses exclusively on this market because we know it, understand it, and help our clients succeed in it.</p>

<p>Whether you're selling to capitalize on strong demand or buying to secure your place in this market, the fundamentals support smart decisions right now.</p>

<p><strong>Let's talk about your move in Southern NH's hot market.</strong> The Hoover Home Team is ready to help.</p>"

echo "========================================"
echo "📝 Publishing Blog Post via WordPress"
echo "========================================"
echo ""

# Create JSON payload using Python to ensure proper escaping
python3 - <<'EOF'
import json
import subprocess
import requests
import base64

title = "Why New Hampshire Is the #8 Hottest Real Estate Market in 2026"
content = """<p>New Hampshire just earned a top ten ranking among the hottest real estate markets in 2026. And if you've been watching the Southern NH market, you know exactly why.</p>

<h2>The Numbers Are Clear</h2>

<p>Hillsborough County tells the story:</p>

<ul>
<li>Median home price: <strong>$548,750</strong> (March 2026)</li>
<li>Closed sales up <strong>6.6%</strong> year over year (178 sold in March vs 167 last year)</li>
<li>Inventory: just <strong>1.43 months</strong> (balanced market is 5 to 6 months)</li>
<li>Price appreciation forecast: <strong>2 to 4%</strong> through 2026</li>
<li>Homes selling at <strong>100.86% of asking price</strong></li>
</ul>

<p>These aren't theoretical numbers. These are real transactions in real communities. Mont Vernon. Amherst. Milford. Nashua. Salem. Smart investors and homebuyers are choosing Southern NH.</p>

<h2>What Makes Southern NH Different</h2>

<p>So why is New Hampshire hot while other markets cool down?</p>

<p><strong>Quality of life</strong> tops the list. New England character, strong schools, outdoor recreation, thriving communities. You don't get that everywhere.</p>

<p><strong>Market fundamentals are solid.</strong> Limited inventory keeps prices stable. Strong buyer demand keeps the market active. Homes priced right sell quickly at or above asking. Homes that linger? They're overpriced, and the market corrects fast.</p>

<p><strong>Smart money is moving in.</strong> Out of state relocations, growing families escaping higher cost metros, retirees seeking quality communities. They're all recognizing what we already knew: Southern NH is worth the investment.</p>

<h2>What This Means for Sellers</h2>

<p>If you've been thinking about selling, the market is in your favor right now.</p>

<p>With only 1.43 months of inventory, your home will have less competition. Buyer interest is strong. Homes selling at 100.86% of asking means your pricing strategy matters enormously, but the fundamentals support strong results.</p>

<p>The window is open. Early movers who list now capture peak buyer interest and momentum.</p>

<h2>What This Means for Buyers</h2>

<p>Low inventory sounds discouraging, but here's the reality: with closed sales up 6.6%, the market is actively moving. Homes are selling. And buyers who move quickly, get pre-approved, and make informed offers are winning in this market.</p>

<p>The key? Work with someone who understands the market, knows what's realistic in your price range, and can help you move fast when the right home shows up.</p>

<h2>The Bottom Line</h2>

<p>New Hampshire's top ten ranking isn't random. It reflects real value, real opportunity, and real quality. The Hoover Home Team focuses exclusively on this market because we know it, understand it, and help our clients succeed in it.</p>

<p>Whether you're selling to capitalize on strong demand or buying to secure your place in this market, the fundamentals support smart decisions right now.</p>

<p><strong>Let's talk about your move in Southern NH's hot market.</strong> The Hoover Home Team is ready to help.</p>"""

WP_URL = "https://thehooverhometeam.com"
WP_USER = "chris@cbcoastrealty.com"
WP_PASSWORD = "Au1M DJEn iU9X 7YSh m7am nPSA"
WP_CATEGORY = 5

# Create basic auth
credentials = f"{WP_USER}:{WP_PASSWORD}"
auth_header = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json"
}

post_data = {
    "title": title,
    "content": content,
    "status": "publish",
    "categories": [WP_CATEGORY],
}

try:
    print(f"Title: {title}")
    print(f"URL: {WP_URL}/wp-json/wp/v2/posts")
    print("")

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=post_data,
        headers=headers,
        timeout=30
    )

    if response.status_code not in [200, 201]:
        print(f"❌ Failed: HTTP {response.status_code}")
        print(f"Response: {response.text}")
    else:
        response_data = response.json()
        post_id = response_data.get("id")
        post_url = response_data.get("link")
        print(f"✓ Blog post created successfully!")
        print(f"  Post ID: {post_id}")
        print(f"  URL: {post_url}")

except Exception as e:
    print(f"❌ Request failed: {e}")

EOF

echo ""
echo "========================================"
echo "Blog publishing process complete"
echo "========================================"
