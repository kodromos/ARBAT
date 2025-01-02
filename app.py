# app.py
import asyncio
import logging
from typing import Dict
import yaml
from .config import EXCHANGE_CONFIGS, REDIS_URL
from .cache import RedisCache
from .exchange_client import ExchangeClient
from .arbitrage import ArbitrageAnalyzer

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('main')
    try:
        # Initialize cache
        cache = RedisCache(REDIS_URL)

        # Initialize exchange clients
        exchanges: Dict[str, ExchangeClient] = {}
        for exchange_id, config in EXCHANGE_CONFIGS.items():
            client = ExchangeClient(config, cache)
            await client.initialize()
            exchanges[exchange_id] = client

        # Initialize analyzer
        analyzer = ArbitrageAnalyzer(exchanges)

        # Main loop
        while True:
            try:
                opportunities = await analyzer.find_opportunities(
                    symbols=['BTC/USDT', 'ETH/USDT'],
                    min_spread=Decimal('2.0'),
                    min_volume_usd=Decimal('100.0')
                )

                if opportunities:
                    logger.info("\nArbitrage Opportunities Found:")
                    for opp in opportunities:
                        logger.info(
                            f"\nSymbol: {opp.symbol}"
                            f"\nBuy: {opp.buy_exchange} @ {opp.buy_price:.8f}"
                            f"\nSell: {opp.sell_exchange} @ {opp.sell_price:.8f}"
                            f"\nSpread: {opp.spread:.2f}%"
                            f"\nVolume: {opp.volume:.4f} ({opp.volume_usd:.2f} USD)"
                        )
                else:
                    logger.info("No opportunities found matching criteria")

                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        # Cleanup
        for client in exchanges.values():
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())