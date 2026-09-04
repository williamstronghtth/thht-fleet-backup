#!/usr/bin/env python3
"""
Entertainment & Culture Market Scanner
Targets highest-bias categories per research

Categories: Entertainment, Culture, Crypto, Social Media, TV, Music
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient
from bias_calibration import score_opportunity, calculate_bias, get_category_multiplier

# Configuration
WORKSPACE = Path('/root/.openclaw/workspace-elliot-crane')
OUTPUT_DIR = WORKSPACE / 'kalshi' / 'scans'

API_KEY_ID = "adcd595f-ac7a-4d70-b6df-a859a2f3ac63"
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQEAtTsPAY837dUOdT4JWFH8KMsomqooJe1fWgWWaFxRZCsFIqeC
IjknFX4JplBI4NcRhs6RNCI+NzCaTLtHEJ58XNEDEJszoG9PNCyTKaJ+nxUhOOdf
M1oGE8fRcTrTlcBcnqpDsvYTBS/OFdZfencAeR8SMkCSY9LxMVLZIU1TqunPBOVP
GuZyOHL29nXukbWPUNtWrZav7Rz/LRVSgJWWp7o78TE2t2t9UJ3zvGuNBsh7f4/0
/0cb1T8Nk8vQiug/c2zmnkB5ldEuW4VUT/IOYMGKXxdszbRAtv8DCZuQMh+3dkeR
l2VbfH/F8Cvmhd3qONzZuWc7Iti1dJX+dndkSQIDAQABAoH/G+U+V8g/5egEAnWc
XCaLl3K6KLLXh2CCOoO6CquYz2qrNQXEXYxiWTvKNEMnVh8Z7vVWrYT5V8JaRu83
XIItKGVlMdnuySq6ehaTIp6dZPeYmVRZKFd8KkYjs9ZH6++p8HkT/scq3S21bI6x
O/3MGvEI1eQai/nZ3SVXRp5RMEyWXSHngkTuxmaL3sT2E7xyvY1P+5+GG2fHmNGc
OS7COo76ll8rRmkurJqCKNOH9CBKJwkyCfVfVqKIw2vCGYZd97GVXdoiyn+j0b4Z
ybuWVXhO0m2xoWsbDaIZDCnbrzhxPrLcLZGBTumfTMmqITk/dg+wdUxwxH9CGiru
Mo6BAoGBAMEu+3RInfcIF1fw97ZMujarjEKm/e9y3BBWHajqbIaDx5/7hMBiRLoN
UxOG/hhXSOZJh+nDOA4/JongojEVdzrUP/nwF64/Te4IwxcgAqPjSxIXJyDT9Ob9
6d7hA1fK942oGEGgzY+mEU70TYJrYqb4Jjby8axvIZuab5GTxaJhAoGBAPApGNaA
Gf3q59dsURCV1g7cELT6fGaof9nxPhbT/KF/x38DozeBfYHl3PJ0OD6VkrrYWBMZ
9N59dCP+UgJ58cZ9D1upAmqo27bpGbCw8IkmATo2eHgkBR/mtX5m73SiWooWlpO9
+tdP7Zn0GbXZAO4PN5eC8QigUjwqSwcNUNrpAoGBAK9CMF4Og0DZ1lOyCQkaEtYG
S/ksBrR1P7CSb9YO1uYyJ6i8RnNCs5cW/4d3sI3kof5KN0OcF/7Uy+HKKVreXozA
gkn9x34NcGXDDTqtj7efPTvsRVNC96uYL9RDzwSW3n9lQJxJhjQMNSer+6WWRqmz
9vdi8F2/dH32XcF0jpgBAoGAQ4h6+I6LQJDW4wgNf6lyyTju5cVuR/vn/+RLvmWc
K9nfwoLGWexq26VEzVULH+Y1nZ8KnUx2RD5o81onu5SI/XTbZb4P9OhI6JWB6OLI
sPhj7fe1RqtyWXcp4EKX4WdqKFyTuTX6HKPYP6uZsz4zeb4DtvJWT0Ot/Ec0U+ZV
r0kCgYAPIRVuO/UjE8/BNH2UtLUL/wqOQG9ue0N3ozjvbgjSVl6SqSCSerSnivgd
CxYnXR6t9SpBBGOMqNtYH20uhaZ/17jBuA2ARQkxmc/SlWjAdlHuc3aZPzLWK32q
Fjg1duDrPKul1ANybep9ttsHpqdlKmqbVUijA7gIXBWLGnvUag==
-----END RSA PRIVATE KEY-----"""

