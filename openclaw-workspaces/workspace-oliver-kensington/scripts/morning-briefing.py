#!/usr/bin/env python3
"""
Oliver Kensington's Morning Financial Briefing
Aggregates insights from 12 financial experts daily.

Usage:
    python morning-briefing.py
    python morning-briefing.py --test  # Test mode (fewer sources)
"""

import subprocess
import json
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

# Try importing scrapling
try:
    from scrapling.fetchers import StealthyFetcher
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False
    print("⚠️ Scrapling not available - install with: pip install scrapling")

import urllib.request
import urllib.error
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# =============================================================================
# CONFIGURATION
# =============================================================================

BLOG_SOURCES = {
    "Howard Marks": {
        "url": "https://www.oaktreecapital.com/insights",
        "type": "memo",
        "css_title": "h3 a, .card-title, .memo-title",
        "css_date": ".date, time, .memo-date"
    },
    "Aswath Damodaran": {
        "url": "http://aswathdamodaran.blogspot.com/",
        "type": "blog",
        "css_title": ".post-title a, h3.post-title",
        "css_content": ".post-body"
    },
    "Josh Brown": {
        "url": "https://thereformedbroker.com/",
        "type": "blog", 
        "css_title": "h2.entry-title a, article h2 a",
        "css_content": ".entry-content p"
    },
    "Michael Batnick": {
        "url": "https://theirrelevantinvestor.com/",
        "type": "blog",
        "css_title": "h2.entry-title a, .post-title a",
        "css_content": ".entry-content p"
    },
    "Lyn Alden": {
        "url": "https://www.lynalden.com/blog/",
        "type": "blog",
        "css_title": "h2 a, .entry-title a",
        "css_content": ".entry-summary, .entry-content"
    },
    "Dave Meyer": {
        "url": "https://www.biggerpockets.com/blog/author/davemeyer",
        "type": "blog",
        "css_title": "h2 a, .post-title a",
        "css_content": ".post-excerpt, .entry-content"
    }
}

TWITTER_HANDLES = {
    "Nick Timiraos": "@NickTimiraos",
    "Ray Dalio": "@RayDalio",  
    "Chamath Palihapitiya": "@chamath",
    "David Friedberg": "@friedberg",
    "Tracy Alloway": "@tracyalloway",
    "Joe Weisenthal": "@TheStalwart"
}

SEARCH_X_SCRIPT = Path(__file__).parent.parent / "skills/search-xepv0/scripts/search.js"


# =============================================================================
# FETCHING FUNCTIONS
# =============================================================================

def extract_text_from_html(html):
    """Clean HTML to plain text"""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch_blog(name, config):
    """Fetch blog content using Scrapling"""
    if not SCRAPLING_AVAILABLE:
        return {"error": "Scrapling not installed"}
    
    try:
        page = StealthyFetcher.fetch(config["url"], headless=True, network_idle=True)
        
        result = {
            "source": config["url"],
            "type": config["type"],
            "posts": []
        }
        
        # Try to get latest post titles
        titles = []
        for selector in config.get("css_title", "h2 a, h3 a").split(", "):
            found = page.css(f'{selector}::text').getall()
            if found:
                titles.extend(found)
        
        # Get content preview
        content = []
        for selector in config.get("css_content", ".entry-content p, article p").split(", "):
            found = page.css(f'{selector}::text').getall()
            if found:
                content.extend(found)
        
        # If CSS selectors fail, try extracting from raw HTML
        if not titles and not content:
            body_html = str(page.body) if hasattr(page, 'body') else ""
            
            # Try to find post titles in HTML
            title_matches = re.findall(r'<h[23][^>]*>.*?<a[^>]*>([^<]+)</a>', body_html, re.DOTALL)
            if title_matches:
                titles = [t.strip() for t in title_matches[:3]]
            
            # Get some body text
            if body_html:
                clean_text = extract_text_from_html(body_html)
                # Skip navigation/header content (usually first ~500 chars)
                if len(clean_text) > 700:
                    content = [clean_text[500:1200]]
        
        # Clean up titles
        titles = [t.strip() for t in titles if t.strip() and len(t.strip()) > 10][:3]
        content = [c.strip() for c in content if c.strip() and len(c.strip()) > 20][:2]
        
        result["titles"] = titles
        result["preview"] = " ".join(content)[:400] if content else ""
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


