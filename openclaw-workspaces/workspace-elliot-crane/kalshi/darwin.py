"""
Darwinian Signal Weighting System
=================================

Inspired by ATLAS's autoresearch + Darwinian weights.

Core concept: Track every signal source's accuracy over time.
Good signals get louder. Bad signals get quieter.

Signal sources:
- Weather forecasts (Open-Meteo, NWS)
- Sentiment analysis (Grok X Search)
- Microstructure (VPIN, Kyle's λ, Hawkes)
- Economic nowcasts (Cleveland Fed, Atlanta Fed)
- Edge estimates (our probability vs market)

Each signal gets a weight (0.3 to 2.5) that evolves based on:
- Hit rate (did the trade win?)
- Calibration (was our probability estimate accurate?)
- Edge realized (did we capture the expected edge?)
"""

import json
import math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class SignalSource(Enum):
    WEATHER_FORECAST = "weather_forecast"
    SENTIMENT_GROK = "sentiment_grok"
    VPIN = "vpin"
    KYLE_LAMBDA = "kyle_lambda"
    HAWKES = "hawkes"
    CLEVELAND_NOWCAST = "cleveland_nowcast"
    ATLANTA_NOWCAST = "atlanta_nowcast"
    EDGE_ESTIMATE = "edge_estimate"
    POLYMARKET = "polymarket"


@dataclass
class SignalRecord:
    """A single signal observation with outcome."""
    signal_id: str
    source: str
    timestamp: str
    trade_id: str
    ticker: str
    
    # Signal details
    signal_value: float  # The raw signal (e.g., VPIN=0.73, sentiment=0.65)
    signal_direction: str  # "bullish", "bearish", "neutral"
    confidence: float  # 0-1
    
    # Trade details
    our_estimate: float  # Our probability estimate
    market_price: float  # Market's probability
    edge_expected: float  # our_estimate - market_price
    
    # Outcome (filled after settlement)
    outcome: Optional[str] = None  # "win", "loss", None
    actual_result: Optional[float] = None  # 1.0 for YES, 0.0 for NO
    edge_realized: Optional[float] = None  # actual profit vs expected
    
    # Scoring
    scored: bool = False
    hit: Optional[bool] = None  # Did signal direction match outcome?
    calibration_error: Optional[float] = None  # |our_estimate - actual|


@dataclass
class SignalWeight:
    """Current weight and stats for a signal source."""
    source: str
    weight: float  # 0.3 to 2.5
    
    # Rolling stats (last 30 days)
    total_signals: int = 0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.5
    avg_calibration_error: float = 0.0
    avg_edge_realized: float = 0.0
    sharpe: float = 0.0
    
    # History
    last_updated: str = ""
    weight_history: List[Dict] = field(default_factory=list)


