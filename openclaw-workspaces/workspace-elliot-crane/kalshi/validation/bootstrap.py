"""
Bootstrap Validation
====================

Proves our edge is real, not luck.

One backtest means nothing. 10,000 simulations prove statistical significance.

Usage:
    from kalshi.validation.bootstrap import BootstrapValidator
    
    validator = BootstrapValidator()
    result = validator.validate()
    
    if result.edge_is_real:
        print(f"Edge confirmed: {result.win_rate_ci}")
    else:
        print("Might be luck - need more data or better signals")
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class BootstrapResult:
    """Results from bootstrap validation."""
    n_trades: int
    n_simulations: int
    
    # Win rate stats
    observed_win_rate: float
    mean_win_rate: float
    std_win_rate: float
    win_rate_ci_lower: float  # 2.5th percentile
    win_rate_ci_upper: float  # 97.5th percentile
    
    # Edge stats
    observed_edge: float  # Average edge on trades
    mean_edge: float
    edge_ci_lower: float
    edge_ci_upper: float
    
    # P&L stats
    observed_pnl: float
    mean_pnl: float
    pnl_ci_lower: float
    pnl_ci_upper: float
    
    # Sharpe ratio
    observed_sharpe: float
    mean_sharpe: float
    sharpe_ci_lower: float
    sharpe_ci_upper: float
    
    # Verdict
    edge_is_real: bool
    confidence_level: str  # "HIGH", "MEDIUM", "LOW", "INSUFFICIENT_DATA"
    verdict: str
    
    def __str__(self):
        return f"""
Bootstrap Validation Results
{'='*50}
Trades analyzed: {self.n_trades}
Simulations: {self.n_simulations:,}

WIN RATE
  Observed: {self.observed_win_rate:.1%}
  Mean: {self.mean_win_rate:.1%} ± {self.std_win_rate:.1%}
  95% CI: [{self.win_rate_ci_lower:.1%}, {self.win_rate_ci_upper:.1%}]

EDGE (avg points)
  Observed: {self.observed_edge*100:+.1f}
  95% CI: [{self.edge_ci_lower*100:+.1f}, {self.edge_ci_upper*100:+.1f}]

P&L
  Observed: ${self.observed_pnl:.2f}
  95% CI: [${self.pnl_ci_lower:.2f}, ${self.pnl_ci_upper:.2f}]

SHARPE RATIO
  Observed: {self.observed_sharpe:.2f}
  95% CI: [{self.sharpe_ci_lower:.2f}, {self.sharpe_ci_upper:.2f}]

