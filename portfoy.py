import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.express as px
from streamlit_option_menu import option_menu

# --- MODÜLLER ---
from utils import (
    ANALYSIS_COLS,
    KNOWN_FUNDS,
    MARKET_DATA,
    smart_parse,
    styled_dataframe,
    get_yahoo_symbol,
)
from data_loader import (
    get_data_from_sheet,
    save_data_to_sheet,
    get_sales_history,
    add_sale_record,
    get_usd_try,
    get_tickers_data,
    get_financial_news,
    get_tefas_data,
    get_binance_positions,
)
from charts import (
    render_pie_bar_charts,
    render_pazar_tab,
    render_detail_view,
    get_historical_chart,
)

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Merter’in Terminali",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed",
)

# --- CSS ---
st.markdown(
    """
<style>
    /* Streamlit Header Gizle */
    header { visibility: hidden; height: 0px; }
    
    /* Kenar Boşluklarını Sıfırla */
    div.st-emotion-cache-1c9v9c4 { padding: 0 !important; }
    .block-container {
        padding-top: 1rem;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Metric Kutuları */
    div[data-testid="stMetric"] {
        background-color: #262730 !important;
        border: 1px solid #464b5f;
        border-radius: 10px;
        padding: 15px;
        color: #ffffff !important;
    }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="stMetricLabel"] { color: #bfbfbf !important; }

    /* Ticker Alanı */
    .ticker-container {
        width: 100%;
        overflow: hidden;
        background-color: #161616;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
        white-space: nowrap;
        position: relative;
    }
    .market-ticker {
        background-color: #0e1117;
        border-bottom: 1px solid #333;
        padding: 8px 0;
    }
    .portfolio-ticker {
        background-color: #1a1c24;
        border-bottom: 2px solid #FF4B4B;
        padding: 8px 0;
        margin-bottom: 20px;
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        padding-left: 0;
        font-family: 'Courier New', Courier, monospace;
        font-weight: 900;
        color: #00e676;
    }
    
    /* Animasyonlar */
    .animate-market { animation: ticker 65s linear infinite; color: #4da6ff; }
    .animate-portfolio { animation: ticker 55s linear infinite; color: #ffd700; }

    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-50%, 0, 0); }
    }

    /* Haber Kartları */
    .news-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF4B4B;
        margin-bottom: 10px;
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: #ffffff;
        text-decoration: none;
    }
    .news-meta {
        font-size: 12px;
        color: #888;
        margin-top: 5px;
    }
    a { text-decoration: none !important; }
    a:hover { text-decoration: underline !important; }

    /* KRAL HEADER (B Şıkkı – hafif renkli kart) */
    .kral-header {
        background: linear-gradient(135deg, #232837, #171b24);
        border-radius: 14px;
        padding: 14px 20px 10px 20px;
        margin-bottom: 14px;
        border: 1px solid #2f3440;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
    }
    .kral-header-title {
        font-size: 26px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .kral-header-sub {
        font-size: 13px;
        color: #b3b7c6;
    }

    /* Mini Info Bar */
    .kral-infobar {
        display: flex;
        gap: 18px;
        flex-wrap: wrap;
        margin-top: 6px;
        margin-bottom: 10px;
    }
    .kral-infobox {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        padding: 8px 14px;
        border: 1px solid #303542;
        min-width: 165px;
    }
    .kral-infobox-label {
        font-size: 11px;
        color: #b0b3c0;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kral-infobox-value {
        display: block;
        margin-top: 2px;
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
    }
    .kral-infobox-sub {
        font-size: 11px;
        color: #9da1b3;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- HABER UI ---
def render_news_section(name, key):
    st.subheader(f"📰 {name}")
    news = get_financial_news(key)
    if news:
        for n in news:
            st.markdown(
                f"""
                <div class="news-card">
                    <a href="{n['link']}" target="_blank" class="news-title">
                        {n['title']}
                    </a>
                    <div class="news-meta">🕒 {n['date']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Haber akışı yüklenemedi.")


# --- ANA DATA ---
portfoy_df = get_data_from_sheet()

# --- HEADER (B ŞIKKI – Hafif renkli kart + Para Birimi) ---
with st.container():
    st.markdown('<div class="kral-header">', unsafe_allow_html=True)
    c_title, c_toggle = st.columns([3, 1])
    with c_title:
        st.markdown(
            "<div class='kral-header-title'>🏦 Merter'in Varlık Yönetim Terminali</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='kral-header-sub'>Toplam portföyünü tek ekranda izlemek için kişisel kontrol panelin.</div>",
            unsafe_allow_html=True,
        )
    with c_toggle:
        st.write("")
        GORUNUM_PB = st.radio("Para Birimi:", ["TRY", "USD"], horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

USD_TRY = get_usd_try()
sym = "₺" if GORUNUM_PB == "TRY" else "$"

mh, ph = get_tickers_data(portfoy_df, USD_TRY)
st.markdown(
    f"""
<div class="ticker-container market-ticker">{mh}</div>
<div class="ticker-container portfolio-ticker">{ph}</div>
""",
    unsafe_allow_html=True,
)

# --- YENİ MENÜ (Sade 6 Buton) ---
selected = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
        "Portföy",
        "İzleme",
        "Satışlar",
        "Haberler",
        "Ekle/Çıkar",
    ],
    icons=[
        "speedometer2",
        "pie-chart-fill",
        "eye",
        "receipt",
        "newspaper",
