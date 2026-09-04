#!/usr/bin/env python3
"""
Cross-Platform Arbitrage Scanner
Compares prices between Kalshi and Polymarket

Looks for:
- Same event priced differently across platforms
- Risk-free spreads when one platform is higher than other
"""

import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient

WORKSPACE = Path('/root/.openclaw/workspace-elliot-crane')
OUTPUT_DIR = WORKSPACE / 'kalshi' / 'arbitrage'

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


# Polymarket GraphQL endpoint
POLYMARKET_API = "https://gamma-api.polymarket.com"


def fetch_polymarket_markets() -> List[Dict]:
    """Fetch active markets from Polymarket"""
    import urllib.request
    
    try:
        # Polymarket has a REST API for markets
        url = f"{POLYMARKET_API}/markets?closed=false&limit=100"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else data.get('markets', [])
    except Exception as e:
        print(f"Error fetching Polymarket: {e}")
        return []


def normalize_event_name(title: str) -> str:
    """Normalize event title for matching"""
    # Remove common prefixes/suffixes
    title = title.lower()
    title = re.sub(r'\?$', '', title)  # Remove trailing ?
    title = re.sub(r'^will ', '', title)
    title = re.sub(r' in \d{4}$', '', title)
    title = re.sub(r' by [a-z]+ \d+, \d{4}$', '', title)
    title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation
    title = ' '.join(title.split())  # Normalize whitespace
    return title


def find_matching_markets(kalshi_markets: List[Dict], poly_markets: List[Dict]) -> List[Dict]:
    """Find markets that exist on both platforms"""
    matches = []
    
    # Create lookup by normalized name
    poly_lookup = {}
    for pm in poly_markets:
        title = pm.get('question', pm.get('title', ''))
        normalized = normalize_event_name(title)
        if normalized:
            poly_lookup[normalized] = pm
    
    # Match Kalshi markets
    for km in kalshi_markets:
        k_title = km.get('title', '')
        k_normalized = normalize_event_name(k_title)
        
        # Try exact match
        if k_normalized in poly_lookup:
            matches.append({
                'kalshi': km,
                'polymarket': poly_lookup[k_normalized],
                'match_type': 'exact',
            })
            continue
        
        # Try partial match (at least 3 words in common)
        k_words = set(k_normalized.split())
        for p_norm, pm in poly_lookup.items():
            p_words = set(p_norm.split())
            common = k_words & p_words
            if len(common) >= 3 and len(common) / max(len(k_words), len(p_words)) > 0.5:
                matches.append({
                    'kalshi': km,
                    'polymarket': pm,
                    'match_type': 'partial',
                    'common_words': list(common),
                })
                break
    
    return matches


def calculate_arbitrage(kalshi: Dict, polymarket: Dict) -> Optional[Dict]:
    """Calculate if there's an arbitrage opportunity"""
    
    # Kalshi prices
    k_yes_bid = float(kalshi.get('yes_bid_dollars', 0) or 0)
    k_yes_ask = float(kalshi.get('yes_ask_dollars', 0) or 0)
    
    # Polymarket prices (typically in cents or decimal)
    p_yes = polymarket.get('outcomePrices', [0, 0])
    if isinstance(p_yes, list) and len(p_yes) >= 1:
        p_yes_price = float(p_yes[0]) if p_yes[0] else 0
    else:
        p_yes_price = float(polymarket.get('price', 0) or 0)
    
    if not (k_yes_bid and k_yes_ask and p_yes_price):
        return None
    
    # Normalize to 0-1 scale
    if p_yes_price > 1:
        p_yes_price = p_yes_price / 100
    
    k_mid = (k_yes_bid + k_yes_ask) / 2
    
    # Calculate spread
    spread = abs(k_mid - p_yes_price)
    
    # Arbitrage exists if:
    # - We can buy YES on one platform cheaper than we can sell on other
    # - Spread > transaction costs (estimated 3% round trip)
    
    arb_opportunity = None
    
    if k_yes_bid > p_yes_price + 0.03:
        # Buy on Polymarket, sell on Kalshi
        arb_opportunity = {
            'type': 'BUY_POLY_SELL_KALSHI',
            'buy_price': p_yes_price,
            'sell_price': k_yes_bid,
            'gross_spread': k_yes_bid - p_yes_price,
            'net_spread': k_yes_bid - p_yes_price - 0.03,
        }
    elif p_yes_price > k_yes_ask + 0.03:
        # Buy on Kalshi, sell on Polymarket
        arb_opportunity = {
            'type': 'BUY_KALSHI_SELL_POLY',
            'buy_price': k_yes_ask,
            'sell_price': p_yes_price,
            'gross_spread': p_yes_price - k_yes_ask,
            'net_spread': p_yes_price - k_yes_ask - 0.03,
        }
    
    return {
        'kalshi_title': kalshi.get('title', '')[:50],
        'kalshi_ticker': kalshi.get('ticker', ''),
        'kalshi_yes_bid': k_yes_bid,
        'kalshi_yes_ask': k_yes_ask,
        'polymarket_title': polymarket.get('question', '')[:50],
        'polymarket_price': p_yes_price,
        'spread': round(spread * 100, 1),
        'arbitrage': arb_opportunity,
    }


