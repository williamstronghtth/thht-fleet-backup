#!/usr/bin/env python3
"""
Search for specific market series
"""

import sys
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

# Known Kalshi series for economic/political events
KNOWN_SERIES = [
    # Economics
    'KXINTR',      # Interest rates / Fed funds
    'KXCPI',       # CPI / Inflation
    'KXPCE',       # PCE Inflation  
    'KXGDP',       # GDP
    'KXUNEMPLOYMENT', # Unemployment
    'KXJOBLESS',   # Jobless claims
    'KXINITIAL',   # Initial jobless claims
    'KXNFP',       # Nonfarm payrolls
    
    # Weather
    'KXHIGHTEMP',  # High temperature
    'KXLOWTEMP',   # Low temperature
    'KXRAIN',      # Rainfall
    'KXSNOW',      # Snowfall
    'KXHURRICANE', # Hurricanes
    
    # Politics
    'KXPRES',      # Presidential
    'KXSENATE',    # Senate
    'KXHOUSE',     # House
    'KXGOV',       # Governors
    
    # Entertainment
    'KXOSCARPIC',  # Oscars - Best Picture
    'KXOSCARACT',  # Oscars - Best Actor
    
    # Tech/Crypto
    'KXBTC',       # Bitcoin
    'KXETH',       # Ethereum
]

print("=" * 70)
print("SEARCHING FOR KNOWN SERIES")
print("=" * 70)

found_any = False

for series in KNOWN_SERIES:
    try:
        # Try to get events for this series
        data = client.get_events(series_ticker=series, limit=10)
        events = data.get('events', [])
        
        if events:
            found_any = True
            print(f"\n✅ {series} ({len(events)} events)")
            for e in events[:3]:
                print(f"   - {e.get('title', '')[:60]}")
                
            # Get markets for first event
            first_event = events[0].get('event_ticker')
            if first_event:
                markets = client.get_markets(event_ticker=first_event, limit=10)
                mkts = markets.get('markets', [])
                if mkts:
                    print(f"   Markets for {first_event}:")
                    for m in mkts[:3]:
                        yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
                        yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
                        vol = float(m.get('volume_fp', '0') or 0)
                        title = m.get('title', '')[:40]
                        if yes_bid > 0 or yes_ask > 0:
                            print(f"      {title}: Bid {yes_bid*100:.0f}¢ / Ask {yes_ask*100:.0f}¢ (Vol: {vol:.0f})")
                        else:
                            print(f"      {title}: No quotes (Vol: {vol:.0f})")
    except Exception as e:
        pass  # Series doesn't exist or API error

if not found_any:
    print("\nNo known series found in active events.")
    print("\nLet me check what series DO exist...")
    
    # Get all events and list unique series
    all_series = set()
    cursor = None
    
    print("\nFetching all events to find series...")
    for _ in range(10):
        data = client.get_events(limit=200, cursor=cursor)
        events = data.get('events', [])
        for e in events:
            if e.get('series_ticker'):
                all_series.add(e.get('series_ticker'))
        cursor = data.get('cursor')
        if not cursor:
            break
    
    print(f"\nFound {len(all_series)} unique series:")
    for s in sorted(all_series):
        print(f"   {s}")

# Also check current position for context
print("\n" + "=" * 70)
print("YOUR CURRENT POSITION")
print("=" * 70)

positions = client.get_positions()
for pos in positions.get('market_positions', []):
    ticker = pos.get('ticker')
    qty = float(pos.get('position_fp', 0))
    cost = float(pos.get('total_traded_dollars', '0').replace('$', ''))
    
    # Get market details
    try:
        market = client.get_market(ticker)
        title = market.get('market', {}).get('title', 'Unknown')
        yes_bid = float(market.get('market', {}).get('yes_bid_dollars', '0') or 0)
        yes_ask = float(market.get('market', {}).get('yes_ask_dollars', '0') or 0)
        
        print(f"\n{ticker}")
        print(f"   Title: {title}")
        print(f"   Position: {qty:.0f} contracts")
        print(f"   Cost: ${cost:.2f}")
        if yes_bid > 0 or yes_ask > 0:
            print(f"   Current: Bid {yes_bid*100:.0f}¢ / Ask {yes_ask*100:.0f}¢")
    except:
        print(f"\n{ticker}: {qty:.0f} contracts, ${cost:.2f} cost")
