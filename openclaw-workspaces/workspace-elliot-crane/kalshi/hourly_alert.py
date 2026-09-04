#!/usr/bin/env python3
"""
Hourly Market Alert System
Prioritizes broad, liquid non-sports markets first; weather/econ are secondary.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')


def load_kalshi_creds():
    """Load Kalshi API credentials from openclaw.json config."""
    config_path = '/root/.openclaw/openclaw.json'
    with open(config_path) as f:
        config = json.load(f)
    env_vars = config.get('env', {}).get('vars', {})
    return {
        'api_key_id': env_vars.get('KALSHI_API_KEY_ID', ''),
        'private_key': env_vars.get('KALSHI_PRIVATE_KEY', '').replace('\\n', '\n'),
    }


def get_positions():
    from kalshi.kalshi_client import KalshiClient
    creds = load_kalshi_creds()
    client = KalshiClient(api_key_id=creds['api_key_id'], private_key_pem=creds['private_key'])
    positions = client._request('GET', '/portfolio/positions')
    balance = client._request('GET', '/portfolio/balance')

    active = []
    for pos in positions.get('market_positions', []):
        qty = float(pos.get('position_fp', 0))
        if qty > 0:
            active.append({'ticker': pos.get('ticker'), 'contracts': int(qty)})

    return active, float(balance.get('balance', 0)) / 100


def get_held_tickers(positions):
    """Return set of tickers already held so we don't pyramid the same market every hour."""
    return {p['ticker'] for p in positions if p.get('ticker')}


def check_settlements():
    try:
        from kalshi.execution.outcome_tracker import OutcomeTracker
        tracker = OutcomeTracker()
        resolved = tracker.check_settlements()
        if resolved:
            print(f"  Settlements: {len(resolved)} trades resolved")
            return resolved
        return []
    except Exception as e:
        print(f"  Settlement check error: {e}")
        return []


def check_news_signals():
    try:
        from kalshi.news_monitor import NewsMonitor
        monitor = NewsMonitor()
        signals = monitor.get_market_signals()
        if signals.get('actionable'):
            print(f"  News: {signals.get('overall_sentiment').upper()} - {len(signals.get('news_signals', []))} signals")
            return signals
        print("  News: No actionable signals")
        return None
    except Exception as e:
        print(f"  News check error: {e}")
        return None


def scan_broad_liquid_markets():
    """Scan broad, liquid non-sports markets with actual posted asks."""
    try:
        from kalshi.broad_scanner import BroadScanner
        scanner = BroadScanner()
        markets = scanner.get_interesting_markets(min_volume=10000, max_spread=6.0)
        print(f"  Broad liquid markets: {len(markets)}")
        return markets
    except Exception as e:
        print(f"Broad scan error: {e}")
        return []


def scan_weather():
    try:
        from kalshi.weather_scanner import WeatherScanner
        scanner = WeatherScanner()
        opps = scanner.scan()
        return [o for o in opps if abs(o.edge) >= 0.08][:5]
    except Exception as e:
        print(f"Weather scan error: {e}")
        return []


def scan_economics():
    all_opps = []
    try:
        from kalshi.gdp_scanner import GDPScanner
        scanner = GDPScanner()
        opps = scanner.scan()
        all_opps.extend([o for o in opps if abs(o.edge) >= 0.08][:3])
    except Exception as e:
        print(f"GDP scan error: {e}")
    try:
        from kalshi.cpi_scanner import CPIScanner
        scanner = CPIScanner()
        opps = scanner.scan()
        all_opps.extend([o for o in opps if abs(o.edge) >= 0.08][:3])
    except Exception as e:
        print(f"CPI scan error: {e}")
    try:
        from kalshi.fed_scanner import FedScanner
        scanner = FedScanner()
        opps = scanner.scan()
        all_opps.extend([o for o in opps if abs(o.edge) >= 0.08][:3])
    except Exception as e:
        print(f"Fed scan error: {e}")
    return all_opps


