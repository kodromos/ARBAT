from backend.order_book_handlers import (
    fetch_order_book_mercado_bitcoin,
    fetch_order_book_bybit,
    fetch_order_book_binance,
    fetch_order_book_kucoin,
)

def validate_common_tokens(tokens):
    """
    Valida tokens disponíveis em todas as corretoras.
    """
    valid_tokens = []
    for token in tokens:
        try:
            # Testa token em todas as exchanges
            is_valid = all([
                fetch_order_book_mercado_bitcoin(token),
                fetch_order_book_bybit(token),
                fetch_order_book_binance(token),
                fetch_order_book_kucoin(token),
            ])
            if is_valid:
                valid_tokens.append(token)
        except Exception as e:
            print(f"Erro ao validar token {token}: {e}")
    return valid_tokens