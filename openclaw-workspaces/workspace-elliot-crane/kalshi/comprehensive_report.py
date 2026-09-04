#!/usr/bin/env python3
"""
Comprehensive Market Report for Chris
Phase 2: Market Scan, Watchlist, and Risk Analysis
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


def get_all_markets_for_series(series_ticker, limit=100):
    """Get all events and markets for a series"""
    results = []
    try:
        events_data = client.get_events(series_ticker=series_ticker, limit=50)
        events = events_data.get('events', [])
        
        for event in events:
            event_ticker = event.get('event_ticker')
            markets_data = client.get_markets(event_ticker=event_ticker, limit=limit)
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
                        'ticker': m.get('ticker'),
                        'title': m.get('title', ''),
                        'yes_bid': yes_bid,
                        'yes_ask': yes_ask,
                        'spread': (yes_ask - yes_bid) * 100 if yes_bid > 0 and yes_ask > 0 else None,
                        'mid': (yes_bid + yes_ask) / 2 if yes_bid > 0 and yes_ask > 0 else None,
                        'volume': volume,
                        'hours_to_exp': hours,
                        'has_quotes': yes_bid > 0 or yes_ask > 0,
                    })
    except Exception as e:
        print(f"Error fetching {series_ticker}: {e}")
    
    return results


# Fetch all tradeable series
print("=" * 80)
print("KALSHI MARKET INTELLIGENCE REPORT")
print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("=" * 80)

SERIES_TO_SCAN = {
    'Economics': ['KXCPI', 'KXGDP', 'KXJOBLESS', 'KXINTR', 'KXPCE', 'KXUNEMPLOYMENT'],
    'Politics': ['KXPRES', 'KXSENATE', 'KXHOUSE', 'KXGOV', 'KXTRUMP', 'KXBIDEN'],
    'Entertainment': ['KXOSCARPIC', 'KXOSCARACT', 'KXOSCARACTRS', 'KXOSCARDIR'],
    'Weather': ['KXHIGHTEMP', 'KXLOWTEMP', 'KXRAIN', 'KXSNOW'],
    'Crypto': ['KXBTC', 'KXETH'],
}

all_markets = []

for category, series_list in SERIES_TO_SCAN.items():
    print(f"\n{'='*60}")
    print(f"📊 {category.upper()}")
    print('='*60)
    
    for series in series_list:
        markets = get_all_markets_for_series(series)
        if markets:
            # Filter to those with quotes
            with_quotes = [m for m in markets if m['has_quotes']]
            all_markets.extend(markets)
            
            print(f"\n  {series}: {len(with_quotes)} liquid / {len(markets)} total markets")
            
            # Show top markets by volume
            top = sorted(with_quotes, key=lambda x: x['volume'], reverse=True)[:5]
            for m in top:
                spread = m['spread']
                mid = m['mid']
                vol = m['volume']
                hrs = m['hours_to_exp']
                title = m['title'][:45]
                
                if mid:
                    prob_str = f"{mid*100:>5.1f}%"
                    spread_str = f"{spread:>4.1f}¢" if spread else "N/A"
                else:
                    prob_str = "  N/A"
                    spread_str = "N/A"
                
                hrs_str = f"{hrs:>5.0f}h" if hrs else "  N/A"
                
                print(f"    {prob_str} | Spr:{spread_str:>5} | Vol:{vol:>8.0f} | {hrs_str} | {title}")

# Summary statistics
print("\n\n" + "=" * 80)
print("MARKET LANDSCAPE SUMMARY")
print("=" * 80)

liquid_markets = [m for m in all_markets if m['has_quotes']]
by_category = defaultdict(list)
for m in all_markets:
    cat = None
    for c, series_list in SERIES_TO_SCAN.items():
        if m['series'] in series_list:
            cat = c
            break
    if cat:
        by_category[cat].append(m)

print(f"\n{'Category':<15} {'Total':>8} {'Liquid':>8} {'Avg Spread':>12} {'Total Vol':>12}")
print("-" * 60)

for cat in ['Economics', 'Politics', 'Entertainment', 'Weather', 'Crypto']:
    markets = by_category[cat]
    liquid = [m for m in markets if m['has_quotes']]
    spreads = [m['spread'] for m in liquid if m['spread']]
    avg_spread = sum(spreads) / len(spreads) if spreads else 0
    total_vol = sum(m['volume'] for m in markets)
    print(f"{cat:<15} {len(markets):>8} {len(liquid):>8} {avg_spread:>10.1f}¢ {total_vol:>12.0f}")


# Current position analysis
print("\n\n" + "=" * 80)
print("CURRENT POSITION ANALYSIS")
print("=" * 80)

positions = client.get_positions()
for pos in positions.get('market_positions', []):
    ticker = pos.get('ticker')
    qty = float(pos.get('position_fp', 0))
    cost = float(pos.get('total_traded_dollars', '0').replace('$', ''))
    avg_price = cost / qty if qty > 0 else 0
    
    try:
        market_data = client.get_market(ticker)
        market = market_data.get('market', {})
        title = market.get('title', 'Unknown')
        yes_bid = float(market.get('yes_bid_dollars', '0') or 0)
        yes_ask = float(market.get('yes_ask_dollars', '0') or 0)
        volume = float(market.get('volume_fp', '0') or 0)
        
        print(f"\n🎯 {ticker}")
        print(f"   Market: {title}")
        print(f"   Position: {qty:.0f} YES contracts")
        print(f"   Cost Basis: ${cost:.2f} (avg {avg_price*100:.1f}¢ per contract)")
        
        if yes_bid > 0:
            current_value = qty * yes_bid
            pnl = current_value - cost
            pnl_pct = (pnl / cost * 100) if cost > 0 else 0
            print(f"   Current Bid: {yes_bid*100:.0f}¢ | Ask: {yes_ask*100:.0f}¢")
            print(f"   Mark-to-Market: ${current_value:.2f}")
            print(f"   Unrealized P&L: ${pnl:.2f} ({pnl_pct:+.1f}%)")
            print(f"   Volume: {volume:.0f} contracts")
            
            # Risk assessment
            spread = (yes_ask - yes_bid) * 100
            print(f"\n   📊 RISK ASSESSMENT:")
            print(f"   - Spread: {spread:.1f}¢ ({spread/yes_bid*100:.1f}% of bid)")
            print(f"   - Exit cost: ~${spread * qty / 100:.2f} to sell at bid")
            print(f"   - If NO wins: Lose ${cost:.2f} (100% of position)")
            print(f"   - If YES wins: Gain ${(1 - avg_price) * qty:.2f} (${qty:.2f} payout - ${cost:.2f} cost)")
            
    except Exception as e:
        print(f"\n{ticker}: {qty:.0f} contracts, ${cost:.2f} cost (error getting details: {e})")


# Save full data
output = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'all_markets': all_markets,
    'liquid_count': len(liquid_markets),
}

with open('/root/.openclaw/workspace-elliot-crane/kalshi/intelligence_report.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("\n\nFull data saved to: kalshi/intelligence_report.json")
