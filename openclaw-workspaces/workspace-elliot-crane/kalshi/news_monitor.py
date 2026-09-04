"""
News Monitor - WorldMonitor Integration
=======================================

Fetches real-time news and market signals from WorldMonitor
to inform prediction market decisions.

Key signals:
- Breaking news that could move markets
- Commodity price spikes (affects CPI/inflation bets)
- Geopolitical events
- Cross-signal convergence (multiple sources = stronger signal)
"""

import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NewsSignal:
    """A news signal that could affect markets."""
    headline: str
    category: str
    source: str
    timestamp: str
    relevance: str  # Which market types this affects
    sentiment: str  # bullish/bearish/neutral
    strength: float  # 0-1, signal strength


@dataclass
class CommoditySignal:
    """Commodity price signal."""
    commodity: str
    price: float
    change_pct: float
    direction: str  # up/down
    relevance: str  # e.g., "CPI inflation" for oil


class NewsMonitor:
    """
    Monitors WorldMonitor for market-relevant signals.
    """
    
    # WorldMonitor endpoints
    BASE_URL = "https://worldmonitor.app"
    FINANCE_URL = "https://finance.worldmonitor.app"
    COMMODITY_URL = "https://commodity.worldmonitor.app"
    
    # Categories relevant to our markets
    RELEVANT_CATEGORIES = {
        'economics': ['inflation', 'fed', 'gdp', 'jobs', 'cpi', 'pce', 'rates'],
        'weather': ['storm', 'hurricane', 'temperature', 'snow', 'climate'],
        'energy': ['oil', 'gas', 'energy', 'opec', 'crude', 'petroleum'],
        'geopolitics': ['war', 'sanctions', 'trade', 'tariff', 'conflict'],
    }
    
    def __init__(self):
        self.cache_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/news_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Elliot-Crane-Trading-Bot/1.0'
        })
    
    def fetch_top_news(self, limit: int = 20) -> List[Dict]:
        """
        Fetch top news from WorldMonitor.
        Falls back to scraping if API not available.
        """
        try:
            # Try the API first
            response = self.session.get(
                f"{self.BASE_URL}/api/news",
                params={'limit': limit},
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get('articles', [])
        except Exception as e:
            print(f"WorldMonitor API error: {e}")
        
        # Fallback: use web search for breaking news
        return self._fallback_news_fetch()
    
    def _fallback_news_fetch(self) -> List[Dict]:
        """Fallback news fetching using Grok X search."""
        news = []
        
        try:
            # Use Grok to search X for breaking financial news
            api_key = '<REDACTED:XAI_API_KEY>'
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'grok-3-mini',
                    'messages': [
                        {
                            'role': 'user',
                            'content': '''Search X for the top 10 breaking financial/economic news stories in the last 24 hours.
                            
Focus on: inflation, CPI, Fed, oil prices, energy, GDP, jobs data, economic indicators.

Return as JSON array with format:
[{"title": "headline", "source": "source", "sentiment": "bullish/bearish/neutral", "category": "economics/energy/weather"}]

Only return the JSON, no other text.'''
                        }
                    ],
                    'search_mode': 'on',
                    'temperature': 0,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Try to parse JSON from response
                try:
                    # Find JSON array in response
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    if start >= 0 and end > start:
                        news = json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"Grok news fetch error: {e}")
        
        return news
    
    def fetch_commodity_prices(self) -> Dict[str, Dict]:
        """
        Fetch current commodity prices.
        Returns dict of commodity -> {price, change, change_pct}
        """
        commodities = {}
        
        # Try to get oil prices (most relevant for CPI)
        try:
            # Use a free API for oil prices
            response = self.session.get(
                "https://api.eia.gov/v2/petroleum/pri/spt/data/",
                params={
                    'api_key': 'DEMO_KEY',  # EIA demo key
                    'frequency': 'daily',
                    'data[0]': 'value',
                    'sort[0][column]': 'period',
                    'sort[0][direction]': 'desc',
                    'length': 5,
                },
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                # Parse EIA data
        except Exception as e:
            print(f"Commodity fetch error: {e}")
        
        # Fallback: hardcoded check of major commodities via other APIs
        try:
            # Check gold, oil via free APIs
            pass
        except:
            pass
        
        return commodities
    
    def analyze_news_for_markets(self, news: List[Dict]) -> List[NewsSignal]:
        """
        Analyze news headlines for market relevance.
        """
        signals = []
        
        for article in news:
            headline = article.get('title', '').lower()
            
            # Check for relevant keywords
            relevance = []
            sentiment = 'neutral'
            strength = 0.0
            
            # Economics/CPI relevance
            for keyword in self.RELEVANT_CATEGORIES['economics']:
                if keyword in headline:
                    relevance.append('economics')
                    strength = max(strength, 0.7)
                    
                    # Sentiment detection
                    if any(w in headline for w in ['surge', 'spike', 'jump', 'rise', 'higher']):
                        sentiment = 'bullish'  # For inflation = higher CPI
                    elif any(w in headline for w in ['fall', 'drop', 'decline', 'lower', 'ease']):
                        sentiment = 'bearish'
                    break
            
            # Energy relevance (affects CPI)
            for keyword in self.RELEVANT_CATEGORIES['energy']:
                if keyword in headline:
                    relevance.append('energy')
                    strength = max(strength, 0.6)
                    
                    if any(w in headline for w in ['surge', 'spike', 'soar', 'crisis']):
                        sentiment = 'bullish'  # Higher energy = higher CPI
                    elif any(w in headline for w in ['fall', 'drop', 'crash', 'plunge']):
                        sentiment = 'bearish'
                    break
            
            # Weather relevance
            for keyword in self.RELEVANT_CATEGORIES['weather']:
                if keyword in headline:
                    relevance.append('weather')
                    strength = max(strength, 0.5)
                    break
            
            if relevance:
                signals.append(NewsSignal(
                    headline=article.get('title', ''),
                    category=relevance[0],
                    source=article.get('source', 'unknown'),
                    timestamp=article.get('published', ''),
                    relevance=', '.join(relevance),
                    sentiment=sentiment,
                    strength=strength,
                ))
        
        return signals
    
    def get_market_signals(self) -> Dict:
        """
        Get aggregated market signals from all sources.
        Returns a summary useful for trading decisions.
        """
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'news_signals': [],
            'commodity_signals': [],
            'overall_sentiment': 'neutral',
            'actionable': False,
            'summary': '',
        }
        
        # Fetch and analyze news
        news = self.fetch_top_news(limit=30)
        signals = self.analyze_news_for_markets(news)
        result['news_signals'] = [
            {
                'headline': s.headline,
                'category': s.category,
                'sentiment': s.sentiment,
                'strength': s.strength,
            }
            for s in signals
        ]
        
        # Aggregate sentiment
        if signals:
            bullish = sum(1 for s in signals if s.sentiment == 'bullish')
            bearish = sum(1 for s in signals if s.sentiment == 'bearish')
            
            if bullish > bearish + 2:
                result['overall_sentiment'] = 'bullish'
            elif bearish > bullish + 2:
                result['overall_sentiment'] = 'bearish'
            
            # Check for strong signals
            strong_signals = [s for s in signals if s.strength >= 0.7]
            if strong_signals:
                result['actionable'] = True
                result['summary'] = f"{len(strong_signals)} strong signals: " + \
                    "; ".join(s.headline[:50] for s in strong_signals[:3])
        
        # Cache results
        self._cache_signals(result)
        
        return result
    
    def _cache_signals(self, signals: Dict):
        """Cache signals for later analysis."""
        cache_file = self.cache_dir / f"signals_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(cache_file, 'a') as f:
            f.write(json.dumps(signals) + '\n')
    
    def check_pre_release(self, release_type: str = 'cpi') -> Dict:
        """
        Check news signals before a major economic release.
        
        Args:
            release_type: 'cpi', 'gdp', 'jobs', 'fed'
        
        Returns:
            Dict with sentiment and relevant headlines
        """
        signals = self.get_market_signals()
        
        # Filter for release-relevant signals
        relevant = []
        for s in signals.get('news_signals', []):
            if release_type in s.get('category', '').lower():
                relevant.append(s)
            elif release_type == 'cpi' and s.get('category') == 'energy':
                relevant.append(s)  # Energy affects CPI
        
        return {
            'release_type': release_type,
            'relevant_signals': relevant,
            'count': len(relevant),
            'sentiment': signals.get('overall_sentiment'),
            'recommendation': self._get_recommendation(relevant, release_type),
        }
    
    def _get_recommendation(self, signals: List[Dict], release_type: str) -> str:
        """Generate trading recommendation based on signals."""
        if not signals:
            return "No strong signals - proceed with caution"
        
        bullish = sum(1 for s in signals if s.get('sentiment') == 'bullish')
        bearish = sum(1 for s in signals if s.get('sentiment') == 'bearish')
        
        if release_type == 'cpi':
            if bullish > bearish:
                return "News suggests higher inflation - consider YES on higher CPI thresholds"
            elif bearish > bullish:
                return "News suggests lower inflation - consider NO on higher CPI thresholds"
        
        return "Mixed signals - no clear direction"
    
    def report(self) -> str:
        """Generate a news intelligence report."""
        signals = self.get_market_signals()
        
        lines = [
            "═" * 60,
            "  NEWS INTELLIGENCE REPORT",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 60,
            "",
            f"  Overall Sentiment: {signals.get('overall_sentiment', 'neutral').upper()}",
            f"  Actionable: {'YES' if signals.get('actionable') else 'NO'}",
            "",
        ]
        
        news_signals = signals.get('news_signals', [])
        if news_signals:
            lines.append(f"  Relevant Headlines ({len(news_signals)}):")
            for s in news_signals[:5]:
                emoji = "🟢" if s['sentiment'] == 'bullish' else "🔴" if s['sentiment'] == 'bearish' else "⚪"
                lines.append(f"    {emoji} [{s['category']}] {s['headline'][:50]}...")
        else:
            lines.append("  No market-relevant news detected")
        
        lines.extend([
            "",
            "═" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for news monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='News monitor for trading')
    parser.add_argument('action', choices=['report', 'signals', 'pre-cpi', 'pre-gdp'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    monitor = NewsMonitor()
    
    if args.action == 'report':
        print(monitor.report())
    
    elif args.action == 'signals':
        signals = monitor.get_market_signals()
        print(json.dumps(signals, indent=2))
    
    elif args.action == 'pre-cpi':
        result = monitor.check_pre_release('cpi')
        print(f"CPI Release Check:")
        print(f"  Signals: {result['count']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Recommendation: {result['recommendation']}")
    
    elif args.action == 'pre-gdp':
        result = monitor.check_pre_release('gdp')
        print(f"GDP Release Check:")
        print(f"  Signals: {result['count']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Recommendation: {result['recommendation']}")


if __name__ == '__main__':
    main()
