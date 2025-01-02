# tests/test_foxbit.py
import sys
from pathlib import Path
# Adiciona o diretório do projeto ao Python Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import unittest
from unittest.mock import AsyncMock, MagicMock
from brazilian_exchanges.foxbit import Foxbit

class TestFoxbit(unittest.TestCase):
    def setUp(self):
        self.foxbit = Foxbit()
        self.foxbit.session = MagicMock()
        self.foxbit.logger = MagicMock()

    async def test_get_symbols_success(self):
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=200, 
                json=AsyncMock(return_value=[
                    {"base": "BTC", "quote": "USDT", "id": "btc_usdt"}
                ])
            )
        )
        symbols = await self.foxbit.get_symbols()
        self.assertIn("BTC/USDT", symbols)

    async def test_get_orderbook_success(self):
        self.foxbit.symbols_cache = {"BTC/USDT": "btc_usdt"}
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=200, 
                json=AsyncMock(return_value={
                    "asks": [["100", "1"]],
                    "bids": [["99", "1"]],
                })
            )
        )
        orderbook = await self.foxbit.get_orderbook("BTC/USDT")
        self.assertEqual(orderbook.asks[0][0], 100)
        self.assertEqual(orderbook.bids[0][0], 99)
class TestFoxbit(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.foxbit = Foxbit()
        self.foxbit.session = MagicMock()
        self.foxbit.logger = MagicMock()

    async def test_get_symbols_success(self):
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=200, 
                json=AsyncMock(return_value=[
                    {"base": "BTC", "quote": "USDT", "id": "btc_usdt"}
                ])
            )
        )
        symbols = await self.foxbit.get_symbols()
        self.assertIn("BTC/USDT", symbols)

    async def test_get_symbols_failure(self):
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=500, 
                json=AsyncMock(return_value={"error": "Internal Server Error"})
            )
        )
        with self.assertRaises(Exception):
            await self.foxbit.get_symbols()

    async def test_get_orderbook_success(self):
        self.foxbit.symbols_cache = {"BTC/USDT": "btc_usdt"}
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=200, 
                json=AsyncMock(return_value={
                    "asks": [["100", "1"]],
                    "bids": [["99", "1"]],
                })
            )
        )
        orderbook = await self.foxbit.get_orderbook("BTC/USDT")
        self.assertEqual(orderbook.asks[0][0], 100)
        self.assertEqual(orderbook.bids[0][0], 99)

    async def test_get_orderbook_failure(self):
        self.foxbit.symbols_cache = {"BTC/USDT": "btc_usdt"}
        self.foxbit.session.get = AsyncMock(
            return_value=MagicMock(
                status=500, 
                json=AsyncMock(return_value={"error": "Internal Server Error"})
            )
        )
        with self.assertRaises(Exception):
            await self.foxbit.get_orderbook("BTC/USDT")
            