#!/usr/bin/env python3
"""
Full Market Search - Exhaustively scan all markets
"""

import json
import sys
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient

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

client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)


def hours_until(time_str):
    if not time_str:
        return None
    try:
        time_str = time_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(time_str)
        now = datetime.now(timezone.utc)
        return (dt - now).total_seconds() / 3600
    except:
        return None


# Keywords to look for
ECONOMICS_KEYWORDS = ['cpi', 'inflation', 'fed', 'fomc', 'rate', 'gdp', 'jobs', 'payroll', 
                      'unemployment', 'jobless', 'nonfarm', 'pce', 'treasury', 'yield']
WEATHER_KEYWORDS = ['temp', 'temperature', 'rain', 'snow', 'precip', 'hurricane', 'storm',
                    'weather', 'high of', 'low of', 'inches']
POLITICS_KEYWORDS = ['trump', 'biden', 'president', 'senate', 'house', 'congress', 'election',
                     'governor', 'vote', 'poll', 'republican', 'democrat', 'cabinet']
ENTERTAINMENT_KEYWORDS = ['oscar', 'emmy', 'grammy', 'movie', 'film', 'boxoffice', 'award',
                          'netflix', 'disney', 'streaming']


def categorize(m):
    """Simple keyword categorization"""
    text = (m.get('title', '') + ' ' + m.get('ticker', '') + ' ' + 
            m.get('event_ticker', '')).lower()
    
    for kw in ECONOMICS_KEYWORDS:
        if kw in text:
            return 'Economics'
    for kw in WEATHER_KEYWORDS:
        if kw in text:
            return 'Weather'
    for kw in POLITICS_KEYWORDS:
        if kw in text:
            return 'Politics'
    for kw in ENTERTAINMENT_KEYWORDS:
        if kw in text:
            return 'Entertainment'
    
    # Check for sports (negative - to exclude)
    sports_kw = ['nba', 'nfl', 'mlb', 'nhl', 'ncaa', 'game', 'match', 'team', 
                 'player', 'score', 'win', 'spread', 'over/under']
    for kw in sports_kw:
        if kw in text:
            return 'Sports'
    
    return 'Other'


# Fetch ALL markets
print("Fetching all markets...")
all_markets = []
cursor = None

while len(all_markets) < 5000:
    data = client.get_markets(limit=200, cursor=cursor)
    markets = data.get('markets', [])
    all_markets.extend(markets)
    print(f"   Fetched {len(all_markets)} markets...", end='\r')
    cursor = data.get('cursor')
    if not cursor:
        break

print(f"\nTotal markets fetched: {len(all_markets)}")

# Categorize all
by_category = defaultdict(list)
for m in all_markets:
    if m.get('status') != 'active':
        continue
    cat = categorize(m)
    by_category[cat].append(m)

print("\n" + "=" * 80)
print("MARKET BREAKDOWN BY CATEGORY")
print("=" * 80)

for cat in ['Economics', 'Weather', 'Politics', 'Entertainment', 'Sports', 'Other']:
    markets = by_category[cat]
    print(f"\n{cat}: {len(markets)} markets")

# Now detail non-sports
print("\n" + "=" * 80)
print("NON-SPORTS MARKET DETAILS")
print("=" * 80)

for cat in ['Economics', 'Weather', 'Politics', 'Entertainment']:
    markets = by_category[cat]
    if not markets:
        continue
    
    print(f"\n{'='*40}")
    print(f"📊 {cat.upper()} ({len(markets)} markets)")
    print('='*40)
    
    # Sort by volume
    sorted_markets = sorted(markets, 
                           key=lambda x: float(x.get('volume_fp', '0') or 0), 
                           reverse=True)
    
    for m in sorted_markets[:20]:
        ticker = m.get('ticker', '')
        title = m.get('title', '')[:60]
        event = m.get('event_ticker', '')
        yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
        yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
        volume = float(m.get('volume_fp', '0') or 0)
        hours = hours_until(m.get('expiration_time'))
        
        print(f"\n{ticker[:50]}")
        print(f"   Title: {title}")
        print(f"   Event: {event}")
        
        if yes_bid > 0 and yes_ask > 0:
            mid = (yes_bid + yes_ask) / 2
            spread = (yes_ask - yes_bid) * 100
            print(f"   Yes Bid: {yes_bid*100:.1f}¢ | Yes Ask: {yes_ask*100:.1f}¢ | Spread: {spread:.1f}¢")
            print(f"   Implied Prob: {mid*100:.1f}%")
        else:
            print(f"   No active quotes")
        
        print(f"   Volume: {volume:.0f} contracts")
        if hours:
            if hours < 24:
                print(f"   Expires: {hours:.1f} hours")
            elif hours < 168:
                print(f"   Expires: {hours/24:.1f} days")
            else:
                print(f"   Expires: {hours/24/7:.1f} weeks")

# Print unique event tickers for non-sports
print("\n" + "=" * 80)
print("UNIQUE EVENT TICKERS (Non-Sports)")
print("=" * 80)

event_tickers = set()
for cat in ['Economics', 'Weather', 'Politics', 'Entertainment']:
    for m in by_category[cat]:
        if m.get('event_ticker'):
            event_tickers.add(m.get('event_ticker'))

for ticker in sorted(event_tickers):
    print(f"   {ticker}")
