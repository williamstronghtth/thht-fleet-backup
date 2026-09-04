"""
Unified Opportunity Evaluator
=============================

Combines all signals and scoring systems to make final trade decisions.

Pipeline:
1. Detect category → apply category multiplier
2. Check microstructure → VPIN, Kyle R²
3. Get sentiment → Grok analysis
4. Calculate edge → model vs market
5. Check signal disagreement → adjust size or skip
6. Final decision → trade or not

This is the "brain" that orchestrates all our systems.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TradeDecision:
    """Final trade decision with all context."""
    ticker: str
    
    # Decision
    should_trade: bool
    direction: str  # "YES" or "NO"
    position_size: float  # Dollar amount
    
    # Scores
    raw_edge: float
    adjusted_edge: float
    category: str
    category_multiplier: float
    confidence_threshold: float
    
    # Signals
    signal_count: int
    disagreement_score: float
    size_multiplier: float
    
    # Microstructure
    vpin: Optional[float]
    r_squared: Optional[float]
    microstructure_safe: bool
    
    # Sentiment
    sentiment_score: Optional[float]
    
    # Final reasoning
    reasoning: str
    warnings: list


class OpportunityEvaluator:
    """
    Unified evaluator that combines all scoring systems.
    
    Usage:
        evaluator = OpportunityEvaluator()
        decision = evaluator.evaluate(
            ticker="KXCPI-26MAR-T0.7",
            market_price=0.48,
            our_estimate=0.65,
            max_position=50.0,
        )
        
        if decision.should_trade:
            # Execute trade at decision.position_size
    """
    
    # Base confidence threshold
    # Note: This is multiplied by category multiplier
    # Weather: 0.85x → 34% threshold
    # Economics: 1.20x → 48% threshold
    BASE_CONFIDENCE = 0.40  # Aggressive mode for first 2 months
    
    # Minimum edge to consider (after adjustments)
    MIN_EDGE = 0.05  # 5% - lower bar, more volume
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/evaluator_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / 'decisions.jsonl'
        
        # Initialize sub-systems
        self._category_scorer = None
        self._disagreement_detector = None
        self._microstructure = None
        self._sentiment = None
    
    @property
    def category_scorer(self):
        if self._category_scorer is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.category_scoring import CategoryScorer
            self._category_scorer = CategoryScorer()
        return self._category_scorer
    
    @property
    def disagreement_detector(self):
        if self._disagreement_detector is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.signal_disagreement import SignalDisagreementDetector
            self._disagreement_detector = SignalDisagreementDetector()
        return self._disagreement_detector
    
    def evaluate(
        self,
        ticker: str,
        market_price: float,
        our_estimate: float,
        max_position: float = 50.0,
        vpin: Optional[float] = None,
        r_squared: Optional[float] = None,
        sentiment_score: Optional[float] = None,
        additional_signals: Optional[list] = None,
    ) -> TradeDecision:
        """
        Evaluate an opportunity using all available signals.
        
        Args:
            ticker: Market ticker
            market_price: Current market price (0-1)
            our_estimate: Our probability estimate (0-1)
            max_position: Maximum position size in dollars
            vpin: VPIN score if available (0-1)
            r_squared: Kyle R² if available (0-1)
            sentiment_score: Grok sentiment if available (0-1)
            additional_signals: Any additional Signal objects
        
        Returns:
            TradeDecision with final recommendation
        """
        warnings = []
        
        # Step 1: Calculate raw edge
        raw_edge = our_estimate - market_price
        direction = "YES" if raw_edge > 0 else "NO"
        
        # Step 2: Get category score
        cat_score = self.category_scorer.get_score(ticker)
        category = cat_score.category
        category_multiplier = cat_score.confidence_multiplier
        
        # Adjust confidence threshold
        confidence_threshold = self.BASE_CONFIDENCE * category_multiplier
        
        # Step 3: Check microstructure
        microstructure_safe = True
        
        if vpin is not None and vpin > 0.65:
            microstructure_safe = False
            warnings.append(f"High VPIN ({vpin:.2f}) - toxic flow")
        
        if r_squared is not None and r_squared > 0.15:
            microstructure_safe = False
            warnings.append(f"High R² ({r_squared:.2f}) - informed traders")
        
        # Step 4: Build signals for disagreement detection
        signals = []
        
        # Edge signal
        edge_signal = self.disagreement_detector.create_signal_from_edge(raw_edge)
        signals.append(edge_signal)
        
        # Category signal
        cat_signal = self.disagreement_detector.create_signal_from_category(
            category, category_multiplier
        )
        signals.append(cat_signal)
        
        # Microstructure signals
        if vpin is not None:
            vpin_signal = self.disagreement_detector.create_signal_from_vpin(vpin)
            signals.append(vpin_signal)
        
        if r_squared is not None:
            r2_signal = self.disagreement_detector.create_signal_from_rsquared(r_squared)
            signals.append(r2_signal)
        
        # Sentiment signal
        if sentiment_score is not None:
            sent_signal = self.disagreement_detector.create_signal_from_sentiment(sentiment_score)
            signals.append(sent_signal)
        
        # Additional signals
        if additional_signals:
            signals.extend(additional_signals)
        
        # Step 5: Check disagreement
        disagreement = self.disagreement_detector.analyze(signals)
        
        # Step 6: Make final decision
        adjusted_edge = abs(raw_edge) * disagreement.size_multiplier
        
        should_trade = (
            microstructure_safe and
            disagreement.should_trade and
            adjusted_edge >= self.MIN_EDGE and
            our_estimate >= confidence_threshold
        )
        
        # Calculate position size
        if should_trade:
            # Scale by disagreement multiplier and edge strength
            edge_factor = min(adjusted_edge / 0.15, 1.0)  # Cap at 15% edge
            position_size = max_position * disagreement.size_multiplier * edge_factor
        else:
            position_size = 0.0
        
        # Build reasoning
        reasoning_parts = []
        
        if not microstructure_safe:
            reasoning_parts.append("BLOCKED: Microstructure unsafe")
        elif not disagreement.should_trade:
            reasoning_parts.append(f"BLOCKED: {disagreement.explanation}")
        elif adjusted_edge < self.MIN_EDGE:
            reasoning_parts.append(f"BLOCKED: Adjusted edge too low ({adjusted_edge:.1%} < {self.MIN_EDGE:.0%})")
        elif our_estimate < confidence_threshold:
            reasoning_parts.append(f"BLOCKED: Below confidence threshold ({our_estimate:.0%} < {confidence_threshold:.0%})")
        else:
            reasoning_parts.append(f"APPROVED: {direction} with ${position_size:.0f}")
            reasoning_parts.append(f"Edge: {adjusted_edge:.1%}, Confidence: {our_estimate:.0%}")
        
        reasoning = " | ".join(reasoning_parts)
        
        decision = TradeDecision(
            ticker=ticker,
            should_trade=should_trade,
            direction=direction,
            position_size=position_size,
            raw_edge=raw_edge,
            adjusted_edge=adjusted_edge,
            category=category,
            category_multiplier=category_multiplier,
            confidence_threshold=confidence_threshold,
            signal_count=len(signals),
            disagreement_score=disagreement.disagreement_score,
            size_multiplier=disagreement.size_multiplier,
            vpin=vpin,
            r_squared=r_squared,
            microstructure_safe=microstructure_safe,
            sentiment_score=sentiment_score,
            reasoning=reasoning,
            warnings=warnings,
        )
        
        # Log decision
        self._log_decision(decision)
        
        return decision
    
    def _log_decision(self, decision: TradeDecision):
        """Log decision for analysis."""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ticker': decision.ticker,
            'should_trade': decision.should_trade,
            'direction': decision.direction,
            'position_size': decision.position_size,
            'raw_edge': decision.raw_edge,
            'adjusted_edge': decision.adjusted_edge,
            'category': decision.category,
            'disagreement_score': decision.disagreement_score,
            'size_multiplier': decision.size_multiplier,
            'reasoning': decision.reasoning,
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def quick_evaluate(
        self,
        ticker: str,
        market_price: float,
        our_estimate: float,
    ) -> Tuple[bool, str]:
        """
        Quick evaluation without all the bells and whistles.
        
        Returns (should_trade, reason)
        """
        decision = self.evaluate(
            ticker=ticker,
            market_price=market_price,
            our_estimate=our_estimate,
            max_position=25.0,
        )
        
        return decision.should_trade, decision.reasoning
    
    def get_stats(self) -> Dict:
        """Get evaluation statistics."""
        if not self.log_file.exists():
            return {'evaluations': 0}
        
        records = []
        with open(self.log_file) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        if not records:
            return {'evaluations': 0}
        
        trades = [r for r in records if r['should_trade']]
        skips = [r for r in records if not r['should_trade']]
        
        # Group by category
        by_category = {}
        for r in records:
            cat = r.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'trades': 0}
            by_category[cat]['total'] += 1
            if r['should_trade']:
                by_category[cat]['trades'] += 1
        
        return {
            'evaluations': len(records),
            'trades': len(trades),
            'skips': len(skips),
            'trade_rate': len(trades) / len(records) if records else 0,
            'by_category': by_category,
            'avg_disagreement': sum(r['disagreement_score'] for r in records) / len(records) if records else 0,
        }
    
    def report(self) -> str:
        """Generate evaluation report."""
        stats = self.get_stats()
        
        lines = [
            "═" * 60,
            "  OPPORTUNITY EVALUATOR REPORT",
            "═" * 60,
            "",
            f"  Total evaluations: {stats.get('evaluations', 0)}",
            f"  Trades approved: {stats.get('trades', 0)}",
            f"  Trades skipped: {stats.get('skips', 0)}",
            f"  Trade rate: {stats.get('trade_rate', 0):.1%}",
            f"  Avg disagreement: {stats.get('avg_disagreement', 0):.1%}",
            "",
            "  By Category:",
        ]
        
        for cat, data in stats.get('by_category', {}).items():
            rate = data['trades'] / data['total'] if data['total'] > 0 else 0
            lines.append(f"    {cat}: {data['trades']}/{data['total']} ({rate:.0%})")
        
        lines.extend([
            "",
            "═" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for opportunity evaluator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Opportunity evaluator')
    parser.add_argument('action', choices=['evaluate', 'stats', 'report'],
                        help='Action to perform')
    parser.add_argument('--ticker', help='Ticker to evaluate')
    parser.add_argument('--market', type=float, help='Market price')
    parser.add_argument('--estimate', type=float, help='Our estimate')
    parser.add_argument('--max-position', type=float, default=50.0,
                        help='Max position size')
    
    args = parser.parse_args()
    
    evaluator = OpportunityEvaluator()
    
    if args.action == 'evaluate':
        if not all([args.ticker, args.market, args.estimate]):
            print("Error: --ticker, --market, and --estimate required")
            return
        
        decision = evaluator.evaluate(
            ticker=args.ticker,
            market_price=args.market,
            our_estimate=args.estimate,
            max_position=args.max_position,
        )
        
        print("Trade Decision")
        print("=" * 50)
        print(f"Ticker: {decision.ticker}")
        print(f"Category: {decision.category} ({decision.category_multiplier:.2f}x)")
        print(f"Raw edge: {decision.raw_edge*100:+.1f}%")
        print(f"Adjusted edge: {decision.adjusted_edge*100:+.1f}%")
        print(f"Disagreement: {decision.disagreement_score:.1%}")
        print(f"Size multiplier: {decision.size_multiplier:.0%}")
        print()
        print(f"Should trade: {'✅ YES' if decision.should_trade else '❌ NO'}")
        print(f"Direction: {decision.direction}")
        print(f"Position size: ${decision.position_size:.2f}")
        print(f"Reasoning: {decision.reasoning}")
        
        if decision.warnings:
            print()
            print("Warnings:")
            for w in decision.warnings:
                print(f"  ⚠️ {w}")
    
    elif args.action == 'stats':
        stats = evaluator.get_stats()
        for k, v in stats.items():
            if k == 'by_category':
                print(f"{k}:")
                for cat, data in v.items():
                    print(f"  {cat}: {data}")
            elif isinstance(v, float):
                print(f"{k}: {v:.1%}")
            else:
                print(f"{k}: {v}")
    
    elif args.action == 'report':
        print(evaluator.report())


if __name__ == '__main__':
    main()