def scan_pairs():
    try:
        from kalshi.pairs_scanner import PairsScanner
        scanner = PairsScanner()
        scanner.record_prices()
        opps = scanner.scan_all()
        return [o for o in opps if o.confidence in ['HIGH', 'MEDIUM'] and abs(o.z_score) >= 2.5][:3]
    except Exception as e:
        print(f"Pairs scan error: {e}")
        return []


def run_validation_check():
    try:
        from kalshi.validation.bootstrap import BootstrapValidator
        from kalshi.validation.feature_importance import FeatureImportanceTracker

        validator = BootstrapValidator()
        trades = validator.load_resolved_trades()
        if len(trades) >= 20:
            result = validator.validate(n_simulations=5000)
            return {
                'bootstrap': {
                    'win_rate': result.observed_win_rate,
                    'ci': [result.win_rate_ci_lower, result.win_rate_ci_upper],
                    'edge_is_real': result.edge_is_real,
                    'verdict': result.verdict,
                }
            }

        tracker = FeatureImportanceTracker()
        signals = tracker.load_signal_outcomes()
        if len(signals) >= 10:
            report = tracker.generate_report()
            return {
                'feature_importance': {
                    'best_signal': report.best_signal,
                    'amplify': report.amplify,
                    'reduce': report.reduce,
                }
            }

        return {'status': f'{len(trades)} trades, {len(signals)} signals - need more data'}
    except Exception as e:
        return {'error': str(e)}


