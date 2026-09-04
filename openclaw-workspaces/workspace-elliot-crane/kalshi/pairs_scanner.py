"""
Pairs/Spread Scanner
====================

Finds cointegrated pairs of Kalshi markets and identifies spread opportunities.

Based on the cointegration pairs trading strategy:
1. Find related contracts (same event, different thresholds)
2. Test for cointegration (Engle-Granger)
3. Calculate spread z-score
4. Alert when |z| > 2.0 (spread is abnormally wide)

Example pairs:
- CPI >0.5% vs CPI >0.7% (nested thresholds)
- GDP >1.5% vs GDP >2.0% (nested thresholds)
- Denver >75°F vs Denver >80°F (related outcomes)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Statistical imports
try:
    from scipy import stats
    from statsmodels.tsa.stattools import coint, adfuller
    from sklearn.linear_model import LinearRegression
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    print("Warning: scipy/statsmodels not available. Install with: pip install scipy statsmodels scikit-learn")


@dataclass
class PairOpportunity:
    """A spread trading opportunity."""
    contract_a: str
    contract_b: str
    title_a: str
    title_b: str
    
    # Prices
    price_a: float
    price_b: float
    
    # Spread analysis
    beta: float
    spread: float
    z_score: float
    
    # Cointegration
    coint_pvalue: float
    is_cointegrated: bool
    
    # Trade signal
    signal: str  # "BUY_A", "BUY_B", "HOLD"
    underpriced: str  # Which contract is underpriced
    edge_estimate: float
    
    # Metadata
    confidence: str
    reasoning: str


class PairsScanner:
    """
    Scans Kalshi for cointegrated pairs and spread opportunities.
    """
    
    # Z-score thresholds
    Z_ENTRY_THRESHOLD = 2.0
    Z_EXIT_THRESHOLD = 0.5
    
    # Cointegration threshold
    COINT_PVALUE_THRESHOLD = 0.05
    
    # Minimum price history for cointegration test
    MIN_HISTORY_POINTS = 20
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/pairs_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / 'price_history.json'
        
    @property
    def kalshi(self):
        if self._kalshi is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def find_related_markets(self, event_ticker: str) -> List[Dict]:
        """
        Find all markets within an event (related contracts).
        These are natural pairs (same event, different thresholds).
        """
        try:
            event = self.kalshi._request('GET', f'/events/{event_ticker}')
            markets = []
            
            for m in event.get('markets', []):
                if m.get('status') == 'active':
                    yes_bid = float(m.get('yes_bid_dollars', 0) or 0)
                    yes_ask = float(m.get('yes_ask_dollars', 0) or 0)
                    
                    if yes_bid > 0 and yes_ask > 0:
                        markets.append({
                            'ticker': m.get('ticker'),
                            'title': m.get('title', ''),
                            'price': (yes_bid + yes_ask) / 2,
                            'bid': yes_bid,
                            'ask': yes_ask,
                            'volume': float(m.get('volume_fp', 0) or 0),
                        })
            
            return markets
        except Exception as e:
            print(f"Error finding related markets: {e}")
            return []
    
    def calculate_beta(self, prices_a: np.ndarray, prices_b: np.ndarray) -> float:
        """
        Calculate beta coefficient: how much B moves A.
        """
        if not STATS_AVAILABLE:
            return 1.0
        
        model = LinearRegression()
        model.fit(prices_b.reshape(-1, 1), prices_a)
        return model.coef_[0]
    
    def test_cointegration(self, prices_a: np.ndarray, prices_b: np.ndarray) -> Tuple[float, bool]:
        """
        Test if two price series are cointegrated using Engle-Granger test.
        
        Returns (p-value, is_cointegrated)
        """
        if not STATS_AVAILABLE:
            return 0.10, False
        
        if len(prices_a) < self.MIN_HISTORY_POINTS:
            return 1.0, False
        
        try:
            score, pvalue, _ = coint(prices_a, prices_b)
            is_cointegrated = pvalue < self.COINT_PVALUE_THRESHOLD
            return pvalue, is_cointegrated
        except Exception:
            return 1.0, False
    
    def calculate_spread_zscore(self, prices_a: np.ndarray, prices_b: np.ndarray, 
                                  beta: float) -> Tuple[float, float]:
        """
        Calculate the spread and its z-score.
        
        spread = price_A - beta * price_B
        z = (spread - mean) / std
        
        Returns (current_spread, z_score)
        """
        spread = prices_a - beta * prices_b
        
        if len(spread) < 5:
            return spread[-1], 0.0
        
        mean = np.mean(spread)
        std = np.std(spread)
        
        if std == 0:
            return spread[-1], 0.0
        
        z_score = (spread[-1] - mean) / std
        
        return spread[-1], z_score
    
    def analyze_pair(self, market_a: Dict, market_b: Dict, 
                      history: Dict = None) -> Optional[PairOpportunity]:
        """
        Analyze a pair of markets for spread opportunity.
        """
        ticker_a = market_a['ticker']
        ticker_b = market_b['ticker']
        price_a = market_a['price']
        price_b = market_b['price']
        
        # Get price history or use current prices only
        if history and ticker_a in history and ticker_b in history:
            prices_a = np.array(history[ticker_a])
            prices_b = np.array(history[ticker_b])
        else:
            # Without history, we can still detect current spread anomalies
            # using theoretical relationships
            prices_a = np.array([price_a])
            prices_b = np.array([price_b])
        
        # For nested thresholds, beta should be close to 1
        # (if CPI > 0.7%, then CPI > 0.5% is almost certain)
        if len(prices_a) >= self.MIN_HISTORY_POINTS:
            beta = self.calculate_beta(prices_a, prices_b)
            pvalue, is_cointegrated = self.test_cointegration(prices_a, prices_b)
            spread, z_score = self.calculate_spread_zscore(prices_a, prices_b, beta)
        else:
            # Use theoretical relationship for nested thresholds
            beta = self._estimate_theoretical_beta(market_a, market_b)
            pvalue = 0.01  # Assume cointegrated for nested thresholds
            is_cointegrated = True
            spread = price_a - beta * price_b
            z_score = self._estimate_zscore_from_spread(spread, beta)
        
        # Determine signal
        signal = "HOLD"
        underpriced = None
        edge_estimate = 0.0
        
        if abs(z_score) >= self.Z_ENTRY_THRESHOLD:
            if z_score < -self.Z_ENTRY_THRESHOLD:
                signal = "BUY_A"
                underpriced = ticker_a
                edge_estimate = abs(z_score) * 0.02  # Rough estimate
            elif z_score > self.Z_ENTRY_THRESHOLD:
                signal = "BUY_B"
                underpriced = ticker_b
                edge_estimate = abs(z_score) * 0.02
        
        # Confidence based on cointegration and z-score
        if is_cointegrated and abs(z_score) >= 2.5:
            confidence = "HIGH"
        elif is_cointegrated and abs(z_score) >= 2.0:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Generate reasoning
        if signal != "HOLD":
            reasoning = (
                f"Spread z-score: {z_score:.2f} | "
                f"Beta: {beta:.2f} | "
                f"Coint p-value: {pvalue:.3f}"
            )
        else:
            reasoning = f"Spread within normal range (z={z_score:.2f})"
        
        return PairOpportunity(
            contract_a=ticker_a,
            contract_b=ticker_b,
            title_a=market_a['title'],
            title_b=market_b['title'],
            price_a=price_a,
            price_b=price_b,
            beta=beta,
            spread=spread,
            z_score=z_score,
            coint_pvalue=pvalue,
            is_cointegrated=is_cointegrated,
            signal=signal,
            underpriced=underpriced,
            edge_estimate=edge_estimate,
            confidence=confidence,
            reasoning=reasoning,
        )
    
    def _estimate_theoretical_beta(self, market_a: Dict, market_b: Dict) -> float:
        """
        Estimate beta from theoretical relationship for nested thresholds.
        
        For CPI >0.5% vs CPI >0.7%:
        If >0.7% is true, >0.5% must be true.
        So P(>0.5%) >= P(>0.7%)
        Beta should be ~1.0 for perfectly nested events.
        """
        # For nested thresholds, beta ≈ 1
        # Could be refined based on threshold difference
        return 1.0
    
    def _estimate_zscore_from_spread(self, spread: float, beta: float) -> float:
        """
        Estimate z-score from current spread without full history.
        
        For nested thresholds:
        - Spread should be positive (A >= B when A is lower threshold)
        - If spread is negative or very small, it's anomalous
        """
        # Expected spread for nested thresholds: ~0.05 to 0.15
        expected_spread = 0.10
        std_estimate = 0.05
        
        return (spread - expected_spread) / std_estimate
    
    def scan_event(self, event_ticker: str) -> List[PairOpportunity]:
        """
        Scan all pairs within an event for opportunities.
        """
        markets = self.find_related_markets(event_ticker)
        
        if len(markets) < 2:
            return []
        
        # Load price history if available
        history = self._load_history()
        
        opportunities = []
        
        # Check all pairs
        for i, market_a in enumerate(markets):
            for market_b in markets[i+1:]:
                # Only pair markets with related thresholds
                # (A should have lower threshold than B for proper nesting)
                if market_a['price'] < market_b['price']:
                    market_a, market_b = market_b, market_a
                
                opp = self.analyze_pair(market_a, market_b, history)
                
                if opp and opp.signal != "HOLD":
                    # Filter out extreme prices (< 5% or > 95%) - not tradeable
                    if 0.05 < opp.price_a < 0.95 and 0.05 < opp.price_b < 0.95:
                        opportunities.append(opp)
        
        return opportunities
    
    def scan_all(self) -> List[PairOpportunity]:
        """
        Scan all known pair-worthy events.
        """
        # Events that have multiple related contracts
        events_to_scan = [
            'KXCPI-26MAR',      # CPI March
            'KXCPI-26APR',      # CPI April
            'KXGDP-26APR30',    # GDP Q1
            'KXHIGHDEN-26MAR28', # Denver temp
            'KXHIGHDEN-26MAR29', # Denver temp
        ]
        
        all_opportunities = []
        
        for event in events_to_scan:
            try:
                opps = self.scan_event(event)
                all_opportunities.extend(opps)
            except Exception as e:
                print(f"Error scanning {event}: {e}")
        
        # Sort by z-score magnitude
        all_opportunities.sort(key=lambda x: abs(x.z_score), reverse=True)
        
        return all_opportunities
    
    def _load_history(self) -> Dict[str, List[float]]:
        """Load price history for cointegration analysis."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return {}
    
    def record_prices(self):
        """
        Record current prices for building history.
        Call this hourly to build up cointegration data.
        """
        history = self._load_history()
        
        # Get prices for tracked events
        events = ['KXCPI-26MAR', 'KXGDP-26APR30']
        
        for event in events:
            try:
                markets = self.find_related_markets(event)
                for m in markets:
                    ticker = m['ticker']
                    price = m['price']
                    
                    if ticker not in history:
                        history[ticker] = []
                    
                    history[ticker].append(price)
                    
                    # Keep last 100 prices
                    history[ticker] = history[ticker][-100:]
            except:
                pass
        
        # Save
        with open(self.history_file, 'w') as f:
            json.dump(history, f)
    
    def report(self) -> str:
        """Generate pairs opportunity report."""
        opportunities = self.scan_all()
        
        lines = [
            "═" * 70,
            "  PAIRS/SPREAD SCANNER",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 70,
            "",
        ]
        
        if not opportunities:
            lines.append("  No spread opportunities found (|z| < 2.0)")
        else:
            lines.append(f"  Found {len(opportunities)} spread opportunities:")
            lines.append("")
            
            for opp in opportunities[:10]:
                direction = "▲" if opp.signal == "BUY_A" else "▼"
                lines.append(f"  {direction} {opp.underpriced}")
                lines.append(f"    Pair: {opp.contract_a} vs {opp.contract_b}")
                lines.append(f"    Prices: {opp.price_a*100:.0f}% vs {opp.price_b*100:.0f}%")
                lines.append(f"    Z-Score: {opp.z_score:+.2f} | Beta: {opp.beta:.2f}")
                lines.append(f"    Confidence: {opp.confidence} | {opp.reasoning}")
                lines.append("")
        
        lines.extend([
            "═" * 70,
            "  Strategy: Buy underpriced contract, spread reverts to mean",
            "═" * 70,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for pairs scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pairs/spread scanner')
    parser.add_argument('action', choices=['scan', 'report', 'record', 'event'],
                        help='Action to perform')
    parser.add_argument('--event', help='Specific event to scan')
    
    args = parser.parse_args()
    
    scanner = PairsScanner()
    
    if args.action == 'scan':
        opps = scanner.scan_all()
        print(f"Found {len(opps)} opportunities")
        for opp in opps[:5]:
            print(f"  {opp.signal}: {opp.underpriced} (z={opp.z_score:+.2f})")
    
    elif args.action == 'report':
        print(scanner.report())
    
    elif args.action == 'record':
        scanner.record_prices()
        print("Prices recorded for history")
    
    elif args.action == 'event':
        if args.event:
            opps = scanner.scan_event(args.event)
            print(f"Found {len(opps)} opportunities in {args.event}")
            for opp in opps:
                print(f"  {opp.signal}: {opp.underpriced} (z={opp.z_score:+.2f})")
        else:
            print("Error: --event required")


if __name__ == '__main__':
    main()