class DarwinianWeights:
    """
    Manages signal weights using Darwinian selection.
    
    Good signals survive and get amplified.
    Bad signals fade toward minimum weight.
    """
    
    # Weight constraints
    MIN_WEIGHT = 0.3
    MAX_WEIGHT = 2.5
    DEFAULT_WEIGHT = 1.0
    
    # Update parameters
    BOOST_FACTOR = 1.05  # Daily boost for top performers
    DECAY_FACTOR = 0.95  # Daily decay for bottom performers
    ROLLING_WINDOW = 30  # Days for rolling stats
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/darwin_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.weights_file = self.data_dir / 'signal_weights.json'
        self.signals_file = self.data_dir / 'signal_history.jsonl'
        self.daily_file = self.data_dir / 'daily_updates.json'
        
        # Load or initialize weights
        self.weights: Dict[str, SignalWeight] = self._load_weights()
    
    def _load_weights(self) -> Dict[str, SignalWeight]:
        """Load weights from file or initialize defaults."""
        if self.weights_file.exists():
            with open(self.weights_file) as f:
                data = json.load(f)
            
            weights = {}
            for source, w in data.items():
                weights[source] = SignalWeight(
                    source=source,
                    weight=w.get('weight', self.DEFAULT_WEIGHT),
                    total_signals=w.get('total_signals', 0),
                    hits=w.get('hits', 0),
                    misses=w.get('misses', 0),
                    hit_rate=w.get('hit_rate', 0.5),
                    avg_calibration_error=w.get('avg_calibration_error', 0.0),
                    avg_edge_realized=w.get('avg_edge_realized', 0.0),
                    sharpe=w.get('sharpe', 0.0),
                    last_updated=w.get('last_updated', ''),
                    weight_history=w.get('weight_history', []),
                )
            return weights
        
        # Initialize all signal sources at default weight
        return {
            source.value: SignalWeight(
                source=source.value,
                weight=self.DEFAULT_WEIGHT,
            )
            for source in SignalSource
        }
    
    def _save_weights(self):
        """Save current weights to file."""
        data = {
            source: asdict(w)
            for source, w in self.weights.items()
        }
        
        with open(self.weights_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_signal(self, record: SignalRecord):
        """Log a new signal observation."""
        with open(self.signals_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def get_weight(self, source: str) -> float:
        """Get current weight for a signal source."""
        if source in self.weights:
            return self.weights[source].weight
        return self.DEFAULT_WEIGHT
    
    def get_weighted_signal(self, source: str, raw_signal: float) -> float:
        """Apply Darwinian weight to a raw signal."""
        weight = self.get_weight(source)
        return raw_signal * weight
    
    def combine_signals(self, signals: Dict[str, float]) -> float:
        """
        Combine multiple signals using Darwinian weights.
        
        Args:
            signals: Dict mapping source name to signal value (0-1)
        
        Returns:
            Weighted average signal
        """
        if not signals:
            return 0.5
        
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for source, signal in signals.items():
            weight = self.get_weight(source)
            weighted_sum += signal * weight
            weight_sum += weight
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.5
    
    def score_signal(self, signal_id: str, outcome: str, actual_result: float):
        """
        Score a signal after trade settlement.
        
        Args:
            signal_id: ID of the signal to score
            outcome: "win" or "loss"
            actual_result: 1.0 for YES won, 0.0 for NO won
        """
        # Find and update the signal record
        signals = self._load_signals()
        
        for signal in signals:
            if signal.get('signal_id') == signal_id and not signal.get('scored'):
                source = signal['source']
                
                # Calculate metrics
                our_estimate = signal.get('our_estimate', 0.5)
                market_price = signal.get('market_price', 0.5)
                edge_expected = signal.get('edge_expected', 0)
                
                # Was signal direction correct?
                signal_dir = signal.get('signal_direction', 'neutral')
                if signal_dir == 'bullish':
                    hit = actual_result > 0.5
                elif signal_dir == 'bearish':
                    hit = actual_result < 0.5
                else:
                    hit = True  # Neutral is always "correct"
                
                # Calibration error
                calibration_error = abs(our_estimate - actual_result)
                
                # Edge realized
                if outcome == 'win':
                    edge_realized = edge_expected  # Captured expected edge
                else:
                    edge_realized = -edge_expected  # Lost expected edge
                
                # Update signal record
                signal['scored'] = True
                signal['outcome'] = outcome
                signal['actual_result'] = actual_result
                signal['hit'] = hit
                signal['calibration_error'] = calibration_error
                signal['edge_realized'] = edge_realized
                
                # Update source weights
                self._update_source_stats(source, hit, calibration_error, edge_realized)
                
                break
        
        # Save updated signals
        self._save_signals(signals)
    
    def _load_signals(self) -> List[Dict]:
        """Load signal history."""
        if not self.signals_file.exists():
            return []
        
        signals = []
        with open(self.signals_file) as f:
            for line in f:
                if line.strip():
                    signals.append(json.loads(line))
        return signals
    
    def _save_signals(self, signals: List[Dict]):
        """Save signal history."""
        with open(self.signals_file, 'w') as f:
            for signal in signals:
                f.write(json.dumps(signal) + '\n')
    
    def _update_source_stats(self, source: str, hit: bool, 
                              calibration_error: float, edge_realized: float):
        """Update rolling stats for a signal source."""
        if source not in self.weights:
            self.weights[source] = SignalWeight(
                source=source,
                weight=self.DEFAULT_WEIGHT,
            )
        
        w = self.weights[source]
        
        # Update counts
        w.total_signals += 1
        if hit:
            w.hits += 1
        else:
            w.misses += 1
        
        # Update rolling stats (exponential moving average)
        alpha = 0.1  # Smoothing factor
        w.hit_rate = alpha * (1.0 if hit else 0.0) + (1 - alpha) * w.hit_rate
        w.avg_calibration_error = alpha * calibration_error + (1 - alpha) * w.avg_calibration_error
        w.avg_edge_realized = alpha * edge_realized + (1 - alpha) * w.avg_edge_realized
        
        w.last_updated = datetime.now(timezone.utc).isoformat()
        
        self._save_weights()
    
    def run_daily_update(self):
        """
        Run daily Darwinian weight update.
        
        Top performers get boosted, bottom performers decay.
        """
        # Get signals from last 24 hours
        cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        signals = self._load_signals()
        recent = [s for s in signals if s.get('timestamp', '') >= cutoff and s.get('scored')]
        
        if not recent:
            return {"message": "No scored signals in last 24h"}
        
        # Calculate daily performance by source
        source_performance = {}
        
        for signal in recent:
            source = signal['source']
            if source not in source_performance:
                source_performance[source] = {
                    'hits': 0,
                    'total': 0,
                    'edge_sum': 0,
                }
            
            source_performance[source]['total'] += 1
            if signal.get('hit'):
                source_performance[source]['hits'] += 1
            source_performance[source]['edge_sum'] += signal.get('edge_realized', 0)
        
        # Rank sources by hit rate
        rankings = []
        for source, stats in source_performance.items():
            hit_rate = stats['hits'] / stats['total'] if stats['total'] > 0 else 0.5
            rankings.append((source, hit_rate, stats['total']))
        
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Apply Darwinian updates
        updates = {}
        n = len(rankings)
        
        for i, (source, hit_rate, count) in enumerate(rankings):
            if source not in self.weights:
                continue
            
            old_weight = self.weights[source].weight
            
            # Top quartile gets boosted
            if i < n / 4:
                new_weight = old_weight * self.BOOST_FACTOR
            # Bottom quartile decays
            elif i >= 3 * n / 4:
                new_weight = old_weight * self.DECAY_FACTOR
            else:
                new_weight = old_weight
            
            # Apply constraints
            new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
            
            if abs(new_weight - old_weight) > 0.001:
                self.weights[source].weight = new_weight
                self.weights[source].weight_history.append({
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'old': old_weight,
                    'new': new_weight,
                    'hit_rate': hit_rate,
                })
                
                updates[source] = {
                    'old': old_weight,
                    'new': new_weight,
                    'change': new_weight - old_weight,
                    'hit_rate': hit_rate,
                }
        
        self._save_weights()
        
        # Save daily update log
        daily_log = {
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'signals_scored': len(recent),
            'sources_updated': len(updates),
            'updates': updates,
            'rankings': [(s, hr, c) for s, hr, c in rankings],
        }
        
        with open(self.daily_file, 'w') as f:
            json.dump(daily_log, f, indent=2)
        
        return daily_log
    
    def calculate_combined_edge(self, signals: Dict[str, Dict]) -> Dict:
        """
        Calculate combined edge estimate from multiple signals.
        
        Args:
            signals: Dict mapping source to {value, direction, confidence}
        
        Returns:
            Combined analysis with weighted edge
        """
        if not signals:
            return {
                'combined_probability': 0.5,
                'combined_edge': 0.0,
                'confidence': 'LOW',
                'dominant_signal': None,
            }
        
        weighted_probs = []
        weight_sum = 0.0
        
        for source, sig in signals.items():
            weight = self.get_weight(source)
            prob = sig.get('value', 0.5)
            
            weighted_probs.append(prob * weight)
            weight_sum += weight
        
        combined_prob = sum(weighted_probs) / weight_sum if weight_sum > 0 else 0.5
        
        # Find dominant signal (highest weighted contribution)
        dominant = max(signals.keys(), key=lambda s: self.get_weight(s) * signals[s].get('confidence', 0.5))
        
        # Confidence based on signal agreement
        probs = [s.get('value', 0.5) for s in signals.values()]
        spread = max(probs) - min(probs)
        
        if spread < 0.1:
            confidence = 'HIGH'  # Strong agreement
        elif spread < 0.2:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'  # Signals disagree
        
        return {
            'combined_probability': combined_prob,
            'confidence': confidence,
            'dominant_signal': dominant,
            'signal_count': len(signals),
            'weights_used': {s: self.get_weight(s) for s in signals},
        }
    
    def report(self) -> str:
        """Generate signal weights report."""
        lines = [
            "═" * 70,
            "  DARWINIAN SIGNAL WEIGHTS",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 70,
            "",
            f"  {'Source':<25} {'Weight':>8} {'Hit Rate':>10} {'Signals':>8}",
            "  " + "-" * 55,
        ]
        
        # Sort by weight
        sorted_weights = sorted(
            self.weights.values(),
            key=lambda w: w.weight,
            reverse=True
        )
        
        for w in sorted_weights:
            bar = "█" * int(w.weight * 4) + "░" * (10 - int(w.weight * 4))
            lines.append(
                f"  {w.source:<25} {w.weight:>7.2f}x {w.hit_rate*100:>8.0f}% {w.total_signals:>8}"
            )
        
        lines.extend([
            "",
            "  Weight Range: 0.3x (silenced) to 2.5x (amplified)",
            "  Default: 1.0x",
            "",
            "═" * 70,
        ])
        
        return "\n".join(lines)


def create_signal_record(
    source: str,
    trade_id: str,
    ticker: str,
    signal_value: float,
    signal_direction: str,
    confidence: float,
    our_estimate: float,
    market_price: float
) -> SignalRecord:
    """Helper to create a signal record."""
    return SignalRecord(
        signal_id=f"SIG{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        source=source,
        timestamp=datetime.now(timezone.utc).isoformat(),
        trade_id=trade_id,
        ticker=ticker,
        signal_value=signal_value,
        signal_direction=signal_direction,
        confidence=confidence,
        our_estimate=our_estimate,
        market_price=market_price,
        edge_expected=our_estimate - market_price,
    )


def main():
    """CLI for Darwinian weights."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Darwinian Signal Weighting System')
    parser.add_argument('action', choices=['report', 'update', 'weights', 'history'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    darwin = DarwinianWeights()
    
    if args.action == 'report':
        print(darwin.report())
    
    elif args.action == 'update':
        result = darwin.run_daily_update()
        print(f"Daily update complete:")
        print(json.dumps(result, indent=2))
    
    elif args.action == 'weights':
        for source, w in darwin.weights.items():
            print(f"{source}: {w.weight:.2f}x (hit_rate: {w.hit_rate:.0%})")
    
    elif args.action == 'history':
        for source, w in darwin.weights.items():
            if w.weight_history:
                print(f"\n{source}:")
                for h in w.weight_history[-5:]:
                    print(f"  {h['date']}: {h['old']:.2f} → {h['new']:.2f}")


if __name__ == '__main__':
    main()
