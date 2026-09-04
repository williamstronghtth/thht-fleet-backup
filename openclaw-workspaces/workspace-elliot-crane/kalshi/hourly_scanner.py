#!/usr/bin/env python3
"""
Hourly Market Scanner
Runs on cron, logs data, alerts only when actionable
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient

# Configuration
WORKSPACE = Path('/root/.openclaw/workspace-elliot-crane')
DATA_DIR = WORKSPACE / 'kalshi' / 'price_history'
LAST_SCAN_FILE = DATA_DIR / 'last_scan.json'
HISTORY_FILE = DATA_DIR / 'history.jsonl'

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

# Alert thresholds
MOVEMENT_ALERT_THRESHOLD = 3  # Points for logging
WATCH_THRESHOLD = 5           # Points for 🟡 alert
TRADE_THRESHOLD = 10          # Points for 🟢 alert

# Liquidity filters to avoid phantom signals from thin markets
MIN_VOLUME_THRESHOLD = 1000   # Minimum contracts traded
MAX_SPREAD_THRESHOLD = 10     # Maximum bid-ask spread in cents


def ensure_dirs():
    """Create data directories if needed"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_economics_markets(client):
    """Fetch all active economics markets"""
    markets = {}
    
    for series in ['KXCPI', 'KXGDP']:
        try:
            events_data = client.get_events(series_ticker=series, limit=20)
            events = events_data.get('events', [])
            
            for event in events:
                event_ticker = event.get('event_ticker')
                markets_data = client.get_markets(event_ticker=event_ticker, limit=50)
                
                for m in markets_data.get('markets', []):
                    if m.get('status') != 'active':
                        continue
                    
                    ticker = m.get('ticker')
                    yes_bid = float(m.get('yes_bid_dollars', '0') or 0)
                    yes_ask = float(m.get('yes_ask_dollars', '0') or 0)
                    
                    if yes_bid > 0 and yes_ask > 0:
                        mid = (yes_bid + yes_ask) / 2 * 100  # Convert to percentage
                        spread = (yes_ask - yes_bid) * 100
                    else:
                        mid = None
                        spread = None
                    
                    markets[ticker] = {
                        'ticker': ticker,
                        'title': m.get('title', ''),
                        'series': series,
                        'event': event_ticker,
                        'yes_bid': yes_bid * 100 if yes_bid else None,
                        'yes_ask': yes_ask * 100 if yes_ask else None,
                        'mid': mid,
                        'spread': spread,
                        'volume': float(m.get('volume_fp', '0') or 0),
                    }
        except Exception as e:
            print(f"Error fetching {series}: {e}")
    
    return markets


