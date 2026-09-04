#!/usr/bin/env python3
"""
Kalshi API Client
Production-ready client for Kalshi prediction market trading
"""

import base64
import datetime
import json
import os
from typing import Optional, Dict, Any, List
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


class KalshiClient:
    """
    Client for Kalshi Prediction Market API (v2)
    
    Authentication uses RSA-PSS signing with SHA256.
    """
    
    def __init__(
        self,
        api_key_id: Optional[str] = None,
        private_key_pem: Optional[str] = None,
        base_url: str = "https://api.elections.kalshi.com/trade-api/v2"
    ):
        """
        Initialize Kalshi client.
        
        Args:
            api_key_id: API key ID (or set KALSHI_API_KEY_ID env var)
            private_key_pem: RSA private key in PEM format (or set KALSHI_PRIVATE_KEY env var)
            base_url: API base URL
        """
        self.api_key_id = api_key_id or os.environ.get("KALSHI_API_KEY_ID")
        private_key_pem = private_key_pem or os.environ.get("KALSHI_PRIVATE_KEY")

        # Fallback: load from openclaw.json config if env vars not set
        if not self.api_key_id or not private_key_pem:
            try:
                config_path = '/root/.openclaw/openclaw.json'
                with open(config_path) as f:
                    config = json.load(f)
                env_vars = config.get('env', {}).get('vars', {})
                self.api_key_id = self.api_key_id or env_vars.get('KALSHI_API_KEY_ID', '')
                private_key_pem = private_key_pem or env_vars.get('KALSHI_PRIVATE_KEY', '').replace('\\n', '\n')
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        if not self.api_key_id or not private_key_pem:
            raise ValueError("API key ID and private key are required")
        
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        self.base_url = base_url
        self.session = requests.Session()
    
    def _sign(self, timestamp: str, method: str, path: str) -> str:
        """Generate RSA-PSS signature for request authentication."""
        message = f"{timestamp}{method}{path}".encode()
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Kalshi API."""
        timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000))
        path = f"/trade-api/v2{endpoint}"
        
        signature = self._sign(timestamp, method.upper(), path)
        
        headers = {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            timeout=30
        )
        
        if response.status_code >= 400:
            error_detail = response.text
            try:
                error_detail = response.json()
            except:
                pass
            raise KalshiAPIError(response.status_code, error_detail)
        
        return response.json() if response.text else {}
    
    # ==================== ACCOUNT ====================
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        return self._request("GET", "/portfolio/balance")
    
    def get_positions(self, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get current positions."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/portfolio/positions", params=params)
    
    def get_fills(
        self,
        ticker: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get trade fill history."""
        params = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/portfolio/fills", params=params)
    
    # ==================== MARKETS ====================
    
    def get_markets(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        event_ticker: Optional[str] = None,
        series_ticker: Optional[str] = None,
        status: Optional[str] = None,
        tickers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get list of markets.
        
        Args:
            limit: Max results per page
            cursor: Pagination cursor
            event_ticker: Filter by event
            series_ticker: Filter by series
            status: Filter by status (open, closed, settled)
            tickers: List of specific market tickers
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if event_ticker:
            params["event_ticker"] = event_ticker
        if series_ticker:
            params["series_ticker"] = series_ticker
        if status:
            params["status"] = status
        if tickers:
            params["tickers"] = ",".join(tickers)
        return self._request("GET", "/markets", params=params)
    
    def get_market(self, ticker: str) -> Dict[str, Any]:
        """Get single market details."""
        return self._request("GET", f"/markets/{ticker}")
    
    def get_orderbook(self, ticker: str, depth: int = 10) -> Dict[str, Any]:
        """Get market order book."""
        return self._request("GET", f"/markets/{ticker}/orderbook", params={"depth": depth})
    
    def get_market_history(
        self,
        ticker: str,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get market price history."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", f"/markets/{ticker}/history", params=params)
    
    # ==================== EVENTS ====================
    
    def get_events(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        series_ticker: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of events."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if series_ticker:
            params["series_ticker"] = series_ticker
        if status:
            params["status"] = status
        return self._request("GET", "/events", params=params)
    
    def get_event(self, event_ticker: str) -> Dict[str, Any]:
        """Get single event details."""
        return self._request("GET", f"/events/{event_ticker}")
    
    # ==================== ORDERS ====================
    
    def get_orders(
        self,
        ticker: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get your orders."""
        params = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/portfolio/orders", params=params)
    
    def create_order(
        self,
        ticker: str,
        side: str,  # "yes" or "no"
        action: str,  # "buy" or "sell"
        count: int,
        type: str = "limit",  # "limit" or "market"
        yes_price: Optional[int] = None,  # In cents (1-99)
        no_price: Optional[int] = None,
        client_order_id: Optional[str] = None,
        expiration_ts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new order.
        
        Args:
            ticker: Market ticker
            side: "yes" or "no"
            action: "buy" or "sell"
            count: Number of contracts
            type: "limit" or "market"
            yes_price: Limit price for yes contracts (1-99 cents)
            no_price: Limit price for no contracts (1-99 cents)
            client_order_id: Your order ID for tracking
            expiration_ts: Unix timestamp for order expiration
        
        Returns:
            Created order details
        """
        data = {
            "ticker": ticker,
            "side": side,
            "action": action,
            "count": count,
            "type": type,
        }
        if yes_price is not None:
            data["yes_price"] = yes_price
        if no_price is not None:
            data["no_price"] = no_price
        if client_order_id:
            data["client_order_id"] = client_order_id
        if expiration_ts:
            data["expiration_ts"] = expiration_ts
        
        return self._request("POST", "/portfolio/orders", data=data)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        return self._request("DELETE", f"/portfolio/orders/{order_id}")
    
    def amend_order(
        self,
        order_id: str,
        count: Optional[int] = None,
        yes_price: Optional[int] = None,
        no_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """Amend an existing order."""
        data = {}
        if count is not None:
            data["count"] = count
        if yes_price is not None:
            data["yes_price"] = yes_price
        if no_price is not None:
            data["no_price"] = no_price
        return self._request("PATCH", f"/portfolio/orders/{order_id}", data=data)
    
    # ==================== EXCHANGE ====================
    
    def get_exchange_status(self) -> Dict[str, Any]:
        """Get exchange status (trading active, etc)."""
        return self._request("GET", "/exchange/status")
    
    def get_exchange_schedule(self) -> Dict[str, Any]:
        """Get exchange schedule."""
        return self._request("GET", "/exchange/schedule")


class KalshiAPIError(Exception):
    """Exception for Kalshi API errors."""
    
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Kalshi API Error {status_code}: {detail}")


# Convenience function for quick testing
def get_client() -> KalshiClient:
    """Get a configured Kalshi client from environment variables."""
    return KalshiClient()


if __name__ == "__main__":
    # Quick test
    import sys
    
    # Check if credentials are in env
    if not os.environ.get("KALSHI_API_KEY_ID"):
        print("Set KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY environment variables")
        sys.exit(1)
    
    client = get_client()
    
    print("Testing Kalshi API connection...")
    
    # Test balance
    balance = client.get_balance()
    print(f"\n💰 Balance: ${balance['balance']/100:.2f}")
    print(f"📊 Portfolio Value: ${balance['portfolio_value']/100:.2f}")
    
    # Test exchange status
    status = client.get_exchange_status()
    print(f"\n🏛️ Exchange Active: {status['exchange_active']}")
    print(f"📈 Trading Active: {status['trading_active']}")
    
    # Test markets
    markets = client.get_markets(limit=5)
    print(f"\n📋 Sample Markets ({len(markets.get('markets', []))} returned):")
    for m in markets.get('markets', [])[:3]:
        print(f"   - {m.get('ticker')}: {m.get('title', '')[:50]}")
    
    print("\n✅ All tests passed!")
