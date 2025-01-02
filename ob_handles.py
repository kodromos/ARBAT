import requests
import ccxt
from pybit.unified_trading import HTTP

# Instâncias para Bybit e CCXT Exchanges
bybit = HTTP(testnet=False)
binance = ccxt.binance()
kucoin = ccxt.kucoin()

# Função para Mercado Bitcoin
def fetch_order_book_mercado_bitcoin(symbol):
    url = f"https://api.mercadobitcoin.net/api/v4/{symbol.replace('/', '-')}/orderbook"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "best_bid": data["bids"][0] if data["bids"] else [None, None],
            "best_ask": data["asks"][0] if data["asks"] else [None, None]
        }
    except Exception as e:
        print(f"Erro no Mercado Bitcoin ({symbol}): {e}")
        return {"best_bid": [None, None], "best_ask": [None, None]}

# Função para Bybit
def fetch_order_book_bybit(symbol):
    try:
        response = bybit.get_orderbook(category="spot", symbol=symbol.replace("/", ""))
        data = response["result"]
        return {
            "best_bid": data["b"][0] if data["b"] else [None, None],
            "best_ask": data["a"][0] if data["a"] else [None, None]
        }
    except Exception as e:
        print(f"Erro na Bybit ({symbol}): {e}")
        return {"best_bid": [None, None], "best_ask": [None, None]}

# Função para Binance
def fetch_order_book_binance(symbol):
    try:
        order_book = binance.fetch_order_book(symbol)
        return {
            "best_bid": order_book["bids"][0] if order_book["bids"] else [None, None],
            "best_ask": order_book["asks"][0] if order_book["asks"] else [None, None]
        }
    except Exception as e:
        print(f"Erro na Binance ({symbol}): {e}")
        return {"best_bid": [None, None], "best_ask": [None, None]}

# Função para KuCoin
def fetch_order_book_kucoin(symbol):
    try:
        order_book = kucoin.fetch_order_book(symbol)
        return {
            "best_bid": order_book["bids"][0] if order_book["bids"] else [None, None],
            "best_ask": order_book["asks"][0] if order_book["asks"] else [None, None]
        }
    except Exception as e:
        print(f"Erro na KuCoin ({symbol}): {e}")
        return {"best_bid": [None, None], "best_ask": [None, None]}