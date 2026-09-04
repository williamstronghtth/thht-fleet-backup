"""
Feature Importance Tracking
===========================

Identifies which signals actually predict wins.

Uses multiple methods:
1. Win rate by signal source
2. Correlation analysis
3. Information gain
4. Permutation importance (when we have enough data)

This feeds back into the Darwinian weighting system.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SignalImportance:
    """Importance metrics for a single signal source."""
    source: str
    n_trades: int
    
    # Win rate metrics
    win_rate: float
    win_rate_vs_baseline: float  # Improvement over 50%
    
    # Correlation with outcomes
    correlation: float
    
    # Information gain (bits)
    information_gain: float
    
    # Consistency (std dev of win rate across time periods)
    consistency: float
    
    # Overall importance score (0-100)
    importance_score: float
    
    # Recommendation
    recommendation: str  # "AMPLIFY", "KEEP", "REDUCE", "REMOVE"


@dataclass
class FeatureReport:
    """Complete feature importance report."""
    timestamp: str
    n_trades: int
    n_signals: int
    
    signals: List[SignalImportance]
    
    # Rankings
    best_signal: str
    worst_signal: str
    
    # Recommendations
    amplify: List[str]
    keep: List[str]
    reduce: List[str]
    remove: List[str]
    
    def __str__(self):
        lines = [
            "=" * 60,
            "  FEATURE IMPORTANCE REPORT",
            f"  {self.timestamp}",
            "=" * 60,
            "",
            f"  Trades analyzed: {self.n_trades}",
            f"  Signal sources: {self.n_signals}",
            "",
            "  SIGNAL RANKINGS",
            "  " + "-" * 55,
            f"  {'Signal':<25} {'WinRate':>8} {'Corr':>7} {'Score':>7} {'Action':<10}",
            "  " + "-" * 55,
        ]
        
        for sig in sorted(self.signals, key=lambda x: x.importance_score, reverse=True):
            lines.append(
                f"  {sig.source:<25} {sig.win_rate:>7.0%} "
                f"{sig.correlation:>+6.2f} {sig.importance_score:>6.0f} "
                f"{sig.recommendation:<10}"
            )
        
        lines.extend([
            "",
            "  RECOMMENDATIONS",
            "  " + "-" * 55,
        ])
        
        if self.amplify:
            lines.append(f"  📈 AMPLIFY (>1.5x weight): {', '.join(self.amplify)}")
        if self.keep:
            lines.append(f"  ✅ KEEP (1.0x weight): {', '.join(self.keep)}")
        if self.reduce:
            lines.append(f"  📉 REDUCE (<0.7x weight): {', '.join(self.reduce)}")
        if self.remove:
            lines.append(f"  ❌ REMOVE (<0.3x weight): {', '.join(self.remove)}")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)


class FeatureImportanceTracker:
    """
    Tracks and analyzes signal importance over time.
    """
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi')
        self.trades_file = self.data_dir / 'execution/logs/trades.jsonl'
        self.darwin_file = self.data_dir / 'darwin_data/signal_history.jsonl'
        self.results_dir = self.data_dir / 'validation/results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_signal_outcomes(self) -> List[Dict]:
        """Load signals with their outcomes."""
        signals = []
        
        # From Darwin signal history
        if self.darwin_file.exists():
            with open(self.darwin_file) as f:
                for line in f:
                    if line.strip():
                        signal = json.loads(line)
                        if signal.get('scored'):
                            signals.append(signal)
        
        return signals
    
    def calculate_win_rate(self, signals: List[Dict]) -> float:
        """Calculate win rate for a set of signals."""
        if not signals:
            return 0.5
        
        wins = sum(1 for s in signals if s.get('hit', False))
        return wins / len(signals)
    
    def calculate_correlation(self, signals: List[Dict]) -> float:
        """
        Calculate correlation between signal value and outcome.
        
        Signal value should correlate with actual probability.
        """
        if len(signals) < 5:
            return 0.0
        
        signal_values = []
        outcomes = []
        
        for s in signals:
            signal_values.append(s.get('signal_value', 0.5))
            outcomes.append(1.0 if s.get('hit', False) else 0.0)
        
        signal_values = np.array(signal_values)
        outcomes = np.array(outcomes)
        
        # Handle constant arrays
        if np.std(signal_values) == 0 or np.std(outcomes) == 0:
            return 0.0
        
        correlation = np.corrcoef(signal_values, outcomes)[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
    
    def calculate_information_gain(self, signals: List[Dict]) -> float:
        """
        Calculate information gain (bits) from signal.
        
        Higher IG = signal provides more information about outcome.
        """
        if len(signals) < 10:
            return 0.0
        
        # Base entropy (50% baseline)
        def entropy(p):
            if p == 0 or p == 1:
                return 0
            return -p * np.log2(p) - (1-p) * np.log2(1-p)
        
        base_entropy = entropy(0.5)  # 1.0 bits
        
        # Split signals by direction
        bullish = [s for s in signals if s.get('signal_direction') == 'bullish']
        bearish = [s for s in signals if s.get('signal_direction') == 'bearish']
        
        # Calculate entropy after split
        conditional_entropy = 0.0
        
        for subset, direction in [(bullish, 'bullish'), (bearish, 'bearish')]:
            if subset:
                weight = len(subset) / len(signals)
                win_rate = self.calculate_win_rate(subset)
                conditional_entropy += weight * entropy(win_rate)
        
        information_gain = base_entropy - conditional_entropy
        
        return max(0, information_gain)
    
    def calculate_consistency(self, signals: List[Dict]) -> float:
        """
        Calculate consistency of signal performance over time.
        
        Lower std dev = more consistent = more reliable.
        Returns consistency score (1 - normalized std dev).
        """
        if len(signals) < 10:
            return 0.5
        
        # Sort by timestamp
        sorted_signals = sorted(signals, key=lambda x: x.get('timestamp', ''))
        
        # Split into chunks
        chunk_size = max(5, len(sorted_signals) // 5)
        chunks = [sorted_signals[i:i+chunk_size] 
                  for i in range(0, len(sorted_signals), chunk_size)]
        
        if len(chunks) < 2:
            return 0.5
        
        # Calculate win rate per chunk
        chunk_win_rates = [self.calculate_win_rate(chunk) for chunk in chunks]
        
        # Consistency = 1 - normalized std dev
        std_dev = np.std(chunk_win_rates)
        consistency = 1 - min(std_dev * 2, 1)  # Normalize: 0.5 std dev = 0 consistency
        
        return consistency
    
    def analyze_signal(self, source: str, signals: List[Dict]) -> SignalImportance:
        """Analyze importance of a single signal source."""
        win_rate = self.calculate_win_rate(signals)
        correlation = self.calculate_correlation(signals)
        information_gain = self.calculate_information_gain(signals)
        consistency = self.calculate_consistency(signals)
        
        # Calculate overall importance score (0-100)
        # Weighted combination of metrics
        score = (
            (win_rate - 0.5) * 100 * 0.4 +      # Win rate improvement (40%)
            correlation * 50 * 0.25 +             # Correlation (25%)
            information_gain * 50 * 0.20 +        # Information gain (20%)
            consistency * 20 * 0.15               # Consistency (15%)
        )
        
        # Normalize to 0-100
        importance_score = max(0, min(100, 50 + score))
        
        # Generate recommendation
        if importance_score >= 70 and win_rate >= 0.60:
            recommendation = "AMPLIFY"
        elif importance_score >= 50 or (win_rate >= 0.55 and len(signals) < 20):
            recommendation = "KEEP"
        elif importance_score >= 30:
            recommendation = "REDUCE"
        else:
            recommendation = "REMOVE"
        
        return SignalImportance(
            source=source,
            n_trades=len(signals),
            win_rate=win_rate,
            win_rate_vs_baseline=win_rate - 0.5,
            correlation=correlation,
            information_gain=information_gain,
            consistency=consistency,
            importance_score=importance_score,
            recommendation=recommendation,
        )
    
    def generate_report(self) -> FeatureReport:
        """Generate full feature importance report."""
        signals = self.load_signal_outcomes()
        
        if not signals:
            return FeatureReport(
                timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'),
                n_trades=0,
                n_signals=0,
                signals=[],
                best_signal="N/A",
                worst_signal="N/A",
                amplify=[],
                keep=[],
                reduce=[],
                remove=[],
            )
        
        # Group by source
        by_source = defaultdict(list)
        for signal in signals:
            source = signal.get('source', 'unknown')
            by_source[source].append(signal)
        
        # Analyze each source
        signal_importance = []
        for source, source_signals in by_source.items():
            importance = self.analyze_signal(source, source_signals)
            signal_importance.append(importance)
        
        # Sort by importance
        signal_importance.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Categorize recommendations
        amplify = [s.source for s in signal_importance if s.recommendation == "AMPLIFY"]
        keep = [s.source for s in signal_importance if s.recommendation == "KEEP"]
        reduce = [s.source for s in signal_importance if s.recommendation == "REDUCE"]
        remove = [s.source for s in signal_importance if s.recommendation == "REMOVE"]
        
        report = FeatureReport(
            timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'),
            n_trades=len(signals),
            n_signals=len(by_source),
            signals=signal_importance,
            best_signal=signal_importance[0].source if signal_importance else "N/A",
            worst_signal=signal_importance[-1].source if signal_importance else "N/A",
            amplify=amplify,
            keep=keep,
            reduce=reduce,
            remove=remove,
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _save_report(self, report: FeatureReport):
        """Save report to file."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        report_file = self.results_dir / f'feature_importance_{timestamp}.json'
        
        report_dict = {
            'timestamp': report.timestamp,
            'n_trades': report.n_trades,
            'n_signals': report.n_signals,
            'signals': [
                {
                    'source': s.source,
                    'n_trades': s.n_trades,
                    'win_rate': s.win_rate,
                    'correlation': s.correlation,
                    'information_gain': s.information_gain,
                    'consistency': s.consistency,
                    'importance_score': s.importance_score,
                    'recommendation': s.recommendation,
                }
                for s in report.signals
            ],
            'recommendations': {
                'amplify': report.amplify,
                'keep': report.keep,
                'reduce': report.reduce,
                'remove': report.remove,
            },
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    def apply_to_darwin(self, dry_run: bool = True) -> Dict[str, float]:
        """
        Apply feature importance recommendations to Darwin weights.
        
        Returns dict of weight changes.
        """
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
        
        from kalshi.darwin import DarwinianWeights
        
        report = self.generate_report()
        darwin = DarwinianWeights()
        
        changes = {}
        
        for sig in report.signals:
            source = sig.source
            current_weight = darwin.get_weight(source)
            
            if sig.recommendation == "AMPLIFY":
                new_weight = min(current_weight * 1.5, darwin.MAX_WEIGHT)
            elif sig.recommendation == "REDUCE":
                new_weight = max(current_weight * 0.7, darwin.MIN_WEIGHT)
            elif sig.recommendation == "REMOVE":
                new_weight = darwin.MIN_WEIGHT
            else:
                new_weight = current_weight
            
            if abs(new_weight - current_weight) > 0.01:
                changes[source] = {
                    'old': current_weight,
                    'new': new_weight,
                    'reason': sig.recommendation,
                }
                
                if not dry_run:
                    darwin.weights[source].weight = new_weight
        
        if not dry_run:
            darwin._save_weights()
        
        return changes


def main():
    """CLI for feature importance tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Feature importance tracking')
    parser.add_argument('action', choices=['report', 'apply', 'status'],
                        help='Action to perform')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply weight changes (default: dry run)')
    
    args = parser.parse_args()
    
    tracker = FeatureImportanceTracker()
    
    if args.action == 'report':
        report = tracker.generate_report()
        print(report)
    
    elif args.action == 'apply':
        changes = tracker.apply_to_darwin(dry_run=not args.apply)
        
        if changes:
            print("Weight changes" + (" (DRY RUN)" if not args.apply else "") + ":")
            for source, change in changes.items():
                print(f"  {source}: {change['old']:.2f} → {change['new']:.2f} ({change['reason']})")
        else:
            print("No weight changes recommended")
    
    elif args.action == 'status':
        signals = tracker.load_signal_outcomes()
        print(f"Scored signals: {len(signals)}")
        
        if signals:
            by_source = defaultdict(int)
            for s in signals:
                by_source[s.get('source', 'unknown')] += 1
            
            print("\nBy source:")
            for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                print(f"  {source}: {count}")


if __name__ == '__main__':
    main()
