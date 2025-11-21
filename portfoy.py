import streamlit as st
import yfinance as yf
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Portföy ve Takip", layout="wide", page_icon="📈")

# --- CSS STİL AYARLARI ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 24px; }
    .big-font { font-size:20px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 Çoklu Varlık Portföy Yöneticisi")

# --- VARLIK LİSTELERİ (AUTOCOMPLETE İÇİN) ---
# Burayı dilediğin gibi genişletebilirsin.
MARKET_DATA = {
    "BIST": [
        "THYAO", "GARAN", "ASELS", "EREGL", "SISE", "BIMAS", "AKBNK", "YKBNK", "KCHOL", "SAHOL",
        "TUPRS", "FROTO", "TOASO", "PGSUS", "TCELL", "PETKM", "HEKTS", "SASA", "ASTOR", "KONTR"
    ],
    "KRIPTO": [
        "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOGE", "SHIB", "DOT", 
        "MATIC", "LTC", "TRX", "UNI", "ATOM", "LINK", "XLM", "ALGO", "VET", "ICP"
    ],
    "EMTIA": [
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "PL=F", "PA=F", "ZC=F"
    ],
    "ABD": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC"
    ],
    "FIZIKI": [
        "Gram Altın", "Çeyrek Altın", "Cumhuriyet Altın", "Dolar Nakit", "Euro Nakit"
    ]
}

# --- SABİTLER VE KUR ---
SHEET_NAME = "PortfoyData" 

@st.cache_data(ttl=3600)
def get_usd_try():
    try:
        ticker = yf.Ticker("TRY=X")
        hist = ticker.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
        return 34.0
    except:
        return 34.0

USD_TRY = get_usd_try()
st.sidebar.metric("🇺🇸 USD/TRY Kuru", f"{USD_TRY:.2f} ₺")

# --- GOOGLE SHEETS FONKSİYONLARI ---
def get_data_from_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        
        if not data:
            return pd.DataFrame(columns=["Kod", "Pazar", "Adet", "Maliyet", "Tip", "Notlar"])
        
        df = pd.DataFrame(data)
        if "Tip" not in df.columns: df["Tip"] = "Portfoy"
        if "Notlar" not in df.columns: df["Notlar"] = ""
        
        return df
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return pd.DataFrame(columns=["Kod", "Pazar", "Adet", "Maliyet", "Tip", "Notlar"])

def save_data_to_sheet(df):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- DATA YÜKLEME ---
portfoy_df = get_data_from_sheet()
if not portfoy_df.empty:
    portfoy_df["Adet"] = pd.to_numeric(portfoy_df["Adet"], errors='coerce').fillna(0)
    portfoy_df["Maliyet"] = pd.to_numeric(portfoy_df["Maliyet"], errors='coerce').fillna(0)

