"""
Signal Disagreement Detection
=============================

When multiple signals disagree, reduce position size or skip the trade.

Based on ensemble trading research:
- High agreement = full position size
- Moderate disagreement = reduced size
- High disagreement = skip trade

Signals we track:
1. Edge estimate (our model vs market)
2. Sentiment (Grok analysis)
3. Microstructure (VPIN, Kyle lambda)
4. Category score
5. Volatility regime
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SignalDirection(Enum):
    """Direction of a signal."""
    BULLISH = "bullish"      # Suggests YES/long
    BEARISH = "bearish"      # Suggests NO/short
    NEUTRAL = "neutral"      # No clear direction
    AVOID = "avoid"          # Stay out entirely


@dataclass
class Signal:
    """A single signal with direction and strength."""
    name: str
    direction: SignalDirection
    strength: float  # 0-1, how confident is this signal
    value: float     # Raw value (e.g., edge %, VPIN, sentiment score)
    weight: float    # Weight in ensemble (default 1.0)


@dataclass
class DisagreementResult:
    """Result of disagreement analysis."""
    signals: List[Signal]
    
    # Disagreement metrics
    disagreement_score: float  # 0-1, higher = more disagreement
    std_dev: float             # Standard deviation of weighted directions
    
    # Recommendations
    should_trade: bool
    size_multiplier: float     # 0-1, multiply position size by this
    consensus_direction: SignalDirection
    
    # Reasoning
    bullish_count: int
    bearish_count: int
    avoid_count: int
    explanation: str


# Thresholds
DISAGREEMENT_THRESHOLD_SKIP = 0.60      # Skip trade if disagreement > 60% (was 40%)
DISAGREEMENT_THRESHOLD_REDUCE = 0.40    # Reduce size if disagreement > 40% (was 25%)
MIN_SIGNALS_FOR_CONSENSUS = 1           # Allow single-signal trades in aggressive mode


class SignalDisagreementDetector:
    """
    Detects when signals disagree and adjusts position sizing.
    
    Usage:
        detector = SignalDisagreementDetector()
        
        signals = [
            Signal("edge", SignalDirection.BULLISH, 0.8, 0.15, weight=1.5),
            Signal("sentiment", SignalDirection.BEARISH, 0.6, -0.3, weight=1.0),
            Signal("vpin", SignalDirection.NEUTRAL, 0.5, 0.45, weight=1.2),
        ]
        
        result = detector.analyze(signals)
        
        if result.should_trade:
            actual_size = planned_size * result.size_multiplier
    """
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/disagreement_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / 'disagreement_history.jsonl'
    
    def analyze(self, signals: List[Signal]) -> DisagreementResult:
        """
        Analyze signals for disagreement.
        
        Returns recommendation on whether to trade and at what size.
        """
        if len(signals) < MIN_SIGNALS_FOR_CONSENSUS:
            return DisagreementResult(
                signals=signals,
                disagreement_score=0.5,
                std_dev=0.5,
                should_trade=False,
                size_multiplier=0.0,
                consensus_direction=SignalDirection.NEUTRAL,
                bullish_count=0,
                bearish_count=0,
                avoid_count=0,
                explanation=f"Need at least {MIN_SIGNALS_FOR_CONSENSUS} signals for consensus",
            )
        
        # Count directions
        bullish = [s for s in signals if s.direction == SignalDirection.BULLISH]
        bearish = [s for s in signals if s.direction == SignalDirection.BEARISH]
        avoid = [s for s in signals if s.direction == SignalDirection.AVOID]
        
        # If any signal says AVOID, respect it
        if avoid:
            return DisagreementResult(
                signals=signals,
                disagreement_score=1.0,
                std_dev=1.0,
                should_trade=False,
                size_multiplier=0.0,
                consensus_direction=SignalDirection.AVOID,
                bullish_count=len(bullish),
                bearish_count=len(bearish),
                avoid_count=len(avoid),
                explanation=f"AVOID signal from: {', '.join(s.name for s in avoid)}",
            )
        
        # Convert directions to numeric values for std dev calculation
        # BULLISH = +1, NEUTRAL = 0, BEARISH = -1
        direction_values = []
        weights = []
        
        for s in signals:
            if s.direction == SignalDirection.BULLISH:
                direction_values.append(1.0 * s.strength)
            elif s.direction == SignalDirection.BEARISH:
                direction_values.append(-1.0 * s.strength)
            else:  # NEUTRAL
                direction_values.append(0.0)
            weights.append(s.weight)
        
        direction_values = np.array(direction_values)
        weights = np.array(weights)
        
        # Weighted mean and std dev
        weighted_mean = np.average(direction_values, weights=weights)
        weighted_variance = np.average((direction_values - weighted_mean) ** 2, weights=weights)
        weighted_std = np.sqrt(weighted_variance)
        
        # Disagreement score (normalized std dev)
        # Max possible std dev is 1.0 (all signals at extremes, split 50/50)
        disagreement_score = min(weighted_std, 1.0)
        
        # Determine consensus direction
        if weighted_mean > 0.2:
            consensus = SignalDirection.BULLISH
        elif weighted_mean < -0.2:
            consensus = SignalDirection.BEARISH
        else:
            consensus = SignalDirection.NEUTRAL
        
        # Determine if we should trade and at what size
        if disagreement_score > DISAGREEMENT_THRESHOLD_SKIP:
            should_trade = False
            size_multiplier = 0.0
            explanation = f"High disagreement ({disagreement_score:.0%}) - SKIP"
        elif disagreement_score > DISAGREEMENT_THRESHOLD_REDUCE:
            should_trade = True
            # Linear reduction from 1.0 to 0.5 as disagreement goes 0.25 to 0.40
            reduction = (disagreement_score - DISAGREEMENT_THRESHOLD_REDUCE) / (DISAGREEMENT_THRESHOLD_SKIP - DISAGREEMENT_THRESHOLD_REDUCE)
            size_multiplier = 1.0 - (0.5 * reduction)
            explanation = f"Moderate disagreement ({disagreement_score:.0%}) - reduce size to {size_multiplier:.0%}"
        else:
            should_trade = True
            size_multiplier = 1.0
            explanation = f"Low disagreement ({disagreement_score:.0%}) - full size"
        
        # If consensus is NEUTRAL, reduce size slightly (was 50%, now 75%)
        if consensus == SignalDirection.NEUTRAL and should_trade:
            size_multiplier *= 0.75
            explanation += " (neutral consensus, reduced)"
        
        result = DisagreementResult(
            signals=signals,
            disagreement_score=disagreement_score,
            std_dev=weighted_std,
            should_trade=should_trade,
            size_multiplier=size_multiplier,
            consensus_direction=consensus,
            bullish_count=len(bullish),
            bearish_count=len(bearish),
            avoid_count=len(avoid),
            explanation=explanation,
        )
        
        # Log for analysis
        self._log_analysis(result)
        
        return result
    
    def create_signal_from_edge(self, edge: float, confidence: float = 0.7) -> Signal:
        """
        Create a signal from edge estimate.
        
        edge > 0.10 = bullish (bet YES)
        edge < -0.10 = bearish (bet NO)
        """
        if edge > 0.10:
            direction = SignalDirection.BULLISH
        elif edge < -0.10:
            direction = SignalDirection.BEARISH
        else:
            direction = SignalDirection.NEUTRAL
        
        return Signal(
            name="edge",
            direction=direction,
            strength=min(abs(edge) * 5, 1.0),  # Scale edge to 0-1
            value=edge,
            weight=1.5,  # Edge is weighted higher
        )
    
    def create_signal_from_sentiment(self, sentiment_score: float) -> Signal:
        """
        Create a signal from Grok sentiment analysis.
        
        sentiment > 0.6 = bullish
        sentiment < 0.4 = bearish
        """
        if sentiment_score > 0.6:
            direction = SignalDirection.BULLISH
        elif sentiment_score < 0.4:
            direction = SignalDirection.BEARISH
        else:
            direction = SignalDirection.NEUTRAL
        
        return Signal(
            name="sentiment",
            direction=direction,
            strength=abs(sentiment_score - 0.5) * 2,  # Distance from 0.5, scaled
            value=sentiment_score,
            weight=1.0,
        )
    
    def create_signal_from_vpin(self, vpin: float) -> Signal:
        """
        Create a signal from VPIN (flow toxicity).
        
        VPIN > 0.65 = AVOID (toxic flow, informed traders)
        VPIN 0.4-0.65 = NEUTRAL (caution)
        VPIN < 0.4 = no signal (clean flow)
        """
        if vpin > 0.65:
            direction = SignalDirection.AVOID
            strength = 1.0
        elif vpin > 0.4:
            direction = SignalDirection.NEUTRAL
            strength = 0.5
        else:
            direction = SignalDirection.NEUTRAL
            strength = 0.3
        
        return Signal(
            name="vpin",
            direction=direction,
            strength=strength,
            value=vpin,
            weight=1.2,  # Microstructure is important
        )
    
    def create_signal_from_category(self, category: str, multiplier: float) -> Signal:
        """
        Create a signal from category scoring.
        
        multiplier < 0.95 = bullish (favorable category)
        multiplier > 1.10 = bearish (unfavorable category)
        """
        if multiplier < 0.95:
            direction = SignalDirection.BULLISH
        elif multiplier > 1.10:
            direction = SignalDirection.BEARISH
        else:
            direction = SignalDirection.NEUTRAL
        
        return Signal(
            name="category",
            direction=direction,
            strength=abs(1.0 - multiplier),
            value=multiplier,
            weight=0.8,
        )
    
    def create_signal_from_rsquared(self, r_squared: float) -> Signal:
        """
        Create a signal from Kyle R² (information detection).
        
        R² > 0.15 = AVOID (informed traders present)
        """
        if r_squared > 0.15:
            direction = SignalDirection.AVOID
            strength = 1.0
        elif r_squared > 0.08:
            direction = SignalDirection.NEUTRAL
            strength = 0.6
        else:
            direction = SignalDirection.NEUTRAL
            strength = 0.3
        
        return Signal(
            name="kyle_rsquared",
            direction=direction,
            strength=strength,
            value=r_squared,
            weight=1.3,
        )
    
    def _log_analysis(self, result: DisagreementResult):
        """Log disagreement analysis for later review."""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'disagreement_score': result.disagreement_score,
            'should_trade': result.should_trade,
            'size_multiplier': result.size_multiplier,
            'consensus': result.consensus_direction.value,
            'signals': [
                {
                    'name': s.name,
                    'direction': s.direction.value,
                    'strength': s.strength,
                    'value': s.value,
                }
                for s in result.signals
            ],
        }
        
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def get_stats(self) -> Dict:
        """Get statistics on disagreement patterns."""
        if not self.history_file.exists():
            return {'analyses': 0}
        
        records = []
        with open(self.history_file) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        if not records:
            return {'analyses': 0}
        
        disagreements = [r['disagreement_score'] for r in records]
        trades = [r for r in records if r['should_trade']]
        skips = [r for r in records if not r['should_trade']]
        
        return {
            'analyses': len(records),
            'avg_disagreement': np.mean(disagreements),
            'trades': len(trades),
            'skips': len(skips),
            'skip_rate': len(skips) / len(records) if records else 0,
        }


def main():
    """CLI for signal disagreement detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Signal disagreement detection')
    parser.add_argument('action', choices=['demo', 'stats'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    detector = SignalDisagreementDetector()
    
    if args.action == 'demo':
        # Demo with sample signals
        signals = [
            detector.create_signal_from_edge(0.15),           # Bullish
            detector.create_signal_from_sentiment(0.35),      # Bearish
            detector.create_signal_from_vpin(0.45),           # Neutral (caution)
            detector.create_signal_from_category("weather", 0.85),  # Bullish
        ]
        
        result = detector.analyze(signals)
        
        print("Signal Disagreement Analysis")
        print("=" * 50)
        print(f"Signals: {len(signals)}")
        for s in signals:
            print(f"  • {s.name}: {s.direction.value} ({s.strength:.1%} strength)")
        print()
        print(f"Disagreement score: {result.disagreement_score:.0%}")
        print(f"Consensus direction: {result.consensus_direction.value}")
        print(f"Should trade: {result.should_trade}")
        print(f"Size multiplier: {result.size_multiplier:.0%}")
        print(f"Explanation: {result.explanation}")
    
    elif args.action == 'stats':
        stats = detector.get_stats()
        print("Disagreement Statistics")
        print("=" * 50)
        for k, v in stats.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.1%}")
            else:
                print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
