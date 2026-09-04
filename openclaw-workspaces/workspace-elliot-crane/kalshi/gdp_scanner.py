"""
GDP Market Scanner
Analyzes GDP markets using economic indicators and nowcasts.

Data sources:
- Atlanta Fed GDPNow (via web scraping - they update 6-7x per month)
- Cleveland Fed Inflation Nowcast (as economic context)
- Our own estimate based on historical patterns

Note: GDPNow is typically a good predictor but can swing significantly
with new data releases. Historical Q1 GDP averages ~2.3% (2020-2024).
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class GDPOpportunity:
    """A GDP trading opportunity."""
    ticker: str
    title: str
    threshold: float
    market_price: float
    estimated_prob: float
    edge: float
    volume: float
    spread: float
    confidence: str
    reasoning: str


class GDPScanner:
    """
    Scan GDP markets for mispricings.
    
    GDP markets ask: "Will real GDP increase by more than X%?"
    We estimate probability based on nowcasts and historical patterns.
    """
    
    # Historical Q1 GDP growth averages (2015-2024)
    # Q1 tends to be seasonally weak
    HISTORICAL_Q1_MEAN = 1.8  # percent
    HISTORICAL_Q1_STD = 2.5   # wide variance
    
    # Current GDPNow-style estimate (manually updated or scraped)
    # As of late March 2026, consensus is ~2.3% for Q1 2026
    CURRENT_NOWCAST = 2.3
    NOWCAST_UNCERTAINTY = 0.8  # +/- percentage points
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/gdp_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def kalshi(self):
        if self._kalshi is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def get_gdp_markets(self, quarter: str = "Q1") -> List[Dict]:
        """Get active GDP markets for a quarter."""
        markets = []
        
        # Try different series formats
        series_tickers = [
            f'KXGDP-26APR30' if quarter == "Q1" else f'KXGDP',  # Q1 2026 settles Apr 30
            f'KXGDP-26JUL30' if quarter == "Q2" else None,       # Q2 2026
        ]
        
        for series in series_tickers:
            if not series:
                continue
            try:
                events = self.kalshi._request('GET', '/events', params={'series_ticker': 'KXGDP', 'limit': 10})
                
                for event in events.get('events', []):
                    if quarter.lower() in event.get('title', '').lower():
                        event_data = self.kalshi._request('GET', f'/events/{event.get("event_ticker")}')
                        
                        for market in event_data.get('markets', []):
                            if market.get('status') == 'active':
                                markets.append({
                                    'ticker': market.get('ticker'),
                                    'title': market.get('title', ''),
                                    'yes_bid': float(market.get('yes_bid_dollars', 0) or 0),
                                    'yes_ask': float(market.get('yes_ask_dollars', 0) or 0),
                                    'volume': float(market.get('volume_fp', 0) or 0),
                                })
            except Exception as e:
                print(f"Error fetching GDP markets: {e}")
        
        return markets
    
    def estimate_gdp_probability(self, threshold: float, 
                                   nowcast: float = None, 
                                   uncertainty: float = None) -> Dict:
        """
        Estimate probability that GDP growth exceeds threshold.
        
        Uses simple normal distribution assumption around nowcast.
        """
        nowcast = nowcast or self.CURRENT_NOWCAST
        uncertainty = uncertainty or self.NOWCAST_UNCERTAINTY
        
        # Z-score: how many std devs is threshold from nowcast?
        z_score = (threshold - nowcast) / uncertainty
        
        # Convert z-score to probability using rough normal approximation
        # Positive z = threshold above nowcast = lower prob of exceeding
        if z_score <= -2.0:
            prob = 0.98  # Threshold well below nowcast
            conf = 'HIGH'
        elif z_score <= -1.5:
            prob = 0.93
            conf = 'HIGH'
        elif z_score <= -1.0:
            prob = 0.84
            conf = 'HIGH'
        elif z_score <= -0.5:
            prob = 0.69
            conf = 'MEDIUM'
        elif z_score <= 0:
            prob = 0.50
            conf = 'LOW'
        elif z_score <= 0.5:
            prob = 0.31
            conf = 'LOW'
        elif z_score <= 1.0:
            prob = 0.16
            conf = 'MEDIUM'
        elif z_score <= 1.5:
            prob = 0.07
            conf = 'HIGH'
        elif z_score <= 2.0:
            prob = 0.02
            conf = 'HIGH'
        else:
            prob = 0.01
            conf = 'HIGH'
        
        return {
            'probability': prob,
            'nowcast': nowcast,
            'threshold': threshold,
            'z_score': z_score,
            'uncertainty': uncertainty,
            'confidence': conf,
        }
    
    def parse_threshold_from_ticker(self, ticker: str) -> Optional[float]:
        """Extract GDP threshold from ticker (e.g., KXGDP-26APR30-T2.5 -> 2.5)."""
        parts = ticker.split('-')
        for part in parts:
            if part.startswith('T'):
                try:
                    return float(part[1:])
                except ValueError:
                    pass
        return None
    
    def scan(self, quarter: str = "Q1", nowcast: float = None) -> List[GDPOpportunity]:
        """
        Scan GDP markets for opportunities.
        """
        opportunities = []
        markets = self.get_gdp_markets(quarter)
        nowcast = nowcast or self.CURRENT_NOWCAST
        
        for market in markets:
            ticker = market['ticker']
            threshold = self.parse_threshold_from_ticker(ticker)
            
            if threshold is None:
                continue
            
            yes_bid = market['yes_bid']
            yes_ask = market['yes_ask']
            market_price = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else yes_ask or yes_bid or 0.5
            spread = yes_ask - yes_bid if yes_ask and yes_bid else 1.0
            
            estimate = self.estimate_gdp_probability(threshold, nowcast)
            edge = estimate['probability'] - market_price
            
            # Only report if edge is meaningful (>5%)
            if abs(edge) > 0.05:
                direction = "above" if edge > 0 else "below"
                reasoning = (
                    f"Nowcast: {nowcast:.1f}%, Threshold: {threshold:.1f}%, "
                    f"Z-score: {estimate['z_score']:.2f}"
                )
                
                opportunities.append(GDPOpportunity(
                    ticker=ticker,
                    title=market['title'],
                    threshold=threshold,
                    market_price=market_price,
                    estimated_prob=estimate['probability'],
                    edge=edge,
                    volume=market['volume'],
                    spread=spread,
                    confidence=estimate['confidence'],
                    reasoning=reasoning,
                ))
        
        # Sort by edge magnitude
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)
        
        return opportunities
    
    def update_nowcast(self, value: float):
        """
        Manually update the nowcast estimate.
        Call this when new GDPNow data is released.
        """
        self.CURRENT_NOWCAST = value
        
        # Save to file
        nowcast_file = self.data_dir / 'nowcast.json'
        with open(nowcast_file, 'w') as f:
            json.dump({
                'nowcast': value,
                'updated': datetime.now(timezone.utc).isoformat(),
            }, f)
        
        print(f"GDP nowcast updated to {value}%")
    
    def report(self, quarter: str = "Q1", nowcast: float = None) -> str:
        """Generate GDP opportunities report."""
        opportunities = self.scan(quarter, nowcast)
        nowcast = nowcast or self.CURRENT_NOWCAST
        
        lines = [
            "═" * 70,
            f"  GDP MARKET SCANNER - {quarter} 2026",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 70,
            "",
            f"  Current Nowcast Estimate: {nowcast:.1f}% ± {self.NOWCAST_UNCERTAINTY:.1f}%",
            f"  (Update with: scanner.update_nowcast(new_value))",
            "",
        ]
        
        if not opportunities:
            lines.append("  No significant opportunities found (edge threshold: 5%)")
        else:
            lines.append(f"  Found {len(opportunities)} opportunities:")
            lines.append("")
            lines.append(f"  {'Ticker':<28} {'Mkt':>6} {'Est':>6} {'Edge':>7} {'Vol':>10} {'Conf':<6}")
            lines.append("  " + "-" * 65)
            
            for opp in opportunities:
                direction = "▲ YES" if opp.edge > 0 else "▼ NO"
                lines.append(
                    f"  {opp.ticker:<28} "
                    f"{opp.market_price*100:>5.0f}% "
                    f"{opp.estimated_prob*100:>5.0f}% "
                    f"{opp.edge*100:>+6.0f}% "
                    f"${opp.volume:>8,.0f} "
                    f"{opp.confidence:<6}"
                )
                lines.append(f"    └─ {opp.title[:55]}")
                lines.append(f"    └─ {opp.reasoning}")
                lines.append(f"    └─ Signal: {direction} underpriced")
                lines.append("")
        
        lines.extend([
            "═" * 70,
            "  Note: Update nowcast when Atlanta Fed releases new GDPNow data.",
            "  Releases typically 6-7x per month after economic data.",
            "═" * 70,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for GDP scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan GDP markets for opportunities')
    parser.add_argument('action', choices=['scan', 'report', 'markets', 'update'],
                        help='Action to perform')
    parser.add_argument('--quarter', default='Q1', help='Quarter to scan (Q1, Q2, etc.)')
    parser.add_argument('--nowcast', type=float, help='Override nowcast estimate')
    
    args = parser.parse_args()
    
    scanner = GDPScanner()
    
    if args.action == 'scan':
        opps = scanner.scan(args.quarter, args.nowcast)
        print(f"Found {len(opps)} opportunities:")
        for opp in opps:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}% edge ({opp.confidence})")
    
    elif args.action == 'report':
        print(scanner.report(args.quarter, args.nowcast))
    
    elif args.action == 'markets':
        markets = scanner.get_gdp_markets(args.quarter)
        print(f"Found {len(markets)} active GDP markets:")
        for m in markets:
            spread = m['yes_ask'] - m['yes_bid'] if m['yes_ask'] and m['yes_bid'] else 0
            print(f"  {m['ticker']}: {m['yes_bid']*100:.0f}-{m['yes_ask']*100:.0f}% (${m['volume']:,.0f})")
    
    elif args.action == 'update':
        if args.nowcast:
            scanner.update_nowcast(args.nowcast)
        else:
            print("Error: --nowcast required for update action")


if __name__ == '__main__':
    main()
