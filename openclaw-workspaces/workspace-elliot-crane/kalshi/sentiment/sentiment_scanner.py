"""
Sentiment Scanner for Kalshi Markets
Combines Grok X Search with market data for sentiment-based trading signals.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .grok_client import GrokClient


@dataclass
class SentimentResult:
    """Complete sentiment analysis for a market."""
    ticker: str
    title: str
    timestamp: datetime
    
    # Market data
    market_price: float
    
    # Sentiment data
    crowd_belief: float
    sentiment: str  # bullish/bearish/neutral/mixed
    confidence: float
    
    # Analysis
    gap: float  # crowd_belief - market_price
    signal: str  # BUY/SELL/WATCH/NEUTRAL
    summary: str
    
    # Quality indicators
    narrative_quality: str  # organic/coordinated
    breaking_news: bool
    
    def __str__(self):
        direction = "📈" if self.gap > 0 else "📉" if self.gap < 0 else "➡️"
        signal_emoji = {
            "BUY": "🟢",
            "SELL": "🔴", 
            "WATCH": "🟡",
            "NEUTRAL": "⚪"
        }.get(self.signal.split()[0], "⚪")
        
        return f"""
═══════════════════════════════════════════
  SENTIMENT ANALYSIS: {self.ticker}
  {self.timestamp.strftime('%Y-%m-%d %H:%M UTC')}
═══════════════════════════════════════════

  {self.title}

  Market Price:  {self.market_price*100:.0f}%
  Crowd Belief:  {self.crowd_belief*100:.0f}% ({self.sentiment})
  Gap:           {direction} {self.gap*100:+.0f} points
  Confidence:    {self.confidence*100:.0f}%
  
  Signal: {signal_emoji} {self.signal}
  
  Narrative: {self.narrative_quality}
  Breaking News: {"🚨 YES" if self.breaking_news else "No"}
  
  Summary:
  {self.summary[:300]}{'...' if len(self.summary) > 300 else ''}
"""


class SentimentScanner:
    """
    Scans Kalshi markets for sentiment-based trading opportunities.
    """
    
    def __init__(self, grok_client: Optional[GrokClient] = None, kalshi_client=None):
        """Initialize with optional pre-configured clients."""
        self._grok = grok_client
        self._kalshi = kalshi_client
    
    @property
    def grok(self):
        """Lazy load Grok client."""
        if self._grok is None:
            self._grok = GrokClient()
        return self._grok
    
    @property
    def kalshi(self):
        """Lazy load Kalshi client."""
        if self._kalshi is None:
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def analyze_market(self, ticker: str) -> SentimentResult:
        """
        Run full sentiment analysis on a Kalshi market.
        
        Parameters:
        -----------
        ticker : Kalshi market ticker
        
        Returns:
        --------
        SentimentResult with sentiment vs market comparison
        """
        # Get market data
        market = self.kalshi._request('GET', f'/markets/{ticker}').get('market', {})
        title = market.get('title', ticker)
        
        # Get current price (yes_bid as proxy for market belief)
        yes_bid = float(market.get('yes_bid_dollars', '0.50') or '0.50')
        yes_ask = float(market.get('yes_ask_dollars', '0.50') or '0.50')
        market_price = (yes_bid + yes_ask) / 2
        
        # Run sentiment analysis
        analysis = self.grok.analyze_market_sentiment(
            market_description=title,
            current_price=market_price
        )
        
        # Determine signal strength
        gap = analysis['gap']
        if abs(gap) >= 0.15:
            signal = "BUY - Strong divergence" if gap > 0 else "SELL - Strong divergence"
        elif abs(gap) >= 0.10:
            signal = "BUY - Moderate divergence" if gap > 0 else "SELL - Moderate divergence"
        elif abs(gap) >= 0.05:
            signal = "WATCH - Slight divergence"
        else:
            signal = "NEUTRAL - Aligned"
        
        # Check for breaking news indicators
        summary_lower = analysis.get('summary', '').lower()
        breaking_keywords = ['breaking', 'just in', 'developing', 'just announced', 'moments ago']
        breaking_news = any(kw in summary_lower for kw in breaking_keywords)
        
        # Check narrative quality (placeholder - would need more sophisticated analysis)
        narrative_quality = "organic"  # Default assumption
        
        return SentimentResult(
            ticker=ticker,
            title=title,
            timestamp=datetime.utcnow(),
            market_price=market_price,
            crowd_belief=analysis['crowd_belief'],
            sentiment=analysis['sentiment'],
            confidence=analysis['confidence'],
            gap=gap,
            signal=signal,
            summary=analysis.get('summary', ''),
            narrative_quality=narrative_quality,
            breaking_news=breaking_news
        )
    
    def scan_markets(
        self,
        tickers: List[str],
        min_gap: float = 0.10
    ) -> List[SentimentResult]:
        """
        Scan multiple markets for sentiment opportunities.
        
        Parameters:
        -----------
        tickers : list of market tickers to scan
        min_gap : minimum sentiment-market gap to report
        
        Returns:
        --------
        List of SentimentResult, sorted by gap magnitude
        """
        results = []
        
        for ticker in tickers:
            try:
                result = self.analyze_market(ticker)
                if abs(result.gap) >= min_gap:
                    results.append(result)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                continue
        
        # Sort by gap magnitude (largest opportunity first)
        results.sort(key=lambda r: abs(r.gap), reverse=True)
        
        return results
    
    def quick_sentiment(self, topic: str) -> Dict[str, Any]:
        """
        Quick sentiment check on any topic (not tied to specific market).
        
        Parameters:
        -----------
        topic : topic to search (e.g., "Federal Reserve rate decision")
        
        Returns:
        --------
        Dict with sentiment, confidence, and summary
        """
        result = self.grok.x_search(topic)
        
        return {
            "topic": topic,
            "sentiment": result.sentiment,
            "confidence": result.confidence,
            "summary": result.summary,
            "timestamp": datetime.utcnow().isoformat()
        }


def main():
    """CLI for sentiment scanning."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Kalshi market sentiment via X')
    parser.add_argument('ticker', nargs='?', help='Market ticker to analyze')
    parser.add_argument('--topic', help='Quick sentiment check on any topic')
    parser.add_argument('--scan', nargs='+', help='Scan multiple tickers')
    parser.add_argument('--min-gap', type=float, default=0.10, help='Minimum gap to report')
    
    args = parser.parse_args()
    
    scanner = SentimentScanner()
    
    if args.topic:
        print(f"\n🔍 Quick sentiment check: {args.topic}\n")
        result = scanner.quick_sentiment(args.topic)
        print(f"Sentiment: {result['sentiment']} (confidence: {result['confidence']:.0%})")
        print(f"Summary: {result['summary'][:500]}")
    
    elif args.scan:
        print(f"\n🔍 Scanning {len(args.scan)} markets...\n")
        results = scanner.scan_markets(args.scan, args.min_gap)
        for r in results:
            print(r)
    
    elif args.ticker:
        print(f"\n🔍 Analyzing {args.ticker}...\n")
        result = scanner.analyze_market(args.ticker)
        print(result)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
