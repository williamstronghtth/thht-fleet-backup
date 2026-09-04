#!/usr/bin/env python3
"""
Backtest Framework for Favorite-Longshot Strategy
Uses Kalshi's historical market data

Strategy: 
- Short overpriced longshots (<20%)
- Long underpriced favorites (>80%)
- Apply category multipliers
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient
from bias_calibration import calculate_bias, get_category_multiplier, score_opportunity

WORKSPACE = Path('/root/.openclaw/workspace-elliot-crane')
BACKTEST_DIR = WORKSPACE / 'kalshi' / 'backtest'

API_KEY_ID = "adcd595f-ac7a-4d70-b6df-a859a2f3ac63"
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQEAtTsPAY837dUOdT4JWFH8KMsomqooJe1fWgWWaFxRZCsFIqeC
IjknFX4JplBI4NcRhs6RNCI+NzCaTLtHEJ58XNEDEJszoG9PNCyTKaJ+nxUhOOdf
M1oGE8fRcTrTlcBcnqpDsvYTBS/OFdZfencAeR8SMkCSY9LxMVLZIU1TqunPBOVP
GuZyOHL29nXukbWPUNtWrZav7Rz/LRVSgJWWp7o78TE2t2t9UJ3zvGuNBsh7f4/0
/0cb1T8Nk8vQiug/c2zmnkB5ldEuW4VUT/IOYMGKXxdszbRAtv8DCZuQMh+3dkeR
l2VbfH/F8Cvmhd3qONzZuWc7Iti1dJX+dndkSQIDAQABAoH/G+U+V8g/5egEAnWc
XCaLl3K6KLLXh2CCOoO6CquYz2qrNQXEXYxiWTvKNEMnVh8Z7vVWrYqb4Jjby8axvIZuab5GTxaJhAoGBAPApGNaA
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


def categorize_market(title: str, series: str = '') -> str:
    """Categorize market for bias adjustment"""
    title_lower = title.lower()
    series_lower = series.lower() if series else ''
    
    if any(x in title_lower or x in series_lower for x in ['oscar', 'grammy', 'emmy', 'award', 'survivor', 'bachelor']):
        return 'entertainment'
    if any(x in title_lower for x in ['bitcoin', 'btc', 'ethereum', 'crypto']):
        return 'crypto'
    if any(x in title_lower for x in ['cpi', 'gdp', 'inflation', 'fed']):
        return 'economics'
    return 'other'


def fetch_settled_markets(client: KalshiClient, limit: int = 500) -> List[Dict]:
    """Fetch recently settled markets for backtesting"""
    settled = []
    
    # Get settled markets
    try:
        result = client.get_markets(limit=limit)
        for m in result.get('markets', []):
            if m.get('status') == 'settled':
                settled.append(m)
    except Exception as e:
        print(f"Error fetching markets: {e}")
    
    return settled


def simulate_strategy(markets: List[Dict], strategy: str = 'favorite_longshot') -> Dict:
    """
    Simulate trading strategy on historical markets
    
    Strategy: favorite_longshot
    - Short contracts priced <20% 
    - Long contracts priced >80%
    - $10 per trade
    - 1¢ fee each way
    """
    results = {
        'total_trades': 0,
        'wins': 0,
        'losses': 0,
        'total_pnl': 0.0,
        'pnl_by_bucket': defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0.0}),
        'pnl_by_category': defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0.0}),
        'trades': [],
    }
    
    FEE = 0.01  # $0.01 per contract
    TRADE_SIZE = 10.0  # $10 per trade
    
    for m in markets:
        ticker = m.get('ticker', '')
        title = m.get('title', '')
        result_val = m.get('result')
        
        # Need settlement result
        if result_val not in ['yes', 'no']:
            continue
        
        settled_yes = (result_val == 'yes')
        
        # Get historical price (use last trade price or close)
        close_price = float(m.get('last_price_fp', 0) or m.get('close_price_fp', 0) or 0)
        if close_price <= 0:
            continue
        
        category = categorize_market(title, m.get('series_ticker', ''))
        
        # Determine bucket
        if close_price < 0.20:
            bucket = 'longshot_short'
            # Strategy: SHORT YES (sell YES, buy NO)
            # Win if settles NO
            position = 'SHORT_YES'
            contracts = int(TRADE_SIZE / close_price)
            entry_cost = contracts * close_price
            
            if not settled_yes:
                # We win - collect the difference
                pnl = entry_cost - (contracts * FEE * 2)  # Gross win minus fees
            else:
                # We lose - they won
                pnl = -((1 - close_price) * contracts) - (contracts * FEE * 2)
                
        elif close_price > 0.80:
            bucket = 'favorite_long'
            # Strategy: LONG YES (buy YES)
            # Win if settles YES
            position = 'LONG_YES'
            contracts = int(TRADE_SIZE / close_price)
            entry_cost = contracts * close_price
            
            if settled_yes:
                # We win
                pnl = (1 - close_price) * contracts - (contracts * FEE * 2)
            else:
                # We lose
                pnl = -entry_cost - (contracts * FEE * 2)
        else:
            # Skip middle range for this strategy
            continue
        
        # Record trade
        won = pnl > 0
        results['total_trades'] += 1
        results['wins'] += 1 if won else 0
        results['losses'] += 0 if won else 1
        results['total_pnl'] += pnl
        
        results['pnl_by_bucket'][bucket]['trades'] += 1
        results['pnl_by_bucket'][bucket]['wins'] += 1 if won else 0
        results['pnl_by_bucket'][bucket]['pnl'] += pnl
        
        results['pnl_by_category'][category]['trades'] += 1
        results['pnl_by_category'][category]['wins'] += 1 if won else 0
        results['pnl_by_category'][category]['pnl'] += pnl
        
        results['trades'].append({
            'ticker': ticker,
            'title': title[:50],
            'close_price': close_price,
            'bucket': bucket,
            'category': category,
            'position': position,
            'contracts': contracts,
            'settled': result_val,
            'pnl': round(pnl, 2),
            'won': won,
        })
    
    return results


def format_backtest_report(results: Dict) -> str:
    """Format backtest results"""
    lines = []
    lines.append("=" * 60)
    lines.append("BACKTEST RESULTS: Favorite-Longshot Strategy")
    lines.append("=" * 60)
    
    if results['total_trades'] == 0:
        lines.append("\n❌ No qualifying trades found in historical data.")
        lines.append("This may be due to limited settled market data available.")
        return '\n'.join(lines)
    
    win_rate = results['wins'] / results['total_trades'] * 100 if results['total_trades'] > 0 else 0
    
    lines.append(f"\nOVERALL:")
    lines.append(f"  Total trades: {results['total_trades']}")
    lines.append(f"  Wins: {results['wins']} | Losses: {results['losses']}")
    lines.append(f"  Win rate: {win_rate:.1f}%")
    lines.append(f"  Total P&L: ${results['total_pnl']:.2f}")
    lines.append(f"  Avg P&L per trade: ${results['total_pnl'] / results['total_trades']:.2f}")
    
    lines.append(f"\nBY BUCKET:")
    for bucket, data in results['pnl_by_bucket'].items():
        wr = data['wins'] / data['trades'] * 100 if data['trades'] > 0 else 0
        lines.append(f"  {bucket}: {data['trades']} trades, {wr:.1f}% win rate, ${data['pnl']:.2f} P&L")
    
    lines.append(f"\nBY CATEGORY:")
    for cat, data in results['pnl_by_category'].items():
        wr = data['wins'] / data['trades'] * 100 if data['trades'] > 0 else 0
        lines.append(f"  {cat}: {data['trades']} trades, {wr:.1f}% win rate, ${data['pnl']:.2f} P&L")
    
    lines.append(f"\nSAMPLE TRADES:")
    for trade in results['trades'][:10]:
        emoji = "✅" if trade['won'] else "❌"
        lines.append(f"  {emoji} {trade['title'][:40]}... | {trade['position']} @ {trade['close_price']*100:.0f}¢ | P&L: ${trade['pnl']:.2f}")
    
    return '\n'.join(lines)


def run_backtest():
    """Main backtest function"""
    BACKTEST_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Starting backtest...")
    
    try:
        client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
        
        # Fetch settled markets
        print("Fetching settled markets...")
        settled = fetch_settled_markets(client, limit=1000)
        print(f"Found {len(settled)} settled markets")
        
        if len(settled) == 0:
            print("No settled markets found. Checking market statuses...")
            all_markets = client.get_markets(limit=100)
            statuses = {}
            for m in all_markets.get('markets', []):
                s = m.get('status', 'unknown')
                statuses[s] = statuses.get(s, 0) + 1
            print(f"Market status distribution: {statuses}")
        
        # Run simulation
        print("Running simulation...")
        results = simulate_strategy(settled)
        
        # Format report
        report = format_backtest_report(results)
        print(report)
        
        # Save results
        output_file = BACKTEST_DIR / 'backtest_results.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'markets_analyzed': len(settled),
                'results': {
                    'total_trades': results['total_trades'],
                    'wins': results['wins'],
                    'losses': results['losses'],
                    'total_pnl': results['total_pnl'],
                    'pnl_by_bucket': dict(results['pnl_by_bucket']),
                    'pnl_by_category': dict(results['pnl_by_category']),
                },
                'sample_trades': results['trades'][:50],
            }, f, indent=2, default=str)
        
        return results
        
    except Exception as e:
        print(f"🔴 BACKTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    run_backtest()
