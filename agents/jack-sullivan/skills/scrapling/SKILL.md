---
name: scrapling
description: Web scraping with anti-bot bypass. Use for Zillow, Cloudflare-protected sites, and any site that blocks regular scrapers.
---

# Scrapling - Anti-Bot Web Scraping

Scrapling bypasses bot detection on sites like Zillow, Cloudflare, and other protected websites.

## Quick Start

```python
from scrapling.fetchers import StealthyFetcher

# Fetch any protected site
page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)

# Extract data with CSS selectors
title = page.css('title::text').get()
items = page.css('.item::text').getall()
```

## Fetcher Types

### StealthyFetcher (Recommended)
Bypasses Cloudflare, Zillow, and most anti-bot systems.

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
```

### DynamicFetcher
Full browser for heavy JavaScript sites.

```python
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch(url, headless=True, network_idle=True)
```

## Common Patterns

### Zillow Property Search
```python
from scrapling.fetchers import StealthyFetcher

url = "https://www.zillow.com/homes/32128_rb/"
page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

for card in page.css('article[data-test="property-card"]'):
    address = card.css('address::text').get()
    price = [s for s in card.css('span::text').getall() if '$' in s][0]
    print(f"{address}: {price}")
```

### Extract All Links
```python
links = page.css('a::attr(href)').getall()
```

### Extract Text Content
```python
text = page.css('p::text').getall()
```

### Find by Class Contains
```python
items = page.css('[class*="product"]')
```

## Tips

1. Always use `headless=True` and `network_idle=True` for JS-heavy sites
2. StealthyFetcher spoofs browser fingerprints automatically
3. Use `page.css()` for CSS selectors, returns Adaptor objects
4. Use `.get()` for single result, `.getall()` for list
5. Add `::text` to get text content, `::attr(href)` for attributes

## Docs
https://scrapling.readthedocs.io