# --- YAN MENÜ: EKLEME / SİLME ---
with st.sidebar:
    st.divider()
    st.header("➕ Ekle / Güncelle")
    
    islem_tipi = st.radio("Kayıt Türü", ["Portföyüme Ekle", "Takip Listesine Ekle"])
    
    # ⚠️ ÖNEMLİ DEĞİŞİKLİK: Pazar seçimini formun DIŞINA aldık.
    # Böylece pazar değiştiğinde sayfa yenilenir ve alttaki liste güncellenir.
    yeni_pazar = st.selectbox("Pazar Seçiniz", ["BIST", "KRIPTO", "ABD", "EMTIA", "FIZIKI"])
    
    # Seçilen pazara göre listeyi getir
    secenekler = MARKET_DATA.get(yeni_pazar, [])
    
    with st.form("ekle_form", clear_on_submit=True):
        # Text input yerine Selectbox geldi
        # options=secenekler -> Pazar'a göre değişen liste
        yeni_kod = st.selectbox(
            "Varlık Seç (Yazarak Ara)", 
            options=secenekler,
            index=None, # Başlangıçta boş gelsin
            placeholder="Sembolü seçin veya yazın..."
        )
        
        # Eğer listede olmayan bir şey girmek isterse diye opsiyonel manuel giriş (İstersen kaldırabilirsin)
        manuel_kod_giris = st.checkbox("Listede yok, manuel gireceğim")
        if manuel_kod_giris:
            yeni_kod = st.text_input("Manuel Kod Giriniz").upper()

        if islem_tipi == "Portföyüme Ekle":
            c1, c2 = st.columns(2)
            yeni_adet = c1.number_input("Adet", min_value=0.0, step=0.01)
            yeni_maliyet = c2.number_input("Birim Maliyet", min_value=0.0, step=0.01)
            kayit_tipi = "Portfoy"
        else:
            yeni_adet = 0
            yeni_maliyet = 0
            kayit_tipi = "Takip"
            
        yeni_not = st.text_input("Not (Opsiyonel)")
        
        submitted = st.form_submit_button("💾 Kaydet")
        
        if submitted:
            if yeni_kod:
                # Update veya Insert mantığı
                portfoy_df = portfoy_df[portfoy_df["Kod"] != yeni_kod]
                
                yeni_veri = pd.DataFrame({
                    "Kod": [yeni_kod], "Pazar": [yeni_pazar], 
                    "Adet": [yeni_adet], "Maliyet": [yeni_maliyet],
                    "Tip": [kayit_tipi], "Notlar": [yeni_not]
                })
                portfoy_df = pd.concat([portfoy_df, yeni_veri], ignore_index=True)
                save_data_to_sheet(portfoy_df)
                st.success(f"{yeni_kod} listeye eklendi!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Lütfen bir varlık seçin.")

    st.divider()
    st.subheader("🗑️ Sil")
    if not portfoy_df.empty:
        silinecek = st.selectbox("Silinecek Varlık", portfoy_df["Kod"].unique())
        if st.button("Seçileni Sil"):
            portfoy_df = portfoy_df[portfoy_df["Kod"] != silinecek]
            save_data_to_sheet(portfoy_df)
            st.rerun()

# --- HESAPLAMA MOTORU ---
def sembol_getir(kod, pazar):
    if pazar == "BIST": return f"{kod}.IS"
    elif pazar == "KRIPTO": return f"{kod}-USD"
    elif pazar == "EMTIA": 
        # Yahoo Finance kodları ile eşleştirme
        if "Altın" in kod and "Ons" not in kod: return "GC=F" # Basit eşleştirme
        return kod 
    else: return kod

def veri_analizi(df, usd_try_rate):
    analiz_listesi = []
    
    prog_bar = st.progress(0)
    status_text = st.empty()
    
    for i, row in df.iterrows():
        prog_bar.progress((i + 1) / len(df))
        status_text.text(f"Veri çekiliyor: {row['Kod']}")
        
        sym = sembol_getir(row["Kod"], row["Pazar"])
        fiyat = 0
        para_birimi = "TL" if row["Pazar"] == "BIST" else "USD"
        
        if row["Pazar"] == "FIZIKI":
            fiyat = row["Maliyet"] 
        else:
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    fiyat = hist['Close'].iloc[-1]
                else:
                    fiyat = row["Maliyet"]
            except:
                fiyat = row["Maliyet"]

        adet = row["Adet"]
        maliyet = row["Maliyet"]
        guncel_deger = fiyat * adet
        toplam_maliyet = maliyet * adet
        
        pnl = guncel_deger - toplam_maliyet
        pnl_yuzde = (pnl / toplam_maliyet * 100) if toplam_maliyet > 0 else 0
        
        if para_birimi == "USD":
            tl_deger = guncel_deger * usd_try_rate
            tl_maliyet = toplam_maliyet * usd_try_rate
        else:
            tl_deger = guncel_deger
            tl_maliyet = toplam_maliyet
            
        analiz_listesi.append({
            "Kod": row["Kod"],
            "Pazar": row["Pazar"],
            "Tip": row["Tip"],
            "Adet": adet,
            "Ort. Maliyet": maliyet,
            "Anlık Fiyat": fiyat,
            "Para Birimi": para_birimi,
            "Varlık Değeri": guncel_deger,
            "P/L": pnl,
            "P/L %": pnl_yuzde,
            "TL Değer": tl_deger,
            "TL Maliyet": tl_maliyet,
            "Notlar": row["Notlar"]
        })
        
    prog_bar.empty()
    status_text.empty()
    return pd.DataFrame(analiz_listesi)

