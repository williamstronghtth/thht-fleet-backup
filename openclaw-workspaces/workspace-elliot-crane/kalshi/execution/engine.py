"""
Trading Execution Engine
Semi-autonomous trading with configurable automation levels.

Rules:
- Edge > 15 points + all checks pass → AUTO-EXECUTE up to $25
- Edge > 10 points OR one check fails → NOTIFY and wait
- Edge < 10 points OR multiple checks fail → SKIP
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .logger import TradeLogger, TradeRecord, Action, Outcome

# Import signal combiner for Darwinian weights
try:
    from kalshi.signal_combiner import SignalCombiner
    from kalshi.darwin import create_signal_record
    SIGNAL_COMBINER_AVAILABLE = True
except ImportError:
    SIGNAL_COMBINER_AVAILABLE = False


class TradeDecision(Enum):
    AUTO_EXECUTE = "auto_execute"
    NOTIFY = "notify"
    SKIP = "skip"


@dataclass
class TradeOutcome:
    """Result of trade evaluation."""
    decision: TradeDecision
    reason: str
    edge: float
    side: str                          # "yes" or "no"
    suggested_size: float              # $ amount
    suggested_contracts: int
    confidence: float
    checks_passed: int
    checks_failed: int
    warnings: list


class TradingEngine:
    """
    Semi-autonomous trading engine.
    
    Evaluates opportunities, makes decisions, executes trades,
    and logs everything for learning.
    """
    
    # Configuration
    AUTO_EXECUTE_EDGE_THRESHOLD = 15    # Points needed for auto-execute
    NOTIFY_EDGE_THRESHOLD = 10          # Points needed for notification
    AUTO_EXECUTE_MAX_SIZE = 25          # Max $ for auto-execution
    
    # Risk limits
    MAX_VPIN = 0.65
    MAX_R_SQUARED = 0.15
    MAX_BRANCHING = 0.80
    MAX_DAILY_LOSS = 50
    MAX_POSITION_SIZE = 100             # Max $ per position
    
    def __init__(self, kalshi_client=None, dry_run: bool = False):
        """
        Initialize the trading engine.
        
        Parameters:
        -----------
        kalshi_client : optional pre-configured client
        dry_run : if True, log decisions but don't execute
        """
        self._kalshi = kalshi_client
        self.dry_run = dry_run
        self.logger = TradeLogger()
        
        # Initialize signal combiner for Darwinian weights
        self.signal_combiner = SignalCombiner() if SIGNAL_COMBINER_AVAILABLE else None
        
        # Load config for API keys
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load gateway config."""
        config_path = Path('/root/.openclaw/openclaw.json')
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}
    
    @property
    def kalshi(self):
        """Lazy load Kalshi client."""
        if self._kalshi is None:
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def evaluate(self, ticker: str) -> Tuple[TradeOutcome, Dict[str, Any]]:
        """
        Evaluate a market for trading opportunity.
        
        Returns:
        --------
        (TradeOutcome, full_analysis_dict)
        """
        from kalshi.microstructure.analyzer import MarketAnalyzer
        
        # Get market data
        market = self.kalshi._request('GET', f'/markets/{ticker}').get('market', {})
        title = market.get('title', ticker)
        
        yes_bid = float(market.get('yes_bid_dollars', '0.50') or '0.50')
        yes_ask = float(market.get('yes_ask_dollars', '0.50') or '0.50')
        market_price = (yes_bid + yes_ask) / 2
        
        # Run microstructure analysis
        analyzer = MarketAnalyzer()
        micro = analyzer.analyze_market(ticker, lookback_trades=100)
        
        # Run sentiment analysis
        sentiment_data = self._get_sentiment(title, market_price)
        
        # Calculate edge
        crowd_belief = sentiment_data.get('crowd_belief', 0.5)
        gap = crowd_belief - market_price
        edge = abs(gap) * 100  # Convert to points
        
        # Determine side
        if gap > 0:
            side = "yes"  # Crowd thinks YES more likely than market
        else:
            side = "no"   # Crowd thinks NO more likely than market
        
        # Run checks
        checks_passed = 0
        checks_failed = 0
        warnings = []
        
        # VPIN check
        if micro.vpin and micro.vpin.vpin > self.MAX_VPIN:
            checks_failed += 1
            warnings.append(f"High VPIN ({micro.vpin.vpin:.0%})")
        else:
            checks_passed += 1
        
        # Kyle R² check
        if micro.kyle and micro.kyle.r_squared > self.MAX_R_SQUARED:
            checks_failed += 1
            warnings.append(f"High R² ({micro.kyle.r_squared:.1%})")
        else:
            checks_passed += 1
        
        # Branching check
        if micro.hawkes and micro.hawkes.branching_ratio > self.MAX_BRANCHING:
            checks_failed += 1
            warnings.append(f"High branching ({micro.hawkes.branching_ratio:.0%})")
        else:
            checks_passed += 1
        
        # Spread check
        spread = (yes_ask - yes_bid) * 100
        if spread > 10:
            checks_failed += 1
            warnings.append(f"Wide spread ({spread:.0f}¢)")
        else:
            checks_passed += 1
        
        # Sentiment confidence check
        sent_conf = sentiment_data.get('confidence', 0.5)
        if sent_conf < 0.6:
            warnings.append(f"Low sentiment confidence ({sent_conf:.0%})")
        
        # Make decision
        if edge >= self.AUTO_EXECUTE_EDGE_THRESHOLD and checks_failed == 0:
            decision = TradeDecision.AUTO_EXECUTE
            reason = f"Strong edge ({edge:.0f}pts), all checks pass"
            suggested_size = min(edge * 1.5, self.AUTO_EXECUTE_MAX_SIZE)  # Scale with edge
        elif edge >= self.NOTIFY_EDGE_THRESHOLD or (edge >= 8 and checks_failed <= 1):
            decision = TradeDecision.NOTIFY
            reason = f"Moderate edge ({edge:.0f}pts), {checks_failed} check(s) failed"
            suggested_size = min(edge * 1.5, self.MAX_POSITION_SIZE * 0.5)
        else:
            decision = TradeDecision.SKIP
            reason = f"Insufficient edge ({edge:.0f}pts) or too many warnings"
            suggested_size = 0
        
        # Calculate contracts
        entry_price = yes_ask if side == "yes" else (1 - yes_bid)  # Pay the spread
        suggested_contracts = int(suggested_size / entry_price) if entry_price > 0 else 0
        
        outcome = TradeOutcome(
            decision=decision,
            reason=reason,
            edge=edge,
            side=side,
            suggested_size=suggested_size,
            suggested_contracts=suggested_contracts,
            confidence=sent_conf,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            warnings=warnings
        )
        
        full_analysis = {
            'ticker': ticker,
            'title': title,
            'market_price': market_price,
            'crowd_belief': crowd_belief,
            'gap': gap,
            'edge': edge,
            'side': side,
            'microstructure': {
                'risk_score': micro.risk_score,
                'vpin': micro.vpin.vpin if micro.vpin else None,
                'r_squared': micro.kyle.r_squared if micro.kyle else None,
                'branching': micro.hawkes.branching_ratio if micro.hawkes else None,
            },
            'sentiment': sentiment_data,
            'decision': outcome,
        }
        
        return outcome, full_analysis
    
    def _log_signals_for_darwin(self, trade_id: str, ticker: str, 
                                   analysis: Dict[str, Any], outcome: 'TradeOutcome'):
        """
        Log all signals from this trade for Darwinian weight tracking.
        
        This enables the system to learn which signals predict winners.
        """
        if not self.signal_combiner:
            return
        
        market_price = analysis.get('market_price', 0.5)
        
        # Get combined analysis which collects all signals
        combined = self.signal_combiner.analyze_market(
            ticker=ticker,
            market_price=market_price,
            title=analysis.get('title', ticker)
        )
        
        # Log each signal for later scoring
        self.signal_combiner.log_trade_signals(combined, trade_id)
        
        # Also log edge estimate as a signal
        if SIGNAL_COMBINER_AVAILABLE:
            from kalshi.darwin import SignalSource
            edge_signal = create_signal_record(
                source=SignalSource.EDGE_ESTIMATE.value,
                trade_id=trade_id,
                ticker=ticker,
                signal_value=combined.combined_probability,
                signal_direction='bullish' if outcome.side == 'yes' else 'bearish',
                confidence=outcome.confidence,
                our_estimate=combined.combined_probability,
                market_price=market_price,
            )
            self.signal_combiner.darwin.log_signal(edge_signal)
    
    def _get_sentiment(self, title: str, market_price: float) -> Dict[str, Any]:
        """Get sentiment analysis."""
        try:
            xai_key = self.config.get('env', {}).get('vars', {}).get('XAI_API_KEY')
            if not xai_key:
                return {'sentiment': None, 'error': 'No XAI key'}
            
            os.environ['XAI_API_KEY'] = xai_key
            
            from kalshi.sentiment.grok_client import GrokClient
            client = GrokClient()
            return client.analyze_market_sentiment(title, market_price)
        except Exception as e:
            return {'sentiment': None, 'error': str(e)}
    
    def execute_trade(self, ticker: str, side: str, contracts: int, 
                      analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade on Kalshi.
        
        Returns dict with execution details.
        """
        if self.dry_run:
            return {
                'executed': False,
                'dry_run': True,
                'would_have': f"BUY {contracts} {side.upper()} @ market"
            }
        
        try:
            # Place market order
            order = self.kalshi._request('POST', '/portfolio/orders', json={
                'ticker': ticker,
                'side': side,
                'action': 'buy',
                'type': 'market',
                'count': contracts,
            })
            
            return {
                'executed': True,
                'order_id': order.get('order', {}).get('order_id'),
                'contracts': contracts,
                'side': side,
                'fills': order.get('order', {}).get('fills', []),
            }
        except Exception as e:
            return {
                'executed': False,
                'error': str(e)
            }
    
    def process_opportunity(self, ticker: str) -> Dict[str, Any]:
        """
        Full pipeline: evaluate, decide, execute (if applicable), log.
        
        Returns complete result dict.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Evaluate
        outcome, analysis = self.evaluate(ticker)
        
        # Create log record
        record = TradeRecord(
            id="",  # Will be generated
            timestamp=timestamp,
            ticker=ticker,
            title=analysis['title'],
            market_price=analysis['market_price'],
            edge_estimate=outcome.edge,
            sentiment=analysis['sentiment'].get('sentiment', 'unknown'),
            sentiment_confidence=outcome.confidence,
            crowd_belief=analysis['crowd_belief'],
            risk_score=analysis['microstructure']['risk_score'],
            vpin=analysis['microstructure']['vpin'],
            kyle_r_squared=analysis['microstructure']['r_squared'],
            branching_ratio=analysis['microstructure']['branching'],
            action=outcome.decision.value,
            reason=outcome.reason,
            executed=False,
            side=outcome.side,
            contracts=None,
            entry_price=None,
            position_size=None,
        )
        
        result = {
            'timestamp': timestamp,
            'ticker': ticker,
            'decision': outcome.decision.value,
            'reason': outcome.reason,
            'edge': outcome.edge,
            'side': outcome.side,
            'suggested_size': outcome.suggested_size,
            'warnings': outcome.warnings,
            'executed': False,
        }
        
        # Execute if auto-execute
        if outcome.decision == TradeDecision.AUTO_EXECUTE:
            exec_result = self.execute_trade(
                ticker, 
                outcome.side, 
                outcome.suggested_contracts,
                analysis
            )
            
            record.executed = exec_result.get('executed', False)
            record.contracts = outcome.suggested_contracts
            record.entry_price = analysis['market_price']
            record.position_size = outcome.suggested_size
            
            result['executed'] = exec_result.get('executed', False)
            result['execution'] = exec_result
        
        # Log the trade
        trade_id = self.logger.log_trade(record)
        result['trade_id'] = trade_id
        
        # Log signals for Darwinian weight tracking
        if result.get('executed') or outcome.decision != TradeDecision.SKIP:
            self._log_signals_for_darwin(trade_id, ticker, analysis, outcome)
        
        return result
    
    def scan_and_execute(self, tickers: list) -> list:
        """
        Scan multiple tickers and process opportunities.
        
        Returns list of results.
        """
        results = []
        
        for ticker in tickers:
            try:
                result = self.process_opportunity(ticker)
                results.append(result)
                
                # Print decision
                emoji = {
                    'auto_execute': '🟢',
                    'notify': '🟡', 
                    'skip': '⚪'
                }.get(result['decision'], '❓')
                
                print(f"{emoji} {ticker}: {result['decision'].upper()}")
                print(f"   Edge: {result['edge']:.0f}pts | Side: {result['side'].upper()}")
                if result['warnings']:
                    print(f"   ⚠️ {', '.join(result['warnings'][:2])}")
                if result['executed']:
                    print(f"   ✅ EXECUTED: ${result['suggested_size']:.0f}")
                print()
                
            except Exception as e:
                print(f"❌ {ticker}: Error - {e}")
                results.append({'ticker': ticker, 'error': str(e)})
        
        return results
    
    def report(self) -> str:
        """Generate performance report."""
        return self.logger.report()
    
    def get_pending(self) -> list:
        """Get trades awaiting outcome resolution."""
        return self.logger.get_pending_trades()
    
    def resolve_trade(self, trade_id: str, won: bool, exit_price: float, pnl: float):
        """Resolve a pending trade with its outcome."""
        outcome = Outcome.WIN if won else Outcome.LOSS
        self.logger.update_outcome(trade_id, outcome, exit_price, pnl)
        
        # Score signals for Darwinian weight updates
        self._score_trade_signals(trade_id, won)
    
    def _score_trade_signals(self, trade_id: str, won: bool):
        """
        Score all signals associated with a trade.
        
        This updates the Darwinian weights based on actual outcomes.
        """
        if not self.signal_combiner:
            return
        
        # Load signal history and find signals for this trade
        signals = self.signal_combiner.darwin._load_signals()
        
        for signal in signals:
            if signal.get('trade_id') == trade_id and not signal.get('scored'):
                # Determine actual result based on signal direction
                # If signal was bullish and trade won (YES), signal was correct
                signal_dir = signal.get('signal_direction', 'neutral')
                
                if signal_dir == 'bullish':
                    actual_result = 1.0 if won else 0.0
                elif signal_dir == 'bearish':
                    actual_result = 0.0 if won else 1.0
                else:
                    actual_result = 0.5  # Neutral is always "correct"
                
                outcome_str = 'win' if won else 'loss'
                
                # Score the signal
                self.signal_combiner.darwin.score_signal(
                    signal['signal_id'],
                    outcome_str,
                    actual_result
                )
    
    def run_daily_darwin_update(self):
        """
        Run daily Darwinian weight update.
        
        Call this at end of day to adjust signal weights.
        """
        if not self.signal_combiner:
            return {"error": "Signal combiner not available"}
        
        return self.signal_combiner.darwin.run_daily_update()


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Execution Engine')
    parser.add_argument('action', choices=['evaluate', 'scan', 'report', 'pending'],
                        help='Action to perform')
    parser.add_argument('--ticker', help='Market ticker for evaluate')
    parser.add_argument('--tickers', nargs='+', help='Multiple tickers for scan')
    parser.add_argument('--dry-run', action='store_true', help='Log but do not execute')
    
    args = parser.parse_args()
    
    engine = TradingEngine(dry_run=args.dry_run)
    
    if args.action == 'evaluate':
        if not args.ticker:
            print("Error: --ticker required for evaluate")
            return
        outcome, analysis = engine.evaluate(args.ticker)
        print(f"\n📊 EVALUATION: {args.ticker}")
        print(f"Decision: {outcome.decision.value.upper()}")
        print(f"Reason: {outcome.reason}")
        print(f"Edge: {outcome.edge:.0f} points")
        print(f"Side: {outcome.side.upper()}")
        print(f"Suggested: {outcome.suggested_contracts} contracts (${outcome.suggested_size:.0f})")
        if outcome.warnings:
            print(f"Warnings: {', '.join(outcome.warnings)}")
    
    elif args.action == 'scan':
        if not args.tickers:
            print("Error: --tickers required for scan")
            return
        print(f"\n🔍 Scanning {len(args.tickers)} markets...\n")
        engine.scan_and_execute(args.tickers)
    
    elif args.action == 'report':
        print(engine.report())
    
    elif args.action == 'pending':
        pending = engine.get_pending()
        if pending:
            print(f"\n⏳ {len(pending)} trades awaiting resolution:\n")
            for t in pending:
                print(f"  {t['id']}: {t['ticker']} - {t['side'].upper()} ${t.get('position_size', 0):.0f}")
        else:
            print("\nNo pending trades.")


if __name__ == '__main__':
    main()
