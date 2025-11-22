# charts.py
import streamlit as st
import plotly.express as px

from utils import styled_dataframe

def render_pie_bar_charts(df, group_col: str):
    if df.empty or "Değer" not in df.columns:
        return
    c_p, c_b = st.columns(2)
    pie_fig = px.pie(df, values="Değer", names=group_col, hole=0.4)
    c_p.plotly_chart(pie_fig, use_container_width=True)

    if "Top. Kâr/Zarar" in df.columns:
        bar_fig = px.bar(
            df.sort_values("Değer"),
            x=group_col,
            y="Değer",
            color="Top. Kâr/Zarar",
        )
    else:
        bar_fig = px.bar(
            df.sort_values("Değer"),
            x=group_col,
            y="Değer",
        )
    c_b.plotly_chart(bar_fig, use_container_width=True)

def render_pazar_tab(df, filter_key, symb, usd_try):
    from utils import styled_dataframe  # circular önlemek için

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
    c2.metric("Toplam Kâr/Zarar", f"{symb}{t_pl:,.0f}", delta=f"{t_pl:,.0f}")

    st.divider()

    if filter_key != "VADELI":
        render_pie_bar_charts(sub, "Kod")

    st.dataframe(
        styled_dataframe(sub),
        use_container_width=True,
        hide_index=True,
    )
