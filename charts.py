import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from utils import styled_dataframe, get_yahoo_symbol
from data_loader import get_tefas_data, get_historical_prices, get_usd_try_history, get_fund_history

# --------------------------------------------------------------------
#  PASTA VE BAR GRAFİKLERİ
# --------------------------------------------------------------------
def render_pie_bar_charts(df, group_col, all_tab=False, varlik_gorunumu="YÜZDE (%)", total_spot_deger=0):
    if df.empty or "Değer" not in df.columns: return
    
    agg = {"Değer": "sum"}
    if "Top. Kâr/Zarar" in df.columns: agg["Top. Kâr/Zarar"] = "sum"
    
    grouped = df.groupby(group_col, as_index=False).agg(agg)
    
    tot = grouped["Değer"].sum()
    if tot > 0:
        grouped["_pct"] = grouped["Değer"] / tot * 100
        major = grouped[grouped["_pct"] >= 1].copy()
        minor = grouped[grouped["_pct"] < 1].copy()
        if not minor.empty:
            other = {group_col: "Diğer", "Değer": minor["Değer"].sum()}
            if "Top. Kâr/Zarar" in minor: other["Top. Kâr/Zarar"] = minor["Top. Kâr/Zarar"].sum()
            major = pd.concat([major, pd.DataFrame([other])], ignore_index=True)
            plot_df = major
        else: plot_df = grouped
    else: plot_df = grouped.copy()

    title_s = "(TUTAR)"
    if varlik_gorunumu == "YÜZDE (%)":
        denom = total_spot_deger if all_tab else plot_df["Değer"].sum()
        if denom > 0: plot_df["Değer"] = plot_df["Değer"] / denom * 100
        title_s = "(Portföy %)" if all_tab else "(Lokal %)"

    texts = []
    for _, r in plot_df.iterrows():
        if r["Değer"] > 0: 
            fmt = f"{r['Değer']:,.1f}%" if varlik_gorunumu == "YÜZDE (%)" else f"{r['Değer']:,.0f}"
            texts.append(f"{r[group_col]} {fmt}")
        else: texts.append("")

    c1, c2 = st.columns([4, 3])
    
    # PIE
    hover_cols = ["Değer"]
    if "Top. Kâr/Zarar" in plot_df.columns: hover_cols.append("Top. Kâr/Zarar")

    fig = px.pie(plot_df, values="Değer", names=group_col, hole=0.4, title=f"Dağılım {title_s}", custom_data=hover_cols)
    
    ht = '<b>%{label}</b><br>Değer: %{customdata[0]:.2f}'
    if "Top. Kâr/Zarar" in plot_df.columns:
        ht += '<br>K/Z: %{customdata[1]:.2f}'

    fig.update_traces(text=texts, textinfo="text", textfont=dict(size=18, color="white", family="Arial Black"), hovertemplate=ht)
    fig.update_layout(legend=dict(font=dict(size=14)), margin=dict(t=40, b=40))
    c1.plotly_chart(fig, use_container_width=True)

    # BAR
    if "Top. Kâr/Zarar" in plot_df:
        fig2 = px.bar(plot_df.sort_values("Değer"), x=group_col, y="Değer", color="Top. Kâr/Zarar", text="Değer", title=f"Değerler {title_s}")
    else:
        fig2 = px.bar(plot_df.sort_values("Değer"), x=group_col, y="Değer", text="Değer", title=f"Değerler {title_s}")
    
    fmt_bar = "%{text:,.2f}%" if varlik_gorunumu == "YÜZDE (%)" else "%{text:,.0f}"
    fig2.update_traces(texttemplate=fmt_bar, textposition="outside", textfont=dict(size=14, color="white"))
    c2.plotly_chart(fig2, use_container_width=True)


