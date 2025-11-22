import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

from utils import styled_dataframe
from data_loader import get_tefas_data


# --------------------------------------------------------------------
#  ORTAK PIE + BAR CHART (BÜYÜTÜLMÜŞ ve OKUNUR HALE GETİRİLMİŞ)
# --------------------------------------------------------------------
def render_pie_bar_charts(df: pd.DataFrame, group_col: str):
    if df.empty or "Değer" not in df.columns:
        return

    # Daha geniş alan / daha büyük pasta
    c_pie, c_bar = st.columns([4, 3])

    # ====================
    # PIE CHART
    # ====================
    pie_fig = px.pie(
        df,
        values="Değer",
        names=group_col,
        hole=0.40,
    )
    pie_fig.update_traces(
        textinfo="percent+label",
        textfont=dict(size=20, color="white"),
    )
    pie_fig.update_layout(
        legend=dict(font=dict(size=14)),
        margin=dict(t=40, l=0, r=0, b=0)
    )
    c_pie.plotly_chart(pie_fig, use_container_width=True)

    # ====================
    # BAR CHART
    # ====================
    if "Top. Kâr/Zarar" in df.columns:
        bar_fig = px.bar(
            df.sort_values("Değer"),
            x=group_col,
            y="Değer",
            color="Top. Kâr/Zarar",
            text="Değer",
        )
    else:
        bar_fig = px.bar(
            df.sort_values("Değer"),
            x=group_col,
            y="Değer",
            text="Değer",
        )

    bar_fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont=dict(size=14, color="white"),
    )
    bar_fig.update_layout(
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14)),
        legend=dict(font=dict(size=14)),
        margin=dict(t=40, l=20, r=20, b=20),
    )
    c_bar.plotly_chart(bar_fig, use_container_width=True)


# --------------------------------------------------------------------
#  TARİHSEL GRAFİK (Şimdilik Stub)
# --------------------------------------------------------------------
def get_historical_chart(df_portfolio: pd.DataFrame, usd_try: float):
    return None


# --------------------------------------------------------------------
#  SEKME BAZLI PAZAR EKRANI (burada grafik çağrılıyor)
# --------------------------------------------------------------------
def render_pazar_tab(df, filter_key, symb, usd_try):
    if df.empty:
        return st.info("Veri yok.")

    if filter_key == "VADELI":
        sub = df[df["Pazar"].str.contains("VADELI", na=False)]
    else:
        sub = df[df["Pazar"].str.contains(filter_key, na=False)]

    if sub.empty:
        return st.info(f"{filter_key} yok.")

    total_val = sub["Değer"].sum()
    total_pnl = sub["Top. Kâr/Zarar"].sum()

    col1, col2 = st.columns(2)

    label = "
