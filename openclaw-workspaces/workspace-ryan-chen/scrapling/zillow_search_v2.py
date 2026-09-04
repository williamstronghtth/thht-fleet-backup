#!/usr/bin/env python3
"""Search Zillow for properties using Scrapling - v2 with better parsing"""

from scrapling.fetchers import StealthyFetcher
import re

# Zillow search URL for 32128, 4+ bed, 3+ bath, $800k+
url = "https://www.zillow.com/homes/32128_rb/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22north%22%3A29.198%2C%22south%22%3A29.05%2C%22east%22%3A-80.93%2C%22west%22%3A-81.12%7D%2C%22usersSearchTerm%22%3A%2232128%22%2C%22filterState%22%3A%7B%22beds%22%3A%7B%22min%22%3A4%7D%2C%22baths%22%3A%7B%22min%22%3A3%7D%2C%22price%22%3A%7B%22min%22%3A800000%7D%2C%22sort%22%3A%7B%22value%22%3A%22days%22%7D%7D%2C%22isListVisible%22%3Atrue%7D"

print("🏠 Searching Zillow: 32128, 4+ bed, 3+ bath, $800k+\n")

try:
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    
    # Get all property cards
    cards = page.css('article[data-test="property-card"]')
    print(f"Found {len(cards)} listings\n")
    print("-" * 60)
    
    for i, card in enumerate(cards, 1):
        # Address
        address = card.css('address::text').get()
        if not address:
            address = card.css('[data-test="property-card-addr"]::text').get()
        
        # Price - try multiple selectors
        price = card.css('span[data-test="property-card-price"]::text').get()
        if not price:
            # Look for any span with $ in it
            all_spans = card.css('span::text').getall()
            for span in all_spans:
                if '$' in span:
                    price = span.strip()
                    break
        
        # Beds/baths/sqft
        details_list = card.css('ul li::text').getall()
        beds = baths = sqft = ""
        for d in details_list:
            d = d.strip()
            if 'bd' in d.lower():
                beds = d
            elif 'ba' in d.lower():
                baths = d
            elif 'sqft' in d.lower():
                sqft = d
        
        # Link
        link = card.css('a[data-test="property-card-link"]::attr(href)').get()
        if not link:
            link = card.css('a::attr(href)').get()
        
        if link and not link.startswith('http'):
            link = f"https://www.zillow.com{link}"
        
        print(f"{i}. {address or 'Address N/A'}")
        print(f"   💰 {price or 'Price N/A'}")
        if beds or baths or sqft:
            print(f"   🏠 {beds} | {baths} | {sqft}")
        if link:
            print(f"   🔗 {link[:70]}...")
        print()
    
    print("-" * 60)
    print(f"✅ Found {len(cards)} properties matching criteria")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
