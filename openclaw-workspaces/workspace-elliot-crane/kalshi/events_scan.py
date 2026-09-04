#!/usr/bin/env python3
"""
Events-based Market Scan
Find real tradeable markets by scanning events first
"""

import json
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


def fetch_all_events(client):
    """Fetch all events"""
    all_events = []
    cursor = None
    
    print("Fetching events", end="", flush=True)
    while True:
        data = client.get_events(limit=200, cursor=cursor)
        events = data.get('events', [])
        all_events.extend(events)
        print(".", end="", flush=True)
        cursor = data.get('cursor')
        if not cursor or len(all_events) > 1000:
            break
    print(f" {len(all_events)} total")
    return all_events


def hours_until(time_str):
    """Calculate hours until expiration"""
    if not time_str:
        return None
    try:
        time_str = time_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(time_str)
        now = datetime.now(timezone.utc)
        delta = dt - now
        return delta.total_seconds() / 3600
    except:
        return None


def categorize_event(e):
    """Categorize event"""
    ticker = e.get('event_ticker', '').upper()
    title = e.get('title', '').upper()
    category = e.get('category', '').upper()
    series = e.get('series_ticker', '').upper()
    
    # Use Kalshi's category if available
    if category:
        if 'ECON' in category:
            return f"Economics: {category}"
        elif 'POLITIC' in category:
            return f"Politics: {category}"
        elif 'SPORT' in category:
            return f"Sports: {category}"
        elif 'WEATHER' in category:
            return f"Weather: {category}"
        return category
    
    # Fall back to pattern matching
    if any(x in ticker or x in series for x in ['CPI', 'INFLATION']):
        return 'Econ: CPI/Inflation'
    elif any(x in ticker or x in series for x in ['FED', 'FOMC', 'INTR']):
        return 'Econ: Fed/Rates'
    elif any(x in ticker or x in series for x in ['GDP']):
        return 'Econ: GDP'
    elif any(x in ticker or x in series for x in ['JOBS', 'EMPLOY', 'NFP', 'JOBLESS', 'INITIAL']):
        return 'Econ: Employment'
    elif any(x in ticker or x in series for x in ['HIGHTEMP', 'LOWTEMP', 'RAIN', 'SNOW', 'PRECIP']):
        return 'Weather'
    elif any(x in ticker or x in series for x in ['PRES', 'TRUMP', 'BIDEN']):
        return 'Politics: Presidential'
    elif any(x in ticker or x in series for x in ['SENATE', 'HOUSE', 'CONGRESS']):
        return 'Politics: Congress'
    elif any(x in ticker or x in series for x in ['NBA']):
        return 'Sports: NBA'
    elif any(x in ticker or x in series for x in ['NFL']):
        return 'Sports: NFL'
    elif any(x in ticker or x in series for x in ['MLB']):
        return 'Sports: MLB'
    elif any(x in ticker or x in series for x in ['NCAA', 'NCAAM', 'NCAAW', 'GAME']):
        return 'Sports: NCAA'
    elif any(x in ticker or x in series for x in ['OSCAR']):
        return 'Entertainment: Oscars'
    else:
        return 'Other'


def main():
    client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
    
    # Fetch events
    events = fetch_all_events(client)
    
    print("\n" + "=" * 80)
    print("KALSHI EVENTS ANALYSIS")
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 80)
    
    # Categorize and analyze
    by_category = defaultdict(list)
    
    for e in events:
        status = e.get('status', 'unknown')
        if status not in ['active', 'open']:
            continue
        
        cat = categorize_event(e)
        hours = hours_until(e.get('expected_expiration_time') or e.get('close_time'))
        
        by_category[cat].append({
            'ticker': e.get('event_ticker'),
            'title': e.get('title', '')[:60],
            'subtitle': e.get('sub_title', ''),
            'category': e.get('category'),
            'series': e.get('series_ticker'),
            'hours_to_exp': hours,
            'mutually_exclusive': e.get('mutually_exclusive', False),
            'status': status,
        })
    
    # Print by category
    print("\n" + "-" * 60)
    print("EVENTS BY CATEGORY (Active Only)")
    print("-" * 60)
    
    interesting_events = []
    
    for cat in sorted(by_category.keys()):
        events_list = by_category[cat]
        print(f"\n📁 {cat} ({len(events_list)} events)")
        
        # Sort by expiration
        sorted_events = sorted(events_list, key=lambda x: x['hours_to_exp'] or 9999)[:10]
        
        for e in sorted_events:
            hours = e['hours_to_exp']
            hours_str = f"{hours:>6.0f}h" if hours and hours < 10000 else "    N/A"
            title = e['title'][:50]
            ticker = e['ticker'][:25]
            print(f"   {hours_str} | {ticker:<25} | {title}")
            
            # Track interesting non-sports events
            if 'Sports' not in cat and 'NCAA' not in cat:
                interesting_events.append(e)
    
    # Print interesting events with more detail
    print("\n" + "=" * 80)
    print("INTERESTING NON-SPORTS EVENTS")
    print("=" * 80)
    
    for e in sorted(interesting_events, key=lambda x: x['hours_to_exp'] or 9999)[:20]:
        print(f"\n{e['ticker']}")
        print(f"   Title: {e['title']}")
        if e['subtitle']:
            print(f"   Subtitle: {e['subtitle'][:80]}")
        print(f"   Category: {e['category'] or 'N/A'}")
        print(f"   Series: {e['series']}")
        print(f"   Hours to exp: {e['hours_to_exp']:.0f}" if e['hours_to_exp'] else "   Hours to exp: N/A")
    
    # Now fetch markets for interesting events
    print("\n" + "=" * 80)
    print("FETCHING MARKET DATA FOR INTERESTING EVENTS")
    print("=" * 80)
    
    for e in interesting_events[:15]:
        event_ticker = e['ticker']
        try:
            markets_data = client.get_markets(event_ticker=event_ticker, limit=50)
            markets = markets_data.get('markets', [])
            
            if not markets:
                continue
            
            print(f"\n📊 {e['title'][:50]}")
            print(f"   Event: {event_ticker}")
            
            for m in markets[:5]:
                ticker = m.get('ticker', '')
                yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
                yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
                volume = float(m.get('volume_fp', '0') or 0)
                title = m.get('title', '')[:40]
                
                if yes_bid > 0 and yes_ask > 0:
                    mid = (yes_bid + yes_ask) / 2
                    spread = (yes_ask - yes_bid) * 100
                    print(f"   → {title}")
                    print(f"      Bid: {yes_bid*100:.1f}¢ | Ask: {yes_ask*100:.1f}¢ | Spread: {spread:.1f}¢ | Vol: {volume:.0f}")
                elif volume > 0:
                    print(f"   → {title} (Vol: {volume:.0f}, no quotes)")
                    
        except Exception as ex:
            print(f"   Error fetching {event_ticker}: {ex}")


if __name__ == "__main__":
    main()
