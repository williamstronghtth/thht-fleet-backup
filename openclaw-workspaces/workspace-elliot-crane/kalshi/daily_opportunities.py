#!/usr/bin/env python3
"""
Daily Opportunity Scan
Proactively finds interesting markets and sends analysis to Chris.
Runs at 9am UTC (4am ET / 5am ET DST).
"""

import sys
import subprocess
from datetime import datetime, timezone
from typing import List, Dict

sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')

from kalshi.kalshi_client import KalshiClient
from kalshi.broad_scanner import BroadScanner


def send_telegram(message: str, chat_id: str = "8560812913"):
    """Send to Telegram."""
    try:
        result = subprocess.run(
            ['openclaw', 'message', 'send', 
             '--channel', 'telegram',
             '--account', 'william',
             '--target', chat_id,
             '--message', message],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def get_portfolio_summary() -> Dict:
    """Get current portfolio status."""
    client = KalshiClient()
    
    positions = client._request('GET', '/portfolio/positions')
    balance = client._request('GET', '/portfolio/balance')
    
    active = []
    for pos in positions.get('market_positions', []):
        qty = float(pos.get('position_fp', 0))
        if qty > 0:
            ticker = pos.get('ticker')
            
            # Get current price
            try:
                # Try to get from events endpoint
                event_ticker = '-'.join(ticker.split('-')[:-1]) if ticker.count('-') > 1 else ticker
                event = client._request('GET', f'/events/{event_ticker}')
                for m in event.get('markets', []):
                    if m.get('ticker') == ticker:
                        bid = float(m.get('yes_bid_dollars', 0) or 0)
                        active.append({
                            'ticker': ticker,
                            'contracts': int(qty),
                            'current_bid': bid,
                            'value': qty * bid,
                        })
                        break
            except:
                active.append({
                    'ticker': ticker,
                    'contracts': int(qty),
                    'current_bid': 0,
                    'value': 0,
                })
    
    return {
        'positions': active,
        'cash': float(balance.get('balance', 0)) / 100,
        'total_value': sum(p['value'] for p in active),
    }


def find_opportunities() -> List[Dict]:
    """Find interesting markets to potentially trade."""
    scanner = BroadScanner()
    markets = scanner.get_interesting_markets(min_volume=10000)
    
    # Categorize opportunities
    opportunities = []
    
    # Focus on categories we can analyze
    focus_categories = ['Economics', 'Politics', 'Science and Technology', 
                       'Climate and Weather', 'Financials', 'Companies']
    
    for m in markets[:50]:  # Check top 50
        if m.category in focus_categories:
            opportunities.append({
                'ticker': m.ticker,
                'title': m.title,
                'category': m.category,
                'mid_price': m.mid_price,
                'volume': m.volume,
                'spread': m.spread,
            })
    
    return opportunities[:15]  # Top 15


def format_daily_report(portfolio: Dict, opportunities: List[Dict]) -> str:
    """Format the daily report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    lines = [
        f"🎯 <b>ELLIOT DAILY SCAN — {timestamp}</b>",
        "",
    ]
    
    # Portfolio summary
    lines.append("<b>📊 PORTFOLIO</b>")
    if portfolio['positions']:
        total_position_value = 0
        for p in portfolio['positions']:
            value_str = f"(${p['value']:.2f})" if p['value'] > 0 else ""
            lines.append(f"  • {p['ticker'][:30]}: {p['contracts']} contracts {value_str}")
            total_position_value += p['value']
        lines.append(f"  💵 Cash: ${portfolio['cash']:,.2f}")
        lines.append(f"  📈 Total: ~${portfolio['cash'] + total_position_value:,.2f}")
    else:
        lines.append(f"  No positions. Cash: ${portfolio['cash']:,.2f}")
    lines.append("")
    
    # Opportunities
    if opportunities:
        lines.append("<b>🔍 INTERESTING MARKETS</b>")
        
        # Group by category
        by_cat = {}
        for opp in opportunities:
            cat = opp['category']
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(opp)
        
        for cat, opps in by_cat.items():
            lines.append(f"<b>{cat}:</b>")
            for opp in opps[:3]:
                lines.append(f"  • {opp['ticker']}")
                lines.append(f"    {opp['title'][:40]}")
                lines.append(f"    Mid: {opp['mid_price']*100:.0f}% | Vol: {opp['volume']:,}")
            lines.append("")
    
    lines.append("Reply with a ticker to analyze, or 'scan' for full report.")
    
    return "\n".join(lines)


def run_daily_scan(notify: bool = True):
    """Run the daily opportunity scan."""
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M UTC')}] Daily scan starting...")
    
    # Get portfolio
    portfolio = get_portfolio_summary()
    print(f"  Portfolio: {len(portfolio['positions'])} positions, ${portfolio['cash']:,.2f} cash")
    
    # Find opportunities
    opportunities = find_opportunities()
    print(f"  Found {len(opportunities)} interesting markets")
    
    # Format and send report
    if notify:
        message = format_daily_report(portfolio, opportunities)
        success = send_telegram(message)
        print(f"  Telegram: {'✅' if success else '❌'}")
    
    return portfolio, opportunities


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-notify', action='store_true')
    args = parser.parse_args()
    
    run_daily_scan(notify=not args.no_notify)
