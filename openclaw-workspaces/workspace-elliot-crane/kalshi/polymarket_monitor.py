"""
Polymarket Price Monitor
Tracks Polymarket for cross-platform intelligence.

KEY FINDING (2026-03-27): Polymarket has NO active CPI/inflation/Fed markets.
Their focus is: sports, politics, crypto, memes.
Cross-platform arb for economics is NOT currently available.

This module remains ready for when/if Polymarket adds economics markets.
For now, we use it to monitor high-volume political markets that might
correlate with economic sentiment (e.g., election → policy → inflation).
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass  
class PolymarketSnapshot:
    """Snapshot of a Polymarket market."""
    question: str
    yes_price: float
    volume_24h: float
    condition_id: str
    category: str
    timestamp: str


class PolymarketMonitor:
    """
    Monitor Polymarket for market intelligence.
    
    Current status: No direct economics overlap with Kalshi.
    Use for: sentiment signals, high-volume market monitoring.
    """
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    
    # Keywords for economics-adjacent markets
    ECONOMICS_KEYWORDS = ['inflation', 'cpi', 'fed', 'rate cut', 'recession', 'gdp', 'tariff', 'economy']
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/polymarket_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_file = self.data_dir / 'latest_snapshot.json'
    
    def _parse_price(self, outcome_prices) -> float:
        """Parse outcomePrices which can be a list or JSON string."""
        if not outcome_prices:
            return 0.5
        
        if isinstance(outcome_prices, str):
            try:
                import json
                outcome_prices = json.loads(outcome_prices)
            except:
                return 0.5
        
        if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
            try:
                return float(outcome_prices[0])
            except:
                return 0.5
        
        return 0.5
    
    def get_all_markets(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Fetch active Polymarket markets."""
        try:
            response = requests.get(
                f"{self.GAMMA_API}/markets",
                params={"limit": limit, "active": True, "closed": False},
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching Polymarket: {e}")
            return []
    
    def find_economics_markets(self) -> List[Dict[str, Any]]:
        """
        Search for economics-related markets.
        NOTE: As of 2026-03-27, Polymarket has ~0 pure economics markets.
        """
        markets = self.get_all_markets()
        
        matches = []
        for m in markets:
            q = m.get('question', '').lower()
            if any(kw in q for kw in self.ECONOMICS_KEYWORDS):
                matches.append(m)
        
        return matches
    
    def get_top_volume_markets(self, n: int = 20) -> List[Dict[str, Any]]:
        """Get highest volume markets (most liquid, best price discovery)."""
        markets = self.get_all_markets()
        
        # Sort by 24h volume
        by_vol = sorted(
            markets, 
            key=lambda x: float(x.get('volume24hr', 0) or 0), 
            reverse=True
        )
        
        return by_vol[:n]
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of Polymarket state.
        Useful for tracking sentiment shifts over time.
        """
        markets = self.get_all_markets()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Categorize
        economics = []
        politics = []
        sports = []
        crypto = []
        other = []
        
        for m in markets:
            q = m.get('question', '').lower()
            cat = m.get('category', '').lower()
            
            if any(kw in q for kw in self.ECONOMICS_KEYWORDS):
                economics.append(m)
            elif 'election' in q or 'president' in q or 'political' in cat:
                politics.append(m)
            elif 'win' in q and any(x in q for x in ['nba', 'nfl', 'fifa', 'world cup']):
                sports.append(m)
            elif 'bitcoin' in q or 'ethereum' in q or 'crypto' in cat:
                crypto.append(m)
            else:
                other.append(m)
        
        snapshot = {
            'timestamp': timestamp,
            'total_markets': len(markets),
            'by_category': {
                'economics': len(economics),
                'politics': len(politics),
                'sports': len(sports),
                'crypto': len(crypto),
                'other': len(other),
            },
            'top_10_volume': [
                {
                    'question': m.get('question', '')[:80],
                    'yes_price': self._parse_price(m.get('outcomePrices')),
                    'volume_24h': float(m.get('volume24hr', 0) or 0),
                }
                for m in self.get_top_volume_markets(10)
            ],
            'economics_markets': [
                {
                    'question': m.get('question', ''),
                    'yes_price': self._parse_price(m.get('outcomePrices')),
                    'volume_24h': float(m.get('volume24hr', 0) or 0),
                }
                for m in economics
            ]
        }
        
        # Save
        with open(self.snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return snapshot
    
    def report(self) -> str:
        """Generate Polymarket status report."""
        snapshot = self.snapshot()
        
        lines = [
            "═" * 60,
            "  POLYMARKET INTELLIGENCE REPORT",
            f"  {snapshot['timestamp'][:19]} UTC",
            "═" * 60,
            "",
            f"  Total Active Markets: {snapshot['total_markets']}",
            "",
            "  By Category:",
        ]
        
        for cat, count in snapshot['by_category'].items():
            lines.append(f"    {cat.capitalize():<12}: {count:>4}")
        
        lines.extend([
            "",
            "  ⚠️ Economics Markets: " + (
                f"{snapshot['by_category']['economics']} found"
                if snapshot['by_category']['economics'] > 0
                else "NONE (Polymarket doesn't focus on economics)"
            ),
            "",
            "  Top 10 by 24h Volume:",
        ])
        
        for m in snapshot['top_10_volume']:
            vol = m['volume_24h']
            price = m['yes_price']
            q = m['question'][:45]
            lines.append(f"    ${vol:>10,.0f} | {price*100:>3.0f}% | {q}")
        
        lines.extend([
            "",
            "═" * 60,
            "  Note: Cross-platform arb with Kalshi economics is NOT",
            "  available. Use this for political/sentiment signals.",
            "═" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for Polymarket monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Polymarket')
    parser.add_argument('action', choices=['snapshot', 'report', 'economics', 'top'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    monitor = PolymarketMonitor()
    
    if args.action == 'snapshot':
        snapshot = monitor.snapshot()
        print(f"📸 Snapshot saved: {snapshot['total_markets']} markets")
        print(f"   Economics: {snapshot['by_category']['economics']}")
    
    elif args.action == 'report':
        print(monitor.report())
    
    elif args.action == 'economics':
        markets = monitor.find_economics_markets()
        if markets:
            print(f"Found {len(markets)} economics-related markets:")
            for m in markets[:10]:
                print(f"  - {m.get('question', 'N/A')}")
        else:
            print("⚠️ No economics markets found on Polymarket.")
    
    elif args.action == 'top':
        markets = monitor.get_top_volume_markets(20)
        print("Top 20 by 24h volume:")
        for m in markets:
            vol = float(m.get('volume24hr', 0) or 0)
            q = m.get('question', 'N/A')[:50]
            print(f"  ${vol:>12,.0f} | {q}")


if __name__ == '__main__':
    main()