# --------------------------------------------------------------------
#  TARIHSEL GRAFIK MOTORU (DÜZELTİLDİ)
# --------------------------------------------------------------------
def get_historical_chart(df_portfolio, usd_try, gorunum_pb):
    """
    Portföyün tarihsel değerini hesaplar.
    Timezone sorunlarını ve kur çevrim hatalarını giderir.
    """
    if df_portfolio.empty: return None
    
    # 1. Varlıkları Hazırla
    symbol_map = {} 
    fund_map = []   
    cash_map = []   
    
    for _, row in df_portfolio.iterrows():
        kod = row["Kod"]
        pazar = row["Pazar"]
        adet = row["Adet"]
        
        if "FON" in pazar: 
            fund_map.append((kod, adet))
        elif "NAKIT" in pazar:
            cash_map.append((kod, adet))
        elif "VADELI" not in pazar: 
            s = get_yahoo_symbol(kod, pazar)
            symbol_map[kod] = {"symbol": s, "adet": adet, "pazar": pazar}

    try:
        # 2. Ana Referans (USDTRY Tarihçesi)
        usd_hist_df = get_usd_try_history()
        if usd_hist_df.empty: return None
        
        # Timezone temizliği (Hatanın ana kaynağı burasıydı)
        usd_hist = usd_hist_df["TRY=X"].copy()
        usd_hist.index = usd_hist.index.tz_localize(None)
        
        # Toplam Serisi (Referans indeksine göre başlat)
        total_series = pd.Series(0.0, index=usd_hist.index)
        
        # --- A) YAHOO VARLIKLARI (Hisse, Kripto, Emtia) ---
        if symbol_map:
            fetch_map = {k: v["symbol"] for k, v in symbol_map.items()}
            yh = get_historical_prices(fetch_map)
            
            if not yh.empty:
                # Yahoo verisinin de timezone'unu temizle
                yh.index = yh.index.tz_localize(None)
                
                # Eksik günleri (hafta sonu vb) kur verisine uydur
                yh = yh.reindex(usd_hist.index).ffill()
                
                for kod, info in symbol_map.items():
                    if kod in yh.columns:
                        price_series = yh[kod]
                        adet = info["adet"]
                        pazar = info["pazar"]
                        
                        val_series = None
                        
                        # Gram Altın / Gümüş (Özel Hesap: Ons * Kur / 31.1)
                        if "Gram" in kod or "GRAM" in kod:
                            if gorunum_pb == "TRY":
                                # (Ons($) * Kur) / 31.1 * Adet
                                val_series = (price_series * usd_hist / 31.1035) * adet
                            else: 
                                # Ons($) / 31.1 * Adet
                                val_series = (price_series / 31.1035) * adet
                                
                        # Normal Varlıklar (Hisse, Kripto)
                        else:
                            # Varlık TRY mi USD mi?
                            is_try_asset = "BIST" in pazar
                            val_native = price_series * adet
                            
                            if is_try_asset:
                                # Varlık TRY -> İstenen USD ise böl
                                if gorunum_pb == "USD": val_series = val_native / usd_hist
                                else: val_series = val_native
                            else:
                                # Varlık USD -> İstenen TRY ise çarp
                                if gorunum_pb == "TRY": val_series = val_native * usd_hist
                                else: val_series = val_native
                        
                        if val_series is not None:
                            total_series = total_series.add(val_series, fill_value=0)

        # --- B) FONLAR (Hepsi TRY kabul edilir) ---
        for f, adet in fund_map:
            fh = get_fund_history(f)
            if not fh.empty:
                fh.index = fh.index.tz_localize(None) # Timezone temizle
                fh = fh.reindex(usd_hist.index).ffill()
                val = fh * adet
                
                if gorunum_pb == "USD": val = val / usd_hist
                total_series = total_series.add(val, fill_value=0)
                
        # --- C) NAKİT ---
        for kod, adet in cash_map:
            # Nakit miktarı sabittir, değeri kurla değişir
            val_series = pd.Series(float(adet), index=usd_hist.index)
            
            if kod == "TL":
                if gorunum_pb == "USD": val_series = val_series / usd_hist
            elif kod == "USD":
                if gorunum_pb == "TRY": val_series = val_series * usd_hist
            elif kod == "EUR":
                # Basitlik için EUR ~ 1.05 USD varsayabiliriz veya EURTRY çekilebilir. 
                # Şimdilik EURTRY kuru olmadığı için USD gibi davranmasın, sabit kalsın.
                # İdealde get_eur_try_history() gerekir.
                pass 
            
            total_series = total_series.add(val_series, fill_value=0)
        
        # Boşlukları temizle
        total_series = total_series.dropna()
        
        # Grafik Çizimi
        if total_series.empty: return None
        
        fig = px.area(total_series, title=f"Portföy Değeri ({gorunum_pb}) - Son 1 Yıl")
        fig.update_layout(
            showlegend=False, 
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis_title="",
            yaxis_title=f"Değer ({gorunum_pb})"
        )
        return fig

    except Exception as e:
        st.error(f"Grafik Hatası: {e}")
        return None


# --------------------------------------------------------------------
#  SEKME RENDER
# --------------------------------------------------------------------
def render_pazar_tab(df, filter_key, symb, usd_try, varlik_gorunumu, total_spot_deger):
    if df.empty: return st.info("Veri yok.")
    
    if filter_key == "Tümü": sub = df.copy()
    else: sub = df[df["Pazar"].str.contains(filter_key, na=False)]

    if sub.empty: return st.info("Yok.")
    
    tv = sub["Değer"].sum()
    tp = sub["Top. Kâr/Zarar"].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Toplam", f"{symb}{tv:,.0f}")
    
    is_vadeli = "VADELI" in filter_key
    
    if is_vadeli: c2.metric("PNL", f"{symb}{tp:,.0f}")
    else:
        tc = tv - tp
        pct = (tp / tc * 100) if tc != 0 else 0
        c2.metric("K/Z", f"{symb}{tp:,.0f}", delta=f"{pct:.2f}%")
    
    st.divider()
    
    # 1. PASTA GRAFİK (ÜSTTE)
    if not is_vadeli:
        st.subheader(f"📊 {filter_key} Dağılımı")
        render_pie_bar_charts(sub, "Kod", filter_key=="Tümü", varlik_gorunumu, total_spot_deger)
        st.divider()
    
    # 2. TARIHSEL GRAFİK (ALTTA)
    st.subheader(f"📈 {filter_key} Tarihsel Değer")
    h_chart = get_historical_chart(sub, usd_try, "TRY" if symb=="₺" else "USD")
    if h_chart: 
        st.plotly_chart(h_chart, use_container_width=True)
    else:
        st.info("Tarihsel veri hesaplanamıyor.")
    
    # 3. TABLO
    disp = sub.copy()
    if varlik_gorunumu == "YÜZDE (%)" and not is_vadeli:
        disp.rename(columns={"Değer": "Tutar"}, inplace=True)
        denom = total_spot_deger if filter_key == "Tümü" else sub["Değer"].sum()
        if denom > 0: disp["Değer"] = disp["Tutar"] / denom * 100
        else: disp["Değer"] = 0
        
    st.dataframe(styled_dataframe(disp), use_container_width=True, hide_index=True)

def render_detail_view(symbol, pazar):
    st.write(symbol)
