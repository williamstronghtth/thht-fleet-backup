"""
CPI Scanner
===========

Uses Cleveland Fed Inflation Nowcast to find edge in CPI markets.

Data source: https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting
The Cleveland Fed updates their nowcast daily with estimates for current month CPI.
"""

import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CPIOpportunity:
    """A CPI trading opportunity."""
    ticker: str
    title: str
    threshold: float  # e.g., 0.5 for "CPI > 0.5%"
    market_price: float
    our_estimate: float
    edge: float
    direction: str  # YES or NO
    nowcast_value: float
    confidence: str


class CPIScanner:
    """
    Scans CPI markets using Cleveland Fed nowcast data.
    """
    
    # Cleveland Fed Nowcast URL
    NOWCAST_URL = "https://www.clevelandfed.org/api/indicators/inflation-nowcasting/data"
    
    # Fallback: manual nowcast value (update periodically)
    FALLBACK_NOWCAST = {
        'cpi_monthly': 0.35,  # Current month CPI estimate (%)
        'cpi_annual': 3.2,    # Annual CPI estimate (%)
        'updated': '2026-03-30',
    }
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/cpi_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    @property
    def kalshi(self):
        if self._kalshi is None:
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def get_nowcast(self) -> Dict:
        """
        Fetch Cleveland Fed inflation nowcast.
        Returns dict with cpi_monthly, cpi_annual estimates.
        """
        try:
            response = requests.get(self.NOWCAST_URL, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Parse Cleveland Fed data format
                # They provide PCE and CPI nowcasts
                return self._parse_nowcast(data)
        except Exception as e:
            print(f"Cleveland Fed API error: {e}")
        
        # Fallback to manual value
        return self.FALLBACK_NOWCAST
    
    def _parse_nowcast(self, data: Dict) -> Dict:
        """Parse Cleveland Fed nowcast response."""
        try:
            # Extract latest CPI nowcast
            # Format varies - adapt as needed
            return {
                'cpi_monthly': data.get('cpi_monthly', self.FALLBACK_NOWCAST['cpi_monthly']),
                'cpi_annual': data.get('cpi_annual', self.FALLBACK_NOWCAST['cpi_annual']),
                'updated': datetime.now().strftime('%Y-%m-%d'),
            }
        except:
            return self.FALLBACK_NOWCAST
    
    def get_cpi_markets(self) -> List[Dict]:
        """Fetch active CPI markets from Kalshi."""
        markets = []
        
        # Search for CPI events
        try:
            # Get upcoming CPI events
            events = ['KXCPI-26APR', 'KXCPI-26MAY', 'KXCPI-26JUN']
            
            for event_ticker in events:
                try:
                    event = self.kalshi._request('GET', f'/events/{event_ticker}')
                    
                    for m in event.get('markets', []):
                        if m.get('status') != 'active':
                            continue
                        
                        ticker = m.get('ticker', '')
                        yes_bid = float(m.get('yes_bid', 0)) / 100
                        yes_ask = float(m.get('yes_ask', 0)) / 100
                        
                        if yes_bid <= 0 and yes_ask <= 0:
                            continue
                        
                        # Parse threshold from ticker (e.g., KXCPI-26APR-T0.5 -> 0.5)
                        threshold = self._parse_threshold(ticker)
                        
                        markets.append({
                            'ticker': ticker,
                            'title': m.get('title', ''),
                            'threshold': threshold,
                            'yes_bid': yes_bid,
                            'yes_ask': yes_ask,
                            'mid': (yes_bid + yes_ask) / 2 if yes_ask > 0 else yes_bid,
                            'volume': float(m.get('volume', 0)),
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error fetching CPI markets: {e}")
        
        return markets
    
    def _parse_threshold(self, ticker: str) -> float:
        """Parse CPI threshold from ticker."""
        # Format: KXCPI-26APR-T0.5 -> 0.5
        try:
            if '-T' in ticker:
                parts = ticker.split('-T')
                return float(parts[-1])
        except:
            pass
        return 0.0
    
    def calculate_probability(self, threshold: float, nowcast: float, 
                               std_dev: float = 0.15) -> float:
        """
        Calculate probability that CPI exceeds threshold.
        
        Uses normal distribution with nowcast as mean and historical std dev.
        """
        from math import erf, sqrt
        
        # Z-score
        z = (threshold - nowcast) / std_dev
        
        # Probability CPI > threshold (1 - CDF)
        prob = 0.5 * (1 - erf(z / sqrt(2)))
        
        return prob
    
    def scan(self) -> List[CPIOpportunity]:
        """
        Scan CPI markets for opportunities.
        """
        opportunities = []
        
        # Get nowcast
        nowcast = self.get_nowcast()
        nowcast_value = nowcast.get('cpi_monthly', 0.35)
        
        print(f"  CPI Nowcast: {nowcast_value:.2f}%")
        
        # Get markets
        markets = self.get_cpi_markets()
        
        for m in markets:
            threshold = m['threshold']
            market_price = m['mid']
            
            if market_price <= 0:
                continue
            
            # Calculate our probability estimate
            our_estimate = self.calculate_probability(threshold, nowcast_value)
            
            # Calculate edge
            edge = our_estimate - market_price
            
            # Determine direction
            if edge > 0.05:  # 5% edge for YES
                direction = 'YES'
            elif edge < -0.05:  # 5% edge for NO
                direction = 'NO'
                edge = -edge  # Make positive for comparison
            else:
                continue  # No edge
            
            # Confidence based on edge magnitude
            if abs(edge) >= 0.15:
                confidence = 'HIGH'
            elif abs(edge) >= 0.10:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            opportunities.append(CPIOpportunity(
                ticker=m['ticker'],
                title=m['title'],
                threshold=threshold,
                market_price=market_price,
                our_estimate=our_estimate,
                edge=edge if direction == 'YES' else -edge,
                direction=direction,
                nowcast_value=nowcast_value,
                confidence=confidence,
            ))
        
        # Sort by edge
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)
        
        return opportunities
    
    def report(self) -> str:
        """Generate CPI scanner report."""
        opps = self.scan()
        nowcast = self.get_nowcast()
        
        lines = [
            "═" * 60,
            "  CPI SCANNER",
            f"  Cleveland Fed Nowcast: {nowcast.get('cpi_monthly', 'N/A'):.2f}%",
            "═" * 60,
            "",
        ]
        
        if not opps:
            lines.append("  No CPI opportunities found")
        else:
            lines.append(f"  Found {len(opps)} opportunities:")
            lines.append("")
            
            for opp in opps[:10]:
                direction = "▲" if opp.direction == 'YES' else "▼"
                lines.append(f"  {direction} {opp.ticker}")
                lines.append(f"     Threshold: CPI > {opp.threshold}%")
                lines.append(f"     Market: {opp.market_price*100:.0f}% | Ours: {opp.our_estimate*100:.0f}%")
                lines.append(f"     Edge: {opp.edge*100:+.0f}% | {opp.confidence}")
                lines.append("")
        
        lines.append("═" * 60)
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CPI market scanner')
    parser.add_argument('action', choices=['scan', 'report', 'nowcast'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    scanner = CPIScanner()
    
    if args.action == 'scan':
        opps = scanner.scan()
        for opp in opps[:5]:
            print(f"{opp.direction} {opp.ticker}: {opp.edge*100:+.0f}% edge")
    
    elif args.action == 'report':
        print(scanner.report())
    
    elif args.action == 'nowcast':
        nowcast = scanner.get_nowcast()
        print(f"CPI Monthly: {nowcast.get('cpi_monthly', 'N/A')}%")
        print(f"CPI Annual: {nowcast.get('cpi_annual', 'N/A')}%")
        print(f"Updated: {nowcast.get('updated', 'N/A')}")


if __name__ == '__main__':
    main()
