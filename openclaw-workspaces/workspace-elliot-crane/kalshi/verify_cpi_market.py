#!/usr/bin/env python3
"""
Verify CPI market pricing and order book depth
"""

import json
import sys
from datetime import datetime, timezone

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

print("=" * 70)
print("CPI MARKET VERIFICATION")
print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("=" * 70)

# Get all March CPI markets
markets_data = client.get_markets(event_ticker="KXCPI-26MAR", limit=50)
markets = markets_data.get('markets', [])

print(f"\nFound {len(markets)} March 2026 CPI markets")

# Find the >0.5% market
target_market = None
for m in markets:
    if '0.5%' in m.get('title', '') and 'more than 0.5' in m.get('title', '').lower():
        target_market = m
        break

if target_market:
    ticker = target_market['ticker']
    print(f"\n--- TARGET MARKET: {ticker} ---")
    print(f"Title: {target_market['title']}")
    
    yes_bid = float(target_market.get('yes_bid_dollars', '0') or 0)
    yes_ask = float(target_market.get('yes_ask_dollars', '0') or 0)
    volume = float(target_market.get('volume_fp', '0') or 0)
    open_interest = float(target_market.get('open_interest_fp', '0') or 0)
    
    print(f"\nCURRENT PRICING:")
    print(f"   YES Bid: {yes_bid*100:.0f}¢")
    print(f"   YES Ask: {yes_ask*100:.0f}¢")
    print(f"   Midpoint: {(yes_bid+yes_ask)/2*100:.1f}¢")
    print(f"   Spread: {(yes_ask-yes_bid)*100:.1f}¢")
    print(f"   Volume: {volume:.0f} contracts")
    print(f"   Open Interest: {open_interest:.0f}")
    
    # Get order book
    print(f"\n--- ORDER BOOK ---")
    try:
        orderbook = client.get_orderbook(ticker, depth=20)
        ob = orderbook.get('orderbook', {})
        
        yes_bids = ob.get('yes', [])
        no_bids = ob.get('no', [])
        
        print(f"\nYES side (bids to buy YES):")
        total_yes_bid_size = 0
        for level in yes_bids[:10]:
            price = level[0]  # Price in cents
            size = level[1]   # Size
            total_yes_bid_size += size
            print(f"   {price}¢: {size} contracts")
        
        print(f"\nNO side (bids to buy NO = offers to sell YES):")
        total_no_bid_size = 0
        for level in no_bids[:10]:
            price = level[0]
            size = level[1]
            total_no_bid_size += size
            # NO bid at X¢ = YES offer at (100-X)¢
            yes_offer_price = 100 - price
            print(f"   {yes_offer_price}¢ (NO bid {price}¢): {size} contracts")
        
        print(f"\n--- LIQUIDITY SUMMARY ---")
        print(f"Total YES bid depth (top 10 levels): {total_yes_bid_size} contracts")
        print(f"Total NO bid depth (top 10 levels): {total_no_bid_size} contracts")
        
        # Can we fill 12-13 contracts?
        print(f"\n--- CAN WE FILL 13 CONTRACTS? ---")
        if total_no_bid_size >= 13:
            print(f"✅ YES - {total_no_bid_size} contracts available on NO bid side")
        else:
            print(f"⚠️  MAYBE - Only {total_no_bid_size} contracts immediately available")
            
    except Exception as e:
        print(f"Error fetching orderbook: {e}")
    
    # Get all strikes for context
    print(f"\n--- ALL MARCH 2026 CPI STRIKES ---")
    print(f"{'Strike':<45} {'Bid':>6} {'Ask':>6} {'Mid':>7} {'Volume':>10}")
    print("-" * 80)
    
    for m in sorted(markets, key=lambda x: x.get('title', '')):
        title = m.get('title', '')[:45]
        yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
        yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
        mid = (yes_bid + yes_ask) / 2 if yes_bid > 0 and yes_ask > 0 else 0
        vol = float(m.get('volume_fp', '0') or 0)
        
        bid_str = f"{yes_bid*100:.0f}¢" if yes_bid > 0 else "-"
        ask_str = f"{yes_ask*100:.0f}¢" if yes_ask > 0 else "-"
        mid_str = f"{mid*100:.1f}%" if mid > 0 else "-"
        
        print(f"{title:<45} {bid_str:>6} {ask_str:>6} {mid_str:>7} {vol:>10.0f}")

else:
    print("Could not find the >0.5% market!")
    print("Available markets:")
    for m in markets:
        print(f"   {m.get('ticker')}: {m.get('title')}")
