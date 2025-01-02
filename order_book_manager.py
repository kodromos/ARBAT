from concurrent.futures import ThreadPoolExecutor
from backend.order_book_handlers import (
    fetch_order_book_mercado_bitcoin,
    fetch_order_book_bybit,
    fetch_order_book_binance,
    fetch_order_book_kucoin,
)

# Configuração de funções por corretora
EXCHANGE_FUNCTIONS = {
    "mercado_bitcoin": fetch_order_book_mercado_bitcoin,
    "bybit": fetch_order_book_bybit,
    "binance": fetch_order_book_binance,
    "kucoin": fetch_order_book_kucoin,
}

def fetch_order_books_for_token(token):
    """
    Busca os livros de ofertas para um token específico em todas as corretoras.
    """
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            exchange: executor.submit(func, token)
            for exchange, func in EXCHANGE_FUNCTIONS.items()
        }
        for exchange, future in futures.items():
            try:
                results[exchange] = future.result()
            except Exception as e:
                print(f"Erro ao buscar dados para {exchange}: {e}")
                results[exchange] = {"best_bid": [None, None], "best_ask": [None, None]}
    return results

def fetch_all_order_books(tokens):
    """
    Busca os livros de ofertas para uma lista de tokens em todas as corretoras.
    """
    all_order_books = {}
    for token in tokens:
        all_order_books[token] = fetch_order_books_for_token(token)
    return all_order_books