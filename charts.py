import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from data_loader import get_tefas_data

def render_pie_bar_charts(df, group_col):
    if df.empty or "Değer" not in df.columns: return
    c_p, c_b = st.columns(2)
    pie_fig = px.pie(df, values="Değer", names=group_col, hole=0.4)
    c_p.plotly_chart(pie_fig, use_container_width=True)
    
    if "Top. Kâr/Zarar" in df.columns:
        bar_fig = px.bar(df.sort_values("Değer"), x=group_col, y="Değer", color="Top. Kâr/Zarar")
    else:
        bar_fig = px.bar(df.sort_values("Değer"), x=group_col, y="Değer")
    c_b.plotly_chart(bar_fig, use_container_width=True)

def render_detail_view(symbol, pazar):
    st.markdown(f"### 🔎 {symbol} Detaylı Analizi")
    if "FON" in pazar:
        price, _ = get_tefas_data(symbol)
        st.metric(f"{symbol} Son Fiyat", f"₺{price:,.6f}")
        st.info("Fon grafikleri TEFAS kısıtlaması nedeniyle sınırlıdır.")
        return

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        if not hist.empty:
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"],
                                                 low=hist["Low"], close=hist["Close"], name=symbol)])
            fig.update_layout(title=f"{symbol} Grafiği", template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            info = ticker.info
            c1, c2, c3 = st.columns(3)
            c1.metric("Sektör", info.get("sector", "-"))
            c2.metric("F/K", info.get("trailingPE", "-"))
            c3.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,.0f}")
        else:
            st.warning("Grafik verisi yok.")
    except Exception as e:
        st.error(f"Veri hatası: {e}")