def load_last_scan():
    """Load previous scan data"""
    if LAST_SCAN_FILE.exists():
        with open(LAST_SCAN_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_scan(scan_data):
    """Save current scan data"""
    with open(LAST_SCAN_FILE, 'w') as f:
        json.dump(scan_data, f, indent=2)


def append_history(record):
    """Append to history log"""
    with open(HISTORY_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')


def compare_scans(current, previous):
    """Compare current vs previous scan, find movements"""
    movements = []
    
    for ticker, data in current.items():
        if data['mid'] is None:
            continue
            
        prev_data = previous.get('markets', {}).get(ticker)
        if prev_data and prev_data.get('mid'):
            change = data['mid'] - prev_data['mid']
            if abs(change) >= MOVEMENT_ALERT_THRESHOLD:
                volume = data.get('volume', 0)
                spread = data.get('spread', 999)
                
                # Apply liquidity filters
                passes_volume = volume >= MIN_VOLUME_THRESHOLD
                passes_spread = spread <= MAX_SPREAD_THRESHOLD
                passes_filters = passes_volume and passes_spread
                
                filter_notes = []
                if not passes_volume:
                    filter_notes.append(f'Low vol ({volume:.0f})')
                if not passes_spread:
                    filter_notes.append(f'Wide spread ({spread:.0f}¢)')
                
                movements.append({
                    'ticker': ticker,
                    'title': data['title'],
                    'previous': prev_data['mid'],
                    'current': data['mid'],
                    'change': change,
                    'spread': spread,
                    'volume': volume,
                    'passes_filters': passes_filters,
                    'filter_notes': filter_notes,
                })
    
    return movements


def categorize_alert(movements):
    """Categorize alert level based on movements that pass liquidity filters"""
    if not movements:
        return None, [], []
    
    # Separate actionable from filtered movements
    actionable = [m for m in movements if m['passes_filters']]
    filtered_out = [m for m in movements if not m['passes_filters']]
    
    # Sort both by absolute change
    actionable = sorted(actionable, key=lambda x: abs(x['change']), reverse=True)
    filtered_out = sorted(filtered_out, key=lambda x: abs(x['change']), reverse=True)
    
    if not actionable:
        return 'FILTERED_ONLY', actionable, filtered_out
    
    max_change = max(abs(m['change']) for m in actionable)
    
    if max_change >= TRADE_THRESHOLD:
        return 'GREEN', actionable, filtered_out
    elif max_change >= WATCH_THRESHOLD:
        return 'YELLOW', actionable, filtered_out
    else:
        return 'LOG_ONLY', actionable, filtered_out


def format_scan_output(timestamp, markets, actionable, filtered_out, alert_level):
    """Format output for logging/display"""
    lines = []
    lines.append(f"=== HOURLY SCAN: {timestamp} ===")
    lines.append(f"Markets scanned: {len(markets)}")
    
    if actionable:
        lines.append(f"\n📊 Actionable movements: {len(actionable)}")
        for m in actionable[:10]:  # Top 10
            direction = "↑" if m['change'] > 0 else "↓"
            lines.append(f"  {direction} {m['title'][:40]}: {m['previous']:.1f}% → {m['current']:.1f}% ({m['change']:+.1f})")
            lines.append(f"      Vol: {m['volume']:,.0f} | Spread: {m['spread']:.0f}¢")
    
    if filtered_out:
        lines.append(f"\n⚠️  Filtered (thin liquidity): {len(filtered_out)}")
        for m in filtered_out[:5]:  # Top 5 filtered
            direction = "↑" if m['change'] > 0 else "↓"
            lines.append(f"  {direction} {m['title'][:35]}... ({m['change']:+.1f}) — {', '.join(m['filter_notes'])}")
    
    if not actionable and not filtered_out:
        lines.append("\nNo significant movements.")
    
    if alert_level == 'GREEN':
        lines.append("\n🟢 POTENTIAL TRADE OPPORTUNITY DETECTED")
    elif alert_level == 'YELLOW':
        lines.append("\n🟡 SIGNIFICANT SHIFT - WATCHING")
    elif alert_level == 'FILTERED_ONLY':
        lines.append("\n⚠️  All movements filtered due to thin liquidity")
    
    return '\n'.join(lines)


def run_scan():
    """Main scan function"""
    ensure_dirs()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        client = KalshiClient(api_key_id=API_KEY_ID, private_key_pem=PRIVATE_KEY)
        
        # Fetch current markets
        markets = get_economics_markets(client)
        
        # Load previous scan
        previous = load_last_scan()
        
        # Compare
        movements = compare_scans(markets, previous)
        
        # Categorize alert (now returns actionable and filtered separately)
        alert_level, actionable, filtered_out = categorize_alert(movements)
        
        # Build scan record
        scan_record = {
            'timestamp': timestamp,
            'markets': markets,
            'movements': actionable,
            'filtered_movements': filtered_out,
            'alert_level': alert_level,
        }
        
        # Save current as last
        save_scan(scan_record)
        
        # Append to history (summary only)
        history_entry = {
            'timestamp': timestamp,
            'market_count': len(markets),
            'actionable_count': len(actionable),
            'filtered_count': len(filtered_out),
            'alert_level': alert_level,
            'top_movements': actionable[:5] if actionable else [],
        }
        append_history(history_entry)
        
        # Format output
        output = format_scan_output(timestamp, markets, actionable, filtered_out, alert_level)
        
        return {
            'success': True,
            'timestamp': timestamp,
            'output': output,
            'alert_level': alert_level,
            'movements': actionable,
            'filtered_movements': filtered_out,
            'market_count': len(markets),
        }
        
    except Exception as e:
        error_msg = f"🔴 SCAN FAILED: {str(e)}"
        return {
            'success': False,
            'timestamp': timestamp,
            'output': error_msg,
            'alert_level': 'RED',
            'error': str(e),
        }


if __name__ == "__main__":
    result = run_scan()
    print(result['output'])
    
    # Exit with appropriate code
    if not result['success']:
        sys.exit(1)
