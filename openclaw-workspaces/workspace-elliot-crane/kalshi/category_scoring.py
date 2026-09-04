"""
Category Risk Scoring
=====================

Adjusts confidence thresholds by market category based on historical performance.

Key insight from kalshi-ai-trading-bot:
- Sports (NCAAB): 74% win rate, +10% ROI — best category
- Economics (CPI, Fed): -70% ROI — worst category

We apply multipliers to the base confidence threshold:
- Lower multiplier = easier to trade (proven edge)
- Higher multiplier = harder to trade (no edge historically)
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CategoryScore:
    """Score and metadata for a market category."""
    category: str
    confidence_multiplier: float
    reason: str
    historical_win_rate: Optional[float] = None
    historical_roi: Optional[float] = None
    sample_size: int = 0


# Default category multipliers based on industry research
# Lower = easier to trade, Higher = harder to trade
DEFAULT_MULTIPLIERS = {
    # Weather - verifiable edge (forecasts vs market)
    "weather": 0.85,
    
    # Sports - historically profitable (per kalshi-ai-trading-bot)
    "sports": 0.90,
    
    # Entertainment - thin edge, high volume
    "entertainment": 1.00,
    
    # Economics - worst performer, heavily arbitraged
    "economics": 1.20,
    
    # Politics - volatile, hard to predict
    "politics": 1.15,
    
    # Crypto - extreme volatility
    "crypto": 1.25,
    
    # Default for unknown categories
    "default": 1.00,
}


class CategoryScorer:
    """
    Adjusts confidence thresholds based on market category.
    
    Usage:
        scorer = CategoryScorer()
        adjusted_threshold = scorer.adjust_threshold("KXCPI-26MAR", base_threshold=0.60)
        # Returns 0.72 (0.60 * 1.20 for economics)
    """
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/category_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.performance_file = self.data_dir / 'category_performance.json'
        
        # Load custom multipliers or use defaults
        self.multipliers = self._load_multipliers()
    
    def _load_multipliers(self) -> Dict[str, float]:
        """Load multipliers, using defaults if no custom file exists."""
        custom_file = self.data_dir / 'custom_multipliers.json'
        
        if custom_file.exists():
            with open(custom_file) as f:
                custom = json.load(f)
                return {**DEFAULT_MULTIPLIERS, **custom}
        
        return DEFAULT_MULTIPLIERS.copy()
    
    def detect_category(self, ticker: str) -> str:
        """
        Detect market category from ticker.
        
        Examples:
            KXCPI-26MAR-T0.7 -> economics
            KXHIGHDEN-26MAR28 -> weather
            KXNBA-... -> sports
            KXOSCARPIC-... -> entertainment
        """
        ticker_upper = ticker.upper()
        
        # Economics indicators
        economics_prefixes = ['KXCPI', 'KXGDP', 'KXPCE', 'KXUNRATE', 'KXFED', 'KXFOMC', 
                              'KXJOBLESS', 'KXPAYROLL', 'KXRETAIL']
        for prefix in economics_prefixes:
            if ticker_upper.startswith(prefix):
                return "economics"
        
        # Weather
        weather_prefixes = ['KXHIGH', 'KXLOW', 'KXRAIN', 'KXSNOW', 'KXTEMP', 'KXWIND']
        for prefix in weather_prefixes:
            if ticker_upper.startswith(prefix):
                return "weather"
        
        # Sports
        sports_prefixes = ['KXNBA', 'KXNFL', 'KXMLB', 'KXNHL', 'KXNCAA', 'KXSOCCER',
                           'KXTENNIS', 'KXGOLF', 'KXUFC', 'KXMMA']
        for prefix in sports_prefixes:
            if ticker_upper.startswith(prefix):
                return "sports"
        
        # Entertainment
        entertainment_prefixes = ['KXOSCAR', 'KXEMMY', 'KXGRAMMY', 'KXGOLDEN', 'KXBOX']
        for prefix in entertainment_prefixes:
            if ticker_upper.startswith(prefix):
                return "entertainment"
        
        # Politics
        politics_prefixes = ['KXPRES', 'KXSEN', 'KXHOUSE', 'KXGOV', 'KXAMEND', 'KXSCOTUS',
                             'KXBIDEN', 'KXTRUMP', 'KXELEC']
        for prefix in politics_prefixes:
            if ticker_upper.startswith(prefix):
                return "politics"
        
        # Crypto
        crypto_prefixes = ['KXBTC', 'KXETH', 'KXCRYPTO', 'KXSOL']
        for prefix in crypto_prefixes:
            if ticker_upper.startswith(prefix):
                return "crypto"
        
        return "default"
    
    def get_multiplier(self, ticker: str) -> Tuple[float, str]:
        """
        Get confidence multiplier for a ticker.
        
        Returns (multiplier, category)
        """
        category = self.detect_category(ticker)
        multiplier = self.multipliers.get(category, self.multipliers["default"])
        
        return multiplier, category
    
    def adjust_threshold(self, ticker: str, base_threshold: float = 0.60) -> float:
        """
        Adjust confidence threshold based on category.
        
        Example:
            base_threshold = 0.60
            economics multiplier = 1.20
            adjusted = 0.60 * 1.20 = 0.72
        """
        multiplier, _ = self.get_multiplier(ticker)
        return base_threshold * multiplier
    
    def get_score(self, ticker: str) -> CategoryScore:
        """Get full category score with metadata."""
        category = self.detect_category(ticker)
        multiplier = self.multipliers.get(category, 1.0)
        
        # Load historical performance if available
        performance = self._load_performance()
        cat_perf = performance.get(category, {})
        
        reason = self._get_reason(category)
        
        return CategoryScore(
            category=category,
            confidence_multiplier=multiplier,
            reason=reason,
            historical_win_rate=cat_perf.get('win_rate'),
            historical_roi=cat_perf.get('roi'),
            sample_size=cat_perf.get('trades', 0),
        )
    
    def _get_reason(self, category: str) -> str:
        """Get explanation for category multiplier."""
        reasons = {
            "weather": "Verifiable edge from forecast comparison",
            "sports": "Historically profitable (74% WR in research)",
            "entertainment": "Moderate edge, high liquidity",
            "economics": "Heavily arbitraged, -70% ROI in research",
            "politics": "High volatility, unpredictable",
            "crypto": "Extreme volatility, noise dominates",
            "default": "Unknown category, use base threshold",
        }
        return reasons.get(category, reasons["default"])
    
    def _load_performance(self) -> Dict:
        """Load historical performance by category."""
        if self.performance_file.exists():
            with open(self.performance_file) as f:
                return json.load(f)
        return {}
    
    def update_performance(self, category: str, won: bool, pnl: float):
        """
        Update category performance after a trade settles.
        Called by outcome_tracker.
        """
        performance = self._load_performance()
        
        if category not in performance:
            performance[category] = {
                'trades': 0,
                'wins': 0,
                'total_pnl': 0.0,
            }
        
        performance[category]['trades'] += 1
        if won:
            performance[category]['wins'] += 1
        performance[category]['total_pnl'] += pnl
        
        # Calculate derived metrics
        trades = performance[category]['trades']
        wins = performance[category]['wins']
        total_pnl = performance[category]['total_pnl']
        
        performance[category]['win_rate'] = wins / trades if trades > 0 else 0
        performance[category]['roi'] = total_pnl / trades if trades > 0 else 0
        
        with open(self.performance_file, 'w') as f:
            json.dump(performance, f, indent=2)
    
    def recalculate_multipliers(self, min_trades: int = 10):
        """
        Recalculate multipliers based on actual performance.
        
        Categories with better performance get lower multipliers.
        """
        performance = self._load_performance()
        new_multipliers = DEFAULT_MULTIPLIERS.copy()
        
        for category, perf in performance.items():
            if perf.get('trades', 0) < min_trades:
                continue
            
            win_rate = perf.get('win_rate', 0.5)
            roi = perf.get('roi', 0)
            
            # Calculate adjustment based on performance
            # Win rate > 60% and positive ROI = lower multiplier
            # Win rate < 40% or negative ROI = higher multiplier
            
            if win_rate >= 0.65 and roi > 0:
                new_multipliers[category] = 0.85
            elif win_rate >= 0.55 and roi > 0:
                new_multipliers[category] = 0.95
            elif win_rate < 0.45 or roi < -0.10:
                new_multipliers[category] = 1.25
            elif win_rate < 0.50 or roi < 0:
                new_multipliers[category] = 1.15
        
        # Save custom multipliers
        custom_file = self.data_dir / 'custom_multipliers.json'
        with open(custom_file, 'w') as f:
            json.dump(new_multipliers, f, indent=2)
        
        self.multipliers = new_multipliers
        return new_multipliers
    
    def report(self) -> str:
        """Generate category scoring report."""
        lines = [
            "═" * 60,
            "  CATEGORY RISK SCORING",
            "═" * 60,
            "",
            "  Category         Multiplier  Reason",
            "  " + "-" * 56,
        ]
        
        for category in sorted(self.multipliers.keys()):
            if category == "default":
                continue
            mult = self.multipliers[category]
            reason = self._get_reason(category)[:35]
            indicator = "🟢" if mult < 1.0 else "🟡" if mult == 1.0 else "🔴"
            lines.append(f"  {indicator} {category:<14} {mult:.2f}x      {reason}")
        
        lines.extend([
            "",
            "  Legend: 🟢 = favorable, 🟡 = neutral, 🔴 = unfavorable",
            "═" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for category scoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Category risk scoring')
    parser.add_argument('action', choices=['report', 'check', 'recalculate'],
                        help='Action to perform')
    parser.add_argument('--ticker', help='Ticker to check')
    parser.add_argument('--threshold', type=float, default=0.60,
                        help='Base confidence threshold')
    
    args = parser.parse_args()
    
    scorer = CategoryScorer()
    
    if args.action == 'report':
        print(scorer.report())
    
    elif args.action == 'check':
        if args.ticker:
            score = scorer.get_score(args.ticker)
            adjusted = scorer.adjust_threshold(args.ticker, args.threshold)
            print(f"Ticker: {args.ticker}")
            print(f"Category: {score.category}")
            print(f"Multiplier: {score.confidence_multiplier:.2f}x")
            print(f"Reason: {score.reason}")
            print(f"Base threshold: {args.threshold:.0%}")
            print(f"Adjusted threshold: {adjusted:.0%}")
        else:
            print("Error: --ticker required for check")
    
    elif args.action == 'recalculate':
        new_mults = scorer.recalculate_multipliers()
        print("Recalculated multipliers:")
        for cat, mult in sorted(new_mults.items()):
            print(f"  {cat}: {mult:.2f}x")


if __name__ == '__main__':
    main()