# High-bias categories to scan
TARGET_CATEGORIES = [
    'entertainment',
    'culture', 
    'crypto',
    'social_media',
    'television',
    'music',
    'streaming',
    'awards',
]

# Series tickers for entertainment/culture (will discover more)
KNOWN_SERIES = [
    'KXOSCARPIC',   # Oscars - Best Picture
    'KXOSCARACTOR', # Oscars - Best Actor
    'KXOSCARDIR',   # Oscars - Best Director
    'KXGRAMMYS',    # Grammys
    'KXEMMYS',      # Emmys
    'KXSURVIVOR',   # Survivor
    'KXBACHELOR',   # The Bachelor
    'KXSNL',        # SNL ratings
    'KXSPOTIFY',    # Spotify charts
    'KXNETFLIX',    # Netflix viewership
    'KXTWITTER',    # Twitter/X metrics
    'KXTIKTOK',     # TikTok
]


def categorize_market(title: str, series: str) -> str:
    """Determine category from title/series"""
    title_lower = title.lower()
    series_lower = series.lower() if series else ''
    
    if any(x in title_lower or x in series_lower for x in ['oscar', 'grammy', 'emmy', 'golden globe', 'award']):
        return 'entertainment'
    if any(x in title_lower for x in ['survivor', 'bachelor', 'love island', 'big brother']):
        return 'entertainment'
    if any(x in title_lower for x in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'doge']):
        return 'crypto'
    if any(x in title_lower for x in ['twitter', 'tiktok', 'instagram', 'youtube', 'spotify']):
        return 'social_media'
    if any(x in title_lower for x in ['netflix', 'hbo', 'disney+', 'streaming', 'viewership']):
        return 'entertainment'
    if any(x in title_lower for x in ['snl', 'ratings', 'viewers']):
        return 'entertainment'
    if any(x in title_lower for x in ['album', 'song', 'billboard', 'chart']):
        return 'entertainment'
    if any(x in title_lower for x in ['cpi', 'gdp', 'inflation', 'fed', 'rate']):
        return 'economics'
    
    return 'other'


def scan_entertainment_markets(client: KalshiClient) -> list:
    """Scan all entertainment/culture markets"""
    opportunities = []
    
    print("Scanning entertainment/culture markets...")
    
    # Method 1: Scan known series
    for series in KNOWN_SERIES:
        try:
            events_data = client.get_events(series_ticker=series, limit=10)
            events = events_data.get('events', [])
            
            for event in events:
                event_ticker = event.get('event_ticker')
                markets_data = client.get_markets(event_ticker=event_ticker, limit=50)
                
                for m in markets_data.get('markets', []):
                    if m.get('status') != 'active':
                        continue
                    
                    ticker = m.get('ticker')
                    title = m.get('title', '')
                    yes_bid = float(m.get('yes_bid_dollars', '0') or 0) * 100
                    yes_ask = float(m.get('yes_ask_dollars', '0') or 0) * 100
                    volume = float(m.get('volume_fp', '0') or 0)
                    
                    if yes_bid == 0 or yes_ask == 0:
                        continue
                    
                    category = categorize_market(title, series)
                    
                    market_data = {
                        'ticker': ticker,
                        'title': title,
                        'series': series,
                        'event': event_ticker,
                        'yes_bid': yes_bid,
                        'yes_ask': yes_ask,
                        'category': category,
                        'volume': volume,
                    }
                    
                    # Score the opportunity
                    score_data = score_opportunity(market_data)
                    market_data['score'] = score_data['score']
                    market_data['bias_data'] = score_data['bias_data']
                    market_data['reasons'] = score_data['reasons']
                    market_data['recommendation'] = score_data['recommendation']
                    
                    opportunities.append(market_data)
                    
        except Exception as e:
            print(f"  Error scanning {series}: {e}")
    
    # Method 2: Broad market scan with category filter
    try:
        # Get all active markets
        all_markets = client.get_markets(limit=200, status='active')
        
        for m in all_markets.get('markets', []):
            ticker = m.get('ticker')
            
            # Skip if already captured
            if any(o['ticker'] == ticker for o in opportunities):
                continue
            
            title = m.get('title', '')
            category = categorize_market(title, m.get('series_ticker', ''))
            
            # Only process high-bias categories
            if category not in ['entertainment', 'crypto', 'social_media']:
                continue
            
            yes_bid = float(m.get('yes_bid_dollars', '0') or 0) * 100
            yes_ask = float(m.get('yes_ask_dollars', '0') or 0) * 100
            volume = float(m.get('volume_fp', '0') or 0)
            
            if yes_bid == 0 or yes_ask == 0:
                continue
            
            market_data = {
                'ticker': ticker,
                'title': title,
                'series': m.get('series_ticker', ''),
                'event': m.get('event_ticker', ''),
                'yes_bid': yes_bid,
                'yes_ask': yes_ask,
                'category': category,
                'volume': volume,
            }
            
            score_data = score_opportunity(market_data)
            market_data['score'] = score_data['score']
            market_data['bias_data'] = score_data['bias_data']
            market_data['reasons'] = score_data['reasons']
            market_data['recommendation'] = score_data['recommendation']
            
            opportunities.append(market_data)
            
    except Exception as e:
        print(f"  Error in broad scan: {e}")
    
    return opportunities


