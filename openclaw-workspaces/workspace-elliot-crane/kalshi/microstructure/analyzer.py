"""
Market Analyzer - Unified microstructure analysis for Kalshi markets
Combines Kyle's Lambda, Hawkes, VPIN, and Almgren-Chriss into one interface.
"""

import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

# Add parent directory to path for kalshi_client import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .kyle_lambda import estimate_kyle_lambda, infer_trade_direction, KyleLambdaResult
from .hawkes import fit_hawkes, HawkesResult
from .vpin import compute_vpin, VPINResult
from .almgren_chriss import quick_schedule, ExecutionSchedule


@dataclass
class MarketAnalysis:
    """Complete microstructure analysis for a market."""
    ticker: str
    timestamp: datetime
    
    # Component results
    kyle: Optional[KyleLambdaResult]
    hawkes: Optional[HawkesResult]
    vpin: Optional[VPINResult]
    
    # Orderbook stats
    bid: float
    ask: float
    spread: float
    book_depth: float
    
    # Overall assessment
    safe_to_trade: bool
    risk_score: float            # 0-100, higher = more risk
    recommendation: str
    warnings: List[str]
    
    # News check (when suspicious activity detected)
    news_check: Optional[Dict[str, Any]] = None
    
    def __str__(self):
        status = "✅ TRADEABLE" if self.safe_to_trade else "⚠️ AVOID"
        
        lines = [
            f"═══════════════════════════════════════════",
            f"  MARKET ANALYSIS: {self.ticker}",
            f"  {self.timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
            f"═══════════════════════════════════════════",
            f"",
            f"  Status: {status}",
            f"  Risk Score: {self.risk_score:.0f}/100",
            f"  Bid/Ask: {self.bid:.2f} / {self.ask:.2f} (spread: {self.spread:.2f})",
            f"  Book Depth: ${self.book_depth:,.0f}",
            f"",
        ]
        
        if self.warnings:
            lines.append("  ⚠️ WARNINGS:")
            for w in self.warnings:
                lines.append(f"    - {w}")
            lines.append("")
        
        lines.append(f"  → {self.recommendation}")
        lines.append("")
        
        if self.kyle:
            lines.append("  ─── Kyle's Lambda ───")
            lines.append(f"    λ = {self.kyle.lambda_value:.6f}, R² = {self.kyle.r_squared:.4f}")
            lines.append(f"    {self.kyle.interpretation}")
            lines.append("")
        
        if self.vpin:
            lines.append("  ─── VPIN ───")
            lines.append(f"    VPIN = {self.vpin.vpin:.3f} ({self.vpin.imbalance_direction} pressure)")
            lines.append(f"    {self.vpin.interpretation}")
            lines.append("")
        
        if self.hawkes:
            lines.append("  ─── Hawkes Process ───")
            lines.append(f"    Branching = {self.hawkes.branching_ratio:.1%}")
            lines.append(f"    {self.hawkes.interpretation}")
        
        return "\n".join(lines)