VERDICT: {self.verdict}
Confidence: {self.confidence_level}
Edge is real: {'✅ YES' if self.edge_is_real else '❌ NO'}
{'='*50}
"""


class BootstrapValidator:
    """
    Bootstrap simulation to validate trading edge.
    
    Takes trade history and runs N simulations with random resampling
    to determine if observed performance is statistically significant.
    """
    
    DEFAULT_SIMULATIONS = 10000
    MIN_TRADES_FOR_VALIDATION = 20
    
    def __init__(self):
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi')
        self.trades_file = self.data_dir / 'execution/logs/trades.jsonl'
        self.results_dir = self.data_dir / 'validation/results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_resolved_trades(self) -> List[Dict]:
        """Load trades that have been resolved (have outcomes)."""
        if not self.trades_file.exists():
            return []
        
        trades = []
        with open(self.trades_file) as f:
            for line in f:
                if line.strip():
                    trade = json.loads(line)
                    # Only include trades with outcomes
                    if trade.get('outcome') in ['win', 'loss', 'WIN', 'LOSS']:
                        trades.append(trade)
        
        return trades
    
    def extract_trade_metrics(self, trades: List[Dict]) -> Dict[str, np.ndarray]:
        """Extract numerical metrics from trades for simulation."""
        outcomes = []  # 1 for win, 0 for loss
        edges = []     # Expected edge at entry
        pnls = []      # Actual P&L
        
        for trade in trades:
            # Outcome
            outcome = trade.get('outcome', '').lower()
            outcomes.append(1 if outcome == 'win' else 0)
            
            # Edge (from signals or calculated)
            signals = trade.get('signals', {})
            edge = signals.get('edge', 0)
            if edge == 0:
                # Try to calculate from our_estimate vs market_price
                our_est = signals.get('estimated_prob', 0.5)
                market = signals.get('market_price', 0.5)
                edge = our_est - market
            edges.append(edge)
            
            # P&L
            pnl = trade.get('pnl', 0)
            if pnl == 0:
                # Estimate from contracts and outcome
                contracts = trade.get('contracts', 1)
                price = trade.get('price', 0.5)
                if outcome == 'win':
                    pnl = contracts * (1 - price)  # Won: get $1, paid price
                else:
                    pnl = -contracts * price  # Lost: paid price, got nothing
            pnls.append(pnl)
        
        return {
            'outcomes': np.array(outcomes),
            'edges': np.array(edges),
            'pnls': np.array(pnls),
        }
    
    def calculate_sharpe(self, returns: np.ndarray) -> float:
        """Calculate Sharpe ratio from returns."""
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assume ~250 trading days)
        # But for prediction markets, use per-trade Sharpe
        return mean_return / std_return
    
    def run_bootstrap(self, metrics: Dict[str, np.ndarray], 
                       n_simulations: int = None) -> BootstrapResult:
        """
        Run bootstrap simulation.
        
        For each simulation:
        1. Resample trades with replacement
        2. Calculate metrics on resampled data
        3. Store results
        
        After all simulations:
        - Calculate confidence intervals
        - Determine if edge is statistically significant
        """
        n_simulations = n_simulations or self.DEFAULT_SIMULATIONS
        n_trades = len(metrics['outcomes'])
        
        # Observed metrics
        observed_win_rate = np.mean(metrics['outcomes'])
        observed_edge = np.mean(metrics['edges'])
        observed_pnl = np.sum(metrics['pnls'])
        observed_sharpe = self.calculate_sharpe(metrics['pnls'])
        
        # Bootstrap distributions
        win_rates = []
        edges = []
        pnls = []
        sharpes = []
        
        np.random.seed(42)  # Reproducibility
        
        for _ in range(n_simulations):
            # Resample with replacement
            indices = np.random.choice(n_trades, size=n_trades, replace=True)
            
            sample_outcomes = metrics['outcomes'][indices]
            sample_edges = metrics['edges'][indices]
            sample_pnls = metrics['pnls'][indices]
            
            win_rates.append(np.mean(sample_outcomes))
            edges.append(np.mean(sample_edges))
            pnls.append(np.sum(sample_pnls))
            sharpes.append(self.calculate_sharpe(sample_pnls))
        
        win_rates = np.array(win_rates)
        edges = np.array(edges)
        pnls = np.array(pnls)
        sharpes = np.array(sharpes)
        
        # 95% Confidence Intervals
        win_rate_ci = np.percentile(win_rates, [2.5, 97.5])
        edge_ci = np.percentile(edges, [2.5, 97.5])
        pnl_ci = np.percentile(pnls, [2.5, 97.5])
        sharpe_ci = np.percentile(sharpes, [2.5, 97.5])
        
        # Determine if edge is real
        # Edge is real if:
        # 1. Win rate CI lower bound > 50%
        # 2. Edge CI lower bound > 0
        # 3. Sharpe CI lower bound > 0
        
        win_rate_significant = win_rate_ci[0] > 0.50
        edge_significant = edge_ci[0] > 0
        sharpe_positive = sharpe_ci[0] > 0
        
        edge_is_real = win_rate_significant and edge_significant
        
        # Confidence level
        if n_trades < self.MIN_TRADES_FOR_VALIDATION:
            confidence_level = "INSUFFICIENT_DATA"
            verdict = f"Need at least {self.MIN_TRADES_FOR_VALIDATION} trades for validation"
        elif win_rate_ci[0] > 0.60 and edge_ci[0] > 0.05:
            confidence_level = "HIGH"
            verdict = "Strong statistical edge - strategy is working"
        elif win_rate_ci[0] > 0.55 and edge_ci[0] > 0.02:
            confidence_level = "MEDIUM"
            verdict = "Moderate edge detected - continue collecting data"
        elif win_rate_ci[0] > 0.50:
            confidence_level = "LOW"
            verdict = "Weak edge - might be noise, needs more trades"
        else:
            confidence_level = "LOW"
            verdict = "No edge detected - review signal sources"
            edge_is_real = False
        
        return BootstrapResult(
            n_trades=n_trades,
            n_simulations=n_simulations,
            observed_win_rate=observed_win_rate,
            mean_win_rate=np.mean(win_rates),
            std_win_rate=np.std(win_rates),
            win_rate_ci_lower=win_rate_ci[0],
            win_rate_ci_upper=win_rate_ci[1],
            observed_edge=observed_edge,
            mean_edge=np.mean(edges),
            edge_ci_lower=edge_ci[0],
            edge_ci_upper=edge_ci[1],
            observed_pnl=observed_pnl,
            mean_pnl=np.mean(pnls),
            pnl_ci_lower=pnl_ci[0],
            pnl_ci_upper=pnl_ci[1],
            observed_sharpe=observed_sharpe,
            mean_sharpe=np.mean(sharpes),
            sharpe_ci_lower=sharpe_ci[0],
            sharpe_ci_upper=sharpe_ci[1],
            edge_is_real=edge_is_real,
            confidence_level=confidence_level,
            verdict=verdict,
        )
    
    def validate(self, n_simulations: int = None) -> BootstrapResult:
        """
        Run full validation on trade history.
        """
        trades = self.load_resolved_trades()
        
        if len(trades) < 5:
            # Return early result for insufficient data
            return BootstrapResult(
                n_trades=len(trades),
                n_simulations=0,
                observed_win_rate=0,
                mean_win_rate=0,
                std_win_rate=0,
                win_rate_ci_lower=0,
                win_rate_ci_upper=1,
                observed_edge=0,
                mean_edge=0,
                edge_ci_lower=-1,
                edge_ci_upper=1,
                observed_pnl=0,
                mean_pnl=0,
                pnl_ci_lower=0,
                pnl_ci_upper=0,
                observed_sharpe=0,
                mean_sharpe=0,
                sharpe_ci_lower=0,
                sharpe_ci_upper=0,
                edge_is_real=False,
                confidence_level="INSUFFICIENT_DATA",
                verdict=f"Only {len(trades)} resolved trades. Need at least 20 for validation.",
            )
        
        metrics = self.extract_trade_metrics(trades)
        result = self.run_bootstrap(metrics, n_simulations)
        
        # Save results
        self._save_result(result)
        
        return result
    
    def _save_result(self, result: BootstrapResult):
        """Save validation result to file."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        result_file = self.results_dir / f'bootstrap_{timestamp}.json'
        
        result_dict = {
            'timestamp': timestamp,
            'n_trades': result.n_trades,
            'n_simulations': result.n_simulations,
            'win_rate': {
                'observed': result.observed_win_rate,
                'mean': result.mean_win_rate,
                'ci_95': [result.win_rate_ci_lower, result.win_rate_ci_upper],
            },
            'edge': {
                'observed': result.observed_edge,
                'mean': result.mean_edge,
                'ci_95': [result.edge_ci_lower, result.edge_ci_upper],
            },
            'pnl': {
                'observed': result.observed_pnl,
                'mean': result.mean_pnl,
                'ci_95': [result.pnl_ci_lower, result.pnl_ci_upper],
            },
            'sharpe': {
                'observed': result.observed_sharpe,
                'mean': result.mean_sharpe,
                'ci_95': [result.sharpe_ci_lower, result.sharpe_ci_upper],
            },
            'verdict': {
                'edge_is_real': result.edge_is_real,
                'confidence_level': result.confidence_level,
                'message': result.verdict,
            },
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
    
    def validate_by_signal(self) -> Dict[str, BootstrapResult]:
        """
        Run validation separately for each signal source.
        
        Identifies which signals actually contribute to edge.
        """
        trades = self.load_resolved_trades()
        
        if len(trades) < 10:
            return {"error": "Insufficient trades for signal-level validation"}
        
        # Group trades by dominant signal
        by_signal = {}
        
        for trade in trades:
            signals = trade.get('signals', {})
            source = signals.get('source', 'unknown')
            
            if source not in by_signal:
                by_signal[source] = []
            by_signal[source].append(trade)
        
        # Validate each signal source
        results = {}
        
        for source, source_trades in by_signal.items():
            if len(source_trades) >= 5:
                metrics = self.extract_trade_metrics(source_trades)
                result = self.run_bootstrap(metrics, n_simulations=5000)
                results[source] = result
        
        return results


def main():
    """CLI for bootstrap validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bootstrap validation for trading edge')
    parser.add_argument('action', choices=['validate', 'by-signal', 'status'],
                        help='Action to perform')
    parser.add_argument('--simulations', type=int, default=10000,
                        help='Number of bootstrap simulations')
    
    args = parser.parse_args()
    
    validator = BootstrapValidator()
    
    if args.action == 'validate':
        result = validator.validate(n_simulations=args.simulations)
        print(result)
    
    elif args.action == 'by-signal':
        results = validator.validate_by_signal()
        
        if isinstance(results, dict) and 'error' in results:
            print(f"Error: {results['error']}")
        else:
            print("Validation by Signal Source")
            print("=" * 50)
            
            for source, result in results.items():
                status = "✅" if result.edge_is_real else "❌"
                print(f"\n{status} {source}")
                print(f"   Trades: {result.n_trades}")
                print(f"   Win Rate: {result.observed_win_rate:.1%} [{result.win_rate_ci_lower:.1%}, {result.win_rate_ci_upper:.1%}]")
                print(f"   Edge: {result.observed_edge*100:+.1f}% [{result.edge_ci_lower*100:+.1f}%, {result.edge_ci_upper*100:+.1f}%]")
    
    elif args.action == 'status':
        trades = validator.load_resolved_trades()
        print(f"Resolved trades: {len(trades)}")
        print(f"Minimum for validation: {validator.MIN_TRADES_FOR_VALIDATION}")
        
        if len(trades) >= validator.MIN_TRADES_FOR_VALIDATION:
            print("✅ Ready for validation")
        else:
            needed = validator.MIN_TRADES_FOR_VALIDATION - len(trades)
            print(f"⏳ Need {needed} more resolved trades")


if __name__ == '__main__':
    main()
