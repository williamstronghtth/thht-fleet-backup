#!/usr/bin/env python3
"""
Spike Alert System
Monitors entertainment contracts for +15pt moves in 24h
Triggers on hype-driven overreactions that can be faded

Now includes:
- Microstructure analysis (VPIN, Kyle's lambda)
- Sentiment analysis (X Search via Grok)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane/kalshi')
from kalshi_client import KalshiClient

WORKSPACE = Path('/root/.openclaw/workspace-elliot-crane')
DATA_DIR = WORKSPACE / 'kalshi' / 'spike_monitor'
HISTORY_FILE = DATA_DIR / 'price_history.json'
ALERT_THRESHOLD = 15  # Points (15¢)

# Liquidity filters to avoid phantom signals from thin markets
MIN_VOLUME_THRESHOLD = 1000  # Minimum contracts traded
MAX_SPREAD_THRESHOLD = 10    # Maximum bid-ask spread in cents

# Entertainment series to monitor
ENTERTAINMENT_SERIES = ['KXSURVIVOR', 'KXOSCARPIC', 'KXOSCARDIR', 'KXSNL', 'KXGRAMMYS']

# Risk thresholds for microstructure
MAX_VPIN = 0.65          # Above this = informed flow, avoid
MAX_R_SQUARED = 0.15     # Above this = price reveals info, avoid
MAX_BRANCHING = 0.80     # Above this = momentum cascade, fade


def load_config():
    """Load API credentials from gateway config"""
    config_path = '/root/.openclaw/openclaw.json'
    with open(config_path) as f:
        config = json.load(f)
    env_vars = config.get('env', {}).get('vars', {})
    return {
        'api_key': <REDACTED:CREDENTIAL>('KALSHI_API_KEY_ID', ''),
        'private_key': env_vars.get('KALSHI_PRIVATE_KEY', '').replace('\\n', '\n'),
        'xai_key': env_vars.get('XAI_API_KEY', ''),
    }


def load_price_history():
    """Load previous price snapshots"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {'snapshots': []}