class MarketAnalyzer:
    """
    Unified market microstructure analyzer for Kalshi.
    """
    
    def __init__(self, kalshi_client=None):
        """
        Initialize analyzer with optional Kalshi client.
        If not provided, will import on first use.
        """
        self._client = kalshi_client
    
    @property
    def client(self):
        """Lazy load Kalshi client."""
        if self._client is None:
            try:
                from kalshi.kalshi_client import KalshiClient
                self._client = KalshiClient()
            except Exception as e:
                raise RuntimeError(f"Could not initialize Kalshi client: {e}")
        return self._client
    
    def check_breaking_news(self, title: str) -> dict:
        """
        Check for breaking news when suspicious activity is detected.
        Returns news context to help interpret unusual flow.
        """
        try:
            import os
            xai_key = os.environ.get('XAI_API_KEY')
            if not xai_key:
                # Try loading from config
                from pathlib import Path
                import json
                config_path = Path('/root/.openclaw/openclaw.json')
                if config_path.exists():
                    with open(config_path) as f:
                        config = json.load(f)
                    xai_key = config.get('env', {}).get('vars', {}).get('XAI_API_KEY')
            
            if not xai_key:
                return {'has_news': None, 'error': 'No XAI key'}
            
            os.environ['XAI_API_KEY'] = xai_key
            
            from kalshi.sentiment.grok_client import GrokClient
            client = GrokClient()
            
            # Search for breaking news in last 2 hours
            result = client.responses(
                f"""Search X for any BREAKING NEWS in the last 2 hours about: {title}
                
Focus on:
1. Official announcements or leaks
2. Insider information being shared
3. Unexpected developments
4. Any news that could move a prediction market

If there is significant breaking news, summarize it.
If there is NO breaking news, say "NO BREAKING NEWS FOUND" clearly.

This is to determine if unusual trading activity might be based on public or non-public information.""",
                tools=["x_search"]
            )
            
            # Extract text
            text = ""
            for item in result.get("output", []):
                if "content" in item:
                    for c in item.get("content", []):
                        if c.get("type") == "output_text":
                            text = c.get("text", "")
            
            has_news = "NO BREAKING NEWS FOUND" not in text.upper()
            
            return {
                'has_news': has_news,
                'summary': text[:500] if text else "",
                'interpretation': "Public news may explain activity" if has_news else "No public news - possible informed trading"
            }
        except Exception as e:
            return {'has_news': None, 'error': str(e)}
    
    def analyze_market(self, ticker: str, lookback_trades: int = 200) -> MarketAnalysis:
        """
        Run full microstructure analysis on a Kalshi market.
        
        Parameters:
        -----------
        ticker : Kalshi market ticker (e.g., 'KXCPI-26MAR-T0.7')
        lookback_trades : number of recent trades to analyze
        
        Returns:
        --------
        MarketAnalysis with all component results
        """
        warnings = []
        
        # Get market data
        try:
            market = self.client._request('GET', f'/markets/{ticker}').get('market', {})
        except Exception as e:
            return self._error_analysis(ticker, f"Could not fetch market: {e}")
        
        # Get orderbook
        try:
            book = self.client._request('GET', f'/markets/{ticker}/orderbook')
            # New API format: orderbook_fp with yes_dollars and no_dollars
            orderbook = book.get('orderbook_fp', book.get('orderbook', {}))
            yes_orders = orderbook.get('yes_dollars', orderbook.get('yes', []))
            no_orders = orderbook.get('no_dollars', orderbook.get('no', []))
            
            # Parse bid/ask - yes_dollars are YES bids, no_dollars are NO bids (YES asks)
            # Format: [price_str, size_str] where prices are in dollars
            if yes_orders:
                bid = max([float(b[0]) for b in yes_orders])
            else:
                bid = 0.01
            
            if no_orders:
                # NO bid at X means YES ask at (1-X)
                ask = 1 - min([float(a[0]) for a in no_orders])
            else:
                ask = 0.99
            
            spread = ask - bid
            
            # Calculate book depth ($ within 5 cents of mid)
            mid = (bid + ask) / 2
            book_depth = sum([float(b[1]) * float(b[0]) for b in yes_orders if float(b[0]) >= mid - 0.05])
            book_depth += sum([float(a[1]) * (1-float(a[0])) for a in no_orders if (1-float(a[0])) <= mid + 0.05])
        except Exception as e:
            warnings.append(f"Orderbook error: {e}")
            bid, ask, spread, book_depth = 0.5, 0.5, 0.0, 0.0
        
        # Get trade history (endpoint is /markets/trades with ticker param)
        try:
            trades_resp = self.client._request('GET', '/markets/trades', 
                                               params={'ticker': ticker, 'limit': lookback_trades})
            trades = trades_resp.get('trades', [])
        except Exception as e:
            warnings.append(f"Trade history error: {e}")
            trades = []
        
        # Run component analyses
        kyle_result = None
        hawkes_result = None
        vpin_result = None
        
        if len(trades) >= 20:
            # Extract trade data
            prices = []
            volumes = []
            signs = []
            timestamps = []
            buy_vols = []
            sell_vols = []
            
            for t in reversed(trades):  # Oldest first
                # Handle new API field names (yes_price_dollars, count_fp)
                price_str = t.get('yes_price_dollars', '0.50')
                price = float(price_str) if price_str else 0.50
                
                size_str = t.get('count_fp', '1')
                size = float(size_str) if size_str else 1.0
                
                ts = t.get('created_time', '')
                
                prices.append(price)
                volumes.append(size)
                
                # Infer direction from taker side if available, else from price movement
                taker_side = t.get('taker_side', '')
                if taker_side == 'yes':
                    sign = 1
                elif taker_side == 'no':
                    sign = -1
                else:
                    # Infer from price vs mid
                    sign = infer_trade_direction(price, bid, ask)
                
                signs.append(sign if sign != 0 else 1)
                
                if sign >= 0:
                    buy_vols.append(size)
                    sell_vols.append(0)
                else:
                    buy_vols.append(0)
                    sell_vols.append(size)
                
                # Parse timestamp for Hawkes
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps.append(dt.timestamp())
                    except:
                        pass
            
            # Kyle's Lambda
            try:
                kyle_result = estimate_kyle_lambda(
                    np.array(prices),
                    np.array(volumes),
                    np.array(signs)
                )
            except Exception as e:
                warnings.append(f"Kyle estimation error: {e}")
            
            # VPIN
            try:
                vpin_result = compute_vpin(
                    np.array(buy_vols),
                    np.array(sell_vols),
                    bucket_size=min(50, len(trades) // 4 + 1)
                )
            except Exception as e:
                warnings.append(f"VPIN error: {e}")
            
            # Hawkes (needs timestamps)
            if len(timestamps) >= 20:
                try:
                    ts_array = np.array(timestamps)
                    T = ts_array[-1] - ts_array[0]
                    hawkes_result = fit_hawkes(ts_array - ts_array[0], T)
                except Exception as e:
                    warnings.append(f"Hawkes fitting error: {e}")
        else:
            warnings.append(f"Insufficient trades for analysis ({len(trades)} < 20)")
        
        # Calculate overall risk score and recommendation
        risk_score = 0
        
        if kyle_result:
            if not kyle_result.safe_to_trade:
                risk_score += 40
            elif kyle_result.r_squared > 0.10:
                risk_score += 20
        
        if vpin_result:
            if not vpin_result.safe_to_trade:
                risk_score += 35
            elif vpin_result.vpin > 0.4:
                risk_score += 15
        
        if hawkes_result:
            if hawkes_result.is_momentum:
                risk_score += 25
            elif hawkes_result.branching_ratio > 0.6:
                risk_score += 10
        
        # Spread/liquidity penalties
        if spread > 0.10:
            risk_score += 15
            warnings.append(f"Wide spread ({spread:.0%})")
        if book_depth < 500:
            risk_score += 10
            warnings.append(f"Thin book (${book_depth:.0f})")
        
        # Check for breaking news if suspicious activity detected
        news_check = None
        if (vpin_result and vpin_result.vpin > 0.65) or (kyle_result and kyle_result.r_squared > 0.15):
            news_check = self.check_breaking_news(market.get('title', ticker))
            if news_check.get('has_news') == False:
                warnings.append("⚠️ Unusual flow with NO public news - possible insider activity")
            elif news_check.get('has_news') == True:
                warnings.append(f"📰 Breaking news detected - may explain flow")
        
        # Overall assessment
        safe_to_trade = risk_score < 50
        
        if risk_score >= 70:
            recommendation = "AVOID - High risk of adverse selection or momentum trap"
        elif risk_score >= 50:
            recommendation = "CAUTION - Elevated risk, reduce position size if trading"
        elif risk_score >= 30:
            recommendation = "MODERATE - Some risk factors, proceed with care"
        else:
            recommendation = "FAVORABLE - Normal market conditions for trading"
        
        return MarketAnalysis(
            ticker=ticker,
            timestamp=datetime.utcnow(),
            kyle=kyle_result,
            hawkes=hawkes_result,
            vpin=vpin_result,
            bid=bid,
            ask=ask,
            spread=spread,
            book_depth=book_depth,
            safe_to_trade=safe_to_trade,
            risk_score=risk_score,
            recommendation=recommendation,
            warnings=warnings,
            news_check=news_check
        )
    
    def get_execution_schedule(
        self,
        ticker: str,
        position_size: float,
        hours_available: float = 2.0
    ) -> ExecutionSchedule:
        """
        Generate optimal execution schedule for a position.
        
        Parameters:
        -----------
        ticker : market ticker
        position_size : total $ to execute
        hours_available : time window for execution
        
        Returns:
        --------
        ExecutionSchedule with trade times and sizes
        """
        # Get current orderbook for parameters
        try:
            book = self.client._request('GET', f'/markets/{ticker}/orderbook')
            orderbook = book.get('orderbook_fp', book.get('orderbook', {}))
            yes_orders = orderbook.get('yes_dollars', orderbook.get('yes', []))
            no_orders = orderbook.get('no_dollars', orderbook.get('no', []))
            
            bid = max([float(b[0]) for b in yes_orders]) if yes_orders else 0.01
            ask = 1 - min([float(a[0]) for a in no_orders]) if no_orders else 0.99
            spread = ask - bid
            
            mid = (bid + ask) / 2
            book_depth = sum([float(b[1]) * float(b[0]) for b in yes_orders if float(b[0]) >= mid - 0.05])
        except:
            spread = 0.05
            book_depth = 1000
        
        return quick_schedule(
            position_size=position_size,
            hours_available=hours_available,
            book_depth=book_depth,
            spread=spread
        )
    
    def _error_analysis(self, ticker: str, error: str) -> MarketAnalysis:
        """Return error state analysis."""
        return MarketAnalysis(
            ticker=ticker,
            timestamp=datetime.utcnow(),
            kyle=None,
            hawkes=None,
            vpin=None,
            bid=0.0,
            ask=0.0,
            spread=0.0,
            book_depth=0.0,
            safe_to_trade=False,
            risk_score=100,
            recommendation=f"ERROR: {error}",
            warnings=[error]
        )


def main():
    """CLI interface for market analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Kalshi market microstructure')
    parser.add_argument('ticker', help='Market ticker (e.g., KXCPI-26MAR-T0.7)')
    parser.add_argument('--trades', type=int, default=200, help='Number of trades to analyze')
    parser.add_argument('--exec', type=float, help='Generate execution schedule for this position size')
    
    args = parser.parse_args()
    
    analyzer = MarketAnalyzer()
    
    # Run analysis
    print(f"\nAnalyzing {args.ticker}...\n")
    analysis = analyzer.analyze_market(args.ticker, args.trades)
    print(analysis)
    
    # Execution schedule if requested
    if args.exec:
        print(f"\n\nExecution schedule for ${args.exec:.0f} position:\n")
        schedule = analyzer.get_execution_schedule(args.ticker, args.exec)
        print(schedule)


if __name__ == '__main__':
    main()
