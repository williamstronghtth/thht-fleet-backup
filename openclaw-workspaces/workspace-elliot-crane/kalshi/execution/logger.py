"""
Trade Logger
Persistent logging of all trading decisions and outcomes for learning.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from enum import Enum


class Action(Enum):
    AUTO_EXECUTE = "auto_execute"      # System executed automatically
    NOTIFY_WAIT = "notify_wait"        # Notified user, waiting for approval
    APPROVED = "approved"              # User approved, executed
    REJECTED = "rejected"              # User rejected
    SKIPPED = "skipped"                # System skipped (insufficient edge)
    MISSED = "missed"                  # Had edge but didn't act (timeout/hesitation)


class Outcome(Enum):
    PENDING = "pending"
    WIN = "win"
    LOSS = "loss"
    PUSH = "push"                      # Breakeven or cancelled


@dataclass
class TradeRecord:
    """Complete record of a trading decision."""
    # Identification
    id: str
    timestamp: str
    ticker: str
    title: str
    
    # Signal data
    market_price: float               # Price at signal time
    edge_estimate: float              # Our estimated edge in points
    sentiment: str                    # bullish/bearish/neutral/mixed
    sentiment_confidence: float
    crowd_belief: float
    
    # Microstructure
    risk_score: int
    vpin: Optional[float]
    kyle_r_squared: Optional[float]
    branching_ratio: Optional[float]
    
    # Decision
    action: str                       # Action enum value
    reason: str                       # Why this action was taken
    
    # Execution (if any)
    executed: bool
    side: Optional[str]               # "yes" or "no"
    contracts: Optional[int]
    entry_price: Optional[float]
    position_size: Optional[float]    # Total $ at risk
    
    # Outcome (filled in later)
    outcome: str = "pending"
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    settlement_date: Optional[str] = None
    
    # Meta
    notes: Optional[str] = None


class TradeLogger:
    """
    Persistent trade logging with analytics.
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path('/root/.openclaw/workspace-elliot-crane/kalshi/execution/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / 'trades.jsonl'
        self.stats_file = self.log_dir / 'stats.json'
    
    def _generate_id(self) -> str:
        """Generate unique trade ID."""
        now = datetime.now(timezone.utc)
        return f"T{now.strftime('%Y%m%d%H%M%S')}"
    
    def log_trade(self, record: TradeRecord) -> str:
        """
        Log a trade record.
        Returns the trade ID.
        """
        if not record.id:
            record.id = self._generate_id()
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
        
        return record.id
    
    def update_outcome(self, trade_id: str, outcome: Outcome, 
                       exit_price: float, pnl: float,
                       settlement_date: Optional[str] = None,
                       notes: Optional[str] = None) -> bool:
        """
        Update a trade with its outcome.
        """
        records = self.get_all_trades()
        updated = False
        
        for record in records:
            if record['id'] == trade_id:
                record['outcome'] = outcome.value
                record['exit_price'] = exit_price
                record['pnl'] = pnl
                record['settlement_date'] = settlement_date or datetime.now(timezone.utc).isoformat()
                if notes:
                    record['notes'] = notes
                updated = True
                break
        
        if updated:
            # Rewrite the log file
            with open(self.log_file, 'w') as f:
                for record in records:
                    f.write(json.dumps(record) + '\n')
        
        return updated
    
    def get_all_trades(self) -> List[Dict[str, Any]]:
        """Load all trade records."""
        if not self.log_file.exists():
            return []
        
        records = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records
    
    def get_pending_trades(self) -> List[Dict[str, Any]]:
        """Get trades awaiting outcome."""
        return [t for t in self.get_all_trades() if t.get('outcome') == 'pending']
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Calculate trading statistics.
        """
        trades = self.get_all_trades()
        
        if not trades:
            return {'total_trades': 0, 'message': 'No trades logged yet'}
        
        # Filter by action type
        executed = [t for t in trades if t.get('executed')]
        auto_executed = [t for t in trades if t.get('action') == 'auto_execute']
        notified = [t for t in trades if t.get('action') == 'notify_wait']
        skipped = [t for t in trades if t.get('action') == 'skipped']
        missed = [t for t in trades if t.get('action') == 'missed']
        
        # Outcomes for executed trades
        resolved = [t for t in executed if t.get('outcome') != 'pending']
        wins = [t for t in resolved if t.get('outcome') == 'win']
        losses = [t for t in resolved if t.get('outcome') == 'loss']
        
        # P&L
        total_pnl = sum(t.get('pnl', 0) or 0 for t in resolved)
        
        # Edge analysis
        edges_available = [t.get('edge_estimate', 0) for t in trades if t.get('edge_estimate')]
        edges_captured = [t.get('edge_estimate', 0) for t in executed if t.get('edge_estimate')]
        edges_missed = [t.get('edge_estimate', 0) for t in missed if t.get('edge_estimate')]
        
        # Signal quality by sentiment
        by_sentiment = {}
        for sent in ['bullish', 'bearish', 'neutral', 'mixed']:
            sent_trades = [t for t in resolved if t.get('sentiment') == sent]
            if sent_trades:
                sent_wins = len([t for t in sent_trades if t.get('outcome') == 'win'])
                by_sentiment[sent] = {
                    'count': len(sent_trades),
                    'win_rate': sent_wins / len(sent_trades) if sent_trades else 0
                }
        
        stats = {
            'total_signals': len(trades),
            'executed': len(executed),
            'auto_executed': len(auto_executed),
            'notified_awaiting': len([t for t in notified if t.get('outcome') == 'pending']),
            'skipped': len(skipped),
            'missed_opportunities': len(missed),
            
            'resolved': len(resolved),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(resolved) if resolved else None,
            
            'total_pnl': total_pnl,
            'avg_pnl_per_trade': total_pnl / len(resolved) if resolved else None,
            
            'avg_edge_available': sum(edges_available) / len(edges_available) if edges_available else 0,
            'avg_edge_captured': sum(edges_captured) / len(edges_captured) if edges_captured else 0,
            'edge_missed_total': sum(edges_missed),
            'missed_opportunity_rate': len(missed) / len(trades) if trades else 0,
            
            'by_sentiment': by_sentiment,
            
            'pending_resolution': len([t for t in executed if t.get('outcome') == 'pending']),
        }
        
        # Save stats
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def report(self) -> str:
        """Generate human-readable report."""
        stats = self.get_stats()
        
        if stats.get('total_signals', 0) == 0:
            return "📊 No trades logged yet."
        
        lines = [
            "═" * 50,
            "  TRADING PERFORMANCE REPORT",
            "═" * 50,
            "",
            f"  Total Signals:     {stats['total_signals']}",
            f"  Executed:          {stats['executed']} ({stats['auto_executed']} auto)",
            f"  Skipped:           {stats['skipped']}",
            f"  Missed:            {stats['missed_opportunities']} ⚠️",
            "",
        ]
        
        if stats['resolved'] > 0:
            lines.extend([
                f"  Resolved Trades:   {stats['resolved']}",
                f"  Win Rate:          {stats['win_rate']*100:.0f}%",
                f"  Total P&L:         ${stats['total_pnl']:.2f}",
                f"  Avg P&L/Trade:     ${stats['avg_pnl_per_trade']:.2f}",
                "",
            ])
        
        if stats['pending_resolution'] > 0:
            lines.append(f"  ⏳ Pending:         {stats['pending_resolution']} trades")
            lines.append("")
        
        if stats['missed_opportunities'] > 0:
            lines.extend([
                f"  ⚠️ MISSED OPPORTUNITIES",
                f"     {stats['missed_opportunities']} signals ({stats['missed_opportunity_rate']*100:.0f}%)",
                f"     Edge left on table: {stats['edge_missed_total']:.0f} points",
                "",
            ])
        
        lines.append("═" * 50)
        
        return "\n".join(lines)
