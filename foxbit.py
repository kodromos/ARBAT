# foxbit.py
from typing import Optional, List
from decimal import Decimal
import time
from models import OrderBook, Symbol
from utils.http_helpers import fetch_json
from .base import BrazilianExchangeBase

class Foxbit(BrazilianExchangeBase):
    """Foxbit exchange integration"""
    
    BASE_URL = "https://api.foxbit.com.br/api/v3"
    
    def __init__(self):
        super().__init__()
        self.symbols_cache = {}
        self.last_symbols_update = 0
        self.symbols_cache_ttl = 3600  # 1 hour

    async def get_symbols(self) -> List[str]:
        current_time = time.time()
        if self.symbols_cache and (current_time - self.last_symbols_update) < self.symbols_cache_ttl:
            return list(self.symbols_cache.keys())

        data = await fetch_json(f"{self.BASE_URL}/markets", session=self.session)
        if data:
            self.symbols_cache = {
                f"{market['base']}/USDT": market['id']
                for market in data
                if market['quote'] in ['BRL', 'USDT']
            }
            self.last_symbols_update = current_time
            return list(self.symbols_cache.keys())
        return []

    async def get_orderbook(self, symbol: str) -> Optional[OrderBook]:
        foxbit_symbol = self.symbols_cache.get(symbol)
        if not foxbit_symbol:
            self.logger.error(f"Symbol {symbol} not found in cache")
            return None

        data = await fetch_json(f"{self.BASE_URL}/orderbook/{foxbit_symbol}", session=self.session)
        if data:
            return OrderBook(
                asks=[(Decimal(price), Decimal(amount)) for price, amount in data['asks'][:5]],
                bids=[(Decimal(price), Decimal(amount)) for price, amount in data['bids'][:5]],
                timestamp=int(time.time() * 1000)
            )
        return None

