import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

from utils import render_table
from data_loader import get_tefas_data


def render_pie_bar_charts(df: pd.DataFrame, group_col: str, all_tab: bool = False):
    """Pastayı ve bar chart'ı tek yerden üretir."""
    if df.empty or "Değer" not in df.columns:
        return

    # Gruplama
    agg_cols = {"Değer": "sum"}
    has_pnl = "Top. Kâr/Zarar" in df.columns
    if has_pnl:
        agg_cols["Top. Kâr/Zarar"] = "sum"

    grouped = df.groupby(group_col, as_index=False).agg(agg_cols)
    total_val = grouped["Değer"].sum()

    if total_val <= 0:
        plot_df = grouped.copy()
    else:
        grouped["_pct"] = grouped["Değer"] / total_val * 100
        major = grouped[grouped["_pct"] >= 1].copy()
        minor = grouped[grouped["_pct"] < 1].copy()

        if not minor.empty and not major.empty:
            other_row = {
                group_col: "Diğer",
                "Değer": minor["Değer"].sum(),
            }
            if has_pnl:
                other_row["Top. Kâr/Zarar"] = minor["Top. Kâr/Zarar"].sum()
            major = pd.concat([major, pd.DataFrame([other_row])], ignore_index=True)
            plot_df = major.drop(columns=["_pct"], errors="ignore")
        else:
            plot_df = grouped.drop(columns=["_pct"], errors="ignore")

    total_plot_val = plot_df["Değer"].sum()
    if total_plot_val > 0:
        plot_df["_pct"] = plot_df["Değer"] / total_plot_val * 100
    else:
        plot_df["_pct"] = 0

    threshold = 5.0 if all_tab else 0.0

    texts = []
    for _, r in plot_df.iterrows():
        if r["_pct"] >= threshold:
            texts.append(f"{r[group_col]} {r['_pct']:.1f}%")
        else:
            texts.append("")

    c_pie, c_bar = st.columns([4, 3])

    pie_fig = px.pie(
        plot_df,
        values="Değer",
        names=group_col,
        hole=0.40,
    )
    pie_fig.update_traces(
        text=texts,
        textinfo="text",
        textfont=dict(size=18, color="white", family="Arial Black"),
    )
    pie_fig.update_layout(
        legend=dict(font=dict(size=14)),
        margin=dict(t=40, l=0, r=0, b=80),
    )
    c_pie.plotly_chart(pie_fig, use_container_width=True)

    if has_pnl:
        bar_fig = px.bar(
            plot_df.sort_values("Değer"),
            x=group_col,
            y="Değer",
            color="Top. Kâr/Zarar",
            text="Değer",
        )
    else:
        bar_fig = px.bar(
            plot_df.sort_values("Değer"),
            x=group_col,
            y="Değer",
            text="Değer",
        )

    bar_fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont=dict(size=14, color="white", family="Arial Black"),
    )
    bar_fig.update_layout(
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(t=40, l=20, r=20, b=40),
    )
    c_bar.plotly_chart(bar_fig, use_container_width=True)


def get_historical_chart(df_portfolio: pd.DataFrame, usd_try: float):
    """Şimdilik stub: KRAL’da da yoktu."""
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
        c2.metric(
            "Toplam Kâr/Zarar",
            f"{symb}{t_pl:,.0f}",
            delta=f"{symb}{t_pl:,.0f}",
        )
    else:
        total_cost = (sub["Değer"] - sub["Top. Kâr/Zarar"]).sum()
        pct = (t_pl / total_cost * 100) if total_cost != 0 else 0
        c2.metric(
            "Toplam Kâr/Zarar",
            f"{symb}{t_pl:,.0f}",
            delta=f"{pct:.2f}%",
        )

    st.divider()

    if filter_key != "VADELI":
        render_pie_bar_charts(sub, "Kod", all_tab=False)

    # <<< BURASI: tablo artık AGGRID ile >>>
    render_table(sub)


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
