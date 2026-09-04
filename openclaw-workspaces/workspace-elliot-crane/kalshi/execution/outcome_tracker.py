"""
Outcome Tracker
Closes the loop: monitors positions → detects settlements → updates trade log → calculates signal accuracy
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .logger import TradeLogger, Outcome


@dataclass
class SignalAccuracy:
    """Accuracy stats for a signal type."""
    signal_type: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    avg_pnl: float


class OutcomeTracker:
    """
    Tracks trade outcomes and calculates signal accuracy.
    """
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.logger = TradeLogger()
        self.stats_file = self.logger.log_dir / 'signal_accuracy.json'
    
    @property
    def kalshi(self):
        if self._kalshi is None:
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def check_settlements(self) -> List[Dict[str, Any]]:
        """
        Check for newly settled markets and update trade outcomes.
        Returns list of newly resolved trades.
        """
        pending = self.logger.get_pending_trades()
        if not pending:
            return []
        
        resolved = []
        
        for trade in pending:
            ticker = trade.get('ticker')
            if not ticker:
                continue
            
            try:
                # Check market status
                market = self.kalshi._request('GET', f'/markets/{ticker}').get('market', {})
                result = market.get('result')
                status = market.get('status')
                
                if status == 'settled' or result in ['yes', 'no']:
                    # Market has settled
                    side = trade.get('side')
                    entry_price = trade.get('entry_price', 0.5)
                    contracts = trade.get('contracts', 0)
                    
                    # Calculate P&L
                    if result == side:
                        # Won
                        exit_price = 1.0
                        pnl = (exit_price - entry_price) * contracts
                        won = True
                    else:
                        # Lost
                        exit_price = 0.0
                        pnl = -entry_price * contracts
                        won = False
                    
                    # Update the trade
                    self.logger.update_outcome(
                        trade_id=trade['id'],
                        outcome=Outcome.WIN if won else Outcome.LOSS,
                        exit_price=exit_price,
                        pnl=pnl,
                        settlement_date=datetime.now(timezone.utc).isoformat(),
                        notes=f"Market settled: {result}"
                    )
                    
                    resolved.append({
                        'trade_id': trade['id'],
                        'ticker': ticker,
                        'side': side,
                        'result': result,
                        'won': won,
                        'pnl': pnl,
                    })
                    
            except Exception as e:
                print(f"Error checking {ticker}: {e}")
                continue
        
        return resolved
    
    def calculate_signal_accuracy(self) -> Dict[str, SignalAccuracy]:
        """
        Calculate win rate by signal type.
        Groups trades by sentiment, VPIN level, and other factors.
        """
        trades = self.logger.get_all_trades()
        resolved = [t for t in trades if t.get('outcome') in ['win', 'loss']]
        
        if not resolved:
            return {}
        
        accuracy = {}
        
        # By sentiment
        for sentiment in ['bullish', 'bearish', 'neutral', 'mixed']:
            sent_trades = [t for t in resolved if t.get('sentiment') == sentiment]
            if sent_trades:
                wins = len([t for t in sent_trades if t['outcome'] == 'win'])
                losses = len(sent_trades) - wins
                total_pnl = sum(t.get('pnl', 0) or 0 for t in sent_trades)
                
                accuracy[f'sentiment_{sentiment}'] = SignalAccuracy(
                    signal_type=f'sentiment_{sentiment}',
                    total_trades=len(sent_trades),
                    wins=wins,
                    losses=losses,
                    win_rate=wins / len(sent_trades),
                    total_pnl=total_pnl,
                    avg_pnl=total_pnl / len(sent_trades)
                )
        
        # By VPIN level
        low_vpin = [t for t in resolved if (t.get('vpin') or 0) < 0.4]
        mid_vpin = [t for t in resolved if 0.4 <= (t.get('vpin') or 0) < 0.65]
        high_vpin = [t for t in resolved if (t.get('vpin') or 0) >= 0.65]
        
        for label, group in [('vpin_low', low_vpin), ('vpin_mid', mid_vpin), ('vpin_high', high_vpin)]:
            if group:
                wins = len([t for t in group if t['outcome'] == 'win'])
                losses = len(group) - wins
                total_pnl = sum(t.get('pnl', 0) or 0 for t in group)
                
                accuracy[label] = SignalAccuracy(
                    signal_type=label,
                    total_trades=len(group),
                    wins=wins,
                    losses=losses,
                    win_rate=wins / len(group),
                    total_pnl=total_pnl,
                    avg_pnl=total_pnl / len(group)
                )
        
        # By risk score
        low_risk = [t for t in resolved if (t.get('risk_score') or 50) < 30]
        mid_risk = [t for t in resolved if 30 <= (t.get('risk_score') or 50) < 60]
        high_risk = [t for t in resolved if (t.get('risk_score') or 50) >= 60]
        
        for label, group in [('risk_low', low_risk), ('risk_mid', mid_risk), ('risk_high', high_risk)]:
            if group:
                wins = len([t for t in group if t['outcome'] == 'win'])
                losses = len(group) - wins
                total_pnl = sum(t.get('pnl', 0) or 0 for t in group)
                
                accuracy[label] = SignalAccuracy(
                    signal_type=label,
                    total_trades=len(group),
                    wins=wins,
                    losses=losses,
                    win_rate=wins / len(group),
                    total_pnl=total_pnl,
                    avg_pnl=total_pnl / len(group)
                )
        
        # By edge size
        small_edge = [t for t in resolved if (t.get('edge_estimate') or 0) < 10]
        medium_edge = [t for t in resolved if 10 <= (t.get('edge_estimate') or 0) < 20]
        large_edge = [t for t in resolved if (t.get('edge_estimate') or 0) >= 20]
        
        for label, group in [('edge_small', small_edge), ('edge_medium', medium_edge), ('edge_large', large_edge)]:
            if group:
                wins = len([t for t in group if t['outcome'] == 'win'])
                losses = len(group) - wins
                total_pnl = sum(t.get('pnl', 0) or 0 for t in group)
                
                accuracy[label] = SignalAccuracy(
                    signal_type=label,
                    total_trades=len(group),
                    wins=wins,
                    losses=losses,
                    win_rate=wins / len(group),
                    total_pnl=total_pnl,
                    avg_pnl=total_pnl / len(group)
                )
        
        # Save stats
        stats_dict = {k: vars(v) for k, v in accuracy.items()}
        with open(self.stats_file, 'w') as f:
            json.dump(stats_dict, f, indent=2)
        
        return accuracy
    
    def report(self) -> str:
        """Generate signal accuracy report."""
        accuracy = self.calculate_signal_accuracy()
        
        if not accuracy:
            return "📊 No resolved trades yet for signal accuracy analysis."
        
        lines = [
            "═" * 55,
            "  SIGNAL ACCURACY REPORT",
            "═" * 55,
            "",
            f"  {'Signal Type':<20} {'Trades':>7} {'Win %':>8} {'Avg P&L':>10}",
            "  " + "-" * 50,
        ]
        
        # Sort by win rate descending
        sorted_signals = sorted(accuracy.items(), key=lambda x: x[1].win_rate, reverse=True)
        
        for signal_type, stats in sorted_signals:
            wr_str = f"{stats.win_rate*100:.0f}%"
            pnl_str = f"${stats.avg_pnl:+.2f}"
            lines.append(f"  {signal_type:<20} {stats.total_trades:>7} {wr_str:>8} {pnl_str:>10}")
        
        lines.extend([
            "",
            "═" * 55,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for outcome tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track trade outcomes and signal accuracy')
    parser.add_argument('action', choices=['check', 'accuracy', 'report'],
                        help='Action: check settlements, calculate accuracy, or full report')
    
    args = parser.parse_args()
    
    tracker = OutcomeTracker()
    
    if args.action == 'check':
        print("🔍 Checking for settled markets...")
        resolved = tracker.check_settlements()
        if resolved:
            print(f"\n✅ Resolved {len(resolved)} trades:")
            for r in resolved:
                emoji = "🟢" if r['won'] else "🔴"
                print(f"  {emoji} {r['ticker']}: {r['side'].upper()} → {r['result'].upper()} (${r['pnl']:+.2f})")
        else:
            print("No new settlements found.")
    
    elif args.action == 'accuracy':
        accuracy = tracker.calculate_signal_accuracy()
        if accuracy:
            print(f"\n📊 Calculated accuracy for {len(accuracy)} signal types")
        else:
            print("No resolved trades for accuracy calculation.")
    
    elif args.action == 'report':
        print(tracker.report())


if __name__ == '__main__':
    main()