def search_twitter(handle, days=1):
    """Search X/Twitter using search-x skill"""
    if not SEARCH_X_SCRIPT.exists():
        return {"error": f"search-x script not found"}
    
    try:
        cmd = [
            "node", str(SEARCH_X_SCRIPT),
            "--handles", handle,
            "--days", str(days),
            "--compact",
            f"from:{handle.replace('@', '')}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            return {"tweets": result.stdout.strip()}
        elif "API key" in result.stderr or "XAI_API_KEY" in result.stderr:
            return {"error": "xAI API key not configured"}
        else:
            return {"error": result.stderr[:100] if result.stderr else "No results"}
            
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}


def fetch_market_data():
    """Fetch key market indices"""
    try:
        # Use Yahoo Finance API endpoint for quick data
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"  # S&P 500
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            result = data.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            return {
                "symbol": "S&P 500",
                "price": meta.get('regularMarketPrice'),
                "change": meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                "change_pct": ((meta.get('regularMarketPrice', 0) / meta.get('previousClose', 1)) - 1) * 100
            }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# BRIEFING GENERATION  
# =============================================================================

def generate_briefing(test_mode=False):
    """Generate the full morning briefing"""
    
    today = datetime.now().strftime("%A, %B %d, %Y")
    sections = []
    
    # Header
    sections.append(f"""📊 **MORNING FINANCIAL BRIEF**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{today}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    # Market Data
    sections.append("\n## 📈 MARKET PULSE\n")
    market = fetch_market_data()
    if "error" not in market:
        direction = "🟢" if market["change"] >= 0 else "🔴"
        sections.append(f"{direction} **{market['symbol']}**: ${market['price']:,.2f} ({market['change_pct']:+.2f}%)")
    else:
        sections.append(f"⚠️ Market data unavailable: {market['error']}")

    # Blog Sources
    sections.append("\n## 📝 EXPERT INSIGHTS\n")
    
    sources = dict(list(BLOG_SOURCES.items())[:2]) if test_mode else BLOG_SOURCES
    
    for name, config in sources.items():
        print(f"📖 {name}...")
        result = fetch_blog(name, config)
        
        if "error" in result:
            sections.append(f"**{name}**: ⚠️ {result['error']}\n")
        else:
            sections.append(f"**{name}** ({result['type']})")
            sections.append(f"🔗 {result['source']}")
            
            if result.get("titles"):
                sections.append("📌 Latest:")
                for title in result["titles"][:2]:
                    sections.append(f"  • {title}")
            
            if result.get("preview"):
                preview = result["preview"][:250]
                if len(result["preview"]) > 250:
                    preview += "..."
                sections.append(f"📄 {preview}")
            
            sections.append("")

    # Twitter/X
    sections.append("\n## 🐦 MARKET VOICES (X/Twitter)\n")
    
    handles = dict(list(TWITTER_HANDLES.items())[:2]) if test_mode else TWITTER_HANDLES
    
    for name, handle in handles.items():
        print(f"🐦 {name}...")
        result = search_twitter(handle, days=1)
        
        if "error" in result:
            sections.append(f"**{name}** ({handle}): ⚠️ {result['error']}")
        elif result.get("tweets"):
            sections.append(f"**{name}** ({handle})")
            tweets = result["tweets"][:350]
            if len(result["tweets"]) > 350:
                tweets += "..."
            sections.append(f"  {tweets}")
        sections.append("")

    # Synthesis section (for Oliver to fill in)
    sections.append("""
## 🧠 SYNTHESIS FRAMEWORK

Based on sources above, analyze:

1. **Key Themes**: What topics appear across multiple experts?
2. **Contrarian Signals**: Who disagrees with consensus?
3. **Macro Watch**: Fed, rates, inflation signals
4. **Sector Rotation**: Where is capital flowing?
5. **Risk Radar**: What should I monitor today?

---
*Pipeline: morning-briefing.py | Run: `python scripts/morning-briefing.py`*
""")

    return "\n".join(sections)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    
    print(f"{'🧪 TEST MODE' if test_mode else '📊 FULL BRIEFING'}\n")
    
    briefing = generate_briefing(test_mode=test_mode)
    
    print("\n" + "="*60)
    print(briefing)
    
    # Save to file
    output_dir = Path(__file__).parent
    output_file = output_dir / f"briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, 'w') as f:
        f.write(briefing)
    print(f"\n💾 Saved: {output_file}")
