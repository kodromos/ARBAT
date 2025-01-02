# arbitrage_analyzer.py
from typing import List, Dict
from decimal import Decimal
import logging
from models import OrderBook, ArbitrageOpportunity
from exchange_client import ExchangeClient

class ArbitrageAnalyzer:
    def __init__(self, exchanges: Dict[str, ExchangeClient]):
        self.exchanges = exchanges
        self.logger = logging.getLogger(self.__class__.__name__)

    async def find_opportunities(
        self,
        symbols: List[str],
        min_spread: Decimal = Decimal('2.0'),
        min_volume_usd: Decimal = Decimal('100.0')
    ) -> List[ArbitrageOpportunity]:
        opportunities = []

        for symbol in symbols:
            self.logger.info(f"Analyzing symbol: {symbol}")
            orderbooks = {}
            tasks = []

            # Fetch orderbooks concurrently
            for exchange_id, client in self.exchanges.items():
                tasks.append(
                    (exchange_id, asyncio.create_task(client.get_orderbook(symbol)))
                )

            # Wait for all tasks
            for exchange_id, task in tasks:
                try:
                    orderbook = await task
                    if orderbook:
                        orderbooks[exchange_id] = orderbook
                except Exception as e:
                    self.logger.error(
                        f"Failed to fetch orderbook for {symbol} on {exchange_id}: {e}"
                    )

            # Analyze opportunities
            opportunities.extend(
                await self._analyze_pair_opportunities(
                    symbol, orderbooks, min_spread, min_volume_usd
                )
            )

        return opportunities

    async def _analyze_pair_opportunities(
        self,
        symbol: str,
        orderbooks: Dict[str, OrderBook],
        min_spread: Decimal,
        min_volume_usd: Decimal
    ) -> List[ArbitrageOpportunity]:
        opportunities = []

        for buy_exchange, buy_ob in orderbooks.items():
            for sell_exchange, sell_ob in orderbooks.items():
                if buy_exchange == sell_exchange:
                    continue

                try:
                    # Calculate spread
                    buy_price = buy_ob.asks[0][0]
                    sell_price = sell_ob.bids[0][0]
                    spread = ((sell_price - buy_price) / buy_price) * 100

                    if spread >= min_spread:
                        # Calculate volume
                        buy_volume = buy_ob.asks[0][1]
                        sell_volume = sell_ob.bids[0][1]
                        max_volume = min(buy_volume, sell_volume)
                        volume_usd = max_volume * buy_price

                        if volume_usd >= min_volume_usd:
                            opportunities.append(
                                ArbitrageOpportunity(
                                    symbol=symbol,
                                    buy_exchange=buy_exchange,
                                    sell_exchange=sell_exchange,
                                    buy_price=buy_price,
                                    sell_price=sell_price,
                                    spread=spread,
                                    volume=max_volume,
                                    volume_usd=volume_usd,
                                    timestamp=max(buy_ob.timestamp, sell_ob.timestamp)
                                )
                            )
                except Exception as e:
                    self.logger.error(
                        f"Error analyzing opportunity for {symbol}: {e}"
                    )

        return opportunities