def run_arbitrage_scan():
    """Main arbitrage scan function"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=== CROSS-PLATFORM ARBITRAGE SCANNER ===\n")
    
    try:
        # Fetch Kalshi markets
        print("Fetching Kalshi markets...")
        client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
        k_result = client.get_markets(limit=200)
        kalshi_markets = [m for m in k_result.get('markets', []) if m.get('status') == 'active']
        print(f"  Found {len(kalshi_markets)} active Kalshi markets")
        
        # Fetch Polymarket markets
        print("Fetching Polymarket markets...")
        poly_markets = fetch_polymarket_markets()
        print(f"  Found {len(poly_markets)} Polymarket markets")
        
        if not poly_markets:
            print("\n⚠️ Could not fetch Polymarket data. API may be restricted or changed.")
            print("Manual comparison recommended for now.")
            
            # Save Kalshi markets for manual review
            output_file = OUTPUT_DIR / 'kalshi_for_manual_review.json'
            with open(output_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'note': 'Compare these with Polymarket manually',
                    'markets': [{
                        'ticker': m.get('ticker'),
                        'title': m.get('title'),
                        'yes_bid': float(m.get('yes_bid_dollars', 0) or 0),
                        'yes_ask': float(m.get('yes_ask_dollars', 0) or 0),
                    } for m in kalshi_markets[:50]],
                }, f, indent=2)
            print(f"  Saved to {output_file}")
            return {'success': True, 'matches': 0, 'arbitrage_opportunities': 0}
        
        # Find matching markets
        print("\nFinding matching markets...")
        matches = find_matching_markets(kalshi_markets, poly_markets)
        print(f"  Found {len(matches)} potential matches")
        
        # Calculate arbitrage
        opportunities = []
        for match in matches:
            arb = calculate_arbitrage(match['kalshi'], match['polymarket'])
            if arb and arb['arbitrage']:
                opportunities.append(arb)
        
        # Report
        print(f"\n🎯 ARBITRAGE OPPORTUNITIES: {len(opportunities)}")
        if opportunities:
            for opp in opportunities:
                print(f"\n  📊 {opp['kalshi_title']}")
                print(f"     Kalshi: {opp['kalshi_yes_bid']*100:.0f}¢ / {opp['kalshi_yes_ask']*100:.0f}¢")
                print(f"     Polymarket: {opp['polymarket_price']*100:.0f}¢")
                print(f"     Spread: {opp['spread']}¢")
                print(f"     Strategy: {opp['arbitrage']['type']}")
                print(f"     Net Spread: {opp['arbitrage']['net_spread']*100:.1f}¢")
        else:
            print("  No risk-free arbitrage found (spreads too tight)")
        
        # Save results
        output_file = OUTPUT_DIR / 'arbitrage_scan.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'kalshi_count': len(kalshi_markets),
                'polymarket_count': len(poly_markets),
                'matches': len(matches),
                'opportunities': opportunities,
            }, f, indent=2)
        
        return {
            'success': True,
            'matches': len(matches),
            'arbitrage_opportunities': len(opportunities),
            'opportunities': opportunities,
        }
        
    except Exception as e:
        print(f"🔴 ARBITRAGE SCAN FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    run_arbitrage_scan()
