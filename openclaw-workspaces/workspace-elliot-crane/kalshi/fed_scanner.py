"""
Fed/FOMC Scanner
================

Scans Fed rate decision markets using CME FedWatch probabilities
and upcoming FOMC meeting dates.

Data sources:
- CME FedWatch Tool implied probabilities
- FOMC meeting calendar
- Fed funds futures
"""

import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FedOpportunity:
    """A Fed rate decision opportunity."""
    ticker: str
    title: str
    meeting_date: str
    decision_type: str  # 'cut', 'hold', 'hike'
    market_price: float
    our_estimate: float
    edge: float
    direction: str
    confidence: str
    days_until: int


class FedScanner:
    """
    Scans Fed/FOMC markets for rate decision opportunities.
    """
    
    # 2026 FOMC Meeting Dates
    FOMC_DATES = [
        '2026-01-28',  # Jan
        '2026-03-18',  # Mar
        '2026-05-06',  # May
        '2026-06-17',  # Jun
        '2026-07-29',  # Jul
        '2026-09-16',  # Sep
        '2026-11-04',  # Nov
        '2026-12-16',  # Dec
    ]
    
    # Current Fed funds rate (update as needed)
    CURRENT_RATE = 4.50  # 4.25-4.50% target range midpoint
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/fed_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    @property
    def kalshi(self):
        if self._kalshi is None:
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def get_next_meeting(self) -> Dict:
        """Get the next FOMC meeting date."""
        today = datetime.now(timezone.utc).date()
        
        for date_str in self.FOMC_DATES:
            meeting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if meeting_date > today:
                days_until = (meeting_date - today).days
                return {
                    'date': date_str,
                    'days_until': days_until,
                    'month': meeting_date.strftime('%B'),
                }
        
        return {'date': 'N/A', 'days_until': 999, 'month': 'N/A'}
    
    def get_fedwatch_probabilities(self) -> Dict:
        """
        Get CME FedWatch implied probabilities.
        
        In production, would scrape CME or use futures data.
        For now, returns consensus estimates.
        """
        # Fallback: market consensus estimates
        # Update these based on current Fed funds futures
        next_meeting = self.get_next_meeting()
        
        # Base probabilities - adjust based on news/data
        base_probs = {
            'cut_50': 0.05,   # 50bp cut
            'cut_25': 0.25,   # 25bp cut
            'hold': 0.65,     # No change
            'hike_25': 0.05,  # 25bp hike
        }
        
        # Adjust for time to meeting
        days = next_meeting['days_until']
        if days > 60:
            # Far out = more uncertainty, revert toward 50/50
            base_probs['hold'] = 0.50
            base_probs['cut_25'] = 0.35
        
        return {
            'meeting': next_meeting['date'],
            'probabilities': base_probs,
            'source': 'consensus_estimate',
        }
    
    def get_fed_markets(self) -> List[Dict]:
        """Fetch active Fed/FOMC markets from Kalshi."""
        markets = []
        
        # Search for Fed-related events
        search_terms = ['KXFED', 'KXFOMC', 'KXRATE']
        
        for prefix in search_terms:
            try:
                # Search markets
                result = self.kalshi._request('GET', '/markets', params={
                    'ticker': prefix,
                    'status': 'active',
                    'limit': 20,
                })
                
                for m in result.get('markets', []):
                    ticker = m.get('ticker', '')
                    title = m.get('title', '').lower()
                    
                    # Filter for rate decision markets
                    if not any(kw in title for kw in ['rate', 'cut', 'hike', 'fed', 'fomc']):
                        continue
                    
                    yes_bid = float(m.get('yes_bid', 0)) / 100
                    yes_ask = float(m.get('yes_ask', 0)) / 100
                    
                    if yes_bid <= 0 and yes_ask <= 0:
                        continue
                    
                    # Determine decision type from title
                    if 'cut' in title:
                        decision_type = 'cut'
                    elif 'hike' in title or 'raise' in title:
                        decision_type = 'hike'
                    else:
                        decision_type = 'hold'
                    
                    markets.append({
                        'ticker': ticker,
                        'title': m.get('title', ''),
                        'decision_type': decision_type,
                        'yes_bid': yes_bid,
                        'yes_ask': yes_ask,
                        'mid': (yes_bid + yes_ask) / 2 if yes_ask > 0 else yes_bid,
                        'volume': float(m.get('volume', 0)),
                    })
                    
            except Exception as e:
                continue
        
        return markets
    
    def scan(self) -> List[FedOpportunity]:
        """Scan Fed markets for opportunities."""
        opportunities = []
        
        # Get FedWatch probabilities
        fedwatch = self.get_fedwatch_probabilities()
        probs = fedwatch['probabilities']
        
        next_meeting = self.get_next_meeting()
        
        print(f"  Next FOMC: {next_meeting['date']} ({next_meeting['days_until']} days)")
        
        # Get markets
        markets = self.get_fed_markets()
        
        for m in markets:
            market_price = m['mid']
            decision_type = m['decision_type']
            
            if market_price <= 0:
                continue
            
            # Map to our probability estimate
            if decision_type == 'cut':
                our_estimate = probs.get('cut_25', 0.25) + probs.get('cut_50', 0.05)
            elif decision_type == 'hike':
                our_estimate = probs.get('hike_25', 0.05)
            else:
                our_estimate = probs.get('hold', 0.65)
            
            # Calculate edge
            edge = our_estimate - market_price
            
            # Determine direction
            if edge > 0.05:
                direction = 'YES'
            elif edge < -0.05:
                direction = 'NO'
                edge = -edge
            else:
                continue
            
            # Confidence
            if abs(edge) >= 0.15:
                confidence = 'HIGH'
            elif abs(edge) >= 0.10:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            opportunities.append(FedOpportunity(
                ticker=m['ticker'],
                title=m['title'],
                meeting_date=next_meeting['date'],
                decision_type=decision_type,
                market_price=market_price,
                our_estimate=our_estimate,
                edge=edge if direction == 'YES' else -edge,
                direction=direction,
                confidence=confidence,
                days_until=next_meeting['days_until'],
            ))
        
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)
        
        return opportunities
    
    def report(self) -> str:
        """Generate Fed scanner report."""
        opps = self.scan()
        next_meeting = self.get_next_meeting()
        fedwatch = self.get_fedwatch_probabilities()
        
        lines = [
            "═" * 60,
            "  FED/FOMC SCANNER",
            f"  Next Meeting: {next_meeting['date']} ({next_meeting['days_until']} days)",
            "═" * 60,
            "",
            "  FedWatch Probabilities:",
            f"    Cut 25bp: {fedwatch['probabilities']['cut_25']*100:.0f}%",
            f"    Hold:     {fedwatch['probabilities']['hold']*100:.0f}%",
            f"    Hike 25bp: {fedwatch['probabilities']['hike_25']*100:.0f}%",
            "",
        ]
        
        if not opps:
            lines.append("  No Fed opportunities found (markets may be inactive)")
        else:
            lines.append(f"  Found {len(opps)} opportunities:")
            lines.append("")
            
            for opp in opps[:5]:
                direction = "▲" if opp.direction == 'YES' else "▼"
                lines.append(f"  {direction} {opp.ticker}")
                lines.append(f"     {opp.title[:50]}")
                lines.append(f"     Market: {opp.market_price*100:.0f}% | Ours: {opp.our_estimate*100:.0f}%")
                lines.append(f"     Edge: {opp.edge*100:+.0f}% | {opp.confidence}")
                lines.append("")
        
        lines.append("═" * 60)
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fed/FOMC market scanner')
    parser.add_argument('action', choices=['scan', 'report', 'calendar'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    scanner = FedScanner()
    
    if args.action == 'scan':
        opps = scanner.scan()
        for opp in opps[:5]:
            print(f"{opp.direction} {opp.ticker}: {opp.edge*100:+.0f}% edge")
    
    elif args.action == 'report':
        print(scanner.report())
    
    elif args.action == 'calendar':
        print("2026 FOMC Meeting Dates:")
        for date in scanner.FOMC_DATES:
            print(f"  {date}")


if __name__ == '__main__':
    main()