# --- ANA EKRAN VE SEKMELER ---
if portfoy_df.empty:
    st.info("Sol menüden portföyünüze veya takip listenize varlık ekleyin.")
else:
    master_df = veri_analizi(portfoy_df, USD_TRY)
    portfoy_only = master_df[master_df["Tip"] == "Portfoy"]
    takip_only = master_df[master_df["Tip"] == "Takip"]

    tab_ozet, tab_kripto, tab_bist, tab_abd, tab_emtia, tab_fiziki, tab_takip = st.tabs([
        "🏠 Genel Özet", "₿ Kripto", "📈 BIST", "🇺🇸 ABD", "🛢️ Emtia", "🏠 Fiziki", "👀 Takip Listesi"
    ])

    # --- TAB 1: GENEL ÖZET (DASHBOARD) ---
    with tab_ozet:
        if not portfoy_only.empty:
            toplam_varlik = portfoy_only["TL Değer"].sum()
            toplam_maliyet = portfoy_only["TL Maliyet"].sum()
            genel_kar = toplam_varlik - toplam_maliyet
            genel_yuzde = (genel_kar / toplam_maliyet * 100) if toplam_maliyet > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Varlık (TL)", f"₺{toplam_varlik:,.2f}")
            c2.metric("Toplam Maliyet (TL)", f"₺{toplam_maliyet:,.2f}")
            c3.metric("Genel Kâr/Zarar (TL)", f"₺{genel_kar:,.2f}", delta=f"%{genel_yuzde:.2f}")
            
            st.divider()
            st.subheader("Varlık Dağılımı")
            pazar_gruplu = portfoy_only.groupby("Pazar")["TL Değer"].sum().reset_index()
            st.bar_chart(pazar_gruplu, x="Pazar", y="TL Değer", color="#4CAF50")
        else:
            st.warning("Portföyünüz boş.")

    # --- YARDIMCI FONKSİYON: TABLO YARATICI ---
    def create_asset_table(df_subset, currency_symbol):
        if df_subset.empty:
            st.info("Bu kategoride varlık yok.")
            return
        
        sub_val = df_subset["Varlık Değeri"].sum()
        sub_pnl = sub_val - (df_subset["Adet"] * df_subset["Ort. Maliyet"]).sum()
        
        k1, k2, k3 = st.columns(3)
        k1.metric(f"Toplam Değer ({currency_symbol})", f"{sub_val:,.2f}")
        k3.metric(f"Kâr/Zarar ({currency_symbol})", f"{sub_pnl:,.2f}", delta_color="normal")
        
        display_df = df_subset[[
            "Kod", "Adet", "Ort. Maliyet", "Anlık Fiyat", 
            "Varlık Değeri", "P/L", "P/L %", "Notlar"
        ]].copy()
        
        def color_pnl(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
            return f'color: {color}'

        st.dataframe(
            display_df.style.format({
                "Ort. Maliyet": "{:.2f}", "Anlık Fiyat": "{:.2f}",
                "Varlık Değeri": "{:.2f}", "P/L": "{:.2f}", "P/L %": "{:.2f}%"
            }).applymap(color_pnl, subset=['P/L', 'P/L %'])
        )

    with tab_kripto: create_asset_table(portfoy_only[portfoy_only["Pazar"] == "KRIPTO"], "$")
    with tab_bist: create_asset_table(portfoy_only[portfoy_only["Pazar"] == "BIST"], "₺")
    with tab_abd: create_asset_table(portfoy_only[portfoy_only["Pazar"] == "ABD"], "$")
    with tab_emtia: create_asset_table(portfoy_only[portfoy_only["Pazar"] == "EMTIA"], "$")
    with tab_fiziki: create_asset_table(portfoy_only[portfoy_only["Pazar"] == "FIZIKI"], "Birim")
    
    with tab_takip:
        st.header("👀 İzleme Listesi")
        if not takip_only.empty:
            watch_df = takip_only[["Kod", "Pazar", "Anlık Fiyat", "Para Birimi", "Notlar"]].copy()
            st.dataframe(watch_df.style.format({"Anlık Fiyat": "{:.2f}"}))
        else:
            st.info("Takip listeniz boş.")

