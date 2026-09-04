#!/usr/bin/env python3
"""Quick test of Scrapling capabilities"""

from scrapling.fetchers import Fetcher, StealthyFetcher

# Test 1: Basic HTTP fetch
print("Test 1: Basic HTTP fetch...")
try:
    page = Fetcher.fetch('https://httpbin.org/headers')
    print(f"✅ Basic fetch works - Status: {page.status}")
except Exception as e:
    print(f"❌ Basic fetch failed: {e}")

# Test 2: Stealthy fetch (browser fingerprint spoofing)
print("\nTest 2: Stealthy fetch with anti-bot bypass...")
try:
    page = StealthyFetcher.fetch('https://www.cloudflare.com', headless=True)
    title = page.css('title::text').get()
    print(f"✅ Stealthy fetch works - Title: {title}")
except Exception as e:
    print(f"❌ Stealthy fetch failed: {e}")

# Test 3: CSS selector parsing
print("\nTest 3: CSS selector parsing...")
try:
    page = Fetcher.fetch('https://example.com')
    heading = page.css('h1::text').get()
    print(f"✅ Parsing works - Heading: {heading}")
except Exception as e:
    print(f"❌ Parsing failed: {e}")

print("\n🎉 Scrapling is ready to use!")
