#!/usr/bin/env python3
"""
Comprehensive Market Scan
Full landscape analysis for Phase 2
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


def categorize_market(m):
    """Categorize market by ticker/title with better granularity"""
    ticker = m.get('ticker', '').upper()
    title = m.get('title', '').upper()
    event = m.get('event_ticker', '').upper()
    
    # Economics
    if any(x in ticker or x in title or x in event for x in ['CPI', 'INFLATION']):
        return 'Econ: Inflation/CPI'
    elif any(x in ticker or x in title or x in event for x in ['FED', 'FOMC', 'RATE']):
        return 'Econ: Fed/Rates'
    elif any(x in ticker or x in title or x in event for x in ['GDP', 'RECESSION']):
        return 'Econ: GDP/Growth'
    elif any(x in ticker or x in title or x in event for x in ['JOBS', 'UNEMPLOYMENT', 'NFP', 'PAYROLL', 'JOBLESS']):
        return 'Econ: Employment'
    
    # Weather
    elif any(x in ticker or x in title or x in event for x in ['WEATHER', 'TEMP', 'RAIN', 'SNOW', 'HURRICANE', 'STORM', 'CLIMATE']):
        return 'Weather'
    
    # Politics
    elif any(x in ticker or x in title or x in event for x in ['PRES', 'TRUMP', 'BIDEN', 'WHITEHOUSE']):
        return 'Politics: Presidential'
    elif any(x in ticker or x in title or x in event for x in ['SENATE', 'HOUSE', 'CONGRESS', 'SPEAKER']):
        return 'Politics: Congress'
    elif any(x in ticker or x in title or x in event for x in ['GOVERNOR', 'STATE', 'LOCAL']):
        return 'Politics: State/Local'
    elif any(x in ticker or x in title or x in event for x in ['ELECTION', 'POLL', 'VOTE', 'BALLOT']):
        return 'Politics: Elections'
    
    # Sports
    elif any(x in ticker or x in event for x in ['NBA', 'BASKETBALL']):
        return 'Sports: NBA'
    elif any(x in ticker or x in event for x in ['NFL', 'FOOTBALL', 'SUPERBOWL']):
        return 'Sports: NFL'
    elif any(x in ticker or x in event for x in ['MLB', 'BASEBALL']):
        return 'Sports: MLB'
    elif any(x in ticker or x in event for x in ['NHL', 'HOCKEY']):
        return 'Sports: NHL'
    elif any(x in ticker or x in event for x in ['NCAA', 'COLLEGE', 'MARCH', 'NCAAM', 'NCAAW']):
        return 'Sports: NCAA'
    elif any(x in ticker or x in event for x in ['TENNIS', 'ATP', 'WTA']):
        return 'Sports: Tennis'
    elif any(x in ticker or x in event for x in ['GOLF', 'PGA']):
        return 'Sports: Golf'
    elif any(x in ticker or x in event for x in ['SOCCER', 'MLS', 'UEFA', 'FIFA']):
        return 'Sports: Soccer'
    elif any(x in ticker or x in event for x in ['GAME', 'SPORTS', 'MATCH', 'MVE']):
        return 'Sports: Other'
    
    # Entertainment
    elif any(x in ticker or x in title or x in event for x in ['OSCAR', 'ACADEMY']):
        return 'Entertainment: Oscars'
    elif any(x in ticker or x in title or x in event for x in ['EMMY', 'GRAMMY', 'GOLDEN', 'AWARD']):
        return 'Entertainment: Awards'
    elif any(x in ticker or x in title or x in event for x in ['MOVIE', 'BOXOFFICE', 'FILM']):
        return 'Entertainment: Box Office'
    elif any(x in ticker or x in title or x in event for x in ['TV', 'STREAMING', 'NETFLIX', 'SERIES']):
        return 'Entertainment: TV/Streaming'
    
    # Tech/Crypto
    elif any(x in ticker or x in title or x in event for x in ['BITCOIN', 'BTC', 'CRYPTO', 'ETH']):
        return 'Crypto'
    elif any(x in ticker or x in title or x in event for x in ['TECH', 'AI', 'APPLE', 'GOOGLE', 'META', 'TESLA']):
        return 'Tech'
    
    # Other
    else:
        return 'Other'


def parse_time(time_str):
    """Parse ISO timestamp"""
    if not time_str:
        return None
    try:
        # Handle various formats
        time_str = time_str.replace('Z', '+00:00')
        return datetime.fromisoformat(time_str)
    except:
        return None


def hours_until(time_str):
    """Calculate hours until expiration"""
    dt = parse_time(time_str)
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    delta = dt - now
    return delta.total_seconds() / 3600


def get_spread_cents(m):
    """Calculate spread in cents"""
    yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
    yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
    if yes_bid > 0 and yes_ask > 0:
        return (yes_ask - yes_bid) * 100
    return None


def fetch_all_markets(client):
    """Fetch all available markets"""
    all_markets = []
    cursor = None
    
    print("Fetching markets", end="", flush=True)
    while True:
        data = client.get_markets(limit=200, cursor=cursor)
        markets = data.get('markets', [])
        all_markets.extend(markets)
        print(".", end="", flush=True)
        cursor = data.get('cursor')
        if not cursor or len(all_markets) > 2000:
            break
    print(f" {len(all_markets)} total")
    return all_markets


def analyze_markets(markets):
    """Comprehensive market analysis"""
    now = datetime.now(timezone.utc)
    
    results = {
        'by_category': defaultdict(list),
        'by_status': defaultdict(int),
        'liquid_markets': [],
        'expiring_soon': [],  # Within 24h
        'spread_analysis': [],
    }
    
    for m in markets:
        status = m.get('status', 'unknown')
        results['by_status'][status] += 1
        
        if status != 'active':
            continue
        
        cat = categorize_market(m)
        
        # Parse key metrics
        yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
        yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
        no_bid = float(m.get('no_bid_dollars', '0') or 0)
        no_ask = float(m.get('no_ask_dollars', '0') or 0)
        volume = float(m.get('volume_fp', '0') or 0)
        volume_24h = float(m.get('volume_24h_fp', '0') or 0)
        open_interest = float(m.get('open_interest_fp', '0') or 0)
        
        hours_to_exp = hours_until(m.get('expiration_time'))
        spread = get_spread_cents(m)
        
        market_info = {
            'ticker': m.get('ticker'),
            'title': m.get('title', '')[:80],
            'event_ticker': m.get('event_ticker'),
            'category': cat,
            'yes_bid': yes_bid,
            'yes_ask': yes_ask,
            'no_bid': no_bid,
            'no_ask': no_ask,
            'mid_price': (yes_bid + yes_ask) / 2 if yes_bid > 0 and yes_ask > 0 else None,
            'spread_cents': spread,
            'volume': volume,
            'volume_24h': volume_24h,
            'open_interest': open_interest,
            'hours_to_exp': hours_to_exp,
            'expiration': m.get('expiration_time'),
            'has_liquidity': yes_bid > 0 or yes_ask > 0 or volume > 0,
        }
        
        results['by_category'][cat].append(market_info)
        
        if market_info['has_liquidity']:
            results['liquid_markets'].append(market_info)
        
        if hours_to_exp and hours_to_exp < 24:
            results['expiring_soon'].append(market_info)
        
        if spread is not None:
            results['spread_analysis'].append({
                'category': cat,
                'spread': spread,
                'volume': volume
            })
    
    return results


def print_report(results):
    """Print comprehensive report"""
    print("\n" + "=" * 80)
    print("KALSHI MARKET LANDSCAPE REPORT")
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 80)
    
    # Status breakdown
    print("\n" + "-" * 40)
    print("MARKET STATUS BREAKDOWN")
    print("-" * 40)
    for status, count in sorted(results['by_status'].items()):
        print(f"   {status}: {count}")
    
    # Category breakdown
    print("\n" + "-" * 40)
    print("MARKETS BY CATEGORY")
    print("-" * 40)
    print(f"{'Category':<30} {'Total':>8} {'Liquid':>8} {'Avg Vol':>10}")
    print("-" * 60)
    
    cat_stats = []
    for cat, markets in sorted(results['by_category'].items()):
        liquid = [m for m in markets if m['has_liquidity']]
        avg_vol = sum(m['volume'] for m in markets) / len(markets) if markets else 0
        total_vol = sum(m['volume'] for m in markets)
        cat_stats.append({
            'category': cat,
            'total': len(markets),
            'liquid': len(liquid),
            'avg_vol': avg_vol,
            'total_vol': total_vol,
            'markets': markets
        })
        print(f"{cat:<30} {len(markets):>8} {len(liquid):>8} {avg_vol:>10.0f}")
    
    # Top liquid categories
    print("\n" + "-" * 40)
    print("TOP LIQUID MARKETS BY CATEGORY")
    print("-" * 40)
    
    for cat_stat in sorted(cat_stats, key=lambda x: x['total_vol'], reverse=True)[:10]:
        cat = cat_stat['category']
        markets = cat_stat['markets']
        liquid = [m for m in markets if m['has_liquidity']]
        
        if not liquid:
            continue
        
        print(f"\n📁 {cat} ({len(liquid)} liquid / {len(markets)} total)")
        
        # Sort by volume
        top_markets = sorted(liquid, key=lambda x: x['volume'], reverse=True)[:5]
        
        for m in top_markets:
            vol = m['volume']
            mid = m['mid_price']
            spread = m['spread_cents']
            hours = m['hours_to_exp']
            title = m['title'][:50]
            
            mid_str = f"{mid*100:>5.1f}%" if mid else "  N/A"
            spread_str = f"{spread:>4.1f}¢" if spread else "  N/A"
            hours_str = f"{hours:>5.0f}h" if hours else "   N/A"
            
            print(f"   {mid_str} | Spr:{spread_str} | Vol:{vol:>7.0f} | Exp:{hours_str} | {title}")
    
    # Spread analysis
    print("\n" + "-" * 40)
    print("SPREAD ANALYSIS BY CATEGORY")
    print("-" * 40)
    
    spread_by_cat = defaultdict(list)
    for item in results['spread_analysis']:
        if item['spread'] is not None:
            spread_by_cat[item['category']].append(item['spread'])
    
    print(f"{'Category':<30} {'Avg Spread':>12} {'Min':>8} {'Max':>8} {'Count':>8}")
    print("-" * 70)
    
    for cat, spreads in sorted(spread_by_cat.items()):
        if spreads:
            avg = sum(spreads) / len(spreads)
            print(f"{cat:<30} {avg:>10.1f}¢ {min(spreads):>6.1f}¢ {max(spreads):>6.1f}¢ {len(spreads):>8}")
    
    # Expiring soon
    print("\n" + "-" * 40)
    print("EXPIRING WITHIN 24 HOURS")
    print("-" * 40)
    
    expiring = sorted(results['expiring_soon'], key=lambda x: x['hours_to_exp'] or 999)[:15]
    for m in expiring:
        hours = m['hours_to_exp']
        mid = m['mid_price']
        vol = m['volume']
        title = m['title'][:45]
        
        mid_str = f"{mid*100:>5.1f}%" if mid else "  N/A"
        print(f"   {hours:>5.1f}h | {mid_str} | Vol:{vol:>6.0f} | {title}")
    
    # Summary stats
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_liquid = len(results['liquid_markets'])
    total_markets = sum(results['by_status'].values())
    
    print(f"   Total markets: {total_markets}")
    print(f"   Active markets: {results['by_status'].get('active', 0)}")
    print(f"   Markets with liquidity: {total_liquid}")
    print(f"   Expiring within 24h: {len(results['expiring_soon'])}")
    
    if results['spread_analysis']:
        all_spreads = [x['spread'] for x in results['spread_analysis'] if x['spread']]
        if all_spreads:
            print(f"   Average spread: {sum(all_spreads)/len(all_spreads):.1f}¢")
            print(f"   Median spread: {sorted(all_spreads)[len(all_spreads)//2]:.1f}¢")


def save_market_data(markets, results, filepath):
    """Save full market data to JSON for further analysis"""
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_markets': sum(results['by_status'].values()),
            'by_status': dict(results['by_status']),
            'liquid_count': len(results['liquid_markets']),
        },
        'categories': {
            cat: {
                'total': len(mkts),
                'liquid': len([m for m in mkts if m['has_liquidity']]),
                'total_volume': sum(m['volume'] for m in mkts),
            }
            for cat, mkts in results['by_category'].items()
        },
        'liquid_markets': results['liquid_markets'],
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nFull data saved to: {filepath}")


def main():
    client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
    
    # Fetch all markets
    markets = fetch_all_markets(client)
    
    # Analyze
    results = analyze_markets(markets)
    
    # Print report
    print_report(results)
    
    # Save data
    save_market_data(markets, results, '/root/.openclaw/workspace-elliot-crane/kalshi/market_data.json')


if __name__ == "__main__":
    main()
