import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

from utils import styled_dataframe, get_yahoo_symbol
from data_loader import (
    get_tefas_data,
    read_portfolio_history,
    write_portfolio_history,
    get_timeframe_changes
)

# ============================================================
#               🔥 SPARKLINE YARDIMCI FONKSİYONU
# ============================================================
def render_sparkline(data_list, height=55, color="#00e676"):
    """
    Minimal sparkline çizgisi döner.
    """
    if not data_list or len(data_list) < 2:
        return None

    df = pd.DataFrame({"x": list(range(len(data_list))), "y": data_list})

    fig = px.line(
        df,
        x="x",
        y="y"
    )
    fig.update_traces(line=dict(width=2, color=color))
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


# ============================================================
#             🔥 KPI Hesaplama + Sparkline Paket Fonksiyonu
# ============================================================
def get_kpi_data(total_value_try, total_value_usd):
    """
    - Günlük portföy değerini Google Sheet'e yaz
    - Tarihsel datayı oku
    - Haftalık - Aylık - YTD hesapları çıkar
    - Sparkline listelerini al
    """
    # --- 1) Tarihsel veriyi oku ---
    history = read_portfolio_history()

    # --- 2) Bugün yoksa ekle ---
    today_value = total_value_try
    if history.empty or history["Tarih"].iloc[-1].date() != pd.Timestamp.today().date():
        write_portfolio_history(total_value_try, total_value_usd)
        history = read_portfolio_history()

    # --- 3) KPİ verilerini üret ---
    tf = get_timeframe_changes(history)
    if tf is None:
        return None

    return tf


# ============================================================
#       🔥 PIE + BAR (Portföy dağılımı) — Değişmedi
# ============================================================
def render_pie_bar_charts(
    df: pd.DataFrame,
    group_col: str,
    all_tab: bool = False,
    varlik_gorunumu: str = "YÜZDE (%)",
    total_spot_deger: float = 0.0,
) -> None:

    if df is None or df.empty or "Değer" not in df.columns:
        st.info("Grafik üretmek için veri bulunamadı.")
        return

    # Gruplama
    agg = {"Değer": "sum"}
    if "Top. Kâr/Zarar" in df.columns:
        agg["Top. Kâr/Zarar"] = "sum"

    grouped = df.groupby(group_col, as_index=False).agg(agg)
    grouped = grouped.sort_values("Değer", ascending=False)

    # Yüzde hesap
    if all_tab and total_spot_deger > 0:
        denom = float(total_spot_deger)
    else:
        denom = float(grouped["Değer"].sum())

    grouped["Pay (%)"] = (grouped["Değer"] / denom * 100) if denom > 0 else 0

    # Labels
    grouped["Label"] = grouped[group_col].astype(str)

    col_pie, col_bar = st.columns([1.2, 1])

    # ---------------- PIE ----------------
    with col_pie:
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=grouped["Label"],
                    values=grouped["Değer"],
                    hole=0.6,
                    hovertemplate="<b>%{label}</b><br>Değer: %{value:,.0f}<br>%{percent:.1%}<extra></extra>",
                )
            ]
        )
        fig_pie.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True,
            legend_title=group_col,
            annotations=[
                dict(
                    text="TOPLAM",
                    x=0.5,
                    y=0.52,
                    font=dict(size=11, color="#bfc3d4"),
                    showarrow=False,
                ),
                dict(
                    text=f"{grouped['Değer'].sum():,.0f}",
                    x=0.5,
                    y=0.42,
                    font=dict(size=16, color="#ffffff"),
                    showarrow=False,
                ),
            ],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- BAR ----------------
    with col_bar:
        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                x=grouped["Değer"],
                y=grouped["Label"],
                orientation="h",
            )
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=0, l=0, r=0),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tablo
    disp = grouped[[group_col, "Değer", "Pay (%)"]].copy()
    disp["Pay (%)"] = disp["Pay (%)"].round(2)
    st.dataframe(styled_dataframe(disp), hide_index=True, use_container_width=True)


