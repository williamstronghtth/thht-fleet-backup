# Scrapling Setup

Adaptive web scraping framework with anti-bot bypass capabilities.

## Installation

```bash
cd /root/.openclaw/workspace-ryan-chen
source scrapling_env/bin/activate
```

## Quick Usage

### StealthyFetcher (Anti-bot bypass)
Best for sites with Cloudflare, bot detection, etc.

```python
from scrapling.fetchers import StealthyFetcher

# Fetch a protected site
page = StealthyFetcher.fetch('https://example.com', headless=True)

# Extract data
title = page.css('title::text').get()
links = page.css('a::attr(href)').getall()
```

### DynamicFetcher (JavaScript-heavy sites)
For sites that require full browser rendering.

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True, network_idle=True)
```

### Adaptive Scraping
Automatically relocates elements when site structure changes.

```python
# First scrape - save the element patterns
products = page.css('.product', auto_save=True)

# Later, if site changes, find them adaptively
products = page.css('.product', adaptive=True)
```

### Spider for Full Site Crawls

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    
    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {
                "title": item.css('h2::text').get(),
                "url": item.css('a::attr(href)').get()
            }

# Run
MySpider().start()
```

## Features

- ✅ Cloudflare Turnstile bypass
- ✅ Browser fingerprint spoofing
- ✅ TLS fingerprint impersonation
- ✅ Proxy rotation support
- ✅ Adaptive element tracking
- ✅ Pause/resume crawls
- ✅ MCP server for AI integration

## Docs

https://scrapling.readthedocs.io