def format_report(opportunities: list) -> str:
    """Format opportunities report"""
    lines = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    lines.append(f"=== ENTERTAINMENT/CULTURE SCAN ===")
    lines.append(f"Timestamp: {timestamp}")
    lines.append(f"Markets found: {len(opportunities)}")
    lines.append("")
    
    # Sort by score
    sorted_opps = sorted(opportunities, key=lambda x: x['score'], reverse=True)
    
    # Top opportunities
    lines.append("🎯 TOP OPPORTUNITIES (by bias score):")
    lines.append("-" * 60)
    
    for opp in sorted_opps[:15]:
        mid = (opp['yes_bid'] + opp['yes_ask']) / 2
        spread = opp['yes_ask'] - opp['yes_bid']
        bias = opp['bias_data']
        
        lines.append(f"\n📊 {opp['title'][:50]}")
        lines.append(f"   Ticker: {opp['ticker']}")
        lines.append(f"   Price: {opp['yes_bid']:.0f}¢ / {opp['yes_ask']:.0f}¢ (spread: {spread:.0f}¢)")
        lines.append(f"   Mid: {mid:.0f}% | Bias-adjusted: {bias['actual']:.1f}%")
        lines.append(f"   Bias: {bias['bias']:+.1f} points | Category: {opp['category']}")
        lines.append(f"   Volume: {opp['volume']:,.0f} | Score: {opp['score']:.0f}")
        lines.append(f"   Rec: {opp['recommendation']} | {', '.join(opp['reasons'][:3])}")
    
    # Summary by category
    lines.append("\n" + "=" * 60)
    lines.append("CATEGORY BREAKDOWN:")
    
    by_category = {}
    for opp in opportunities:
        cat = opp['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(opp)
    
    for cat, opps in sorted(by_category.items()):
        avg_score = sum(o['score'] for o in opps) / len(opps) if opps else 0
        lines.append(f"  {cat}: {len(opps)} markets, avg score: {avg_score:.1f}")
    
    return '\n'.join(lines)


def run_scan():
    """Main scan function"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
        
        opportunities = scan_entertainment_markets(client)
        
        # Save raw data
        output_file = OUTPUT_DIR / 'entertainment_scan.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'count': len(opportunities),
                'opportunities': opportunities,
            }, f, indent=2)
        
        # Generate report
        report = format_report(opportunities)
        print(report)
        
        return {
            'success': True,
            'count': len(opportunities),
            'top_score': max((o['score'] for o in opportunities), default=0),
            'opportunities': opportunities,
        }
        
    except Exception as e:
        print(f"🔴 SCAN FAILED: {e}")
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    result = run_scan()
    if not result['success']:
        sys.exit(1)
