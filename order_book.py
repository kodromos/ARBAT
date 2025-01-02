import streamlit as st

def display_opportunities(opportunities):
    """
    Exibe oportunidades de arbitragem no dashboard como cartões.
    """
    st.title("Dashboard de Arbitragem")

    # Garantir que há oportunidades a exibir
    if not opportunities:
        st.info("Nenhuma oportunidade de arbitragem encontrada.")
        return    # Exibir 3 cartões por linha
    cols = st.columns(3)
    for i, opp in enumerate(opportunities):
        with cols[i % 3]:
            st.metric("Token", opp["symbol"])
            st.metric("Spread (%)", f"{opp['real_spread']:.2f}")
            st.write(f"Comprar em: {opp['buy_exchange']} a {opp['weighted_buy_price']:.2f}")
            st.write(f"Vender em: {opp['sell_exchange']} a {opp['weighted_sell_price']:.2f}")
            st.write(f"Volume disponível: {opp['volume']:.2f}")
        with cols[i % 3]:
            st.metric("Token", opp["symbol"])
            st.metric("Spread (%)", f"{opp['real_spread']:.2f}")
            st.write(f"Comprar em: {opp['buy_exchange']} a {opp['weighted_buy_price']:.2f}")
            st.write(f"Vender em: {opp['sell_exchange']} a {opp['weighted_sell_price']:.2f}")
            st.write(f"Volume disponível: {opp['volume']:.2f}")