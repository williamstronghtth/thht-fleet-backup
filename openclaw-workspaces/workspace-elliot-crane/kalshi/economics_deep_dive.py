#!/usr/bin/env python3
"""
Economics Deep Dive
Pull all active economics markets and prepare for consensus comparison
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


def get_all_markets_for_series(series_ticker):
    """Get all events and markets for a series"""
    results = []
    try:
        events_data = client.get_events(series_ticker=series_ticker, limit=50)
        events = events_data.get('events', [])
        
        for event in events:
            event_ticker = event.get('event_ticker')
            markets_data = client.get_markets(event_ticker=event_ticker, limit=200)
            markets = markets_data.get('markets', [])
            
            for m in markets:
                if m.get('status') == 'active':
                    yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
                    yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
                    volume = float(m.get('volume_fp', '0') or 0)
                    hours = hours_until(m.get('expiration_time'))
                    
                    results.append({
                        'series': series_ticker,
                        'event': event_ticker,
                        'event_title': event.get('title', ''),
                        'event_subtitle': event.get('sub_title', ''),
                        'ticker': m.get('ticker'),
                        'title': m.get('title', ''),
                        'yes_bid': yes_bid,
                        'yes_ask': yes_ask,
                        'spread': (yes_ask - yes_bid) * 100 if yes_bid > 0 and yes_ask > 0 else None,
                        'mid': (yes_bid + yes_ask) / 2 if yes_bid > 0 and yes_ask > 0 else None,
                        'volume': volume,
                        'hours_to_exp': hours,
                        'expiration': m.get('expiration_time'),
                        'has_quotes': yes_bid > 0 or yes_ask > 0,
                    })
    except Exception as e:
        print(f"Error fetching {series_ticker}: {e}")
    
    return results


# Fetch all economics series
ECON_SERIES = ['KXCPI', 'KXGDP', 'KXJOBLESS', 'KXINTR', 'KXPCE', 'KXUNEMPLOYMENT', 'KXNFP', 'KXINITIAL']

print("=" * 80)
print("ECONOMICS MARKETS DEEP DIVE")
print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("=" * 80)

all_econ_markets = []

for series in ECON_SERIES:
    markets = get_all_markets_for_series(series)
    if markets:
        all_econ_markets.extend(markets)
        print(f"\n✅ {series}: {len(markets)} markets found")
    else:
        print(f"\n❌ {series}: No active markets")

# Group by event
by_event = defaultdict(list)
for m in all_econ_markets:
    by_event[m['event']].append(m)

# Print detailed breakdown
print("\n\n" + "=" * 80)
print("DETAILED MARKET BREAKDOWN")
print("=" * 80)

for event_ticker in sorted(by_event.keys()):
    markets = by_event[event_ticker]
    if not markets:
        continue
    
    event_title = markets[0]['event_title']
    series = markets[0]['series']
    
    print(f"\n{'='*70}")
    print(f"📊 {event_title}")
    print(f"   Series: {series} | Event: {event_ticker}")
    print(f"   Markets: {len(markets)}")
    print('='*70)
    
    # Sort by strike (extract from title)
    sorted_markets = sorted(markets, key=lambda x: x['title'])
    
    print(f"\n{'Strike':<50} {'Bid':>6} {'Ask':>6} {'Mid':>7} {'Spread':>7} {'Volume':>10}")
    print("-" * 95)
    
    for m in sorted_markets:
        title = m['title'][:50]
        bid = m['yes_bid']
        ask = m['yes_ask']
        mid = m['mid']
        spread = m['spread']
        vol = m['volume']
        
        bid_str = f"{bid*100:.0f}¢" if bid > 0 else "-"
        ask_str = f"{ask*100:.0f}¢" if ask > 0 else "-"
        mid_str = f"{mid*100:.1f}%" if mid else "-"
        spread_str = f"{spread:.1f}¢" if spread else "-"
        
        print(f"{title:<50} {bid_str:>6} {ask_str:>6} {mid_str:>7} {spread_str:>7} {vol:>10.0f}")

# Save to JSON for further analysis
output = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'markets': all_econ_markets,
    'by_event': {k: v for k, v in by_event.items()},
}

with open('/root/.openclaw/workspace-elliot-crane/kalshi/economics_markets.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n\nData saved to: kalshi/economics_markets.json")
print(f"Total economics markets: {len(all_econ_markets)}")
