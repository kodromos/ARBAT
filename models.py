# models.py
from pydantic import BaseModel
from typing import List, Tuple
from decimal import Decimal

class Symbol(BaseModel):
    id: str
    base: str
    quote: str

class OrderBook(BaseModel):
    asks: List[Tuple[Decimal, Decimal]]  # List of (price, volume)
    bids: List[Tuple[Decimal, Decimal]]  # List of (price, volume)
    timestamp: int
