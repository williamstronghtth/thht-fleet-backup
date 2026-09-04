"""
Grok API Client with X Search capability.
Uses xAI's Responses API with server-side tools for real-time Twitter/X sentiment analysis.
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class XSearchResult:
    """Result from X Search query."""
    text: str                    # Full analysis text with citations
    sentiment: str               # "bullish", "bearish", "neutral", "mixed"
    confidence: float            # 0-1
    sources: List[str]           # X post URLs cited
    tool_calls: int              # Number of searches performed
    raw_response: Dict[str, Any]


class GrokClient:
    """
    Client for xAI Grok API with X Search tool.
    
    Uses the Responses API which has native server-side tool support.
    
    Pricing:
    - grok-4-1-fast: $0.20/1M input, $0.50/1M output
    - X Search tool: $5/1000 calls ($0.005 per search)
    """
    
    BASE_URL = "https://api.x.ai/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key from param or environment."""
        self.api_key = api_key or os.environ.get('XAI_API_KEY')
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment or parameters")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # Default model - fast and cheap
        self.default_model = "grok-4-1-fast-non-reasoning"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code != 200:
            raise Exception(f"xAI API Error {response.status_code}: {response.text}")
        
        return response.json()
    
    def responses(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Use the Responses API with server-side tools.
        
        Parameters:
        -----------
        prompt : user input/query
        model : model to use (default: grok-4-1-fast-non-reasoning)
        tools : list of tool types ["x_search", "web_search"]
        """
        payload = {
            "model": model or self.default_model,
            "input": prompt,
        }
        
        if tools:
            payload["tools"] = [{"type": t} for t in tools]
        
        return self._request("POST", "/responses", json=payload)
    
    # Credible sources for economic/market analysis
    ECON_EXPERTS = [
        # Economists & Fed Watchers
        "NickTimiraos",      # WSJ Fed reporter
        "M_C_Klein",         # Barron's economics
        "TheStalwart",       # Bloomberg's Joe Weisenthal
        "markets",           # Bloomberg Markets
        "lisaabramowicz1",   # Bloomberg
        "zaborowski",        # Citi economist
        "EconBrianCalle",    # Economic analysis
        "LizAnnSonders",     # Schwab chief strategist
        "JosephPolitano",    # Apricitas Economics
        "jasonfurman",       # Harvard economist, former CEA
        "FedGuy12",          # Former Fed trader
        "Newsquawk",         # Real-time market news
        "FirstSquawk",       # Breaking financial news
        # Data sources
        "BLS_gov",           # Bureau of Labor Statistics
        "AtlantaFed",        # Atlanta Fed
        "CleveFed",          # Cleveland Fed (inflation nowcast)
        "staboreau",         # BEA data
        "elerianm",          # Mohamed El-Erian
        "MishGEA",           # Mike Shedlock
    ]
    
    def x_search(
        self,
        query: str,
        context: Optional[str] = None,
        filter_experts: bool = True,
    ) -> XSearchResult:
        """
        Search X/Twitter for real-time sentiment on a topic.
        
        Parameters:
        -----------
        query : search query (e.g., "CPI inflation March 2026")
        context : additional context for analysis
        filter_experts : if True, prioritize credible economic sources
        
        Returns:
        --------
        XSearchResult with analysis, sentiment, and sources
        """
        expert_instruction = ""
        if filter_experts:
            expert_list = ", ".join(self.ECON_EXPERTS[:15])
            expert_instruction = f"""
IMPORTANT: Prioritize posts from credible sources like economists, Fed watchers, 
financial journalists, and official data accounts. Look especially for posts from 
accounts like: {expert_list}

Weight expert analysis heavily over retail speculation. Ignore memes, political hot takes,
and random opinions. Focus on data-driven analysis and professional forecasts.
"""
        
        prompt = f"""Search X for recent posts about: {query}
{expert_instruction}
Analyze the sentiment and provide:
1. Overall sentiment (bullish/bearish/neutral/mixed) based on EXPERT views
2. Key themes and data points being discussed
3. Any breaking news or time-sensitive information
4. Distinguish between expert consensus and retail noise

"""
        if context:
            prompt += f"\nContext: {context}"
        
        response = self.responses(prompt, tools=["x_search"])
        
        # Parse response
        text = ""
        sources = []
        tool_calls = 0
        
        for item in response.get("output", []):
            # Count tool calls
            if item.get("type") == "custom_tool_call":
                tool_calls += 1
            
            # Get text output
            if "content" in item:
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text = c.get("text", "")
                        # Extract X URLs from citations
                        import re
                        sources = re.findall(r'https://x\.com/\S+', text)
        
        # Infer sentiment from text
        text_lower = text.lower()
        if "bearish" in text_lower or "high inflation" in text_lower or "expecting higher" in text_lower:
            sentiment = "bearish"  # Bearish on prices = expecting inflation
            confidence = 0.75
        elif "bullish" in text_lower or "low inflation" in text_lower or "expecting lower" in text_lower:
            sentiment = "bullish"  # Bullish on prices = expecting deflation/low inflation
            confidence = 0.75
        elif "mixed" in text_lower:
            sentiment = "mixed"
            confidence = 0.50
        else:
            sentiment = "neutral"
            confidence = 0.50
        
        # Adjust confidence based on source count
        if len(sources) >= 10:
            confidence = min(confidence + 0.15, 0.95)
        elif len(sources) >= 5:
            confidence = min(confidence + 0.10, 0.90)
        
        return XSearchResult(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            sources=sources,
            tool_calls=tool_calls,
            raw_response=response
        )
    
    def analyze_market_sentiment(
        self,
        market_description: str,
        current_price: float,
        threshold: Optional[str] = None,
        num_queries: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze sentiment for a prediction market with averaged results.
        
        Parameters:
        -----------
        market_description : what the market is about
        current_price : current market probability (0-1)
        threshold : optional threshold being predicted
        num_queries : number of X searches to average (reduces variance)
        
        Returns:
        --------
        Dict with crowd_belief, market_price, gap, and recommendation
        """
        # Run multiple queries with different phrasings to reduce variance
        queries = [
            market_description,
            f"{market_description} expectations predictions",
            f"{market_description} what people think",
        ][:num_queries]
        
        if threshold:
            queries = [f"{q} {threshold}" for q in queries]
        
        context = f"This is a prediction market currently priced at {current_price*100:.0f}%"
        
        # Collect results from multiple searches
        sentiments = []
        confidences = []
        all_sources = 0
        all_tool_calls = 0
        summaries = []
        
        for query in queries:
            try:
                result = self.x_search(query, context=context)
                sentiments.append(result.sentiment)
                confidences.append(result.confidence)
                all_sources += len(result.sources)
                all_tool_calls += result.tool_calls
                if result.text:
                    summaries.append(result.text[:300])
            except Exception as e:
                # Skip failed queries
                continue
        
        if not sentiments:
            return {
                "market": market_description,
                "market_price": current_price,
                "crowd_belief": 0.50,
                "sentiment": "unknown",
                "confidence": 0.0,
                "gap": 0.0,
                "recommendation": "ERROR - No sentiment data",
                "summary": "",
                "sources": 0,
                "tool_calls": 0,
                "error": "All queries failed"
            }
        
        # Map sentiment to numeric belief for averaging
        # For inflation markets: 
        #   "bearish" on economy = worried about inflation = expects high CPI = YES
        #   "bullish" on economy = optimistic = expects low CPI = NO
        #   "mixed" = uncertainty, slight upward bias given current energy situation
        if "inflation" in market_description.lower() or "cpi" in market_description.lower():
            sentiment_to_belief = {
                "bearish": 0.72,  # Worried about inflation = YES on CPI>X
                "bullish": 0.35,  # Optimistic = NO on CPI>X
                "neutral": 0.50,
                "mixed": 0.58    # Mixed with slight inflation concern bias
            }
        else:
            sentiment_to_belief = {
                "bullish": 0.70,
                "bearish": 0.30,
                "neutral": 0.50,
                "mixed": 0.50
            }
        
        # Average the beliefs weighted by confidence
        total_weight = 0
        weighted_belief = 0
        
        for sent, conf in zip(sentiments, confidences):
            base_belief = sentiment_to_belief.get(sent, 0.50)
            weight = conf
            weighted_belief += base_belief * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_belief = weighted_belief / total_weight
        else:
            avg_belief = 0.50
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Determine majority sentiment
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        majority_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Final crowd belief (pull toward 0.5 based on confidence)
        crowd_belief = 0.50 + (avg_belief - 0.50) * avg_confidence
        
        gap = crowd_belief - current_price
        
        # Recommendation based on gap
        if abs(gap) > 0.15:
            if gap > 0:
                recommendation = "BUY - Crowd more bullish than market"
            else:
                recommendation = "SELL - Crowd more bearish than market"
        elif abs(gap) > 0.08:
            recommendation = "WATCH - Moderate sentiment divergence"
        else:
            recommendation = "NEUTRAL - Sentiment aligned with market"
        
        return {
            "market": market_description,
            "market_price": current_price,
            "crowd_belief": crowd_belief,
            "sentiment": majority_sentiment,
            "confidence": avg_confidence,
            "gap": gap,
            "recommendation": recommendation,
            "summary": summaries[0] if summaries else "",
            "sources": all_sources,
            "tool_calls": all_tool_calls,
            "queries_run": len(sentiments),
            "sentiment_breakdown": sentiment_counts,
        }


def test_client():
    """Quick test of the Grok client."""
    client = GrokClient()
    
    print("Testing xAI Grok API with X Search...")
    print()
    
    result = client.x_search("CPI inflation March 2026 energy prices expectations")
    
    print(f"Sentiment: {result.sentiment.upper()}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Sources cited: {len(result.sources)}")
    print(f"X searches performed: {result.tool_calls}")
    print()
    print("Analysis:")
    print(result.text[:1000])
    print()
    print("✅ X Search working!")


if __name__ == "__main__":
    test_client()
