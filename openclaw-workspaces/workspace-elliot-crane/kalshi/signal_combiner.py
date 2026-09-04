"""
Signal Combiner
===============

Combines signals from all sources using Darwinian weights.
This is the integration layer between our scanners and the weighting system.

Usage:
    from kalshi.signal_combiner import SignalCombiner
    
    combiner = SignalCombiner()
    analysis = combiner.analyze_market('KXCPI-26MAR-T0.7')
    
    print(f"Combined probability: {analysis['combined_probability']:.0%}")
    print(f"Dominant signal: {analysis['dominant_signal']}")
    print(f"Recommendation: {analysis['recommendation']}")
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

from kalshi.darwin import DarwinianWeights, SignalSource, create_signal_record


@dataclass
class MarketAnalysis:
    """Complete analysis of a market opportunity."""
    ticker: str
    title: str
    market_price: float
    
    # Individual signals
    signals: Dict[str, Dict]
    
    # Combined analysis
    combined_probability: float
    combined_edge: float
    confidence: str
    dominant_signal: str
    
    # Recommendation
    recommendation: str  # "STRONG_YES", "YES", "HOLD", "NO", "STRONG_NO"
    position_size: str  # "full", "half", "quarter", "skip"
    reasoning: str


class SignalCombiner:
    """
    Combines multiple signal sources using Darwinian weights.
    """
    
    def __init__(self):
        self.darwin = DarwinianWeights()
        
        # Lazy load scanners
        self._weather_scanner = None
        self._sentiment_client = None
        self._microstructure = None
    
    @property
    def weather_scanner(self):
        if self._weather_scanner is None:
            from kalshi.weather_scanner import WeatherScanner
            self._weather_scanner = WeatherScanner()
        return self._weather_scanner
    
    @property
    def sentiment_client(self):
        if self._sentiment_client is None:
            try:
                from kalshi.sentiment.grok_client import GrokSentimentClient
                self._sentiment_client = GrokSentimentClient()
            except:
                self._sentiment_client = None
        return self._sentiment_client
    
    @property
    def microstructure(self):
        if self._microstructure is None:
            try:
                from kalshi.microstructure.analyzer import MarketAnalyzer
                self._microstructure = MarketAnalyzer()
            except:
                self._microstructure = None
        return self._microstructure
    
    def get_weather_signal(self, ticker: str) -> Optional[Dict]:
        """Get weather forecast signal for a ticker."""
        try:
            opps = self.weather_scanner.scan()
            
            for opp in opps:
                if opp.ticker == ticker:
                    return {
                        'source': SignalSource.WEATHER_FORECAST.value,
                        'value': opp.forecast_prob,
                        'direction': 'bullish' if opp.edge > 0 else 'bearish',
                        'confidence': 0.8 if opp.confidence == 'HIGH' else 0.6 if opp.confidence == 'MEDIUM' else 0.4,
                        'detail': opp.forecast_detail,
                    }
            return None
        except Exception as e:
            print(f"Weather signal error: {e}")
            return None
    
    def get_sentiment_signal(self, ticker: str, topic: str = None) -> Optional[Dict]:
        """Get sentiment signal for a ticker/topic."""
        if not self.sentiment_client:
            return None
        
        try:
            # Extract topic from ticker if not provided
            if topic is None:
                if 'CPI' in ticker:
                    topic = "CPI inflation March 2026"
                elif 'GDP' in ticker:
                    topic = "GDP Q1 2026 growth"
                elif 'HIGHDEN' in ticker:
                    topic = "Denver weather temperature"
                else:
                    return None
            
            result = self.sentiment_client.analyze(topic)
            
            return {
                'source': SignalSource.SENTIMENT_GROK.value,
                'value': result.get('bullish_probability', 0.5),
                'direction': result.get('direction', 'neutral'),
                'confidence': result.get('confidence', 0.5),
                'detail': result.get('summary', ''),
            }
        except Exception as e:
            print(f"Sentiment signal error: {e}")
            return None
    
    def get_microstructure_signal(self, ticker: str) -> Optional[Dict]:
        """Get microstructure signals (VPIN, Kyle's λ, etc.)."""
        if not self.microstructure:
            return None
        
        try:
            result = self.microstructure.analyze_market(ticker)
            
            # VPIN signal - handle both float and VPINResult
            vpin_raw = result.vpin if hasattr(result, 'vpin') else 0.5
            vpin = float(vpin_raw.vpin) if hasattr(vpin_raw, 'vpin') else float(vpin_raw)
            
            # Convert VPIN to probability adjustment
            # High VPIN = informed trading = market might be right
            if vpin > 0.65:
                direction = 'neutral'  # Don't fight informed flow
                confidence = 0.3  # Low confidence in our edge
            elif vpin < 0.4:
                direction = 'bullish'  # Normal flow, trust our analysis
                confidence = 0.7
            else:
                direction = 'neutral'
                confidence = 0.5
            
            return {
                'source': SignalSource.VPIN.value,
                'value': 1 - vpin,  # Invert: low VPIN = good for us
                'direction': direction,
                'confidence': confidence,
                'detail': f"VPIN: {vpin:.2f}, Risk: {result.risk_score}/100",
                'vpin': vpin,
                'risk_score': result.risk_score,
            }
        except Exception as e:
            print(f"Microstructure signal error: {e}")
            return None
    
    def analyze_market(self, ticker: str, market_price: float = None, 
                        title: str = None) -> MarketAnalysis:
        """
        Perform complete analysis of a market using all available signals.
        """
        # Collect signals
        signals = {}
        
        # Weather signal
        weather = self.get_weather_signal(ticker)
        if weather:
            signals[weather['source']] = weather
        
        # Microstructure signal
        micro = self.get_microstructure_signal(ticker)
        if micro:
            signals[micro['source']] = micro
        
        # Sentiment (if available and relevant)
        # sentiment = self.get_sentiment_signal(ticker)
        # if sentiment:
        #     signals[sentiment['source']] = sentiment
        
        # Calculate combined analysis
        if signals:
            combined = self.darwin.calculate_combined_edge(
                {s: {'value': d['value'], 'confidence': d['confidence']} 
                 for s, d in signals.items()}
            )
            combined_prob = combined['combined_probability']
            confidence = combined['confidence']
            dominant = combined['dominant_signal']
        else:
            combined_prob = 0.5
            confidence = 'LOW'
            dominant = None
        
        # Get market price if not provided
        if market_price is None:
            market_price = 0.5  # Default
        
        combined_edge = combined_prob - market_price
        
        # Generate recommendation
        recommendation, position_size, reasoning = self._generate_recommendation(
            combined_edge, confidence, signals
        )
        
        return MarketAnalysis(
            ticker=ticker,
            title=title or ticker,
            market_price=market_price,
            signals=signals,
            combined_probability=combined_prob,
            combined_edge=combined_edge,
            confidence=confidence,
            dominant_signal=dominant,
            recommendation=recommendation,
            position_size=position_size,
            reasoning=reasoning,
        )
    
    def _generate_recommendation(self, edge: float, confidence: str, 
                                   signals: Dict) -> tuple:
        """Generate trading recommendation from analysis."""
        abs_edge = abs(edge)
        direction = "YES" if edge > 0 else "NO"
        
        # Check for danger signals
        vpin_signal = signals.get(SignalSource.VPIN.value, {})
        if vpin_signal.get('vpin', 0) > 0.65:
            return "HOLD", "skip", "High VPIN indicates informed trading - stay out"
        
        if vpin_signal.get('risk_score', 0) > 70:
            return "HOLD", "skip", f"High risk score ({vpin_signal['risk_score']}/100)"
        
        # Generate recommendation based on edge and confidence
        if abs_edge >= 0.15 and confidence == 'HIGH':
            rec = f"STRONG_{direction}"
            size = "full"
            reason = f"Strong {abs_edge*100:.0f}% edge with high confidence"
        elif abs_edge >= 0.10:
            rec = direction
            size = "half" if confidence == 'HIGH' else "quarter"
            reason = f"Good {abs_edge*100:.0f}% edge, {confidence.lower()} confidence"
        elif abs_edge >= 0.05:
            rec = direction
            size = "quarter"
            reason = f"Modest {abs_edge*100:.0f}% edge - small position only"
        else:
            rec = "HOLD"
            size = "skip"
            reason = f"Edge too small ({abs_edge*100:.0f}%)"
        
        return rec, size, reason
    
    def log_trade_signals(self, analysis: MarketAnalysis, trade_id: str):
        """Log all signals from an analysis for later scoring."""
        for source, signal in analysis.signals.items():
            record = create_signal_record(
                source=source,
                trade_id=trade_id,
                ticker=analysis.ticker,
                signal_value=signal['value'],
                signal_direction=signal['direction'],
                confidence=signal['confidence'],
                our_estimate=analysis.combined_probability,
                market_price=analysis.market_price,
            )
            self.darwin.log_signal(record)
    
    def report(self, ticker: str = None) -> str:
        """Generate analysis report."""
        lines = [
            "═" * 70,
            "  SIGNAL COMBINER ANALYSIS",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 70,
            "",
        ]
        
        if ticker:
            analysis = self.analyze_market(ticker)
            
            lines.extend([
                f"  Market: {analysis.ticker}",
                f"  Market Price: {analysis.market_price*100:.0f}%",
                f"  Combined Probability: {analysis.combined_probability*100:.0f}%",
                f"  Combined Edge: {analysis.combined_edge*100:+.0f}%",
                f"  Confidence: {analysis.confidence}",
                f"  Dominant Signal: {analysis.dominant_signal}",
                "",
                f"  Recommendation: {analysis.recommendation}",
                f"  Position Size: {analysis.position_size}",
                f"  Reasoning: {analysis.reasoning}",
                "",
                "  Individual Signals:",
            ])
            
            for source, signal in analysis.signals.items():
                weight = self.darwin.get_weight(source)
                lines.append(
                    f"    {source}: {signal['value']*100:.0f}% ({signal['direction']}) "
                    f"[weight: {weight:.2f}x]"
                )
        
        lines.extend([
            "",
            "═" * 70,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for signal combiner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Signal Combiner')
    parser.add_argument('action', choices=['analyze', 'weights'],
                        help='Action to perform')
    parser.add_argument('--ticker', help='Ticker to analyze')
    
    args = parser.parse_args()
    
    combiner = SignalCombiner()
    
    if args.action == 'analyze':
        if args.ticker:
            print(combiner.report(args.ticker))
        else:
            print("Error: --ticker required for analyze")
    
    elif args.action == 'weights':
        print(combiner.darwin.report())


if __name__ == '__main__':
    main()
