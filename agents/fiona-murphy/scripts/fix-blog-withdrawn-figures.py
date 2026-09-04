#!/usr/bin/env python3
"""
Fix withdrawn figures in published blog posts (49569, 49572, 49575).
Uses WordPress REST API to update post content.
"""

import requests
import json
from base64 import b64encode

# WordPress config
WP_URL = "https://thehooverhometeam.com"
WP_USER = "fiona"
WP_PASS = "jD%82!mQ@vKL9wXpZ"  # In .env in production
WP_AUTH = b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

headers = {
    "Authorization": f"Basic {WP_AUTH}",
    "Content-Type": "application/json"
}

def fix_post_49569():
    """
    Fix "Why August 2026 Is Your Rate-Lock Window"
    Remove: "Fannie Mae is forecasting rates could climb to 6.8 percent or higher by year-end"
    Remove: "averaging 7 days on market"
    """
    post_id = 49569

    # Get current post
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", headers=headers)
    resp.raise_for_status()
    post = resp.json()

    content = post["content"]["rendered"]

    # Remove the 6.8% forecast line
    content = content.replace(
        "Fannie Mae is forecasting rates could climb to 6.8 percent or higher by year-end. If you're planning to relocate, your rate-lock window is closing.",
        "If you're planning to relocate, your rate-lock window is important."
    )

    # Remove 7-day reference
    content = content.replace(
        ", averaging 7 days on market,",
        ","
    )

    # Update post
    update_data = {"content": content}
    resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", json=update_data, headers=headers)
    resp.raise_for_status()
    print(f"✅ Fixed post {post_id}: removed '6.8% or higher' and '7 days' references")

def fix_post_49572():
    """
    Fix "Nashua's Hot Real Estate Market"
    Replace: "Inventory is at 1.4 months" with "Inventory levels are shifting"
    """
    post_id = 49572

    # Get current post
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", headers=headers)
    resp.raise_for_status()
    post = resp.json()

    content = post["content"]["rendered"]

    # Replace unsourced 1.4 months figures
    content = content.replace(
        "Inventory is at 1.4 months across the region.",
        "Inventory levels are shifting across the region."
    )

    content = content.replace(
        "Inventory is at 1.4 months, which is still favorable for sellers, but it's real movement.",
        "Inventory levels are improving, which means real movement and more options for buyers."
    )

    # Update post
    update_data = {"content": content}
    resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", json=update_data, headers=headers)
    resp.raise_for_status()
    print(f"✅ Fixed post {post_id}: replaced unsourced '1.4 months' with 'inventory levels are shifting'")

def fix_post_49575():
    """
    Fix "Why Sellers Should List Before October"
    Replace: "7-day average sales time" with "strong sales velocity"
    """
    post_id = 49575

    # Get current post
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", headers=headers)
    resp.raise_for_status()
    post = resp.json()

    content = post["content"]["rendered"]

    # Replace 7-day references
    content = content.replace(
        "Here's what 7-day average sales time means: if you list a home in Southern New Hampshire right now, it will sell before the weekend is over. That velocity is real,",
        "Homes are selling with strong velocity right now in Southern New Hampshire. That pace is real,"
    )

    content = content.replace(
        "When homes in Hillsborough County are selling in 7 days on average,",
        "When homes in Hillsborough County are selling with strong velocity,"
    )

    content = content.replace(
        "Days-on-market metrics are holding at historic lows.",
        "Sales are moving quickly."
    )

    # Update post
    update_data = {"content": content}
    resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}", json=update_data, headers=headers)
    resp.raise_for_status()
    print(f"✅ Fixed post {post_id}: replaced unsourced '7-day' metrics with 'strong velocity'")

if __name__ == "__main__":
    try:
        fix_post_49569()
        fix_post_49572()
        fix_post_49575()
        print("\n✅ All blog posts fixed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
