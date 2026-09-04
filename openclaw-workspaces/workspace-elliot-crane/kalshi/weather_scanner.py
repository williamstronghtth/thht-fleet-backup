"""
Weather Market Scanner
Compares weather forecasts to Kalshi market prices to find edge.

Data sources:
- National Weather Service (NWS) API - free, official forecasts
- Open-Meteo API - free, global coverage
- Kalshi market prices

Edge thesis: Weather forecasts are public, but markets may misprice
tail events or lag forecast updates.
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class WeatherOpportunity:
    """A potential weather trading opportunity."""
    ticker: str
    title: str
    market_price: float  # YES price
    forecast_prob: float  # Our estimated probability
    edge: float  # forecast_prob - market_price (positive = underpriced YES)
    forecast_source: str
    forecast_detail: str
    volume: float
    spread: float
    confidence: str  # HIGH, MEDIUM, LOW


class WeatherScanner:
    """
    Scan weather markets for mispricings.
    """
    
    # NWS grid points for cities (lat, lon -> gridpoint)
    NWS_GRIDPOINTS = {
        'NYC': ('OKX', 33, 37),      # New York
        'CHICAGO': ('LOT', 76, 73),   # Chicago  
        'DENVER': ('BOU', 62, 62),    # Denver
        'AUSTIN': ('EWX', 156, 91),   # Austin
        'HOUSTON': ('HGX', 65, 97),   # Houston
        'SEATTLE': ('SEW', 124, 67),  # Seattle
        'PHOENIX': ('PSR', 161, 56),  # Phoenix
        'LA': ('LOX', 154, 44),       # Los Angeles
        'MIAMI': ('MFL', 110, 50),    # Miami
        'BOSTON': ('BOX', 71, 90),    # Boston
        'ATLANTA': ('FFC', 51, 87),   # Atlanta
        'DALLAS': ('FWD', 79, 108),   # Dallas
    }
    
    # Market series to city mapping
    MARKET_CITY_MAP = {
        'KXNYCSNOWM': 'NYC',
        'KXHIGHDEN': 'DENVER',
        'KXRAINAUSM': 'AUSTIN',
        'KXHIGHOU': 'HOUSTON',
        'RAINSEA': 'SEATTLE',
        'KXSNOWAZ': 'PHOENIX',
        'SNOWCHIM': 'CHICAGO',
    }
    
    def __init__(self, kalshi_client=None):
        self._kalshi = kalshi_client
        self.data_dir = Path('/root/.openclaw/workspace-elliot-crane/kalshi/weather_data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def kalshi(self):
        if self._kalshi is None:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace-elliot-crane')
            from kalshi.kalshi_client import KalshiClient
            self._kalshi = KalshiClient()
        return self._kalshi
    
    def get_nws_forecast(self, city: str) -> Optional[Dict]:
        """
        Get NWS forecast for a city.
        Returns hourly forecast data.
        """
        if city not in self.NWS_GRIDPOINTS:
            return None
        
        office, grid_x, grid_y = self.NWS_GRIDPOINTS[city]
        
        try:
            # Get hourly forecast
            url = f"https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast/hourly"
            response = requests.get(url, headers={'User-Agent': 'KalshiWeatherScanner'}, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"NWS forecast error for {city}: {e}")
            return None
    
    def get_open_meteo_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict]:
        """
        Get Open-Meteo forecast (backup/comparison source).
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'hourly': 'temperature_2m,precipitation_probability,precipitation,snowfall',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,precipitation_probability_max',
                'temperature_unit': 'fahrenheit',
                'precipitation_unit': 'inch',
                'forecast_days': days,
                'timezone': 'America/New_York',
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Open-Meteo error: {e}")
            return None
    
    def get_weather_markets(self) -> List[Dict]:
        """Get all active weather markets from Kalshi."""
        weather_markets = []
        
        # Check known weather series
        weather_series = [
            'KXNYCSNOWM',   # NYC Snow monthly
            'KXHIGHDEN',    # Denver high temp
            'KXRAINAUSM',   # Austin rain
            'KXHIGHOU',     # Houston high temp
            'RAINSEA',      # Seattle rain
            'SNOWCHIM',     # Chicago snow
        ]
        
        for series in weather_series:
            try:
                events = self.kalshi._request('GET', '/events', params={'series_ticker': series, 'limit': 10})
                
                for event in events.get('events', []):
                    event_data = self.kalshi._request('GET', f'/events/{event.get("event_ticker")}')
                    
                    for market in event_data.get('markets', []):
                        if market.get('status') == 'active':
                            weather_markets.append({
                                'series': series,
                                'ticker': market.get('ticker'),
                                'title': market.get('title', ''),
                                'yes_bid': float(market.get('yes_bid_dollars', 0) or 0),
                                'yes_ask': float(market.get('yes_ask_dollars', 0) or 0),
                                'volume': float(market.get('volume_fp', 0) or 0),
                                'close_time': market.get('close_time'),
                            })
            except Exception as e:
                print(f"Error fetching {series}: {e}")
        
        return weather_markets
    
    def estimate_snow_probability(self, city: str, threshold_inches: float, 
                                   start_date: str, end_date: str) -> Optional[Dict]:
        """
        Estimate probability of snow exceeding threshold.
        """
        # Get coordinates for Open-Meteo
        coords = {
            'NYC': (40.7128, -74.0060),
            'CHICAGO': (41.8781, -87.6298),
            'DENVER': (39.7392, -104.9903),
        }
        
        if city not in coords:
            return None
        
        lat, lon = coords[city]
        forecast = self.get_open_meteo_forecast(lat, lon, days=14)
        
        if not forecast:
            return None
        
        # Parse dates
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        except:
            return None
        
        # Sum snowfall in date range
        daily = forecast.get('daily', {})
        dates = daily.get('time', [])
        snowfall = daily.get('snowfall_sum', [])
        
        total_snow = 0.0
        for i, date_str in enumerate(dates):
            date = datetime.fromisoformat(date_str).date()
            if start <= date <= end and i < len(snowfall):
                total_snow += snowfall[i] or 0
        
        # Convert forecast to probability
        # If forecast shows X inches, estimate prob of exceeding threshold
        if total_snow >= threshold_inches * 1.5:
            prob = 0.85  # High confidence YES
        elif total_snow >= threshold_inches:
            prob = 0.65  # Moderate confidence YES
        elif total_snow >= threshold_inches * 0.5:
            prob = 0.40  # Uncertain
        elif total_snow > 0:
            prob = 0.20  # Low but possible
        else:
            prob = 0.05  # Very unlikely
        
        return {
            'probability': prob,
            'forecast_snow': total_snow,
            'threshold': threshold_inches,
            'source': 'Open-Meteo',
            'confidence': 'MEDIUM' if total_snow > 0 else 'HIGH',
        }
    
    def estimate_temp_probability(self, city: str, threshold_f: float, 
                                   target_date: str, market_type: str = 'above') -> Optional[Dict]:
        """
        Estimate probability for temperature markets.
        
        market_type:
          - 'above': Will temp be ABOVE threshold? (T markets with > in title)
          - 'below': Will temp be BELOW threshold? (T markets with < in title)
          - 'bucket': Will temp be IN this 2-degree bucket? (B markets)
        
        Weather forecast uncertainty is typically:
          - Same day: ±2-3°F
          - Tomorrow: ±3-5°F  
          - 3+ days: ±5-8°F
        """
        coords = {
            'DENVER': (39.7392, -104.9903),
            'HOUSTON': (29.7604, -95.3698),
            'AUSTIN': (30.2672, -97.7431),
            'PHOENIX': (33.4484, -112.0740),
        }
        
        if city not in coords:
            return None
        
        lat, lon = coords[city]
        forecast = self.get_open_meteo_forecast(lat, lon, days=14)
        
        if not forecast:
            return None
        
        # Parse target date
        try:
            if isinstance(target_date, str):
                target = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
            else:
                target = target_date
        except:
            return None
        
        daily = forecast.get('daily', {})
        dates = daily.get('time', [])
        temps_max = daily.get('temperature_2m_max', [])
        
        # Find forecast for target date
        forecast_high = None
        days_out = 0
        
        for i, date_str in enumerate(dates):
            forecast_date = datetime.fromisoformat(date_str).date()
            if forecast_date == target:
                forecast_high = temps_max[i] if i < len(temps_max) else None
                days_out = i
                break
        
        if forecast_high is None:
            return None
        
        # Estimate uncertainty based on days out
        if days_out == 0:
            uncertainty = 3.0  # Same day: ±3°F
        elif days_out == 1:
            uncertainty = 4.0  # Tomorrow: ±4°F
        elif days_out <= 3:
            uncertainty = 5.0  # 2-3 days: ±5°F
        else:
            uncertainty = 7.0  # 4+ days: ±7°F
        
        # Calculate probability using normal distribution approximation
        diff = forecast_high - threshold_f
        
        if market_type == 'below':
            # "Will temp be BELOW threshold?"
            # This is the inverse of 'above'
            # diff = forecast - threshold
            # Negative diff = forecast below threshold = high prob YES
            # Positive diff = forecast above threshold = low prob YES
            
            z_score = diff / uncertainty
            
            # Invert the logic from 'above'
            if z_score <= -2.0:
                prob = 0.97  # Forecast << threshold, YES very likely
                conf = 'HIGH'
            elif z_score <= -1.5:
                prob = 0.93
                conf = 'HIGH'
            elif z_score <= -1.0:
                prob = 0.84
                conf = 'HIGH'
            elif z_score <= -0.5:
                prob = 0.69
                conf = 'MEDIUM'
            elif z_score <= 0:
                prob = 0.50
                conf = 'LOW'
            elif z_score <= 0.5:
                prob = 0.31
                conf = 'LOW'
            elif z_score <= 1.0:
                prob = 0.16
                conf = 'MEDIUM'
            elif z_score <= 1.5:
                prob = 0.07
                conf = 'HIGH'
            elif z_score <= 2.0:
                prob = 0.03
                conf = 'HIGH'
            else:
                prob = 0.01
                conf = 'HIGH'
                
        elif market_type == 'above':
            # "Will temp be ABOVE threshold?"
            # Using rough normal distribution approximation
            # diff = forecast - threshold
            # Positive diff = forecast above threshold = high prob YES
            # Negative diff = forecast below threshold = low prob YES
            
            z_score = diff / uncertainty  # How many std devs away
            
            if z_score >= 2.0:
                prob = 0.97  # Forecast >> threshold
                conf = 'HIGH'
            elif z_score >= 1.5:
                prob = 0.93
                conf = 'HIGH'
            elif z_score >= 1.0:
                prob = 0.84
                conf = 'HIGH'
            elif z_score >= 0.5:
                prob = 0.69
                conf = 'MEDIUM'
            elif z_score >= 0:
                prob = 0.50
                conf = 'LOW'
            elif z_score >= -0.5:
                prob = 0.31
                conf = 'LOW'
            elif z_score >= -1.0:
                prob = 0.16
                conf = 'MEDIUM'
            elif z_score >= -1.5:
                prob = 0.07
                conf = 'HIGH'
            elif z_score >= -2.0:
                prob = 0.03
                conf = 'HIGH'
            else:
                prob = 0.01
                conf = 'HIGH'
                
        elif market_type == 'bucket':
            # "Will temp be IN this 2-degree bucket?" (e.g., 51-52°)
            # Bucket is [threshold, threshold+2)
            bucket_low = threshold_f
            bucket_high = threshold_f + 2.0
            bucket_mid = threshold_f + 1.0
            
            # Distance from forecast to bucket center
            dist_to_bucket = abs(forecast_high - bucket_mid)
            
            if dist_to_bucket < 1.0:
                # Forecast is inside the bucket
                prob = 0.45  # ~45% chance (buckets are ~2° wide, uncertainty spreads it)
                conf = 'MEDIUM'
            elif dist_to_bucket < 2.0:
                prob = 0.30  # Adjacent bucket
                conf = 'LOW'
            elif dist_to_bucket < 4.0:
                prob = 0.15  # 1-2 buckets away
                conf = 'LOW'
            elif dist_to_bucket < 6.0:
                prob = 0.08  # 2-3 buckets away
                conf = 'MEDIUM'
            elif dist_to_bucket < 10.0:
                prob = 0.04  # Far from forecast
                conf = 'HIGH'
            else:
                prob = 0.02  # Very far
                conf = 'HIGH'
        else:
            return None
        
        return {
            'probability': prob,
            'forecast_temp': forecast_high,
            'threshold': threshold_f,
            'market_type': market_type,
            'days_out': days_out,
            'uncertainty': uncertainty,
            'source': 'Open-Meteo',
            'confidence': conf,
        }
    
    def estimate_rain_probability(self, city: str, date_range: str) -> Optional[Dict]:
        """
        Estimate probability of rain in a date range.
        """
        coords = {
            'AUSTIN': (30.2672, -97.7431),
            'SEATTLE': (47.6062, -122.3321),
            'HOUSTON': (29.7604, -95.3698),
        }
        
        if city not in coords:
            return None
        
        lat, lon = coords[city]
        forecast = self.get_open_meteo_forecast(lat, lon, days=14)
        
        if not forecast:
            return None
        
        daily = forecast.get('daily', {})
        precip_probs = daily.get('precipitation_probability_max', [])
        
        # Average precipitation probability
        if precip_probs:
            avg_prob = sum(p or 0 for p in precip_probs[:7]) / min(7, len(precip_probs))
            prob = avg_prob / 100.0
        else:
            return None
        
        return {
            'probability': prob,
            'source': 'Open-Meteo',
            'confidence': 'MEDIUM',
        }
    
    def scan(self) -> List[WeatherOpportunity]:
        """
        Scan all weather markets for opportunities.
        """
        opportunities = []
        markets = self.get_weather_markets()
        
        for market in markets:
            ticker = market['ticker']
            series = market['series']
            title = market['title'].lower()
            
            yes_bid = market['yes_bid']
            yes_ask = market['yes_ask']
            market_price = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else yes_ask or yes_bid or 0.5
            spread = yes_ask - yes_bid if yes_ask and yes_bid else 1.0
            
            city = self.MARKET_CITY_MAP.get(series)
            if not city:
                continue
            
            estimate = None
            
            # Parse market type and get estimate
            if 'snow' in title:
                # Extract threshold from ticker (e.g., KXNYCSNOWM-26MAR-0.1 -> 0.1 inches)
                try:
                    threshold = float(ticker.split('-')[-1])
                except:
                    threshold = 0.1
                
                estimate = self.estimate_snow_probability(
                    city, threshold, 
                    datetime.now(timezone.utc).isoformat(),
                    (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                )
                
            elif 'high' in title and ('temp' in title or '°' in title or 'degrees' in title):
                # Temperature market - parse type and threshold from ticker
                # Examples:
                #   KXHIGHDEN-26MAR27-T49 = "Will high be <49°?" (below)
                #   KXHIGHDEN-26MAR27-B51.5 = "Will high be 51-52°?" (bucket)
                #   Some may have T with > meaning above
                
                try:
                    parts = ticker.split('-')
                    threshold = None
                    market_type = None
                    
                    for p in parts:
                        if p.startswith('B'):
                            threshold = float(p[1:])
                            market_type = 'bucket'
                            break
                        elif p.startswith('T'):
                            threshold = float(p[1:])
                            # Check title to determine if above or below
                            if '<' in title or 'below' in title or 'less than' in title:
                                market_type = 'below'
                            elif '>' in title or 'above' in title or 'more than' in title:
                                market_type = 'above'
                            else:
                                # Default: T usually means "below threshold"
                                market_type = 'below'
                            break
                    
                    if threshold is None:
                        threshold = 50
                        market_type = 'above'
                        
                except:
                    threshold = 50
                    market_type = 'above'
                
                # Extract date from ticker (e.g., 26MAR27 -> 2026-03-27)
                try:
                    date_part = parts[1]  # e.g., "26MAR27"
                    year = 2000 + int(date_part[:2])
                    month_str = date_part[2:5].upper()
                    day = int(date_part[5:])
                    months = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                              'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
                    month = months.get(month_str, 1)
                    target_date = datetime(year, month, day).date()
                except:
                    target_date = datetime.now(timezone.utc).date()
                
                estimate = self.estimate_temp_probability(
                    city, threshold, target_date, market_type
                )
                
            elif 'rain' in title:
                estimate = self.estimate_rain_probability(city, 'monthly')
            
            if estimate and estimate.get('probability') is not None:
                forecast_prob = estimate['probability']
                edge = forecast_prob - market_price
                
                # Build readable forecast detail
                if 'forecast_temp' in estimate:
                    detail = f"Forecast: {estimate['forecast_temp']:.0f}°F"
                    if 'market_type' in estimate:
                        detail += f" | Type: {estimate['market_type']}"
                    if 'days_out' in estimate:
                        detail += f" | {estimate['days_out']}d out (±{estimate.get('uncertainty', 0):.0f}°)"
                elif 'forecast_snow' in estimate:
                    detail = f"Forecast snow: {estimate['forecast_snow']:.1f}in vs threshold {estimate['threshold']:.1f}in"
                elif 'probability' in estimate and 'source' in estimate:
                    # Rain probability
                    detail = f"Rain prob: {estimate['probability']*100:.0f}% (7-day avg)"
                else:
                    detail = str(estimate)
                
                # Only report if edge is meaningful (>5%)
                if abs(edge) > 0.05:
                    opportunities.append(WeatherOpportunity(
                        ticker=ticker,
                        title=market['title'],
                        market_price=market_price,
                        forecast_prob=forecast_prob,
                        edge=edge,
                        forecast_source=estimate.get('source', 'Unknown'),
                        forecast_detail=detail,
                        volume=market['volume'],
                        spread=spread,
                        confidence=estimate.get('confidence', 'LOW'),
                    ))
        
        # Sort by edge magnitude
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)
        
        return opportunities
    
    def report(self) -> str:
        """Generate weather opportunities report."""
        opportunities = self.scan()
        
        lines = [
            "═" * 70,
            "  WEATHER MARKET SCANNER",
            f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "═" * 70,
            "",
        ]
        
        if not opportunities:
            lines.append("  No significant opportunities found (edge threshold: 5%)")
        else:
            lines.append(f"  Found {len(opportunities)} opportunities:")
            lines.append("")
            lines.append(f"  {'Ticker':<28} {'Mkt':>6} {'Fcst':>6} {'Edge':>7} {'Vol':>10} {'Conf':<6}")
            lines.append("  " + "-" * 65)
            
            for opp in opportunities:
                direction = "▲ YES" if opp.edge > 0 else "▼ NO"
                lines.append(
                    f"  {opp.ticker:<28} "
                    f"{opp.market_price*100:>5.0f}% "
                    f"{opp.forecast_prob*100:>5.0f}% "
                    f"{opp.edge*100:>+6.0f}% "
                    f"${opp.volume:>8,.0f} "
                    f"{opp.confidence:<6}"
                )
                lines.append(f"    └─ {opp.title[:55]}")
                lines.append(f"    └─ Signal: {direction} underpriced")
        
        lines.extend([
            "",
            "═" * 70,
            "  Sources: NWS, Open-Meteo | Edge = Forecast - Market",
            "═" * 70,
        ])
        
        return "\n".join(lines)


def main():
    """CLI for weather scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan weather markets for opportunities')
    parser.add_argument('action', choices=['scan', 'report', 'markets'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    scanner = WeatherScanner()
    
    if args.action == 'scan':
        opps = scanner.scan()
        print(f"Found {len(opps)} opportunities:")
        for opp in opps:
            print(f"  {opp.ticker}: {opp.edge*100:+.0f}% edge ({opp.confidence})")
    
    elif args.action == 'report':
        print(scanner.report())
    
    elif args.action == 'markets':
        markets = scanner.get_weather_markets()
        print(f"Found {len(markets)} active weather markets:")
        for m in markets:
            spread = m['yes_ask'] - m['yes_bid'] if m['yes_ask'] and m['yes_bid'] else 0
            print(f"  {m['ticker']}: {m['yes_bid']*100:.0f}-{m['yes_ask']*100:.0f}% (${m['volume']:,.0f})")


if __name__ == '__main__':
    main()
