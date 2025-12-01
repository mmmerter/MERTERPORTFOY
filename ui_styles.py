"""
UI Styles Module
Tüm CSS ve HTML stillerini merkezi olarak yönetir.
Kod kalabalığını azaltmak için tek bir yerden stil yönetimi.
"""

from typing import Dict, Optional
from config import get_config


def get_base_css() -> str:
    """Temel CSS stilleri - tek bir yerden yönetim."""
    config = get_config()
    
    return f"""
    <style>
    :root {{
        color-scheme: dark;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppBody"] {{
        background-color: {config.app.theme_bg} !important;
        color: {config.app.theme_text} !important;
    }}

    /* Streamlit Header Gizle */
    header {{ visibility: hidden; height: 0px; }}
    
    /* Kenar Boşluklarını Sıfırla */
    div.st-emotion-cache-1c9v9c4 {{ padding: 0 !important; }}
    .block-container {{
        padding-top: 1rem;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}

    /* Metric Kutuları */
    div[data-testid="stMetric"] {{
        background-color: #262730 !important;
        border: 1px solid #464b5f;
        border-radius: 10px;
        padding: 15px;
        color: #ffffff !important;
    }}
    div[data-testid="stMetricValue"] {{ color: #ffffff !important; }}
    div[data-testid="stMetricLabel"] {{ color: #bfbfbf !important; }}
    </style>
    """


def get_ticker_css() -> str:
    """Ticker CSS stilleri."""
    return """
    <style>
    .ticker-container {
        width: 100%;
        overflow: hidden;
        background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%);
        border-bottom: 1px solid #2f3440;
        margin-bottom: 20px;
        white-space: nowrap;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
    }
    .ticker-label {
        flex-shrink: 0;
        background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%);
        padding: 10px 15px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #6b7fd7;
        border-right: 1px solid #2f3440;
        z-index: 10;
        pointer-events: none;
    }
    .ticker-content-wrapper {
        flex: 1;
        overflow: hidden;
        position: relative;
    }
    .market-ticker {
        background: linear-gradient(135deg, #0e1117 0%, #1a1c24 100%);
        border-bottom: 1px solid #2f3440;
    }
    .portfolio-ticker {
        background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%);
        border-bottom: 2px solid #6b7fd7;
        margin-bottom: 20px;
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        padding-left: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 700;
        line-height: 1.6;
    }
    .animate-market { 
        animation: ticker-infinite 40s linear infinite; 
    }
    .animate-portfolio { 
        animation: ticker-infinite 35s linear infinite; 
    }
    @keyframes ticker-infinite {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-50%, 0, 0); }
    }
    </style>
    """


def get_news_css() -> str:
    """Haber kartları CSS stilleri."""
    return """
    <style>
    .news-card {
        background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #6b7fd7;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #6b7fd7 0%, #8b9aff 100%);
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(107, 127, 215, 0.4);
        border-left-color: #8b9aff;
    }
    .news-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
        text-decoration: none;
        line-height: 1.5;
        display: block;
        margin-bottom: 10px;
        transition: color 0.3s ease;
    }
    .news-title:hover {
        color: #8b9aff;
        text-decoration: none;
    }
    .news-meta {
        font-size: 13px;
        color: #b0b3c0;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .news-asset-badge {
        display: inline-block;
        background: rgba(107, 127, 215, 0.2);
        color: #8b9aff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-left: auto;
    }
    .news-source-badge {
        display: inline-block;
        background: rgba(0, 230, 118, 0.2);
        color: #00e676;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 8px;
    }
    .news-source-badge.izleme {
        background: rgba(255, 165, 0, 0.2);
        color: #ffa500;
    }
    a { text-decoration: none !important; }
    a:hover { text-decoration: none !important; }
    </style>
    """


def get_kral_header_css() -> str:
    """Kral header CSS stilleri."""
    return """
    <style>
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
    .kral-infobar {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 8px;
        margin-bottom: 12px;
        width: 100%;
    }
    .kral-infobox {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 12px 18px;
        border: 1px solid #303542;
        flex: 1;
        min-width: 200px;
        max-width: calc(20% - 16px);
    }
    .kral-infobox-label {
        font-size: 12px;
        color: #b0b3c0;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
    }
    .kral-infobox-value {
        display: block;
        margin-top: 4px;
        font-size: 20px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.3;
    }
    .kral-infobox-sub {
        font-size: 11px;
        color: #9da1b3;
        margin-top: 4px;
    }
    </style>
    """


def get_daily_movers_css() -> str:
    """Günlük hareket edenler CSS stilleri."""
    return """
    <style>
    .daily-movers-section {
        width: 100%;
        margin: 20px 0 40px;
    }
    .daily-movers-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 24px;
    }
    .daily-movers-card {
        background: linear-gradient(135deg, #1b1f2b 0%, #10131b 100%);
        border-radius: 20px;
        border: 1px solid #2f3440;
        padding: 24px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .daily-movers-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08);
    }
    .daily-movers-card.positive-card {
        border-top: 4px solid #00e676;
        color: #00e676;
    }
    .daily-movers-card.negative-card {
        border-top: 4px solid #ff5252;
        color: #ff5252;
    }
    </style>
    """


def get_all_css() -> str:
    """Tüm CSS stillerini birleştirir."""
    return (
        get_base_css() +
        get_ticker_css() +
        get_news_css() +
        get_kral_header_css() +
        get_daily_movers_css()
    )


# CSS cache - tekrar tekrar oluşturmayı önler
_css_cache: Optional[str] = None


def inject_css(css: Optional[str] = None) -> None:
    """
    CSS stillerini Streamlit'e enjekte eder.
    Cache kullanarak performansı artırır.
    
    Args:
        css: Özel CSS (None ise tüm stiller kullanılır)
    """
    global _css_cache
    
    if css is None:
        if _css_cache is None:
            _css_cache = get_all_css()
        css = _css_cache
    
    import streamlit as st
    st.markdown(css, unsafe_allow_html=True)
