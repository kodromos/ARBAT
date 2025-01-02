# exchange_manager.py
from typing import Dict, Optional, List
import ccxt.async_support as ccxt
from models import OrderBook
from .brazilian_exchanges.mercado_bitcoin import MercadoBitcoin
from .brazilian_exchanges.foxbit import Foxbit

class ExchangeManager:
    """Unified exchange manager handling both CCXT and custom exchanges"""
    
    def __init__(self):
        self.ccxt_exchanges: Dict[str, ccxt.Exchange] = {
            'binance': ccxt.binance(),
            'bybit': ccxt.bybit(),
            'kucoin': ccxt.kucoin()
        }
        self.brazilian_exchanges = {
            'mercado_bitcoin': MercadoBitcoin(),
            'foxbit': Foxbit()
        }
        self.all_exchanges = {**self.ccxt_exchanges, **self.brazilian_exchanges}

    async def initialize(self):
        for exchange in self.brazilian_exchanges.values():
            await exchange.initialize()

    async def cleanup(self):
        for exchange in self.brazilian_exchanges.values():
            await exchange.cleanup()
        for exchange in self.ccxt_exchanges.values():
            await exchange.close()

    async def get_orderbook(self, exchange_id: str, symbol: str) -> Optional[OrderBook]:
        try:
            if exchange_id in self.ccxt_exchanges:
                orderbook = await self.ccxt_exchanges[exchange_id].fetch_order_book(symbol)
                return OrderBook(
                    asks=orderbook['asks'][:5],
                    bids=orderbook['bids'][:5],
                    timestamp=orderbook.get('timestamp', None)
                )
            elif exchange_id in self.brazilian_exchanges:
                return await self.brazilian_exchanges[exchange_id].get_orderbook(symbol)
            else:
                raise ValueError(f"Unknown exchange: {exchange_id}")
        except Exception as e:
            logging.error(f"Error fetching orderbook from {exchange_id}: {str(e)}")
            return None
