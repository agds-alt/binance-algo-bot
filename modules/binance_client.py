"""
Binance Futures API Client Wrapper
Includes built-in safety checks and rate limiting
"""

import time
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import httpx
import asyncio
from loguru import logger

from modules.config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_TESTNET,
    TESTNET_BASE_URL,
    PROD_BASE_URL,
    RISK_LIMITS,
)


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"


class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    BOTH = "BOTH"


@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    unrealized_pnl: float
    leverage: int
    liquidation_price: float


@dataclass
class OrderResult:
    order_id: str
    symbol: str
    side: str
    type: str
    quantity: float
    price: float
    status: str
    executed_qty: float = 0.0


class BinanceClient:
    """Binance Futures API client with safety checks"""
    
    def __init__(self):
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_API_SECRET
        self.base_url = TESTNET_BASE_URL if BINANCE_TESTNET else PROD_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
        
        logger.info(f"Binance client initialized - Testnet: {BINANCE_TESTNET}")
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    async def _rate_limit(self):
        """Simple rate limiter"""
        async with self._rate_limit_lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                await asyncio.sleep(self._min_request_interval - elapsed)
            self._last_request_time = time.time()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = False
    ) -> Dict:
        """Make API request with error handling"""
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._generate_signature(params)
        
        headers = {"X-MBX-APIKEY": self.api_key}
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, params=params, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    # Account & Balance methods...
    async def get_account_balance(self) -> Dict[str, float]:
        """Get USDT balance"""
        data = await self._request("GET", "/fapi/v2/balance", signed=True)
        balances = {}
        for asset in data:
            if float(asset["balance"]) > 0:
                balances[asset["asset"]] = {
                    "balance": float(asset["balance"]),
                    "available": float(asset["availableBalance"]),
                    "unrealized_pnl": float(asset.get("crossUnPnl", 0))
                }
        return balances
    
    async def get_usdt_balance(self) -> float:
        """Get available USDT balance"""
        balances = await self.get_account_balance()
        return balances.get("USDT", {}).get("available", 0.0)
    
    async def get_positions(self) -> List[Position]:
        """Get all open positions"""
        data = await self._request("GET", "/fapi/v2/positionRisk", signed=True)
        positions = []
        for pos in data:
            size = float(pos["positionAmt"])
            if size != 0:
                positions.append(Position(
                    symbol=pos["symbol"],
                    side="LONG" if size > 0 else "SHORT",
                    size=abs(size),
                    entry_price=float(pos["entryPrice"]),
                    unrealized_pnl=float(pos["unRealizedProfit"]),
                    leverage=int(pos["leverage"]),
                    liquidation_price=float(pos["liquidationPrice"])
                ))
        return positions
    
    # Market Data methods...
    async def get_ticker_price(self, symbol: str) -> float:
        """Get current price"""
        data = await self._request("GET", "/fapi/v1/ticker/price", {"symbol": symbol})
        return float(data["price"])
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get candlestick data"""
        data = await self._request("GET", "/fapi/v1/klines", {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
        return [{
            "open_time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": k[6],
            "quote_volume": float(k[7]),
            "trades": k[8],
        } for k in data]
    
    async def get_orderbook(self, symbol: str, limit: int = 5) -> Dict:
        """Get order book"""
        data = await self._request("GET", "/fapi/v1/depth", {
            "symbol": symbol,
            "limit": limit
        })
        return {
            "bids": [[float(p), float(q)] for p, q in data["bids"]],
            "asks": [[float(p), float(q)] for p, q in data["asks"]],
        }
    
    async def get_spread(self, symbol: str) -> float:
        """Calculate current spread percentage"""
        orderbook = await self.get_orderbook(symbol, limit=1)
        best_bid = orderbook["bids"][0][0]
        best_ask = orderbook["asks"][0][0]
        return ((best_ask - best_bid) / best_bid) * 100
    
    async def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol trading rules"""
        data = await self._request("GET", "/fapi/v1/exchangeInfo")
        for s in data["symbols"]:
            if s["symbol"] == symbol:
                filters = {f["filterType"]: f for f in s["filters"]}
                return {
                    "symbol": symbol,
                    "price_precision": s["pricePrecision"],
                    "qty_precision": s["quantityPrecision"],
                    "min_qty": float(filters["LOT_SIZE"]["minQty"]),
                    "max_qty": float(filters["LOT_SIZE"]["maxQty"]),
                    "step_size": float(filters["LOT_SIZE"]["stepSize"]),
                    "tick_size": float(filters["PRICE_FILTER"]["tickSize"]),
                    "min_notional": float(filters.get("MIN_NOTIONAL", {}).get("notional", 5)),
                }
        raise ValueError(f"Symbol {symbol} not found")
    
    # Order Management methods...
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for symbol"""
        if leverage > RISK_LIMITS.MAX_LEVERAGE:
            logger.warning(f"Leverage {leverage} exceeds max {RISK_LIMITS.MAX_LEVERAGE}")
            leverage = RISK_LIMITS.MAX_LEVERAGE
        
        await self._request("POST", "/fapi/v1/leverage", {
            "symbol": symbol,
            "leverage": leverage
        }, signed=True)
        logger.info(f"Set leverage for {symbol}: {leverage}x")
        return True
    
    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        reduce_only: bool = False
    ) -> OrderResult:
        """Place market order"""
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": "MARKET",
            "quantity": quantity,
        }
        if reduce_only:
            params["reduceOnly"] = "true"
        
        data = await self._request("POST", "/fapi/v1/order", params, signed=True)
        
        return OrderResult(
            order_id=str(data["orderId"]),
            symbol=data["symbol"],
            side=data["side"],
            type=data["type"],
            quantity=float(data["origQty"]),
            price=float(data.get("avgPrice", 0)),
            status=data["status"],
            executed_qty=float(data.get("executedQty", 0))
        )
    
    async def place_stop_loss(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_price: float,
        close_position: bool = False
    ) -> OrderResult:
        """Place stop loss order"""
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": "STOP_MARKET",
            "stopPrice": stop_price,
        }
        
        if close_position:
            params["closePosition"] = "true"
        else:
            params["quantity"] = quantity
        
        data = await self._request("POST", "/fapi/v1/order", params, signed=True)
        
        return OrderResult(
            order_id=str(data["orderId"]),
            symbol=data["symbol"],
            side=data["side"],
            type=data["type"],
            quantity=float(data.get("origQty", 0)),
            price=float(data["stopPrice"]),
            status=data["status"]
        )
    
    async def place_take_profit(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_price: float
    ) -> OrderResult:
        """Place take profit order"""
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": "TAKE_PROFIT_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
        }
        
        data = await self._request("POST", "/fapi/v1/order", params, signed=True)
        
        return OrderResult(
            order_id=str(data["orderId"]),
            symbol=data["symbol"],
            side=data["side"],
            type=data["type"],
            quantity=float(data["origQty"]),
            price=float(data["stopPrice"]),
            status=data["status"]
        )
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel specific order"""
        await self._request("DELETE", "/fapi/v1/order", {
            "symbol": symbol,
            "orderId": order_id
        }, signed=True)
        return True
    
    async def cancel_all_orders(self, symbol: str) -> bool:
        """Cancel all orders for symbol"""
        await self._request("DELETE", "/fapi/v1/allOpenOrders", {
            "symbol": symbol
        }, signed=True)
        return True
    
    async def close_position(self, symbol: str) -> Optional[OrderResult]:
        """Close position for symbol"""
        positions = await self.get_positions()
        for pos in positions:
            if pos.symbol == symbol:
                side = OrderSide.SELL if pos.side == "LONG" else OrderSide.BUY
                return await self.place_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=pos.size,
                    reduce_only=True
                )
        return None
    
    async def close_all_positions(self) -> List[OrderResult]:
        """Emergency: Close all positions"""
        logger.warning("EMERGENCY: Closing all positions")
        positions = await self.get_positions()
        results = []
        for pos in positions:
            result = await self.close_position(pos.symbol)
            if result:
                results.append(result)
        return results
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
