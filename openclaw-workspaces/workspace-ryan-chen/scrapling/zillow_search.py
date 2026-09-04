#!/usr/bin/env python3
"""Search Zillow for properties using Scrapling"""

from scrapling.fetchers import StealthyFetcher
import json

# Zillow search URL for 32128, 4+ bed, 3+ bath, $800k+
url = "https://www.zillow.com/homes/32128_rb/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22north%22%3A29.198%2C%22south%22%3A29.05%2C%22east%22%3A-80.93%2C%22west%22%3A-81.12%7D%2C%22usersSearchTerm%22%3A%2232128%22%2C%22filterState%22%3A%7B%22beds%22%3A%7B%22min%22%3A4%7D%2C%22baths%22%3A%7B%22min%22%3A3%7D%2C%22price%22%3A%7B%22min%22%3A800000%7D%2C%22sort%22%3A%7B%22value%22%3A%22days%22%7D%7D%2C%22isListVisible%22%3Atrue%7D"

print("🏠 Searching Zillow: 32128, 4+ bed, 3+ bath, $800k+\n")

try:
    # Use StealthyFetcher to bypass Zillow's bot detection
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    
    # Try to extract property cards
    cards = page.css('article[data-test="property-card"]')
    
    if not cards:
        # Alternative selectors
        cards = page.css('[class*="property-card"]')
    
    if not cards:
        cards = page.css('[class*="ListItem"]')
    
    print(f"Found {len(cards)} property cards\n")
    
    properties = []
    for card in cards[:10]:  # First 10
        try:
            address = card.css('address::text').get() or card.css('[data-test="property-card-addr"]::text').get()
            price = card.css('[data-test="property-card-price"]::text').get() or card.css('[class*="price"]::text').get()
            details = card.css('[data-test="property-card-details"]::text').get() or ""
            link = card.css('a::attr(href)').get()
            
            if address or price:
                prop = {
                    "address": address.strip() if address else "N/A",
                    "price": price.strip() if price else "N/A",
                    "details": details.strip() if details else "N/A",
                    "link": f"https://zillow.com{link}" if link and not link.startswith('http') else link
                }
                properties.append(prop)
                print(f"📍 {prop['address']}")
                print(f"   💰 {prop['price']}")
                print(f"   🛏️ {prop['details']}")
                print()
        except Exception as e:
            continue
    
    if not properties:
        # Fallback: print page title and check if blocked
        title = page.css('title::text').get()
        print(f"Page title: {title}")
        
        # Check for captcha/block indicators
        if "captcha" in str(page.body).lower() or "robot" in str(page.body).lower():
            print("⚠️ Zillow served a captcha/robot check")
        else:
            print("⚠️ No properties found - page structure may have changed")
            # Print some debug info
            print(f"\nPage length: {len(str(page.body))} chars")
            
except Exception as e:
    print(f"❌ Error: {e}")