def save_price_history(history):
    """Save price history"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_current_prices(client):
    """Fetch current prices for entertainment markets"""
    prices = {}
    
    for series in ENTERTAINMENT_SERIES:
        try:
            events = client.get_events(series_ticker=series, limit=10)
            for event in events.get('events', []):
                markets = client.get_markets(event_ticker=event.get('event_ticker'), limit=50)
                for m in markets.get('markets', []):
                    if m.get('status') != 'active':
                        continue
                    
                    yes_bid = float(m.get('yes_bid_dollars', 0) or 0)
                    yes_ask = float(m.get('yes_ask_dollars', 0) or 0)
                    
                    if yes_bid > 0 and yes_ask > 0:
                        mid = (yes_bid + yes_ask) / 2 * 100  # Convert to cents
                        spread = (yes_ask - yes_bid) * 100   # Spread in cents
                        prices[m.get('ticker')] = {
                            'ticker': m.get('ticker'),
                            'title': m.get('title', ''),
                            'series': series,
                            'mid': mid,
                            'spread': spread,
                            'volume': float(m.get('volume_fp', 0) or 0),
                        }
        except Exception as e:
            print(f"Error fetching {series}: {e}")
    
    return prices


def analyze_microstructure(ticker):
    """
    Run microstructure analysis on a market.
    Returns risk assessment dict.
    """
    try:
        from microstructure.analyzer import MarketAnalyzer
        analyzer = MarketAnalyzer()
        result = analyzer.analyze_market(ticker, lookback_trades=100)
        
        return {
            'risk_score': result.risk_score,
            'safe_to_trade': result.safe_to_trade,
            'vpin': result.vpin.vpin if result.vpin else None,
            'r_squared': result.kyle.r_squared if result.kyle else None,
            'branching': result.hawkes.branching_ratio if result.hawkes else None,
            'recommendation': result.recommendation,
            'warnings': result.warnings,
        }
    except Exception as e:
        return {
            'risk_score': 50,
            'safe_to_trade': None,
            'error': str(e),
        }


def analyze_sentiment(title, current_price):
    """
    Run X sentiment analysis on a market.
    Returns sentiment assessment dict.
    """
    try:
        # Check if XAI key is available
        creds = load_config()
        if not creds.get('xai_key'):
            return {'sentiment': None, 'error': 'XAI_API_KEY not configured'}
        
        os.environ['XAI_API_KEY'] = creds['xai_key']
        
        from sentiment.grok_client import GrokClient
        client = GrokClient()
        
        result = client.analyze_market_sentiment(
            market_description=title,
            current_price=current_price / 100,  # Convert cents to decimal
        )
        
        return {
            'sentiment': result['sentiment'],
            'crowd_belief': result['crowd_belief'],
            'gap': result['gap'],
            'confidence': result['confidence'],
            'signal': result['recommendation'],
            'sources': result.get('sources', 0),
        }
    except Exception as e:
        return {
            'sentiment': None,
            'error': str(e),
        }


def detect_spikes(current_prices, history):
    """Compare current prices to 24h ago, find spikes"""
    spikes = []
    
    # Find snapshot from ~24h ago
    now = datetime.now(timezone.utc)
    target_time = now - timedelta(hours=24)
    
    old_snapshot = None
    for snapshot in reversed(history.get('snapshots', [])):
        snap_time = datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))
        if snap_time <= target_time:
            old_snapshot = snapshot
            break
    
    if not old_snapshot:
        # No 24h history yet, use oldest available
        if history.get('snapshots'):
            old_snapshot = history['snapshots'][0]
        else:
            return []  # No history at all
    
    old_prices = old_snapshot.get('prices', {})
    
    for ticker, current in current_prices.items():
        if ticker in old_prices:
            old_mid = old_prices[ticker]['mid']
            change = current['mid'] - old_mid
            
            if abs(change) >= ALERT_THRESHOLD:
                volume = current['volume']
                spread = current.get('spread', 999)  # Default to high spread if not available
                
                # Apply liquidity filters
                passes_volume = volume >= MIN_VOLUME_THRESHOLD
                passes_spread = spread <= MAX_SPREAD_THRESHOLD
                
                spikes.append({
                    'ticker': ticker,
                    'title': current['title'],
                    'series': current['series'],
                    'old_price': old_mid,
                    'new_price': current['mid'],
                    'change': change,
                    'volume': volume,
                    'spread': spread,
                    'direction': 'UP' if change > 0 else 'DOWN',
                    'passes_filters': passes_volume and passes_spread,
                    'filter_notes': [] if (passes_volume and passes_spread) else 
                        ([f'Low volume ({volume:.0f} < {MIN_VOLUME_THRESHOLD})'] if not passes_volume else []) +
                        ([f'Wide spread ({spread:.0f}¢ > {MAX_SPREAD_THRESHOLD}¢)'] if not passes_spread else []),
                })
    
    return spikes


def run_spike_check(deep_analysis=False):
    """
    Main spike detection function.
    
    Parameters:
    -----------
    deep_analysis : bool - if True, run microstructure + sentiment on actionable spikes
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        # Load credentials and create client
        creds = load_config()
        client = KalshiClient(api_key_id=creds['api_key'], private_key_pem=creds['private_key'])
        
        # Get current prices
        current_prices = get_current_prices(client)
        
        # Load history
        history = load_price_history()
        
        # Detect spikes
        spikes = detect_spikes(current_prices, history)
        
        # Add current snapshot to history
        history['snapshots'].append({
            'timestamp': timestamp,
            'prices': current_prices,
        })
        
        # Keep only last 48 hours of snapshots (48 hourly checks)
        history['snapshots'] = history['snapshots'][-48:]
        
        # Save updated history
        save_price_history(history)
        
        # Report
        result = {
            'timestamp': timestamp,
            'markets_monitored': len(current_prices),
            'spikes_detected': len(spikes),
            'spikes': spikes,
        }
        
        if spikes:
            # Separate actionable spikes from filtered ones
            actionable = [s for s in spikes if s['passes_filters']]
            filtered_out = [s for s in spikes if not s['passes_filters']]
            
            if actionable:
                print("🚨 SPIKE ALERT — Entertainment Market Movement")
                print("=" * 60)
                
                for spike in sorted(actionable, key=lambda x: abs(x['change']), reverse=True):
                    direction = "📈" if spike['direction'] == 'UP' else "📉"
                    print(f"{direction} {spike['title'][:50]}")
                    print(f"   {spike['old_price']:.0f}¢ → {spike['new_price']:.0f}¢ ({spike['change']:+.0f}¢)")
                    print(f"   Volume: {spike['volume']:,.0f} | Spread: {spike['spread']:.0f}¢")
                    
                    # Deep analysis if requested
                    if deep_analysis:
                        print(f"\n   🔬 Running deep analysis...")
                        
                        # Microstructure
                        micro = analyze_microstructure(spike['ticker'])
                        spike['microstructure'] = micro
                        
                        if micro.get('safe_to_trade') is not None:
                            status = "✅" if micro['safe_to_trade'] else "⚠️"
                            print(f"   {status} Microstructure: Risk {micro['risk_score']}/100")
                            if micro.get('vpin'):
                                print(f"      VPIN: {micro['vpin']:.0%} | R²: {micro.get('r_squared', 0):.1%}")
                            if micro.get('warnings'):
                                for w in micro['warnings'][:2]:
                                    print(f"      ⚠️ {w}")
                        
                        # Sentiment (costs money, so only on actionable spikes)
                        sent = analyze_sentiment(spike['title'], spike['new_price'])
                        spike['sentiment'] = sent
                        
                        if sent.get('sentiment'):
                            gap_direction = "+" if sent['gap'] > 0 else ""
                            print(f"   📊 Sentiment: {sent['sentiment'].upper()} ({sent['confidence']:.0%} conf)")
                            print(f"      Crowd: {sent['crowd_belief']*100:.0f}% | Gap: {gap_direction}{sent['gap']*100:.0f}pts")
                            print(f"      Signal: {sent['signal']}")
                        elif sent.get('error'):
                            print(f"   📊 Sentiment: Skipped ({sent['error'][:30]})")
                    
                    print()
            
            if filtered_out:
                print("\n⚠️  FILTERED (thin liquidity — not actionable):")
                print("-" * 60)
                for spike in sorted(filtered_out, key=lambda x: abs(x['change']), reverse=True):
                    direction = "📈" if spike['direction'] == 'UP' else "📉"
                    print(f"{direction} {spike['title'][:40]}...")
                    print(f"   {spike['old_price']:.0f}¢ → {spike['new_price']:.0f}¢ ({spike['change']:+.0f}¢)")
                    print(f"   ❌ {', '.join(spike['filter_notes'])}")
                    print()
            
            if not actionable and filtered_out:
                print(f"\nNo actionable spikes. {len(filtered_out)} movements filtered due to thin liquidity.")
        else:
            print(f"No spikes detected. Monitoring {len(current_prices)} entertainment markets.")
        
        return result
        
    except Exception as e:
        print(f"🔴 SPIKE CHECK FAILED: {e}")
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Spike Alert System')
    parser.add_argument('--deep', action='store_true', help='Run deep analysis (microstructure + sentiment)')
    args = parser.parse_args()
    
    run_spike_check(deep_analysis=args.deep)
