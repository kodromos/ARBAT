# exchange_client.py
from tenacity import retry, stop_after_attempt, wait_exponential
from ratelimit import limits, sleep_and_retry
import aiohttp
import asyncio
import logging
from typing import Dict, Optional, List
from .models import OrderBook, OrderBookEntry
from .cache import RedisCache

class ExchangeClient:
    def __init__(self, config: ExchangeConfig, cache: RedisCache):
        self.config = config
        self.cache = cache
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None

    async def initialize(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout/1000)
            )

    async def cleanup(self):
        if self.session:
            await self.session.close()
            self.session = None
        if self.ws:
            await self.ws.close()
            self.ws = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @sleep_and_retry
    @limits(calls=30, period=60)
    async def get_orderbook(self, symbol: str) -> Optional[OrderBook]:
        cache_key = f"orderbook:{symbol}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return OrderBook(**cached_data)

        try:
            async with self.session.get(
                f"{self.config.api_url}/api/v3/depth",
                params={"symbol": symbol, "limit": 5}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    orderbook = OrderBook(
                        asks=[
                            OrderBookEntry(price=Decimal(price), volume=Decimal(vol))
                            for price, vol in data['asks']
                        ],
                        bids=[
                            OrderBookEntry(price=Decimal(price), volume=Decimal(vol))
                            for price, vol in data['bids']
                        ],
                        timestamp=datetime.fromtimestamp(data['timestamp'] / 1000)
                    )
                    self.cache.set(cache_key, orderbook.dict())
                    return orderbook
                else:
                    self.logger.error(f"Error fetching orderbook: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching orderbook: {str(e)}")
            return None

    async def subscribe_orderbook(self, symbol: str):
        if not self.ws:
            self.ws = await self.session.ws_connect(self.config.websocket_url)
        
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@depth"],
            "id": 1
        }
        await self.ws.send_json(subscribe_msg)
        
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                # Process real-time orderbook updates
                await self._handle_orderbook_update(symbol, data)

    async def _handle_orderbook_update(self, symbol: str, data: Dict):
        try:
            orderbook = OrderBook(
                asks=[
                    OrderBookEntry(price=Decimal(price), volume=Decimal(vol))
                    for price, vol in data['a']
                ],
                bids=[
                    OrderBookEntry(price=Decimal(price), volume=Decimal(vol))
                    for price, vol in data['b']
                ],
                timestamp=datetime.fromtimestamp(data['E'] / 1000)
            )
            self.cache.set(f"orderbook:{symbol}", orderbook.dict())
        except Exception as e:
            self.logger.error(f"Error processing orderbook update: {str(e)}")