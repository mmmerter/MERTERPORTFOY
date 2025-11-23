import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

from utils import styled_dataframe
from data_loader import get_tefas_data


def _prepare_pie_df(df: pd.DataFrame, group_col: str, threshold: float | None):
    """
    threshold:
        None  -> hiçbirini 'Diğer' yapma
        0.01  -> %1 altını Diğer
        0.05  -> %5 altını Diğer
    """
    if df.empty or "Değer" not in df.columns or threshold is None:
        return df

    tmp = df.copy()
    total = tmp["Değer"].sum()
    if total <= 0:
        return df

    tmp["__pay"] = tmp["Değer"] / total
    tmp[group_col] = tmp.apply(
        lambda r: "Diğer" if r["__pay"] < threshold else r[group_col], axis=1
    )
    # aynı isimleri grupla
    agg_cols = {c: "sum" for c in tmp.columns if c not in [group_col, "__pay"]}
    agg_cols["__pay"] = "sum"
    grouped = tmp.groupby(group_col, as_index=False).agg(agg_cols)
    grouped = grouped.drop(columns="__pay", errors="ignore")
    return grouped


def render_pie_bar_charts(
    df: pd.DataFrame,
    group_col: str,
    threshold: float | None = 0.01,
):
    """Pastayı ve bar chart'ı tek yerden üretir."""
    if df.empty or "Değer" not in df.columns:
        return

    df_plot = _prepare_pie_df(df, group_col, threshold)

    c_p, c_b = st.columns([1.2, 1])

    # --- PİE ---
    pie_fig = px.pie(
        df_plot,
        values="Değer",
        names=group_col,
        hole=0.35,
    )
    pie_fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=14, family="Arial Black"),
        pull=[0.03] * len(df_plot),
    )
    pie_fig.update_layout(
        height=430,
        margin=dict(t=40, b=80, l=0, r=0),
        legend=dict(font=dict(size=12)),
    )
    c_p.plotly_chart(pie_fig, use_container_width=True)

    # --- BAR ---
    if "Top. Kâr/Zarar" in df_plot.columns:
        bar_fig = px.bar(
            df_plot.sort_values("Değer"),
            x=group_col,
            y="Değer",
            color="Top. Kâr/Zarar",
            color_continuous_scale="Blues",
        )
    else:
        bar_fig = px.bar(
            df_plot.sort_values("Değer"),
            x=group_col,
            y="Değer",
        )

    bar_fig.update_layout(
        height=430,
        margin=dict(t=40, b=80, l=40, r=40),
        xaxis=dict(
            title="",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Değer",
            title_font=dict(size=12),
            tickfont=dict(size=11),
        ),
        legend=dict(font=dict(size=11)),
    )
    c_b.plotly_chart(bar_fig, use_container_width=True)


def get_historical_chart(df_portfolio: pd.DataFrame, usd_try: float):
    """
    Şimdilik stub: Hata vermemesi için None dönüyor.
    KRAL'da da böyleydi, aynen koruyoruz.
    """
    return None


def render_pazar_tab(df, filter_key, symb, usd_try):
    if df.empty:
        return st.info("Veri yok.")

    if filter_key == "VADELI":
        sub = df[df["Pazar"].str.contains("VADELI", na=False)]
    else:
        sub = df[df["Pazar"].str.contains(filter_key, na=False)]

    if sub.empty:
        return st.info(f"{filter_key} yok.")

    t_val = sub["Değer"].sum()
    t_pl = sub["Top. Kâr/Zarar"].sum()

    c1, c2 = st.columns(2)
    lbl = "Toplam PNL" if filter_key == "VADELI" else "Toplam Varlık"
    c1.metric(lbl, f"{symb}{t_val:,.0f}")

    if filter_key == "VADELI":
        # maliyet bilgisi olmadığı için yüzde hesaplamıyoruz
        c2.metric("Toplam Kâr/Zarar", f"{symb}{t_pl:,.0f}")
    else:
        invested = t_val - t_pl
        pct = (t_pl / invested * 100) if invested > 0 else 0.0
        c2.metric(
            "Toplam Kâr/Zarar",
            f"{symb}{t_pl:,.0f}",
            delta=f"%{pct:.2f}",
        )

    st.divider()

    if filter_key != "VADELI":
        # Sekmeye göre (BIST, ABD, FON vb.) varlık bazlı grafik
        render_pie_bar_charts(sub, "Kod", threshold=0.01)

        if filter_key not in ["FON", "EMTIA", "NAKIT"]:
            try:
                h = get_historical_chart(sub, usd_try)
                if h is not None:
                    st.line_chart(h)
            except Exception:
                st.warning("Tarihsel grafik yüklenemedi.")

    st.dataframe(
        styled_dataframe(sub),
        use_container_width=True,
        hide_index=True,
    )


def render_detail_view(symbol, pazar):
    st.markdown(f"### 🔎 {symbol} Detaylı Analizi")

    if "FON" in pazar:
        price, _ = get_tefas_data(symbol)
        st.metric(f"{symbol} Son Fiyat", f"₺{price:,.6f}")
        st.info("Yatırım fonları için anlık grafik desteği TEFAS kaynaklı sınırlıdır.")
        return

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2y")

        if not hist.empty:
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=hist.index,
                        open=hist["Open"],
                        high=hist["High"],
                        low=hist["Low"],
                        close=hist["Close"],
                        name=symbol,
                    )
                ]
            )
            fig.update_layout(
                title=f"{symbol} Fiyat Grafiği",
                yaxis_title="Fiyat",
                template="plotly_dark",
                height=600,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list(
                            [
                                dict(
                                    count=1,
                                    label="1A",
                                    step="month",
                                    stepmode="backward",
                                ),
                                dict(
                                    count=3,
                                    label="3A",
                                    step="month",
                                    stepmode="backward",
                                ),
                                dict(
                                    count=6,
                                    label="6A",
                                    step="month",
                                    stepmode="backward",
                                ),
                                dict(
                                    count=1,
                                    label="YTD",
                                    step="year",
                                    stepmode="todate",
                                ),
                                dict(
                                    count=1,
                                    label="1Y",
                                    step="year",
                                    stepmode="backward",
                                ),
                                dict(step="all", label="TÜMÜ"),
                            ]
                        ),
                        bgcolor="#262730",
                        font=dict(color="white"),
                    ),
                    rangeslider=dict(visible=False),
                    type="date",
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

            info = ticker.info
            market_cap = info.get("marketCap", "N/A")
            if isinstance(market_cap, int):
                market_cap = f"{market_cap:,.0f}"

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Sektör", info.get("sector", "-"))
            c2.metric("F/K", info.get("trailingPE", "-"))
            c3.metric("Piyasa Değeri", market_cap)
            c4.metric("52H Yüksek", info.get("fiftyTwoWeekHigh", "-"))
            c5.metric("52H Düşük", info.get("fiftyTwoWeekLow", "-"))
        else:
            st.warning("Grafik verisi bulunamadı.")
    except Exception as e:
        st.error(f"Veri çekilemedi: {e}")
