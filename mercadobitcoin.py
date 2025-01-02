# brazilian_exchanges/mercado_bitcoin.py
from typing import Optional, List
from decimal import Decimal
import time
from models import OrderBook, Symbol
from utils.http_helpers import fetch_json
from .base import BrazilianExchangeBase

class MercadoBitcoin(BrazilianExchangeBase):
    """Mercado Bitcoin exchange integration"""
    
    BASE_URL = "https://api.mercadobitcoin.net/api/v4"
    
    def __init__(self):
        super().__init__()
        self.symbols_cache = {}
        self.last_symbols_update = 0
        self.symbols_cache_ttl = 3600  # 1 hour

    async def get_symbols(self) -> List[str]:
        current_time = time.time()
        if self.symbols_cache and (current_time - self.last_symbols_update) < self.symbols_cache_ttl:
            return list(self.symbols_cache.keys())

        url = f"{self.BASE_URL}/symbols"
        data = await fetch_json(url, session=self.session)
        if data:
            self.symbols_cache = {
                f"{symbol['base']}/USDT": symbol['symbol']
                for symbol in data['symbols']
                if symbol['quote'] in ['BRL', 'USDT']
            }
            self.last_symbols_update = current_time
            return list(self.symbols_cache.keys())
        return []

    async def get_orderbook(self, symbol: str) -> Optional[OrderBook]:
        mb_symbol = self.symbols_cache.get(symbol)
        if not mb_symbol:
            self.logger.error(f"Symbol {symbol} not found in cache")
            return None

        url = f"{self.BASE_URL}/orderbook"
        params = {"symbol": mb_symbol}
        data = await fetch_json(url, params=params, session=self.session)
        if data:
            return OrderBook(
                asks=[(Decimal(price), Decimal(amount)) for price, amount in data['asks'][:5]],
                bids=[(Decimal(price), Decimal(amount)) for price, amount in data['bids'][:5]],
                timestamp=int(time.time() * 1000)
            )
        return None