# ============================================================
#               🔥 PAZAR SEKME VIEW (Değişmedi)
# ============================================================
def render_pazar_tab(
    df: pd.DataFrame,
    filter_key: str,
    sym: str,
    usd_try_rate: float,
    varlik_gorunumu: str,
    total_spot_deger: float,
):

    if df is None or df.empty:
        st.info("Bu görünüm için portföyde varlık yok.")
        return

    # Filtre
    if filter_key == "Tümü":
        sub = df.copy()
    else:
        sub = df[df["Pazar"].astype(str).str.contains(filter_key, case=False, na=False)]

    if sub.empty:
        st.info(f"{filter_key} için veri yok.")
        return

    # METRİKLER
    total_val = float(sub["Değer"].sum())
    total_pnl = float(sub["Top. Kâr/Zarar"].sum())
    base = total_val - total_pnl
    pnl_pct = (total_pnl / base * 100) if base != 0 else 0
    daily_pnl = float(sub["Gün. Kâr/Zarar"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Değer", f"{sym}{total_val:,.0f}")
    c2.metric("Toplam K/Z", f"{sym}{total_pnl:,.0f}", delta=f"{pnl_pct:.2f}%")
    c3.metric("Günlük K/Z", f"{sym}{daily_pnl:,.0f}")

    st.divider()

    # Grafikler
    render_pie_bar_charts(
        sub,
        group_col="Kod",
        all_tab=(filter_key == "Tümü"),
        varlik_gorunumu=varlik_gorunumu,
        total_spot_deger=total_spot_deger,
    )

    # Tablo
    st.dataframe(styled_dataframe(sub), hide_index=True, use_container_width=True)


# ============================================================
#        🔥 TARİHSEL PORTFÖY GRAFİĞİ (Düşüş fix'li)
# ============================================================
def get_historical_chart(df: pd.DataFrame, usd_try_rate: float, pb: str):
    if df is None or df.empty:
        return None

    all_series = []

    for _, row in df.iterrows():
        kod = str(row.get("Kod", ""))
        pazar = str(row.get("Pazar", ""))
        adet = float(row.get("Adet", 0) or 0)

        if adet == 0:
            continue

        pazar_upper = pazar.upper()
        kod_upper = kod.upper()

        # TRY mi USD mi?
        if (
            "BIST" in pazar_upper
            or "TL" in kod_upper
            or "FON" in pazar_upper
            or "EMTIA" in pazar_upper
            or "NAKIT" in pazar_upper
        ):
            asset_currency = "TRY"
        else:
            asset_currency = "USD"

        prices = None

        try:
            # --- NAKİT ---
            if "NAKIT" in pazar_upper:
                today = pd.Timestamp.today().normalize()
                if kod == "TL":
                    prices = pd.Series([1.0], index=[today])
                elif kod == "USD":
                    prices = pd.Series([usd_try_rate], index=[today])
                else:
                    prices = pd.Series([1.0], index=[today])

            # --- FON ---
            elif "FON" in pazar_upper:
                price, _ = get_tefas_data(kod)
                if price > 0:
                    idx = pd.date_range(end=pd.Timestamp.today(), periods=30)
                    prices = pd.Series(price, index=idx)

            # --- GRAM GÜMÜŞ ---
            elif "GÜMÜŞ" in kod_upper:
                h = yf.Ticker("SI=F").history(period="60d")
                if not h.empty:
                    prices = (h["Close"] * usd_try_rate) / 31.1035

            # --- GRAM ALTIN ---
            elif "ALTIN" in kod_upper:
                h = yf.Ticker("GC=F").history(period="60d")
                if not h.empty:
                    prices = (h["Close"] * usd_try_rate) / 31.1035

            # --- HİSSE / KRİPTO ---
            else:
                symbol = get_yahoo_symbol(kod, pazar)
                h = yf.Ticker(symbol).history(period="60d")
                if not h.empty:
                    prices = h["Close"]

        except:
            prices = None

        if prices is None or prices.empty:
            continue

        # TZ temizle
        prices.index = pd.to_datetime(prices.index).tz_localize(None)

        # PB çevirisi
        if pb == "TRY":
            if asset_currency == "USD":
                values = prices * adet * usd_try_rate
            else:
                values = prices * adet
        else:
            if asset_currency == "TRY":
                values = prices * adet / usd_try_rate
            else:
                values = prices * adet

        all_series.append(values)

    # Hiç veri yoksa
    if not all_series:
        return None

    df_concat = pd.concat(all_series, axis=1)
    df_concat = df_concat.sort_index().ffill()

    series = df_concat.sum(axis=1)
    series = series.tail(60)

    plot_df = pd.DataFrame({"Tarih": series.index, "Değer": series.values})

    fig = px.line(plot_df, x="Tarih", y="Değer")
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="",
        yaxis_title="",
    )
    return fig
