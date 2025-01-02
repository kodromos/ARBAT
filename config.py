from dotenv import load_dotenv
import os
from pydantic import BaseModel, validator
from typing import Dict, Optional, List
import logging

# Carregar variáveis de ambiente
load_dotenv()

class ExchangeConfig(BaseModel):
    api_key: Optional[str]
    api_secret: Optional[str]
    api_url: str
    websocket_url: str
    timeout: int = 30000
    max_retries: int = 3
    rate_limit_calls: int = 30
    rate_limit_period: int = 60

    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1000 or v > 60000:
            raise ValueError('Timeout deve estar entre 1000 e 60000 ms')
        return v

EXCHANGE_CONFIGS = {
    'binance': ExchangeConfig(
        api_key=os.getenv('BINANCE_API_KEY'),
        api_secret=os.getenv('BINANCE_API_SECRET'),
        api_url='https://api.binance.com',
        websocket_url='wss://stream.binance.com:9443/ws',
        timeout=int(os.getenv('BINANCE_TIMEOUT', 30000))
    ),
    'bybit': ExchangeConfig(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET'),
        api_url='https://api.bybit.com',
        websocket_url='wss://stream.bybit.com/spot/public/v3',
        timeout=int(os.getenv('BYBIT_TIMEOUT', 30000))
    ),
    # ... outras exchanges
}

# Configurações globais
MIN_SPREAD = float(os.getenv('MIN_SPREAD', 2.0))
MIN_VOLUME_USD = float(os.getenv('MIN_VOLUME_USD', 100.0))
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 5))
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')