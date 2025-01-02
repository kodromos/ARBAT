from abc import ABC, abstractmethod
from typing import Dict, Optional
import aiohttp
import logging

class BrazilianExchangeBase(ABC):
    """Base class for Brazilian cryptocurrency exchanges"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None

    @abstractmethod
    async def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """Get order book for specified symbol"""
        pass

    @abstractmethod
    async def get_symbols(self) -> list:
        """Get list of available trading symbols"""
        pass

