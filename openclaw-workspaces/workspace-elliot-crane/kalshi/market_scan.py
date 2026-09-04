#!/usr/bin/env python3
"""
Quick Market Scanner
Scans Kalshi markets for interesting opportunities
"""

import os
import sys
from datetime import datetime

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


def categorize_market(m):
    """Categorize market by ticker/title"""
    ticker = m.get('ticker', '').upper()
    title = m.get('title', '').upper()
    
    if any(x in ticker or x in title for x in ['CPI', 'INFLATION', 'FED', 'FOMC', 'RATE', 'GDP', 'JOBS', 'UNEMPLOYMENT', 'NFP']):
        return 'Economics'
    elif any(x in ticker or x in title for x in ['WEATHER', 'TEMP', 'RAIN', 'SNOW', 'HURRICANE', 'STORM']):
        return 'Weather'
    elif any(x in ticker or x in title for x in ['PRES', 'SENATE', 'HOUSE', 'ELECTION', 'TRUMP', 'BIDEN', 'GOVERNOR', 'CONGRESS']):
        return 'Politics'
    elif any(x in ticker or x in title for x in ['NBA', 'NFL', 'MLB', 'NHL', 'NCAA', 'GAME', 'SPORTS', 'MATCH']):
        return 'Sports'
    elif any(x in ticker or x in title for x in ['OSCAR', 'EMMY', 'GRAMMY', 'MOVIE', 'AWARD']):
        return 'Entertainment'
    else:
        return 'Other'


def scan_markets():
    """Scan for interesting markets"""
    client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
    
    print("=" * 70)
    print("KALSHI MARKET SCAN")
    print(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    
    # Get account status
    balance = client.get_balance()
    print(f"\n💰 ACCOUNT STATUS")
    print(f"   Cash Balance:    ${balance['balance']/100:.2f}")
    print(f"   Portfolio Value: ${balance['portfolio_value']/100:.2f}")
    print(f"   Total:           ${(balance['balance'] + balance['portfolio_value'])/100:.2f}")
    
    # Get positions
    positions = client.get_positions()
    if positions.get('market_positions'):
        print(f"\n📊 CURRENT POSITIONS")
        for pos in positions['market_positions']:
            qty = float(pos.get('position_fp', 0))
            cost = float(pos.get('total_traded_dollars', '0').replace('$', ''))
            ticker = pos.get('ticker', 'unknown')
            print(f"   {ticker}: {qty:.0f} contracts, ${cost:.2f} cost")
    
    # Get markets - fetch more
    print(f"\n🔍 SCANNING MARKETS...")
    
    all_markets = []
    cursor = None
    
    # Fetch up to 500 markets
    for _ in range(5):
        markets_data = client.get_markets(limit=100, cursor=cursor)
        markets = markets_data.get('markets', [])
        all_markets.extend(markets)
        cursor = markets_data.get('cursor')
        if not cursor:
            break
    
    # Filter active markets with liquidity
    active_markets = [m for m in all_markets if m.get('status') == 'active']
    
    # Markets with actual bid/ask
    liquid_markets = [m for m in active_markets 
                      if float(m.get('yes_bid_dollars', '0')) > 0 
                      or float(m.get('volume_fp', '0')) > 0]
    
    # Categorize
    categories = {}
    for m in liquid_markets:
        cat = categorize_market(m)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)
    
    # Print by category
    for cat in ['Economics', 'Politics', 'Weather', 'Entertainment', 'Sports', 'Other']:
        cat_markets = categories.get(cat, [])
        if cat_markets:
            # Sort by volume
            sorted_markets = sorted(cat_markets, 
                                   key=lambda x: float(x.get('volume_fp', '0')), 
                                   reverse=True)[:8]
            
            print(f"\n📁 {cat.upper()} ({len(cat_markets)} markets)")
            
            for m in sorted_markets:
                ticker = m.get('ticker', '')[:35]
                yes_bid = float(m.get('yes_bid_dollars', '0'))
                yes_ask = float(m.get('yes_ask_dollars', '0'))
                volume = float(m.get('volume_fp', '0'))
                title = m.get('title', '')[:40]
                
                # Midpoint as implied prob
                if yes_bid > 0 and yes_ask > 0:
                    mid = (yes_bid + yes_ask) / 2
                    prob_str = f"{mid*100:>5.1f}%"
                elif yes_bid > 0:
                    prob_str = f"{yes_bid*100:>5.1f}%"
                else:
                    prob_str = "  N/A"
                
                vol_str = f"{volume:>8.0f}" if volume > 0 else "      --"
                print(f"   {prob_str} | Vol:{vol_str} | {title}")
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"SUMMARY")
    print(f"   Total markets fetched: {len(all_markets)}")
    print(f"   Active markets: {len(active_markets)}")
    print(f"   With liquidity: {len(liquid_markets)}")
    print("=" * 70)


if __name__ == "__main__":
    scan_markets()