def run_scan(notify: bool = True):
    from kalshi.kalshi_client import KalshiClient

    timestamp = datetime.now(timezone.utc)
    print(f"[{timestamp.strftime('%H:%M')} UTC] Hourly scan starting...")

    settlements = check_settlements()
    news_signals = None
    if timestamp.hour % 4 == 0:
        news_signals = check_news_signals()

    positions, balance = get_positions()
    held_tickers = get_held_tickers(positions)
    print(f"  Positions: {len(positions)}, Balance: ${balance:,.2f}")
    if held_tickers:
        print(f"  Already held: {len(held_tickers)} tickers")

    # PRIORITY 1: broad liquid markets
    broad_markets = scan_broad_liquid_markets()

    # PRIORITY 2: legacy niche scanners
    weather_opps = scan_weather()
    print(f"  Weather opportunities: {len(weather_opps)}")
    econ_opps = []
    if 12 <= timestamp.hour <= 22:
        econ_opps = scan_economics()
        print(f"  Economics opportunities: {len(econ_opps)}")

    pairs_opps = scan_pairs()
    if pairs_opps:
        print(f"  Pairs opportunities: {len(pairs_opps)}")

    trades_made = []
    daily_spend = 0
    DAILY_LIMIT = 0.0  # Paused by Chris: watch-only mode, no auto-trading
    creds = load_kalshi_creds()
    client = KalshiClient(api_key_id=creds['api_key_id'], private_key_pem=creds['private_key'])

    # Auto-trade broad markets only if they are already obviously buyable.
    # For now, we shortlist them for human review rather than inventing estimates.
    shortlist = []
    focus_keywords = [
        'SpaceX', 'Mars', 'Starship', 'IPO', 'GTA', 'recession', 'Fed',
        'oil', 'Iran', 'Saudi', 'Israel', 'Taiwan', 'OpenAI', 'Anthropic'
    ]
    for m in broad_markets[:60]:
        hay = f"{m.ticker} {m.title} {m.category}".lower()
        if any(k.lower() in hay for k in focus_keywords):
            shortlist.append(m)

    print(f"  Broad shortlist: {len(shortlist)}")
    for m in shortlist[:10]:
        sides = []
        if m.can_buy_yes:
            sides.append(f"YES@{m.yes_ask*100:.0f}¢")
        if m.can_buy_no:
            sides.append(f"NO@{m.no_ask*100:.0f}¢")
        held_flag = " [HELD]" if m.ticker in held_tickers else ""
        print(f"  Shortlist: {m.ticker}{held_flag} | {m.title[:40]} | Vol {m.volume:,} | Spread {m.spread:.0f}¢ | {' / '.join(sides)}")

    # Existing evaluator path for niche scanners
    all_opps = list(weather_opps) + list(econ_opps)
    all_opps.sort(key=lambda x: abs(x.edge), reverse=True)

    evaluated_opps = []
    for opp in all_opps[:10]:
        try:
            from kalshi.opportunity_evaluator import OpportunityEvaluator
            evaluator = OpportunityEvaluator()
            decision = evaluator.evaluate(
                ticker=opp.ticker,
                market_price=opp.market_price,
                our_estimate=opp.market_price + opp.edge,
                max_position=50.0,
            )
            if decision and decision.should_trade:
                opp.eval_decision = decision
                evaluated_opps.append(opp)
            elif decision:
                print(f"  Filtered: {opp.ticker} - {decision.reasoning}")
        except Exception as e:
            print(f"Evaluation error: {e}")

    if evaluated_opps:
        print(f"  Passed evaluation: {len(evaluated_opps)}/{len(all_opps[:10])}")

    if DAILY_LIMIT <= 0:
        print("  Auto-trading paused by Chris — watch-only mode")
    
    for opp in evaluated_opps:
        if daily_spend >= DAILY_LIMIT:
            print(f"  Daily limit reached (${DAILY_LIMIT})")
            break

        if opp.ticker in held_tickers:
            print(f"  Skip duplicate: already holding {opp.ticker}")
            continue

        decision = opp.eval_decision
        if not (decision and decision.should_trade and decision.position_size > 0):
            continue

        trade_size = min(decision.position_size, DAILY_LIMIT - daily_spend)
        side = 'yes' if opp.edge > 0 else 'no'

        try:
            event_guess = opp.ticker if opp.ticker.count('-') <= 1 else '-'.join(opp.ticker.split('-')[:-1])
            try:
                event = client._request('GET', f'/events/{event_guess}')
                market = next((m for m in event.get('markets', []) if m.get('ticker') == opp.ticker), None)
            except Exception:
                market = client._request('GET', f'/markets/{opp.ticker}')

            if not market:
                print(f"  Could not load market for {opp.ticker}")
                continue

            ask_cents = int(float(market.get('yes_ask_dollars' if side == 'yes' else 'no_ask_dollars', 0) or 0) * 100)
            if ask_cents <= 0:
                print(f"  No ask for {opp.ticker} {side.upper()} side")
                continue

            contracts = int(trade_size * 100 / ask_cents)
            if contracts <= 0:
                continue

            order = client._request('POST', '/portfolio/orders', data={
                'ticker': opp.ticker,
                'action': 'buy',
                'side': side,
                'type': 'limit',
                'count': contracts,
                'yes_price' if side == 'yes' else 'no_price': ask_cents,
            })

            actual_cost = contracts * ask_cents / 100
            daily_spend += actual_cost
            trades_made.append({
                'ticker': opp.ticker,
                'side': side,
                'contracts': contracts,
                'price_cents': ask_cents,
                'cost': actual_cost,
                'order_id': order.get('order', {}).get('order_id'),
            })
            print(f"  🔔 TRADED: {contracts}x {opp.ticker} {side.upper()} @ {ask_cents}¢")
        except Exception as e:
            print(f"  Trade error ({opp.ticker}): {e}")

    if trades_made:
        print(f"  Trades placed: {len(trades_made)}")
    else:
        print("  No trades placed")

    if timestamp.hour in [0, 6, 12, 18]:
        validation = run_validation_check()
        print(f"  Validation: {validation}")

    log_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/scan_logs')
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"hourly_{timestamp.strftime('%Y-%m-%d')}.jsonl"
    record = {
        'timestamp': timestamp.isoformat(),
        'positions': len(positions),
        'balance': balance,
        'broad_markets': len(broad_markets),
        'shortlist': [m.ticker for m in shortlist[:15]],
        'opportunities': len(all_opps),
        'trades_made': trades_made,
    }
    with open(log_file, 'a') as f:
        f.write(json.dumps(record) + '\n')

    print(f"  Scan complete: {len(broad_markets)} broad liquid markets, {len(all_opps)} niche opportunities")
    return {'broad_markets': broad_markets, 'shortlist': shortlist, 'trades_made': trades_made}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-notify', action='store_true')
    args = parser.parse_args()
    run_scan(notify=not args.no_notify)
